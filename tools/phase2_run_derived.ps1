# path: ./tools/phase2_run_derived.ps1
# desc: Phase2: derived(hourly/daily) を常時運用で自動生成するランナー（lockで多重起動防止・ログ出力）。
param(
  [ValidateSet("NORMAL","DEBUG","BOOST")]
  [string]$Mode = "NORMAL",

  # hourly の実行間隔（秒）
  [int]$HourlyEverySec = 300,

  # daily の実行間隔（秒）
  [int]$DailyEverySec = 900,

  # 0=無期限、>0=指定時間で終了
  [int]$DurationHours = 0,

  # lock が残っていたら「PIDが死んでる場合のみ」掃除して続行
  [switch]$Force,

  # 1回だけ実行して終了（hourly→daily）
  [switch]$Once
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---- process/meta（StrictMode対策 + 終了理由の記録）----
$reason = ""
$lastError = ""
function NowIsoUtc {
  return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
}

function New-DirIfMissing([string]$p) {
  if (-not (Test-Path -LiteralPath $p)) {
    New-Item -ItemType Directory -Force -Path $p | Out-Null
  }
}

# ---- repo root を推定（tools/ 配下で動く想定）----
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

# ---- ENV 正準化（Phase2運用の既定）----
# 重要: 運用の正本（例: E:\btc_ts\*）を尊重する。未設定時のみ repo フォールバックを入れる。
$env:PYTHONPATH  = (Join-Path $RepoRoot "btcts_next\src")
$env:BTC_TS_MODE = $Mode

if (-not $env:BTC_TS_CONFIG_DIR -or -not $env:BTC_TS_CONFIG_DIR.Trim()) {
  $env:BTC_TS_CONFIG_DIR = (Join-Path $RepoRoot "btcts_next\config\ui")
}
if (-not $env:BTC_TS_DATA_DIR -or -not $env:BTC_TS_DATA_DIR.Trim()) {
  $env:BTC_TS_DATA_DIR = (Join-Path $RepoRoot "btcts_next\data")
}
if (-not $env:BTC_TS_LOGS_DIR -or -not $env:BTC_TS_LOGS_DIR.Trim()) {
  $env:BTC_TS_LOGS_DIR = (Join-Path $RepoRoot "btcts_next\logs")
}

New-DirIfMissing $env:BTC_TS_CONFIG_DIR
New-DirIfMissing $env:BTC_TS_DATA_DIR
New-DirIfMissing $env:BTC_TS_LOGS_DIR

$derivedDir = Join-Path $env:BTC_TS_LOGS_DIR "derived"
New-DirIfMissing $derivedDir

$lockPath  = Join-Path $derivedDir "derived_runner.lock"
$logPath   = Join-Path $derivedDir "derived_runner.log"
$jsonlPath = Join-Path $derivedDir "derived_runner.jsonl"

# ---- log archive root（ローテ先）----
$archiveRoot = Join-Path $derivedDir "_archive"
New-DirIfMissing $archiveRoot
function Add-Jsonl([hashtable]$obj) {
  $obj.ts = (NowIsoUtc)
  $line = ($obj | ConvertTo-Json -Compress -Depth 20)
  Add-Content -LiteralPath $jsonlPath -Value $line -Encoding UTF8
}
function Add-Log([string]$level, [string]$msg) {
  $line = "[{0}][{1}] {2}" -f (NowIsoUtc), $level, $msg
  Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
}

function Invoke-LogRotateIfNeeded {
  param(
    [Parameter(Mandatory)][string]$Path,
    [Parameter(Mandatory)][int]$MaxMB,
    [Parameter(Mandatory)][int]$Keep,
    [Parameter(Mandatory)][string]$ArchiveRoot
  )

  if (-not (Test-Path $Path)) { return }

  $fi = Get-Item $Path
  if ($fi.Length -lt ($MaxMB * 1MB)) { return }

  $ts = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss'Z'")
  $archiveDir = Join-Path $ArchiveRoot $ts
  New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null

  $base = [IO.Path]::GetFileNameWithoutExtension($Path)
  $ext  = $fi.Extension
  $dst  = Join-Path $archiveDir ("{0}_{1}{2}" -f $base, $ts, $ext)

  Move-Item -Force -Path $Path -Destination $dst

  # 古いアーカイブを削除（全アーカイブ配下から base_*ext を集めて新しい順に Keep 残す）
  $pattern = "{0}_*{1}" -f $base, $ext
  Get-ChildItem $ArchiveRoot -Recurse -File -Filter $pattern |
    Sort-Object LastWriteTimeUtc -Descending |
    Select-Object -Skip $Keep |
    Remove-Item -Force -ErrorAction SilentlyContinue
}

function Get-ProcessStartUtcOrNull {
  param([Parameter(Mandatory)][int]$Id)
  try {
    $p = Get-Process -Id $Id -ErrorAction Stop
    return $p.StartTime.ToUniversalTime()
  } catch {
    return $null
  }
}

function New-RunnerLock {
  param(
    [Parameter(Mandatory)][string]$LockPath,
    [switch]$Force
  )

  New-DirIfMissing (Split-Path -Parent $LockPath)

  # --- stale lock cleanup ---
  if (Test-Path -LiteralPath $LockPath) {
    $stale = $false
    $lockPid = $null
    $lockStartedUtc = $null

    try {
      $lockObj = Get-Content -LiteralPath $LockPath -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json
      if ($null -ne $lockObj.pid) { $lockPid = [int]$lockObj.pid }
      if ($null -ne $lockObj.started_utc) {
        $lockStartedUtc = [datetime]::Parse($lockObj.started_utc).ToUniversalTime()
      }
    } catch {
      # JSON が壊れてる/読めない = stale 扱い
      $stale = $true
    }

    if ($Force) {
      $stale = $true
    } elseif ($lockPid) {
      $procStartUtc = Get-ProcessStartUtcOrNull -Id $lockPid
      if ($null -eq $procStartUtc) {
        $stale = $true
      } elseif ($lockStartedUtc -and ($procStartUtc -ne $lockStartedUtc)) {
        # PID再利用を検出
        $stale = $true
      }
    } else {
      # pid が無いロックは「古さ」で判定（保守的に 6h）
      try {
        $age = (Get-Date) - (Get-Item -LiteralPath $LockPath).LastWriteTime
        if ($age.TotalHours -ge 6) { $stale = $true }
      } catch {
        $stale = $true
      }
    }

    if ($stale) {
      Remove-Item -LiteralPath $LockPath -Force -ErrorAction SilentlyContinue
    }
  }

  # --- acquire lock (CreateNew + FileShare.None) ---
  try {
    $fs = [System.IO.File]::Open(
      $LockPath,
      [System.IO.FileMode]::CreateNew,
      [System.IO.FileAccess]::ReadWrite,
      [System.IO.FileShare]::None
    )
  } catch {
    throw "lock busy: $LockPath (use -Force only if stale)"
  }

  try {
    $obj = @{
      pid         = $PID
      host        = $env:COMPUTERNAME
      user        = $env:USERNAME
      started_utc = (Get-Date).ToUniversalTime().ToString("o")
    }
    $json  = ($obj | ConvertTo-Json -Compress)
    $bytes = [Text.Encoding]::UTF8.GetBytes($json)

    $fs.Write($bytes, 0, $bytes.Length)
    $fs.Flush()
  } finally {
    $fs.Dispose()
  }

  return $obj
}

function Remove-RunnerLock {
  param([Parameter(Mandatory)][string]$LockPath)
  Remove-Item -LiteralPath $LockPath -Force -ErrorAction SilentlyContinue
}

function Get-LatestHourlyDay {
  # hourly_YYYYMMDD_HH.json を走査して最新日(YYYYMMDD)を返す
  $days = @()
  Get-ChildItem -LiteralPath $derivedDir -Filter "hourly_????????_??.json" -File -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.Name -match '^hourly_(\d{8})_\d{2}\.json$') { $days += $Matches[1] }
  }
  if ($days.Count -eq 0) { return $null }
  return ($days | Sort-Object)[-1]
}

