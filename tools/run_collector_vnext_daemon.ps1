# path: ./tools/run_collector_vnext_daemon.ps1
# desc: Safe smoke-daemon launcher for Collector vNext with repo-local PYTHONPATH and configurable loop interval.

$ErrorActionPreference = 'Stop'

$repoRoot = 'C:\BtcTradeSystem'
$srcRoot = Join-Path $repoRoot 'btcts_next\src'
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'

$env:PYTHONPATH = $srcRoot

if (-not $env:BTCTS_WS_SSL_VERIFY) {
    $env:BTCTS_WS_SSL_VERIFY = 'false'
}

if (-not $env:BTCTS_LOOP_INTERVAL_SEC) {
    $env:BTCTS_LOOP_INTERVAL_SEC = '15'
}

if (-not $env:BTCTS_MAX_FAILURES) {
    $env:BTCTS_MAX_FAILURES = '10'
}

if (-not $env:BTCTS_FAILURE_BACKOFF_SEC) {
    $env:BTCTS_FAILURE_BACKOFF_SEC = '10'
}

Write-Host "[collector_vnext] starting daemon with single-instance lock..."
& $pythonExe -m btcts.collector_vnext.daemon