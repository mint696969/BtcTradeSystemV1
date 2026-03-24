# path: ./tools/run_collector_vnext_exploration_daemon.ps1
# desc: Exploration-first launcher for Collector vNext with repo-local PYTHONPATH and repo venv python.

param(
    [switch]$NoPause
)

$ErrorActionPreference = 'Stop'

$repoRoot = 'C:\BtcTradeSystem'
$srcRoot = Join-Path $repoRoot 'btcts_next\src'
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'

$env:PYTHONPATH = $srcRoot

if (-not $env:BTCTS_WS_SSL_VERIFY) {
    $env:BTCTS_WS_SSL_VERIFY = 'false'
}

if (-not $env:BTCTS_DATA_ROOT) {
    $env:BTCTS_DATA_ROOT = 'D:\btc_ts_hot\data'
}

if (-not $env:BTCTS_LOGS_ROOT) {
    $env:BTCTS_LOGS_ROOT = 'D:\btc_ts_hot\logs'
}

if (-not $env:BTCTS_STATE_ROOT) {
    $env:BTCTS_STATE_ROOT = 'D:\btc_ts_hot\state'
}

$env:BTC_TS_DATA_DIR = $env:BTCTS_DATA_ROOT
$env:BTC_TS_LOGS_DIR = $env:BTCTS_LOGS_ROOT

if (-not $env:BTC_TS_DATA_DIR) {
    $env:BTC_TS_DATA_DIR = $env:BTCTS_DATA_ROOT
}

if (-not $env:BTC_TS_LOGS_DIR) {
    $env:BTC_TS_LOGS_DIR = $env:BTCTS_LOGS_ROOT
}

if (-not $env:BTCTS_EXPLORATION_LOOP_SLEEP_SEC) {
    $env:BTCTS_EXPLORATION_LOOP_SLEEP_SEC = '0.25'
}

& $pythonExe -m btcts.collector_vnext.exploration_daemon

if (-not $NoPause) {
    Write-Host ''
    Read-Host 'Press Enter to exit'
}