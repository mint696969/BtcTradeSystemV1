# path: ./scripts/run.ps1
# desc: 旧起動ラッパ。legacy UI と operator_ui のみを扱う。collector 正式起動は tools/run_collector_vnext_stack.ps1 を使う。
param(
  [ValidateSet('legacy','next')]
  [string]$Target = 'next',
  [switch]$WhatIf
)

# --- ENV: DATA/LOGS/CONFIG 既定値（未設定時のみ） -------------------------
if (-not $env:BTC_TS_DATA_DIR)   { $env:BTC_TS_DATA_DIR   = 'D:\BtcTS_V1\data' }
if (-not $env:BTC_TS_LOGS_DIR)   { $env:BTC_TS_LOGS_DIR   = 'D:\BtcTS_V1\logs' }
if (-not $env:BTC_TS_CONFIG_DIR) { $env:BTC_TS_CONFIG_DIR = 'D:\BtcTS_V1\config\ui' }

# --- リポ直下を解決 ---------------------------------------------------------
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

# --- PYTHONPATH: repoRoot + btcts_next/src を保証（btcts import 用） --------
$src = Join-Path $repoRoot 'btcts_next\src'
$sep = ';'
$env:PYTHONPATH = "$src$sep$repoRoot"

# --- Python 実行体（venv 優先、なければシステム python） -------------------
$py = ".\.venv\Scripts\python.exe"; if (-not (Test-Path $py)) { $py = "python" }

# --- 起動ターゲット ---------------------------------------------------------
$dashLegacy = Join-Path $repoRoot "btc_trade_system\features\dash\dashboard.py"
$dashNext   = Join-Path $repoRoot "btcts_next\src\btcts\apps\operator_ui\app.py"

Write-Host "TARGET=$Target"
Write-Host "DATA=$env:BTC_TS_DATA_DIR"
Write-Host "LOGS=$env:BTC_TS_LOGS_DIR"
Write-Host "CONFIG=$env:BTC_TS_CONFIG_DIR"
Write-Host "PYTHONPATH=$env:PYTHONPATH"
Write-Host "PYTHON=$py"

if ($WhatIf) { Write-Host 'OK: 環境/パス検証のみ'; exit 0 }

if ($Target -eq 'collector') {
  throw "collector target is retired. Use: powershell -ExecutionPolicy Bypass -File C:\BtcTradeSystem\tools\run_collector_vnext_stack.ps1"
}

if ($Target -eq 'legacy') {
  Write-Host "DASH=$dashLegacy"
  & $py -m streamlit run $dashLegacy
  exit $LASTEXITCODE
}

# default: next (= operator_ui)
Write-Host "DASH=$dashNext"
& $py -m streamlit run $dashNext
exit $LASTEXITCODE
