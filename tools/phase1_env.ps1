# path: ./tools/phase1_env.ps1
# desc: Phase1テスト用のENV正準化（PYTHONPATH/各DIR/DEBUG）をセットする。

[CmdletBinding()]
param(
  [string]$RepoRoot = "C:\BtcTradeSystem",
  [string]$Mode = "DEBUG"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$env:PYTHONPATH      = Join-Path $RepoRoot "btcts_next\src"
$env:BTC_TS_MODE     = $Mode
$env:BTC_TS_CONFIG_DIR = Join-Path $RepoRoot "btcts_next\config\ui"
$env:BTC_TS_DATA_DIR   = Join-Path $RepoRoot "btcts_next\data"
$env:BTC_TS_LOGS_DIR   = Join-Path $RepoRoot "btcts_next\logs"

# dirs
New-Item -ItemType Directory -Force -Path $env:BTC_TS_CONFIG_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $env:BTC_TS_DATA_DIR   | Out-Null
New-Item -ItemType Directory -Force -Path $env:BTC_TS_LOGS_DIR   | Out-Null

python -c "import btcts; from btcts.core import env; print('OK', env.config_dir(), env.data_dir(), env.logs_dir())"
python -c "from btcts.settings import svc; print('ready=', svc.exchanges_ready())"