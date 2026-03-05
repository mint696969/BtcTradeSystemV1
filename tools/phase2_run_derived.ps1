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
$runnerPid = $PID
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
$env:PYTHONPATH        = (Join-Path $RepoRoot "btcts_next\src")
$env:BTC_TS_CONFIG_DIR = (Join-Path $RepoRoot "btcts_next\config\ui")
$env:BTC_TS_DATA_DIR   = (Join-Path $RepoRoot "btcts_next\data")
$env:BTC_TS_LOGS_DIR   = (Join-Path $RepoRoot "btcts_next\logs")
$env:BTC_TS_MODE       = $Mode

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

function New-RunnerLock {
  if (Test-Path -LiteralPath $lockPath) {
    $stale = $false
    $lockPid = $null
    try {
      $raw = Get-Content -LiteralPath $lockPath -Raw -Encoding UTF8
      if ($raw) {
        $j = $raw | ConvertFrom-Json
        $lockPid = $j.pid
      }
    } catch {}

    if ($lockPid) {
      $proc = Get-Process -Id $lockPid -ErrorAction SilentlyContinue
      if (-not $proc) { $stale = $true }
    } else {
      $stale = $true
    }

    if ($Force -and $stale) {
      Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
    } else {
      throw "lock busy: $lockPath (use -Force only if stale)"
    }
  }

  # CreateNew 相当（排他）: 既存なら例外
  $fs = [System.IO.File]::Open($lockPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
  try {
    $payload = @{
      pid = $runnerPid
      host = $env:COMPUTERNAME
      start_utc = (NowIsoUtc)
      repo_root = $RepoRoot
      mode = $Mode
      hourly_every_sec = $HourlyEverySec
      daily_every_sec  = $DailyEverySec
      duration_hours   = $DurationHours
      once = [bool]$Once
    } | ConvertTo-Json -Depth 10
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
    $fs.Write($bytes, 0, $bytes.Length)
  } finally {
    $fs.Close()
  }
}

function Remove-RunnerLock {
  Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
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
New-RunnerLock
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
  Remove-RunnerLock
  if (-not $reason) { $reason = "exit" }
  Add-Log "INFO" "derived_runner.exit reason=$reason"
  Add-Jsonl @{ level="INFO"; event="runner.exit"; reason=$reason; last_error=$lastError }
}
