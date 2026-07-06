# path: ./tools/refresh_warroom_plain_candles.ps1
# desc: Non-UI bounded WarRoom plain trade candle cache refresh launcher. Reads D-hot market.trade and writes D-hot derived latest cache.

param(
  [string]$RawRoot = "D:\btc_ts_hot",
  [string]$CacheRoot = "D:\btc_ts_hot",
  [string]$Exchange = "bitflyer",
  [string]$Symbol = "FX_BTC_JPY",
  [int]$TimeframeSec = 60,
  [int]$RangeMinutes = 180,
  [int]$MaxFiles = 8,
  [int]$MaxTrades = 500000,
  [int]$LatestScanDays = 7,
  [int]$LatestScanFilesPerDay = 24,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Py = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
  $Py = "python"
}

$env:PYTHONPATH = Join-Path $RepoRoot "btcts_next\src"

$ArgsList = @(
  "-m", "btcts.prediction.warroom_plain_candle_refresh",
  "--raw-root", $RawRoot,
  "--cache-root", $CacheRoot,
  "--exchange", $Exchange,
  "--symbol", $Symbol,
  "--timeframe-sec", "$TimeframeSec",
  "--range-minutes", "$RangeMinutes",
  "--max-files", "$MaxFiles",
  "--max-trades", "$MaxTrades",
  "--latest-scan-days", "$LatestScanDays",
  "--latest-scan-files-per-day", "$LatestScanFilesPerDay"
)

Write-Host "[warroom-plain-candles-refresh] repo=$RepoRoot"
Write-Host "[warroom-plain-candles-refresh] python=$Py"
Write-Host "[warroom-plain-candles-refresh] raw_root=$RawRoot"
Write-Host "[warroom-plain-candles-refresh] cache_root=$CacheRoot"
Write-Host "[warroom-plain-candles-refresh] exchange=$Exchange symbol=$Symbol timeframe_sec=$TimeframeSec"
Write-Host "[warroom-plain-candles-refresh] range_minutes=$RangeMinutes max_files=$MaxFiles max_trades=$MaxTrades"
Write-Host "[warroom-plain-candles-refresh] latest_scan_days=$LatestScanDays latest_scan_files_per_day=$LatestScanFilesPerDay"
Write-Host "[warroom-plain-candles-refresh] read_only=true broker_send_enabled=false prediction_invoked=false classifier_invoked=false"
Write-Host "[warroom-plain-candles-refresh] ui_trigger_enabled=false streamlit_invoked=false"

if ($DryRun) {
  Write-Host "[warroom-plain-candles-refresh] dry_run=true command: $Py $($ArgsList -join ' ')"
  exit 0
}

& $Py @ArgsList
exit $LASTEXITCODE
