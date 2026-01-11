# path: ./scripts/handoff/make_handoff.ps1
# desc: チャットまたぎ用ハンドオフZIPを作成（最小構成 / tmp\handoff に集約 / external root も map 化）

[CmdletBinding()]
param(
  [switch]$AutoRpTag,
  [string]$RpMemo = "handoff one-click",
  [int]$GitCommits = 30
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
  # scripts/handoff -> scripts -> repo
  $repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
  return $repo
}

function Ensure-Dir([string]$p) {
  New-Item -ItemType Directory -Force -Path $p | Out-Null
}

function Write-Text([string]$path, [string]$text) {
  Ensure-Dir (Split-Path $path -Parent)
  $text | Set-Content -Encoding UTF8 -LiteralPath $path
}

$repo = Resolve-RepoRoot

# 出力先は tmp に固定（docs/handoff は使わない）
$outRoot = Join-Path $repo "tmp\handoff"
Ensure-Dir $outRoot

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$ctxDir = Join-Path $outRoot ("CTX-{0}" -f $ts)
Ensure-Dir $ctxDir

# --- git: 自動 rp タグ（必要なら） ---
if ($AutoRpTag) {
  $tag = "rp-{0}" -f $ts
  git -C $repo tag -f $tag | Out-Null
  Write-Text (Join-Path $ctxDir "git\created_tag.txt") $tag
}

# --- env ---
$envTxt = @(
  "BTC_TS_CONFIG_DIR=$($env:BTC_TS_CONFIG_DIR)"
  "BTC_TS_DATA_DIR=$($env:BTC_TS_DATA_DIR)"
  "BTC_TS_LOGS_DIR=$($env:BTC_TS_LOGS_DIR)"
  "BTC_TS_SECRETS_DIR=$($env:BTC_TS_SECRETS_DIR)"
  "BTC_TS_DATASET_DIR=$($env:BTC_TS_DATASET_DIR)"
  "BTC_TS_MODE=$($env:BTC_TS_MODE)"
) -join "`n"
Write-Text (Join-Path $ctxDir "env\environment.txt") $envTxt

# env manifest（Keyだけに寄せる）
$manifest = @{}
Get-ChildItem Env: |
  Where-Object { $_.Name -match "BTC_TS|BTCTS|BtcTS|RP|BACKUP|GIT" } |
  ForEach-Object { $manifest[$_.Name] = $_.Value }
$yaml = @()
$yaml += "env_manifest:"
foreach($k in ($manifest.Keys | Sort-Object)) {
  $v = $manifest[$k].ToString().Replace("\","/")
  $yaml += ("  {0}: ""{1}""" -f $k, ($v -replace '"','\"'))
}
Write-Text (Join-Path $ctxDir "env\env_manifest.yaml") ($yaml -join "`n")

# --- git info ---
Write-Text (Join-Path $ctxDir "git\BRANCH.txt") (git -C $repo branch --show-current)
Write-Text (Join-Path $ctxDir "git\HEAD.txt") (git -C $repo rev-parse HEAD)
Write-Text (Join-Path $ctxDir "git\recent_commits.txt") (git -C $repo log -n $GitCommits --oneline --decorate)

# rp tags list
$rp = git -C $repo tag -l "rp-*" --sort=-creatordate
Write-Text (Join-Path $ctxDir "git\restore_points.txt") ($rp -join "`n")

# --- docs/handover.md を同梱（存在すれば） ---
$handover = Join-Path $repo "docs\handover.md"
if (Test-Path $handover) {
  Copy-Item -Force -LiteralPath $handover -Destination (Join-Path $ctxDir "handover.md")
} else {
  Write-Text (Join-Path $ctxDir "handover.md") "# handover`n"
}

# --- repo map / structure ---
$py = Join-Path $repo ".venv\Scripts\python.exe"
$tool = Join-Path $repo "tools\make_repo_map_extract.py"

# external root は「CONFIG_DIR から推定」して E:\btc_ts を入れる（あれば）
$extraRoot = ""
if ($env:BTC_TS_CONFIG_DIR) {
  try {
    $cfg = (Resolve-Path $env:BTC_TS_CONFIG_DIR).Path
    $extraRoot = Split-Path (Split-Path $cfg -Parent) -Parent
  } catch {}
}

$mdOut = Join-Path $ctxDir "REPO_MAP.extract.md"
$yOut  = Join-Path $ctxDir "repo_structure.yaml"

if ((Test-Path $py) -and (Test-Path $tool)) {
  $args = @(
    $tool,
    "--root", $repo,
    "--out-md", $mdOut,
    "--out-yaml", $yOut
  )
  if ($extraRoot -and (Test-Path $extraRoot)) {
    $args += @("--extra-root", $extraRoot)
  }
  & $py @args | Out-Host
}

# --- SUMMARY（あれば） ---
$gen = Join-Path $repo "tools\handoff\gen_summary.py"
if ((Test-Path $py) -and (Test-Path $gen)) {
  $sum = Join-Path $ctxDir "SUMMARY.md"

  # gen_summary.py は引数必須（--v1/--data/--logs/--out）
  $v1Root = $repo
  $dataDir = $env:BTC_TS_DATA_DIR
  $logsDir = $env:BTC_TS_LOGS_DIR
  if (-not $dataDir) { $dataDir = Join-Path $repo "data" }
  if (-not $logsDir) { $logsDir = Join-Path $repo "logs" }

  & $py $gen --v1 $v1Root --data $dataDir --logs $logsDir --out $sum | Out-Host
}

# --- ZIP 化（ctxDir を zip にして完了） ---
$zipPath = Join-Path $outRoot ("CTX-{0}.zip" -f $ts)
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }

Compress-Archive -Path (Join-Path $ctxDir "*") -DestinationPath $zipPath -Force

# ZIP 化できたら、元のフォルダは削除（生成物を増やさない）
if (Test-Path $zipPath) {
  try {
    Remove-Item -Recurse -Force -LiteralPath $ctxDir
  } catch {
    # 削除失敗は致命ではない（ZIPが正ならOK）
  }
}

Write-Host ("OK: {0}" -f $zipPath)
exit 0
