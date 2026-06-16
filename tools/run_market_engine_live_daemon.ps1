# path: ./tools/run_market_engine_live_daemon.ps1
# desc: Launcher for Market Engine live runtime using canonical board snapshot/diff inputs.

param(
  [string]$PythonPath = "C:\BtcTradeSystem\btcts_next\src",
  [string]$DataDir = "D:\btc_ts_hot\data",
  [int]$PollSec = 1,
  [int]$RuntimeSeconds = 3600
)

$ErrorActionPreference = 'Stop'

$repoRoot = "C:\BtcTradeSystem"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
  throw "python executable not found: $pythonExe"
}

$env:PYTHONPATH = $PythonPath
$env:BTC_TS_DATA_DIR = $DataDir
$env:BTCTS_MARKET_ENGINE_LIVE_POLL_SEC = "$PollSec"
$env:BTCTS_MARKET_ENGINE_LIVE_SECONDS = "$RuntimeSeconds"

Set-Location $repoRoot

Write-Host "[market_engine_live] starting runtime..."
Write-Host "[market_engine_live] python=$pythonExe"
Write-Host "[market_engine_live] data_root=$env:BTC_TS_DATA_DIR"
Write-Host "[market_engine_live] poll_sec=$env:BTCTS_MARKET_ENGINE_LIVE_POLL_SEC"
Write-Host "[market_engine_live] runtime_seconds=$env:BTCTS_MARKET_ENGINE_LIVE_SECONDS"

& $pythonExe .\tools\run_market_engine_live_runtime.py