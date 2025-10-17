# path: scripts/handoff/make_handoff.ps1
# desc: チャットまたぎ用ハンドオフZIPを作成（最小構成）

param(
  [int]$AuditTail = 200,
  [int]$StatusItems = 50,
  [int]$GitCommits = 20,                 # 追加: 直近コミット件数
  [switch]$AutoRpTag,                    # 追加: 自動で rp-* タグを切る
  [string]$RpMemo = "handoff auto",      # 追加: 自動タグに付けるメモ
  [switch]$IncludeGitScripts,             # 追加: 希望時のみ scripts/git を同梱
  [switch]$TestOutput               # 追加: テスト時は .\tmp 配下に出力
)

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

# --- ルートと出力先 ---
$V1  = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)   # ...\BtcTradeSystemV1
$OUT   = if ($TestOutput) { Join-Path $V1 "tmp" } else { Join-Path $V1 "docs\handoff" }
$stamp = Get-Date -Format "yyyyMMdd_HHmm"   # ← ここで統一
$TMP   = Join-Path $OUT ("CTX-" + $stamp)
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

# 最終値（あれば）
Copy-Item (Join-Path $PKG "config\ui\monitoring.yaml")    -Destination (Join-Path $cfgOut "monitoring.yaml")          -ErrorAction SilentlyContinue
Copy-Item (Join-Path $PKG "config\ui\health.yaml")        -Destination (Join-Path $cfgOut "health.yaml")              -ErrorAction SilentlyContinue

# 既定（新配置）
Copy-Item (Join-Path $PKG "config\ui\monitoring_def.yaml") -Destination (Join-Path $cfgOut "monitoring.defaults.yaml") -ErrorAction SilentlyContinue

# --- 2) ステータス・監査抜粋 ---
$diagOut = Join-Path $TMP "diagnostics"
New-Item -ItemType Directory -Force $diagOut | Out-Null

$st = Join-Path $DATA "collector\status.json"
if (Test-Path $st) {
  $json = Get-Content $st -Raw | ConvertFrom-Json
  # 変更前:
  # $items = @($json.items) | Select-Object -First $StatusItems
  # 変更後（last_ok 降順 → 上位 N 件）
  $items = @($json.items) | Sort-Object { $_.last_ok } -Descending | Select-Object -First $StatusItems

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
streamlit:
  version: "$stVer"
env:
  BTC_TS_DATA_DIR: "$DATA"
  BTC_TS_LOGS_DIR: "$LOGS"
generated_at_utc: "$((Get-Date).ToUniversalTime().ToString("s"))Z"
"@ | Set-Content -Encoding UTF8 (Join-Path $envOut "env_manifest.yaml")

# === 4) REPO_MAP（YAML/MD）を Python サブプロセスで生成 ===
# 既存の $items 収集・手書きYAML化ロジックは不要（置換）
$py = Join-Path $V1 ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
  # .venv が無い場合はシステムの python / py を利用
  $py = (Get-Command python -ErrorAction SilentlyContinue)?.Source
  if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue)?.Source }
}
$pyTool = Join-Path $V1 "tools\make_repo_map_extract.py"
$repoMapMd = Join-Path $TMP "REPO_MAP.extract.md"
$structOut = Join-Path $TMP "repo_structure.yaml"

if ((Test-Path $pyTool) -and $py) {
  Write-Host "[STEP] repo_map via python: $pyTool" -ForegroundColor DarkCyan
  & "$py" "$pyTool" --root "$V1" `
    --out-md "$repoMapMd" `
    --out-yaml "$structOut"
  if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] python生成に失敗。PowerShellフォールバックに切替。" -ForegroundColor Yellow
    $py = $null
  }
}

if (-not $py) {
  # ---- フォールバック（軽量・既存ロジック）----
  $excludeDirs = @(
  ".git",".venv","venv","node_modules",
  "data","logs","artifacts","backup","cache","tmp",
  "docs"                # ← ここを追加（docs 以下はREPO_MAP対象外に）
)

  $textExt = @(".py",".ps1",".psm1",".psd1",".bat",".cmd",".sh",".yaml",".yml",".json",".md",".toml",".ini")
  $items = @()
  Get-ChildItem $V1 -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
      $rel = $_.FullName.Substring($V1.Length + 1)
      $first = ($rel -split '[\\/]')[0].ToLower()
      ($excludeDirs -notcontains $first) -and ($textExt -contains $_.Extension.ToLower())
    } |
    ForEach-Object {
      $rel = $_.FullName.Substring($V1.Length + 1)
      $h1=""; $h2=""
      try {
        $lines = Get-Content -Path $_.FullName -TotalCount 2 -Encoding UTF8 -ErrorAction Stop
        if ($lines.Count -ge 1) { $h1 = $lines[0] }
        if ($lines.Count -ge 2) { $h2 = $lines[1] }
      } catch { }
      $items += [pscustomobject]@{ path=$rel; head1=$h1; head2=$h2 }
    }

  # YAML（repo_structure.yaml）
