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

function NowIsoUtc {
  return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
}

function Ensure-Dir([string]$p) {
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

Ensure-Dir $env:BTC_TS_CONFIG_DIR
Ensure-Dir $env:BTC_TS_DATA_DIR
Ensure-Dir $env:BTC_TS_LOGS_DIR

$derivedDir = Join-Path $env:BTC_TS_LOGS_DIR "derived"
Ensure-Dir $derivedDir

$lockPath  = Join-Path $derivedDir "derived_runner.lock"
$logPath   = Join-Path $derivedDir "derived_runner.log"
$jsonlPath = Join-Path $derivedDir "derived_runner.jsonl"

function Add-Jsonl([hashtable]$obj) {
  $obj.ts = (NowIsoUtc)
  $line = ($obj | ConvertTo-Json -Compress -Depth 20)
  Add-Content -LiteralPath $jsonlPath -Value $line -Encoding UTF8
}
function Add-Log([string]$level, [string]$msg) {
  $line = "[{0}][{1}] {2}" -f (NowIsoUtc), $level, $msg
  Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
}

function Acquire-Lock {
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
      pid = $PID
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

function Release-Lock {
  Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
}

function Latest-Hourly-Day {
  # hourly_YYYYMMDD_HH.json を走査して最新日(YYYYMMDD)を返す
  $days = @()
  Get-ChildItem -LiteralPath $derivedDir -Filter "hourly_????????_??.json" -File -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.Name -match '^hourly_(\d{8})_\d{2}\.json$') { $days += $Matches[1] }
  }
  if ($days.Count -eq 0) { return $null }
  return ($days | Sort-Object)[-1]
}

function Run-Py([string[]]$PyArgs, [string]$EventName) {
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
Acquire-Lock
Add-Log "INFO" "derived_runner.start repo=$RepoRoot mode=$Mode"
Add-Jsonl @{ level="INFO"; event="runner.start"; repo_root=$RepoRoot; mode=$Mode }

$startUtc = (Get-Date).ToUniversalTime()
$nextHourly = (Get-Date).ToUniversalTime()   # 起動直後に1回
$nextDaily  = (Get-Date).ToUniversalTime()   # 起動直後に1回

try {
  while ($true) {
    $now = (Get-Date).ToUniversalTime()

    if ($DurationHours -gt 0) {
      $elapsed = ($now - $startUtc).TotalHours
      if ($elapsed -ge $DurationHours) {
        Add-Log "INFO" "runner.stop duration reached hours=$([math]::Round($elapsed,2))"
        Add-Jsonl @{ level="INFO"; event="runner.stop.duration"; elapsed_hours=$elapsed }
        break
      }
    }

    if ($Once) {
      # hourly → daily を1回ずつ
      [void](Run-Py -PyArgs @("-m","btcts.derived.hourly") -EventName "hourly")
      $day = Latest-Hourly-Day
      if ($day) {
        [void](Run-Py -PyArgs @("-m","btcts.derived.daily","--day",$day) -EventName "daily")
      } else {
        [void](Run-Py -PyArgs @("-m","btcts.derived.daily") -EventName "daily")
      }
      Add-Log "INFO" "runner.stop once"
      Add-Jsonl @{ level="INFO"; event="runner.stop.once" }
      break
    }

    if ($now -ge $nextHourly) {
      [void](Run-Py -PyArgs @("-m","btcts.derived.hourly") -EventName "hourly")
      $nextHourly = $now.AddSeconds([double]$HourlyEverySec)
    }

    if ($now -ge $nextDaily) {
      # daily は「hourly が存在する最新日」を明示指定して空サマリを避ける
      $day = Latest-Hourly-Day
      if ($day) {
        [void](Run-Py -PyArgs @("-m","btcts.derived.daily","--day",$day) -EventName "daily")
      } else {
        [void](Run-Py -PyArgs @("-m","btcts.derived.daily") -EventName "daily")
      }
      $nextDaily = $now.AddSeconds([double]$DailyEverySec)
    }

    Start-Sleep -Seconds 5
  }
}
finally {
  Release-Lock
  Add-Log "INFO" "derived_runner.exit"
  Add-Jsonl @{ level="INFO"; event="runner.exit" }
}
