# path: ./scripts/run.ps1
# desc: Streamlit ダッシュボード起動（PYTHONPATH=リポ直下、venv優先起動／WhatIf対応）
param([switch]$WhatIf)

# --- ENV: DATA/LOGS 既定値（未設定時のみ） -------------------------------
if (-not $env:BTC_TS_DATA_DIR)  { $env:BTC_TS_DATA_DIR  = 'D:\BtcTS_V1\data' }
if (-not $env:BTC_TS_LOGS_DIR)  { $env:BTC_TS_LOGS_DIR  = 'D:\BtcTS_V1\logs' }

# --- リポ直下を解決し、PYTHONPATH を設定 ----------------------------------
# scripts/ の 1 つ上=リポルート
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot
$env:PYTHONPATH = (Get-Location).Path

# --- Python 実行体（venv 優先、なければシステム python） -----------------
$py = ".\.venv\Scripts\python.exe"; if (-not (Test-Path $py)) { $py = "python" }

# --- ダッシュボード エントリ ------------------------------------------------
$dash = Join-Path $repoRoot "btc_trade_system\apps\dashboard.py"

# --- ダイアグ表示 -----------------------------------------------------------
Write-Host "DATA=$env:BTC_TS_DATA_DIR"
Write-Host "LOGS=$env:BTC_TS_LOGS_DIR"
Write-Host "PYTHONPATH=$env:PYTHONPATH"
Write-Host "PYTHON=$py"
Write-Host "DASH=$dash"

if ($WhatIf) { Write-Host 'OK: 環境/パス検証のみ'; exit 0 }

# --- Streamlit 起動 ---------------------------------------------------------
& $py -m streamlit run $dash