$body = ($items | Sort-Object path | ForEach-Object {
  "  - path: `"$($_.path)`"`n" +
  ($(if ($_.head1) { "    head1: `"$($_.head1.Replace('"','\"'))`"`n" } else { "" })) +
  ($(if ($_.head2) { "    head2: `"$($_.head2.Replace('"','\"'))`"`n" } else { "" }))
}) -join ""
$yaml = "repo_structure:`n$body"

$yaml | Set-Content -Encoding UTF8 $structOut

  # Markdown（REPO_MAP.extract.md）
  "# REPO_MAP extract (header2 only)`n" | Set-Content -Encoding UTF8 $repoMapMd
  $items | Sort-Object path | ForEach-Object {
    $p = if ($_.head1 -match "^\s*#\s*path:\s*(.+)$") { $Matches[1].Trim() } else { $_.path }
    $d = if ($_.head2 -match "^\s*#\s*desc:\s*(.+)$") { $Matches[1].Trim() } else { "" }
    "- **$p** — $d" | Add-Content -Encoding UTF8 $repoMapMd
  }
}

# === repo_structure.yaml の先頭キーを強制正規化（files: → repo_structure:） ===
if (Test-Path $structOut) {
  $first = (Get-Content $structOut -TotalCount 1)
  if ($first -match '^\s*files\s*:\s*$') {
    $all = Get-Content $structOut -Raw
    $fixed = $all -replace '^\s*files\s*:\s*', "repo_structure:`r`n"
    $fixed | Set-Content -Encoding UTF8 $structOut
  }
}

# === 追記2: 外部パス(D:\BtcTS_V1\…)のフォルダ構造をコメントとして追記（各フォルダ1ファイルだけ例示） ===
if (Test-Path $structOut) {
  # 1) ルート決定：ENV から親フォルダを推定（data/logs の親が同じならそれを採用）
  $dataDir = $env:BTC_TS_DATA_DIR
  $logsDir = $env:BTC_TS_LOGS_DIR
  $root = $null
  try {
    $dataParent = if ($dataDir) { Split-Path (Resolve-Path $dataDir) -Parent } else { $null }
    $logsParent = if ($logsDir) { Split-Path (Resolve-Path $logsDir) -Parent } else { $null }
    if ($dataParent -and $logsParent -and ($dataParent -eq $logsParent)) {
      $root = $dataParent
    } elseif ($dataParent) {
      $root = $dataParent
    } elseif ($logsParent) {
      $root = $logsParent
    }
  } catch { }

  # フォールバック：明示的に D:\BtcTS_V1 を試す（存在する場合のみ）
  if (-not $root) {
    $fallback = 'D:\BtcTS_V1'
    if (Test-Path $fallback) { $root = (Resolve-Path $fallback).Path }
  }

  if ($root) {
    # 2) ツリー生成（フォルダのみ + 各フォルダで代表1ファイルだけ記載）
    $maxDepth = 4     # 出力が長くなり過ぎないよう適度に制限
    $lines = New-Object System.Collections.Generic.List[string]

    function Add-Tree {
      param(
        [string]$Path,
        [int]$Depth,
        [string]$Prefix
      )
      if ($Depth -ge $maxDepth) { return }

      $dirs = Get-ChildItem -LiteralPath $Path -Directory -Force -ErrorAction SilentlyContinue | Sort-Object Name
      $files = Get-ChildItem -LiteralPath $Path -File -Force -ErrorAction SilentlyContinue | Sort-Object Name

      # 代表ファイル（この階層の直下から1つだけ）
      $sampleFile = $null
      if ($files.Count -gt 0) { $sampleFile = $files[0].Name }

      # 子要素（ディレクトリ + サンプルファイル）を結合して“最後要素”判定
      $items = @()
      foreach ($d in $dirs)  { $items += @{ type='dir';  name=$d.Name;  full=$d.FullName } }
      if ($sampleFile) { $items += @{ type='file'; name=$sampleFile; full=(Join-Path $Path $sampleFile) } }

      for ($i=0; $i -lt $items.Count; $i++) {
        $isLast = ($i -eq $items.Count - 1)
        $connector = $(if ($isLast) { '└── ' } else { '├── ' })
        $line = $Prefix + $connector + $(if ($items[$i].type -eq 'dir') { "$($items[$i].name)/" } else { $items[$i].name })
        $lines.Add('# ' + $line)

        if ($items[$i].type -eq 'dir') {
          $nextPrefix = $Prefix + $(if ($isLast) { '    ' } else { '│   ' })
          Add-Tree -Path $items[$i].full -Depth ($Depth+1) -Prefix $nextPrefix
        }
      }
    }

    # 3) 追記本文のヘッダ
    $header = @(
      '',
      '# logs/data は ENV（BTC_TS_LOGS_DIR/BTC_TS_DATA_DIR）で D:\BtcTS_V1\… を指す',
      '# [EXT_TREE] フォルダ + 各フォルダ直下から代表1ファイルのみ記載'
    )
    $header | ForEach-Object { Add-Content -Path $structOut -Value $_ -Encoding UTF8 }

    # 4) ルート行とツリー本体を追記
    Add-Content -Path $structOut -Value ('# ' + (Split-Path $root -Qualifier) + ( ($root -replace '^[A-Za-z]:\\','\') -replace '\\','/' )) -Encoding UTF8
    Add-Tree -Path $root -Depth 0 -Prefix ''
    $lines | ForEach-Object { Add-Content -Path $structOut -Value $_ -Encoding UTF8 }
  }
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
$pyExe = if ($py) { $py } else { 'python' }
if (Test-Path $pyTool) {
  & $pyExe $pyTool --v1 "$V1" --data "$DATA" --logs "$LOGS" --out (Join-Path $TMP "SUMMARY.md") 2>$null
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
$zip = Join-Path $OUT ("CTX-" + $stamp + ".zip")

if (Test-Path $zip) { Remove-Item $zip -Force }
Add-Type -AssemblyName 'System.IO.Compression.FileSystem'
[System.IO.Compression.ZipFile]::CreateFromDirectory($TMP, $zip)

Write-Host "OK: $zip"
Remove-Item $TMP -Recurse -Force

