# path: ./tools/run_collector_vnext_unified_daemon.ps1
# desc: Unified Collector daemon を D hot 正本で起動する launcher。

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

# 現環境では bitFlyer WS の証明書検証で失敗するため、launcher 側でのみ明示制御する
if (-not $env:BTCTS_WS_SSL_VERIFY) {
    $env:BTCTS_WS_SSL_VERIFY = "false"
}

Write-Host "[unified-daemon] repoRoot=$repoRoot"
Write-Host "[unified-daemon] python=$pythonExe"
Write-Host "[unified-daemon] data=$env:BTC_TS_DATA_DIR"
Write-Host "[unified-daemon] logs=$env:BTC_TS_LOGS_DIR"
Write-Host "[unified-daemon] state=$env:BTCTS_STATE_ROOT"
Write-Host "[unified-daemon] ws_ssl_verify=$env:BTCTS_WS_SSL_VERIFY"

& $pythonExe -m btcts.collector_vnext.unified_daemon
exit $LASTEXITCODE