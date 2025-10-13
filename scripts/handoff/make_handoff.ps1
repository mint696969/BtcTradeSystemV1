# path: scripts/handoff/make_handoff.ps1
# desc: チャットまたぎ用ハンドオフZIPを作成（最小構成）

param(
  [int]$AuditTail = 200,
  [int]$StatusItems = 50,
  [int]$GitCommits = 20,                 # 追加: 直近コミット件数
  [switch]$AutoRpTag,                    # 追加: 自動で rp-* タグを切る
  [string]$RpMemo = "handoff auto",      # 追加: 自動タグに付けるメモ
  [switch]$IncludeGitScripts             # 追加: 希望時のみ scripts/git を同梱
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

# 追記: env_manifest.yaml も作る
$pyVer = if ($py) { & $py -c "import sys;print(sys.version.replace('\n',' '))" } else { "" }
$stVer = try { (& streamlit --version) 2>$null } catch { "" }
@"
repo_root: "$V1"
python:
  path: "$py"
  version: "$pyVer"
streamlit: "$stVer"
env:
  DATA_DIR: "$DATA"
  LOGS_DIR: "$LOGS"
generated_utc: "$((Get-Date).ToUniversalTime().ToString("s"))Z"
"@ | Set-Content -Encoding UTF8 (Join-Path $envOut "env_manifest.yaml")

# --- 4) リポジトリ構造（YAML; 各ファイル先頭2行コメントも） ---
$structOut = Join-Path $TMP "repo_structure.yaml"
$items = @()

Get-ChildItem $V1 -Recurse -File | ForEach-Object {
  $rel = $_.FullName.Substring($V1.Length + 1)
  # 先頭2行だけ安全に読む（バイナリはスキップ）
  $h1 = ""; $h2 = ""
  try {
    $lines = Get-Content -Path $_.FullName -TotalCount 2 -Encoding UTF8 -ErrorAction Stop
    if ($lines.Count -ge 1) { $h1 = $lines[0] }
    if ($lines.Count -ge 2) { $h2 = $lines[1] }
  } catch { }
  $items += [pscustomobject]@{ path=$rel; head1=$h1; head2=$h2 }
}

# 簡易YAML整形
"files:" | Set-Content -Encoding UTF8 $structOut
$items | Sort-Object path | ForEach-Object {
  @"
  - path: "$($_.path)"
    head1: "$(($_.head1 -replace '"',''''))"
    head2: "$(($_.head2 -replace '"',''''))"
"@ | Add-Content -Encoding UTF8 $structOut
}

# --- 5) 起動手順（人向け） ---
@"
# BtcTradeSystemV1 Handoff QuickStart

## 起動（ダッシュボード）
PowerShell:
  & `"$V1\scripts\run.ps1"`

## WhatIf（環境確認のみ）
  & `"$V1\scripts\run.ps1"` -WhatIf

## データ/ログ実体
  DATA = $DATA
  LOGS = $LOGS

## 含まれる主要ファイル
- env/env_manifest.yaml        : 実行環境（Python/Streamlit/Dirs）
- repo_structure.yaml          : リポ構造＋各ファイル先頭2行
- gpt_context_map.yaml         : GPT再開用の文脈マップ（ポインタ類）
- handover.md                  : ライブ引継ぎメモ（次タスク・気づき）
- diagnostics/status_excerpt.json : 最新 status 抜粋
- diagnostics/audit.tail.jsonl : 監査末尾
- git/HEAD.txt / BRANCH.txt    : 現在のHEAD/ブランチ
- git/recent_commits.txt       : 直近コミット
- git/restore_points.txt       : rp-* タグ一覧
- （任意）git/scripts/*        : -IncludeGitScripts 指定時のみ同梱

"@ | Set-Content -Encoding UTF8 (Join-Path $TMP "README_HANDOFF.md")

# --- 5.5) gpt_context_map.yaml（最小構成を自動生成） ---
$ctxOut = Join-Path $TMP "gpt_context_map.yaml"
$branch = try { (git -C $V1 branch --show-current) 2>$null } catch { "" }
$head   = try { (git -C $V1 rev-parse --short HEAD) 2>$null } catch { "" }

@"
phase: "handoff"
mode:  "DEBUG"   # 必要に応じて UI設定から反映してもOK
git:
  branch: "$branch"
  head:   "$head"
pointers:
  status_excerpt: "diagnostics/status_excerpt.json"
  audit_tail:     "diagnostics/audit.tail.jsonl"
  env_manifest:   "env/env_manifest.yaml"
  repo_structure: "repo_structure.yaml"
notes:
  - "This file helps GPT reconstruct context on the next chat."
"@ | Set-Content -Encoding UTF8 $ctxOut

# --- 5.6) handover.md（存在すればコピー、無ければ雛形） ---
$handoverSrc = Join-Path $V1 "docs\handoff\handover.md"
$handoverDst = Join-Path $TMP "handover.md"
if (Test-Path $handoverSrc) {
  Copy-Item $handoverSrc $handoverDst -Force
} else {
@"
# Live Handover

- When: $((Get-Date).ToUniversalTime().ToString("s"))Z
- Phase: handoff
- Summary: 自動生成（必要に応じて上書きしてください）

## Done
- （ここに直近の完了タスクを箇条書き）

## Next
- （ここに明日のタスク・ToDoを箇条書き）

## Notes
- （気づき・検証観点）
"@ | Set-Content -Encoding UTF8 $handoverDst
}

# --- 6) サマリー（Pythonで整形） ---
$pyTool = Join-Path $V1 "tools\handoff\gen_summary.py"
if (Test-Path $pyTool) {
  python $pyTool --v1 "$V1" --data "$DATA" --logs "$LOGS" --out (Join-Path $TMP "SUMMARY.md") 2>$null
}

# --- 6.5) 軽量Git復元情報の生成（自動） ---
$gitOut = Join-Path $TMP "git"
New-Item -ItemType Directory -Force $gitOut | Out-Null

# HEAD / Branch
(git -C $V1 rev-parse --short HEAD) 2>$null | Set-Content -Encoding UTF8 (Join-Path $gitOut "HEAD.txt")
(git -C $V1 branch --show-current) 2>$null | Set-Content -Encoding UTF8 (Join-Path $gitOut "BRANCH.txt")

# 直近コミット一覧（軽量ログ）
(git -C $V1 log -n $GitCommits --pretty=format:"%ad|%h|%s" --date=iso) 2>$null `
  | Set-Content -Encoding UTF8 (Join-Path $gitOut "recent_commits.txt")

# rp-* タグ一覧（復元ポイント）
(git -C $V1 for-each-ref --sort=-taggerdate `
  --format="%(taggerdate:iso)|%(objectname:short)|%(refname:short)|%(contents:subject)" `
  "refs/tags/rp-*") 2>$null `
  | Set-Content -Encoding UTF8 (Join-Path $gitOut "restore_points.txt")

# 要望に応じて scripts/git を同梱
if ($IncludeGitScripts) {
  $src = Join-Path $V1 "scripts\git"
  if (Test-Path $src) {
    Copy-Item $src (Join-Path $gitOut "scripts") -Recurse -Force -ErrorAction SilentlyContinue
  }
}

# オプション: 自動 rp タグ発行
if ($AutoRpTag) {
  $stampTag = Get-Date -Format "yyyyMMdd_HHmmss"
  $tagName = "rp-$stampTag"
  try {
    git -C $V1 tag -a $tagName -m "Restore Point $tagName $RpMemo" | Out-Null
    git -C $V1 tag --list $tagName | Set-Content -Encoding UTF8 (Join-Path $gitOut "created_tag.txt")
  } catch {
    "auto tag failed: $($_.Exception.Message)" | Set-Content -Encoding UTF8 (Join-Path $gitOut "created_tag.txt")
  }
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
