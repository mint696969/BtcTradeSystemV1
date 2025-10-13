# path: scripts/handoff/make_handoff.ps1
# desc: チャットまたぎ用ハンドオフZIPを作成（最小構成）

param(
  [int]$AuditTail = 200,
  [int]$StatusItems = 50
)

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

# --- ルートと出力先 ---
$V1   = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)   # .../BtcTradeSystemV1
$OUT  = Join-Path $V1 "docs\handoff"
$TMP  = Join-Path $OUT ("_tmp_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force $OUT,$TMP | Out-Null

# --- パス定義 ---
$PKG  = Join-Path $V1 "btc_trade_system"
$DATA = $env:BTC_TS_DATA_DIR
if (-not $DATA) { $DATA = "D:\BtcTS_V1\data" }
$LOGS = $env:BTC_TS_LOGS_DIR
if (-not $LOGS) { $LOGS = "D:\BtcTS_V1\logs" }

# --- 1) 有効設定・しきい値 ---
$cfgOut = Join-Path $TMP "config"
New-Item -ItemType Directory -Force $cfgOut | Out-Null
Copy-Item (Join-Path $PKG "config\ui\health.yaml")      -Destination (Join-Path $cfgOut "health.yaml")       -ErrorAction SilentlyContinue
Copy-Item (Join-Path $PKG "config\ui\monitoring.yaml")  -Destination (Join-Path $cfgOut "monitoring.yaml")   -ErrorAction SilentlyContinue
Copy-Item (Join-Path $PKG "config\ui_defaults\health.yaml")     (Join-Path $cfgOut "health.defaults.yaml")     -ErrorAction SilentlyContinue
Copy-Item (Join-Path $PKG "config\ui_defaults\monitoring.yaml") (Join-Path $cfgOut "monitoring.defaults.yaml") -ErrorAction SilentlyContinue

# --- 2) ステータス・監査抜粋 ---
$diagOut = Join-Path $TMP "diagnostics"
New-Item -ItemType Directory -Force $diagOut | Out-Null

$st = Join-Path $DATA "collector\status.json"
if (Test-Path $st) {
  # 最近の items だけ抜粋
  $json = Get-Content $st -Raw | ConvertFrom-Json
  $items = @($json.items) | Select-Object -First $StatusItems
  $o = [pscustomobject]@{
    extracted_at = (Get-Date).ToUniversalTime().ToString("s") + "Z"
    items        = $items
  } | ConvertTo-Json -Depth 10
  $o | Set-Content -Encoding UTF8 (Join-Path $diagOut "status_excerpt.json")
}

$audit = Join-Path $LOGS "audit.jsonl"
if (Test-Path $audit) {
  Get-Content $audit -Tail $AuditTail | Set-Content -Encoding UTF8 (Join-Path $diagOut "audit.tail.jsonl")
}

# --- 3) 環境情報 ---
$envOut = Join-Path $TMP "env"
New-Item -ItemType Directory -Force $envOut | Out-Null
$pyCmd = Get-Command python -ErrorAction SilentlyContinue
$py    = if ($pyCmd) { $pyCmd.Path } else { $null }
@"
repo_root:  $V1
python:     $py
DATA_DIR:   $DATA
LOGS_DIR:   $LOGS
when_utc:   $((Get-Date).ToUniversalTime().ToString("s"))Z
"@ | Set-Content -Encoding UTF8 (Join-Path $envOut "environment.txt")

# --- 4) リポジトリMAP（簡易） ---
$map = Join-Path $TMP "REPO_MAP.txt"
Get-ChildItem $V1 -Recurse -File | ForEach-Object {
  $_.FullName.Substring($V1.Length+1)
} | Sort-Object | Set-Content -Encoding UTF8 $map

# --- 5) 起動手順（人向け） ---
@"
# BtcTradeSystemV1 Handoff QuickStart

## 起動（ダッシュボード）
`powershell`:
  & `"$V1\scripts\run.ps1"`

## WhatIf（環境確認のみ）
  & `"$V1\scripts\run.ps1"` -WhatIf

## データ/ログ実体
  DATA = $DATA
  LOGS = $LOGS

## 参考
- config\health.yaml / monitoring.yaml : UIで保存した有効設定
- diagnostics\status_excerpt.json : 最新 status 抜粋
- diagnostics\audit.tail.jsonl : 監査末尾
"@ | Set-Content -Encoding UTF8 (Join-Path $TMP "README_HANDOFF.md")

# --- 6) サマリー（Pythonで整形） ---
$pyTool = Join-Path $V1 "tools\handoff\gen_summary.py"
if (Test-Path $pyTool) {
  python $pyTool --v1 "$V1" --data "$DATA" --logs "$LOGS" --out (Join-Path $TMP "SUMMARY.md") 2>$null
}

# --- 7) ZIP化 ---
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$zip = Join-Path $OUT ("Handoff_" + $stamp + ".zip")
if (Test-Path $zip) { Remove-Item $zip -Force }
Add-Type -AssemblyName 'System.IO.Compression.FileSystem'
[System.IO.Compression.ZipFile]::CreateFromDirectory($TMP, $zip)

Write-Host "OK: $zip"
# 後片付け
Remove-Item $TMP -Recurse -Force
