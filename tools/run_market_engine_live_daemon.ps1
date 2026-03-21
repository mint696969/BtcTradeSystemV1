# path: ./tools/run_market_engine_live_daemon.ps1
# desc: Launcher for Market Engine live runtime using canonical board snapshot/diff inputs.

param(
  [string]$PythonPath = "C:\BtcTradeSystem\btcts_next\src",
  [string]$DataDir = "D:\btc_ts_hot\data",
  [int]$PollSec = 1,
  [int]$RuntimeSeconds = 3600
)

$env:PYTHONPATH = $PythonPath
$env:BTC_TS_DATA_DIR = $DataDir
$env:BTCTS_MARKET_ENGINE_LIVE_POLL_SEC = "$PollSec"
$env:BTCTS_MARKET_ENGINE_LIVE_SECONDS = "$RuntimeSeconds"

Set-Location "C:\BtcTradeSystem"
python .\tools\run_market_engine_live_runtime.py