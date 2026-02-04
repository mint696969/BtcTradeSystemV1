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

function New-Dir([string]$p) {
  New-Item -ItemType Directory -Force -Path $p | Out-Null
}

function Write-Text([string]$path, [string]$text) {
  New-Dir (Split-Path $path -Parent)
  $text | Set-Content -Encoding UTF8 -LiteralPath $path
}

$repo = Resolve-RepoRoot

# python は .venv を優先し、無ければ PATH の python を使う
$pyVenv = Join-Path $repo ".venv\Scripts\python.exe"
$py = if (Test-Path $pyVenv) { $pyVenv } else { "python" }
if (-not (Get-Command $py -ErrorAction SilentlyContinue)) {
  throw "python not found. (.venv missing and 'python' not on PATH)"
}

# 出力先は tmp に固定（docs/handoff は使わない）
$outRoot = Join-Path $repo "tmp\handoff"
New-Dir $outRoot

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$ctxDir = Join-Path $outRoot ("CTX-{0}" -f $ts)
New-Dir $ctxDir

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

# --- docs/working を同梱（人間向け補助資料 / 任意） ---
$devMemoDir = Join-Path $repo "docs\working"
if (Test-Path $devMemoDir) {
  Copy-Item `
    -Recurse `
    -Force `
    -LiteralPath $devMemoDir `
    -Destination (Join-Path $ctxDir "working")
}

# --- repo map / structure ---
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
  $repoMapArgs = @(
    $tool,
    "--root", $repo,
    "--out-md", $mdOut,
    "--out-yaml", $yOut
  )
  if ($extraRoot -and (Test-Path $extraRoot)) {
    $repoMapArgs += @("--extra-root", $extraRoot)
  }

  $repoMapOut = & $py @repoMapArgs 2>&1 | Out-String
  Write-Text (Join-Path $ctxDir "diag\make_repo_map_stdout_stderr.txt") $repoMapOut
  if ($LASTEXITCODE -ne 0) {
    throw "make_repo_map_extract.py failed (exit=$LASTEXITCODE). See CTX/diag/make_repo_map_stdout_stderr.txt"
  }
} else {
  throw "repo map tool missing. py_exists=$((Test-Path $py)) tool_exists=$((Test-Path $tool))"
}

# --- SUMMARY（必須） ---
$gen = Join-Path $repo "tools\handoff\gen_summary.py"
if (-not (Test-Path $gen)) {
  throw "gen_summary.py not found: $gen"
}

$sum = Join-Path $ctxDir "SUMMARY.md"

$repoRoot = $repo
$dataDir = $env:BTC_TS_DATA_DIR
$logsDir = $env:BTC_TS_LOGS_DIR
if (-not $dataDir) { $dataDir = Join-Path $repo "data" }
if (-not $logsDir) { $logsDir = Join-Path $repo "logs" }

# 失敗時の原因を残す（最小：stdout/stderrのみ）
$diagDir = Join-Path $ctxDir "diag"
New-Dir $diagDir

$cmdOut = & $py $gen --repo $repoRoot --data $dataDir --logs $logsDir --out $sum 2>&1 | Out-String
Write-Text (Join-Path $diagDir "gen_summary_stdout_stderr.txt") $cmdOut

if ($LASTEXITCODE -ne 0) {
  throw "gen_summary.py failed (exit=$LASTEXITCODE). See CTX/diag/gen_summary_stdout_stderr.txt"
}
if (-not (Test-Path $sum)) {
  throw "SUMMARY.md was not generated although gen_summary exited 0."
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
return
