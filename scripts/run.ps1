# path: scripts/run.ps1
# desc: ダッシュボード/コレクターの起動口（WhatIf対応）
param([switch]$WhatIf)

if (-not $env:BTC_TS_DATA_DIR) { $env:BTC_TS_DATA_DIR = 'D:\BtcTS_V1\data' }
if (-not $env:BTC_TS_LOGS_DIR) { $env:BTC_TS_LOGS_DIR = 'D:\BtcTS_V1\logs' }

# V1ルートを PYTHONPATH に通す（子プロセスに継承）
$env:PYTHONPATH = 'C:\Users\mint777\BtcTradeSystemV1'

Write-Host "DATA=D:\BtcTS_V1\data"
Write-Host "LOGS=D:\BtcTS_V1\logs"
Write-Host "PYTHONPATH="

if ($WhatIf) { Write-Host 'OK: 環境/パス検証のみ'; exit 0 }

# Streamlit 起動
$dash = Join-Path $PSScriptRoot '..\btc_trade_system\apps\dashboard.py'
python -m streamlit run $dash