function Invoke-Python([string[]]$PyArgs, [string]$EventName) {
  $py = (Get-Command python -ErrorAction Stop).Source
  $cmd = $py + " " + ($PyArgs -join " ")
  Add-Log "INFO" "$EventName start: $cmd"
  Add-Jsonl @{ level="INFO"; event="$EventName.start"; cmd=$cmd }

  $out = & $py @PyArgs 2>&1
  $txt = ($out -join "`n")

  if ($LASTEXITCODE -ne 0) {
    Add-Log "ERROR" "$EventName failed exit=$LASTEXITCODE"
    Add-Jsonl @{ level="ERROR"; event="$EventName.fail"; exit_code=$LASTEXITCODE; output=$txt }
    return $false
  }

  Add-Log "INFO" "$EventName ok"
  Add-Jsonl @{ level="INFO"; event="$EventName.ok"; output=$txt }
  return $true
}

# ---------------- main ----------------
[void](New-RunnerLock -LockPath $lockPath -Force:$Force)
Add-Log "INFO" "derived_runner.start repo=$RepoRoot mode=$Mode"
Add-Jsonl @{ level="INFO"; event="runner.start"; repo_root=$RepoRoot; mode=$Mode }

$startUtc = (Get-Date).ToUniversalTime()
$nextHourly = (Get-Date).ToUniversalTime()   # 起動直後に1回
$nextDaily  = (Get-Date).ToUniversalTime()   # 起動直後に1回

# StrictMode: 未定義参照で落ちるので事前に初期化
$script:lastTick = $null

