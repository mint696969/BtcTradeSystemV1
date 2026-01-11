# path: ./scripts/run.ps1
# desc: 起動ラッパ（ENV設定→ python -m / streamlit run）。Target で legacy/next/collector を切替、PYTHONPATH に btcts_next/src を必ず含める。
param(
  [ValidateSet('legacy','next','collector')]
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
$dashNext   = Join-Path $repoRoot "btcts_next\src\btcts\ui\app.py"

Write-Host "TARGET=$Target"
Write-Host "DATA=$env:BTC_TS_DATA_DIR"
Write-Host "LOGS=$env:BTC_TS_LOGS_DIR"
Write-Host "CONFIG=$env:BTC_TS_CONFIG_DIR"
Write-Host "PYTHONPATH=$env:PYTHONPATH"
Write-Host "PYTHON=$py"

if ($WhatIf) { Write-Host 'OK: 環境/パス検証のみ'; exit 0 }

if ($Target -eq 'collector') {
  Write-Host "RUN: $py -m btcts.collector.main"
  & $py -m btcts.collector.main
  exit $LASTEXITCODE
}

if ($Target -eq 'legacy') {
  Write-Host "DASH=$dashLegacy"
  & $py -m streamlit run $dashLegacy
  exit $LASTEXITCODE
}

# default: next
Write-Host "DASH=$dashNext"
& $py -m streamlit run $dashNext
exit $LASTEXITCODE
