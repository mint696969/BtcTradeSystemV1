# path: ./tools/run_collector_vnext_unified_watchdog.ps1
# desc: Unified Collector watchdog を D hot 正本で起動する launcher。

$ErrorActionPreference = "Stop"

$repoRoot = "C:\BtcTradeSystem"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

$env:PYTHONPATH = Join-Path $repoRoot "btcts_next\src"

# D hot をリアルタイム正本に固定
$env:BTC_TS_DATA_DIR = "D:\btc_ts_hot\data"
$env:BTC_TS_LOGS_DIR = "D:\btc_ts_hot\logs"
$env:BTCTS_STATE_ROOT = "D:\btc_ts_hot\state"

# 互換 bridge
$env:BTCTS_DATA_ROOT = $env:BTC_TS_DATA_DIR
$env:BTCTS_LOGS_ROOT = $env:BTC_TS_LOGS_DIR

# unified daemon tuning
if (-not $env:BTCTS_UNIFIED_LOOP_SLEEP_SEC) {
    $env:BTCTS_UNIFIED_LOOP_SLEEP_SEC = "0.25"
}
if (-not $env:BTCTS_UNIFIED_MAX_FAILURES) {
    $env:BTCTS_UNIFIED_MAX_FAILURES = "20"
}
if (-not $env:BTCTS_UNIFIED_FAILURE_BACKOFF_SEC) {
    $env:BTCTS_UNIFIED_FAILURE_BACKOFF_SEC = "3"
}
if (-not $env:BTCTS_UNIFIED_WS_BOARD_RECONNECT_BACKOFF_SEC) {
    $env:BTCTS_UNIFIED_WS_BOARD_RECONNECT_BACKOFF_SEC = "2"
}
if (-not $env:BTCTS_UNIFIED_WS_EXECUTIONS_RECONNECT_BACKOFF_SEC) {
    $env:BTCTS_UNIFIED_WS_EXECUTIONS_RECONNECT_BACKOFF_SEC = "2"
}

# supervisor tuning
if (-not $env:BTCTS_UNIFIED_GRACEFUL_TIMEOUT_SEC) {
    $env:BTCTS_UNIFIED_GRACEFUL_TIMEOUT_SEC = "30"
}
if (-not $env:BTCTS_UNIFIED_SUPERVISOR_BACKOFF_SEC) {
    $env:BTCTS_UNIFIED_SUPERVISOR_BACKOFF_SEC = "3"
}
if (-not $env:BTCTS_UNIFIED_SUPERVISOR_MAX_FAILURES) {
    $env:BTCTS_UNIFIED_SUPERVISOR_MAX_FAILURES = "10"
}

# 現環境では bitFlyer WS の証明書検証で失敗するため、launcher 側でのみ明示制御する
if (-not $env:BTCTS_WS_SSL_VERIFY) {
    $env:BTCTS_WS_SSL_VERIFY = "false"
}

Write-Host "[unified-watchdog] repoRoot=$repoRoot"
Write-Host "[unified-watchdog] python=$pythonExe"
Write-Host "[unified-watchdog] data=$env:BTC_TS_DATA_DIR"
Write-Host "[unified-watchdog] logs=$env:BTC_TS_LOGS_DIR"
Write-Host "[unified-watchdog] state=$env:BTCTS_STATE_ROOT"
Write-Host "[unified-watchdog] ws_ssl_verify=$env:BTCTS_WS_SSL_VERIFY"
Write-Host "[unified-watchdog] graceful_timeout_sec=$env:BTCTS_UNIFIED_GRACEFUL_TIMEOUT_SEC"
Write-Host "[unified-watchdog] supervisor_backoff_sec=$env:BTCTS_UNIFIED_SUPERVISOR_BACKOFF_SEC"
Write-Host "[unified-watchdog] supervisor_max_failures=$env:BTCTS_UNIFIED_SUPERVISOR_MAX_FAILURES"

& $pythonExe -m btcts.collector_vnext.unified_watchdog
exit $LASTEXITCODE
   