try {
  while ($true) {
    $now = (Get-Date).ToUniversalTime()

    # runnerログが肥大化しないように回す（常駐前提）
    Invoke-LogRotateIfNeeded -Path $jsonlPath -MaxMB 20 -Keep 20 -ArchiveRoot $archiveRoot
    Invoke-LogRotateIfNeeded -Path $logPath  -MaxMB 10 -Keep 10 -ArchiveRoot $archiveRoot


    # ---- audit / supervisor logs rotation (long-term safety) ----
    $logsArchiveRoot = Join-Path $env:BTC_TS_LOGS_DIR "_archive"
    New-DirIfMissing $logsArchiveRoot

    Invoke-LogRotateIfNeeded -Path (Join-Path $env:BTC_TS_LOGS_DIR "audit.jsonl") -MaxMB 50 -Keep 20 -ArchiveRoot $logsArchiveRoot
    Invoke-LogRotateIfNeeded -Path (Join-Path $env:BTC_TS_LOGS_DIR "supervisor_collector.jsonl") -MaxMB 50 -Keep 20 -ArchiveRoot $logsArchiveRoot
    Invoke-LogRotateIfNeeded -Path (Join-Path $env:BTC_TS_LOGS_DIR "supervisor_collector.log") -MaxMB 20 -Keep 10 -ArchiveRoot $logsArchiveRoot
    # “生きてる証拠” を60秒に1回だけ出す（解析が楽）
    if (-not $script:lastTick) { $script:lastTick = (Get-Date).ToUniversalTime() }
    if ( ((Get-Date).ToUniversalTime() - $script:lastTick).TotalSeconds -ge 60 ) {
      Add-Jsonl @{ level="DEBUG"; event="runner.tick" }
      $script:lastTick = (Get-Date).ToUniversalTime()
    }

    if ($DurationHours -gt 0) {
      $elapsed = ($now - $startUtc).TotalHours
      if ($elapsed -ge $DurationHours) {
        Add-Log "INFO" "runner.stop duration reached hours=$([math]::Round($elapsed,2))"
        Add-Jsonl @{ level="INFO"; event="runner.stop.duration"; elapsed_hours=$elapsed }
        $reason = "duration"
        break
      }
    }

    if ($Once) {
      # hourly → daily を1回ずつ
      [void](Invoke-Python -PyArgs @("-m","btcts.derived.hourly") -EventName "hourly")
      [void](Invoke-Python -PyArgs @("-m","btcts.quality.coverage") -EventName "coverage")
      [void](Invoke-Python -PyArgs @("-m","btcts.quality.gaps") -EventName "gaps")

      $day = Get-LatestHourlyDay
      if ($day) {
        [void](Invoke-Python -PyArgs @("-m","btcts.derived.daily","--day",$day) -EventName "daily")
        [void](Invoke-Python -PyArgs @("-m","btcts.quality.anomaly") -EventName "anomaly")
      } else {
        [void](Invoke-Python -PyArgs @("-m","btcts.derived.daily") -EventName "daily")
        [void](Invoke-Python -PyArgs @("-m","btcts.quality.anomaly") -EventName "anomaly")
      }
      Add-Log "INFO" "runner.stop once"
      Add-Jsonl @{ level="INFO"; event="runner.stop.once" }
      $reason = "once"
      break
    }

    if ($now -ge $nextHourly) {
      [void](Invoke-Python -PyArgs @("-m","btcts.derived.hourly") -EventName "hourly")
      [void](Invoke-Python -PyArgs @("-m","btcts.quality.coverage") -EventName "coverage")
      [void](Invoke-Python -PyArgs @("-m","btcts.quality.gaps") -EventName "gaps")
      $nextHourly = $now.AddSeconds([double]$HourlyEverySec)
    }

    if ($now -ge $nextDaily) {
      # daily は「hourly が存在する最新日」を明示指定して空サマリを避ける
      $day = Get-LatestHourlyDay
      if ($day) {
        [void](Invoke-Python -PyArgs @("-m","btcts.derived.daily","--day",$day) -EventName "daily")
        [void](Invoke-Python -PyArgs @("-m","btcts.quality.anomaly") -EventName "anomaly")
      } else {
        [void](Invoke-Python -PyArgs @("-m","btcts.derived.daily") -EventName "daily")
        [void](Invoke-Python -PyArgs @("-m","btcts.quality.anomaly") -EventName "anomaly")
      }
      $nextDaily = $now.AddSeconds([double]$DailyEverySec)
    }

    Start-Sleep -Seconds 5
  }
}
catch {
  # “黙って死ぬ”を防ぐ：終了理由と最終例外を必ず残す
  $reason = "exception"
  $lastError = ($_ | Out-String)
  throw
}
finally {
  Remove-RunnerLock -LockPath $lockPath
  if (-not $reason) { $reason = "exit" }
  Add-Log "INFO" "derived_runner.exit reason=$reason"
  Add-Jsonl @{ level="INFO"; event="runner.exit"; reason=$reason; last_error=$lastError }
}
