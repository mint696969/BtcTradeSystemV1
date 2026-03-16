# path: ./tools/run_collector_vnext.ps1
# desc: Safe smoke launcher for Collector vNext with repo-local PYTHONPATH and optional dev WS SSL override.

$ErrorActionPreference = 'Stop'

$repoRoot = 'C:\BtcTradeSystem'
$srcRoot = Join-Path $repoRoot 'btcts_next\src'
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'

$env:PYTHONPATH = $srcRoot

if (-not $env:BTCTS_WS_SSL_VERIFY) {
    $env:BTCTS_WS_SSL_VERIFY = 'false'
}

& $pythonExe -m btcts.collector_vnext.app