# path: ./tools/run_collector_vnext_sr_fx_unified_watchdog.ps1
# desc: SR-FX Unified Collector watchdog launcher for D-hot current data. Uses the existing watchdog/daemon path; no ad-hoc loop.

$ErrorActionPreference = "Stop"

$repoRoot = "C:\BtcTradeSystem"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (!(Test-Path $pythonExe)) {
    throw "Python executable not found: $pythonExe"
}

$env:PYTHONPATH = Join-Path $repoRoot "btcts_next\src"

# D hot is the realtime source of truth for Operator UI.
$env:BTC_TS_DATA_DIR = "D:\btc_ts_hot\data"
$env:BTC_TS_LOGS_DIR = "D:\btc_ts_hot\logs"
$env:BTCTS_STATE_ROOT = "D:\btc_ts_hot\state"

# Compatibility bridge.
$env:BTCTS_DATA_ROOT = $env:BTC_TS_DATA_DIR
$env:BTCTS_LOGS_ROOT = $env:BTC_TS_LOGS_DIR

# Legacy collector fields must match the SR-FX execution market because the
# existing unified lanes write paths/channels from cfg.symbol/cfg.instrument_id.
$env:BTCTS_MARKET = "fx"
$env:BTCTS_SYMBOL = "FX_BTC_JPY"
$env:BTCTS_INSTRUMENT_ID = "bitflyer.fx.FX_BTC_JPY"

# Explicit current execution market identity.
$env:BTCTS_EXECUTION_PRODUCT_CODE = "FX_BTC_JPY"
$env:BTCTS_EXECUTION_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"
$env:BTCTS_EXECUTION_MARKET_TYPE = "fx"

# Market Engine L3 output identity. This is the owner of market_state values read by WarRoom.
$env:BTCTS_MARKET_ENGINE_EXCHANGE = "bitflyer"
$env:BTCTS_MARKET_ENGINE_SYMBOL = "FX_BTC_JPY"
$env:BTCTS_MARKET_ENGINE_INSTRUMENT_ID = "bitflyer.fx.FX_BTC_JPY"
$env:BTCTS_MARKET_ENGINE_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"
$env:BTCTS_MARKET_ENGINE_PROFILE = "bitflyer"
$env:BTCTS_MARKET_ENGINE_WRITE_MARKET_STATE = "true"

# Enable the in-daemon L3 market_state lane. This uses the existing unified daemon;
# it is not a separate scheduler/runtime loop and does not belong to the UI.
$env:BTCTS_UNIFIED_MARKET_STATE_ENABLED = "true"

# Unified daemon tuning.
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

# Supervisor tuning.
if (-not $env:BTCTS_UNIFIED_GRACEFUL_TIMEOUT_SEC) {
    $env:BTCTS_UNIFIED_GRACEFUL_TIMEOUT_SEC = "30"
}
if (-not $env:BTCTS_UNIFIED_SUPERVISOR_BACKOFF_SEC) {
    $env:BTCTS_UNIFIED_SUPERVISOR_BACKOFF_SEC = "3"
}
if (-not $env:BTCTS_UNIFIED_SUPERVISOR_MAX_FAILURES) {
    $env:BTCTS_UNIFIED_SUPERVISOR_MAX_FAILURES = "10"
}

# Prefer verified TLS. If the environment needs an explicit bundle and none was
# provided, discover certifi through the same venv Python.
if (-not $env:BTCTS_WS_SSL_VERIFY) {
    $env:BTCTS_WS_SSL_VERIFY = "true"
}
if (-not $env:BTCTS_WS_CA_FILE) {
    $certifiPath = & $pythonExe -c "import certifi; print(certifi.where())" 2>$null
    if ($LASTEXITCODE -eq 0 -and $certifiPath -and (Test-Path $certifiPath)) {
        $env:BTCTS_WS_CA_FILE = $certifiPath
    }
}

Write-Host "[sr-fx-unified-watchdog] repoRoot=$repoRoot"
Write-Host "[sr-fx-unified-watchdog] python=$pythonExe"
Write-Host "[sr-fx-unified-watchdog] data=$env:BTC_TS_DATA_DIR"
Write-Host "[sr-fx-unified-watchdog] logs=$env:BTC_TS_LOGS_DIR"
Write-Host "[sr-fx-unified-watchdog] state=$env:BTCTS_STATE_ROOT"
Write-Host "[sr-fx-unified-watchdog] symbol=$env:BTCTS_SYMBOL"
Write-Host "[sr-fx-unified-watchdog] instrument_id=$env:BTCTS_INSTRUMENT_ID"
Write-Host "[sr-fx-unified-watchdog] market_engine_symbol=$env:BTCTS_MARKET_ENGINE_SYMBOL"
Write-Host "[sr-fx-unified-watchdog] market_engine_uid=$env:BTCTS_MARKET_ENGINE_MARKET_UID"
Write-Host "[sr-fx-unified-watchdog] market_state_lane=$env:BTCTS_UNIFIED_MARKET_STATE_ENABLED"
Write-Host "[sr-fx-unified-watchdog] ws_ssl_verify=$env:BTCTS_WS_SSL_VERIFY"
Write-Host "[sr-fx-unified-watchdog] ws_ca_file=$env:BTCTS_WS_CA_FILE"

# Clear completed/stale supervisor request files only when no supervisor lock is alive.
# This prevents a just-completed safe-stop request from immediately stopping the new SR-FX watchdog.
$preflight = @'
import json
from pathlib import Path
from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.lock import is_pid_alive

cfg = load_config()
state = cfg.roots()["state"]
lock_path = state / "unified_supervisor.lock.json"
request_path = state / "unified_supervisor_request.json"
stop_request_path = state / "unified_daemon_stop_request.json"

lock = {}
if lock_path.exists():
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception:
        lock = {"unreadable": True}

pid = lock.get("pid") if isinstance(lock, dict) else None
pid_alive = is_pid_alive(pid) if pid is not None else False
if lock_path.exists() and pid_alive:
    raise SystemExit(json.dumps({
        "ok": False,
        "reason": "active_unified_supervisor_lock_exists",
        "lock_path": str(lock_path),
        "pid": pid,
    }, ensure_ascii=False))

cleared = []
for path in (request_path, stop_request_path):
    if path.exists():
        path.unlink()
        cleared.append(str(path))

print(json.dumps({
    "ok": True,
    "preflight": "cleared_stale_requests_when_no_supervisor_alive",
    "lock_exists": lock_path.exists(),
    "lock_pid": pid,
    "lock_pid_alive": pid_alive,
    "cleared": cleared,
}, ensure_ascii=False))
'@

$preflight | & $pythonExe
if ($LASTEXITCODE -ne 0) {
    throw "SR-FX watchdog preflight failed; active supervisor may still be running. Do not force launch."
}

& $pythonExe -m btcts.collector_vnext.unified_watchdog
exit $LASTEXITCODE
