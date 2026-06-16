# path: ./tools/run_operator_ui_sr_fx_dhot.ps1
# desc: Launch Operator UI against D-hot SR-FX. Collector tab Start inherits this env and starts the correct Unified watchdog.

param(
  [int]$Port = 501
)

$ErrorActionPreference = "Stop"
Set-Location C:\BtcTradeSystem

$Py = ".\.venv\Scripts\python.exe"
if (!(Test-Path $Py)) {
  throw "Python venv not found: $Py"
}

$env:PYTHONPATH = "C:\BtcTradeSystem\btcts_next\src"

# D-hot realtime roots. E-cold and D:\BtcTS_V1 are not runtime success evidence.
$env:BTC_TS_DATA_DIR = "D:\btc_ts_hot\data"
$env:BTC_TS_LOGS_DIR = "D:\btc_ts_hot\logs"
$env:BTCTS_STATE_ROOT = "D:\btc_ts_hot\state"
$env:BTCTS_DATA_ROOT = "D:\btc_ts_hot\data"
$env:BTCTS_LOGS_ROOT = "D:\btc_ts_hot\logs"

# Current execution market identity.
$env:BTCTS_MARKET = "fx"
$env:BTCTS_SYMBOL = "FX_BTC_JPY"
$env:BTCTS_INSTRUMENT_ID = "bitflyer.fx.FX_BTC_JPY"
$env:BTCTS_EXECUTION_PRODUCT_CODE = "FX_BTC_JPY"
$env:BTCTS_EXECUTION_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"
$env:BTCTS_EXECUTION_MARKET_TYPE = "fx"
$env:BTCTS_MARKET_ENGINE_EXCHANGE = "bitflyer"
$env:BTCTS_MARKET_ENGINE_SYMBOL = "FX_BTC_JPY"
$env:BTCTS_MARKET_ENGINE_INSTRUMENT_ID = "bitflyer.fx.FX_BTC_JPY"
$env:BTCTS_MARKET_ENGINE_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"
$env:BTCTS_MARKET_ENGINE_PROFILE = "bitflyer"
$env:BTCTS_MARKET_ENGINE_WRITE_MARKET_STATE = "true"

# This is required because the Collector tab launches the hidden watchdog from
# the Operator UI process environment via stack_control.start_stack_detached().
$env:BTCTS_UNIFIED_MARKET_STATE_ENABLED = "true"

# Unified daemon tuning inherited by Collector tab Start.
if (-not $env:BTCTS_UNIFIED_LOOP_SLEEP_SEC) { $env:BTCTS_UNIFIED_LOOP_SLEEP_SEC = "0.25" }
if (-not $env:BTCTS_UNIFIED_MAX_FAILURES) { $env:BTCTS_UNIFIED_MAX_FAILURES = "20" }
if (-not $env:BTCTS_UNIFIED_FAILURE_BACKOFF_SEC) { $env:BTCTS_UNIFIED_FAILURE_BACKOFF_SEC = "3" }
if (-not $env:BTCTS_UNIFIED_WS_BOARD_RECONNECT_BACKOFF_SEC) { $env:BTCTS_UNIFIED_WS_BOARD_RECONNECT_BACKOFF_SEC = "2" }
if (-not $env:BTCTS_UNIFIED_WS_EXECUTIONS_RECONNECT_BACKOFF_SEC) { $env:BTCTS_UNIFIED_WS_EXECUTIONS_RECONNECT_BACKOFF_SEC = "2" }
if (-not $env:BTCTS_UNIFIED_GRACEFUL_TIMEOUT_SEC) { $env:BTCTS_UNIFIED_GRACEFUL_TIMEOUT_SEC = "30" }
if (-not $env:BTCTS_UNIFIED_SUPERVISOR_BACKOFF_SEC) { $env:BTCTS_UNIFIED_SUPERVISOR_BACKOFF_SEC = "3" }
if (-not $env:BTCTS_UNIFIED_SUPERVISOR_MAX_FAILURES) { $env:BTCTS_UNIFIED_SUPERVISOR_MAX_FAILURES = "10" }

# Prefer verified TLS. Discover certifi from the same venv when not provided.
if (-not $env:BTCTS_WS_SSL_VERIFY) { $env:BTCTS_WS_SSL_VERIFY = "true" }
if (-not $env:BTCTS_WS_CA_FILE) {
  $certifiPath = & $Py -c "import certifi; print(certifi.where())" 2>$null
  if ($LASTEXITCODE -eq 0 -and $certifiPath -and (Test-Path $certifiPath)) {
    $env:BTCTS_WS_CA_FILE = $certifiPath
  }
}

Write-Host "[operator-ui-srfx-dhot] repo=C:\BtcTradeSystem"
Write-Host "[operator-ui-srfx-dhot] python=$Py"
Write-Host "[operator-ui-srfx-dhot] data=$env:BTC_TS_DATA_DIR"
Write-Host "[operator-ui-srfx-dhot] logs=$env:BTC_TS_LOGS_DIR"
Write-Host "[operator-ui-srfx-dhot] state=$env:BTCTS_STATE_ROOT"
Write-Host "[operator-ui-srfx-dhot] symbol=$env:BTCTS_SYMBOL"
Write-Host "[operator-ui-srfx-dhot] market_uid=$env:BTCTS_EXECUTION_MARKET_UID"
Write-Host "[operator-ui-srfx-dhot] market_state_lane=$env:BTCTS_UNIFIED_MARKET_STATE_ENABLED"
Write-Host "[operator-ui-srfx-dhot] ws_ssl_verify=$env:BTCTS_WS_SSL_VERIFY"
Write-Host "[operator-ui-srfx-dhot] ws_ca_file=$env:BTCTS_WS_CA_FILE"
Write-Host "[operator-ui-srfx-dhot] port=$Port"
Write-Host "[operator-ui-srfx-dhot] read_only=true would_send_to_broker=false"
Write-Host "[operator-ui-srfx-dhot] Collector tab Start/Safe Stop is the normal watchdog control path."

& $Py -m streamlit run btcts_next\src\btcts\apps\operator_ui\app.py --server.port $Port
exit $LASTEXITCODE
