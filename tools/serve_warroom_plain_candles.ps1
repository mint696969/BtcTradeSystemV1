# path: ./tools/serve_warroom_plain_candles.ps1
# desc: Read-only localhost chart data endpoint for WarRoom base candle engine. Serves D-hot derived plain candle cache only.

param(
  [string]$CacheRoot = "D:\btc_ts_hot",
  [string]$HostName = "127.0.0.1",
  [int]$Port = 8765,
  [string]$Exchange = "bitflyer",
  [string]$Symbol = "FX_BTC_JPY",
  [int]$TimeframeSec = 60,
  [int]$MaxCandles = 720
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Py = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
  $Py = "python"
}

$env:PYTHONPATH = Join-Path $RepoRoot "btcts_next\src"
$env:WARROOM_PLAIN_CANDLE_CHART_ENDPOINT = "http://$HostName`:$Port/warroom/plain-candles/latest"

Write-Host "[warroom-plain-candles-serve] repo=$RepoRoot"
Write-Host "[warroom-plain-candles-serve] python=$Py"
Write-Host "[warroom-plain-candles-serve] endpoint=$env:WARROOM_PLAIN_CANDLE_CHART_ENDPOINT"
Write-Host "[warroom-plain-candles-serve] cache_root=$CacheRoot exchange=$Exchange symbol=$Symbol timeframe_sec=$TimeframeSec"
Write-Host "[warroom-plain-candles-serve] read_only=true broker_send_enabled=false order_intent_submitted=false prediction_invoked=false classifier_invoked=false"
Write-Host "[warroom-plain-candles-serve] ui_trigger_enabled=false streamlit_invoked=false"

& $Py -m btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server `
  --host $HostName `
  --port $Port `
  --cache-root $CacheRoot `
  --exchange $Exchange `
  --symbol $Symbol `
  --timeframe-sec $TimeframeSec `
  --max-candles $MaxCandles

exit $LASTEXITCODE
