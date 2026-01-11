# path: scripts/git/git_full_backup.ps1
# desc: リポジトリの**完全バックアップ**（git bundle）を作成し、検証＆メタ情報を出力

param(
  [string]$OutDir = "$env:USERPROFILE\BtcTradeSystemV1_git\git_full",
  [string]$Name,
  [bool]  $Verify = $true
)
# --- 安全設定 ---
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

function Find-RepoRoot([string]$start) {
  $cur = (Resolve-Path -LiteralPath $start).Path
  while ($true) {
    if (Test-Path (Join-Path $cur '.git')) { return $cur }
    $p = Split-Path $cur -Parent
    if ([string]::IsNullOrEmpty($p) -or $p -eq $cur) { break }
    $cur = $p
  }
  return $null
}

# --- 前提チェック ---
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git が見つかりません。PATH を確認してください。"
}
$repo = Find-RepoRoot $PSScriptRoot
if (-not $repo) { throw "ここは Git リポジトリではありません。" }

$branch = (& git -C $repo rev-parse --abbrev-ref HEAD).Trim()
$head   = (& git -C $repo rev-parse --short HEAD).Trim()
$stamp  = Get-Date -Format 'yyyyMMdd_HHmmss'
$repoName = Split-Path $repo -Leaf

# --- 出力名（分かりやすい命名） ---
# 例: BtcTradeSystemV1-full-main-20251014_0810.bundle
$base = if ($Name) { [IO.Path]::GetFileNameWithoutExtension($Name) } else { "$repoName-full-$branch-$stamp" }
$bundle = Join-Path $OutDir ("$base.bundle")
$meta   = [IO.Path]::ChangeExtension($bundle, '.json')

# --- ディレクトリ作成 ---
New-Item -ItemType Directory -Force -Path (Split-Path $bundle -Parent) | Out-Null

Write-Host "[INFO] repo:   $repo"
Write-Host "[INFO] branch: $branch  @ $head"
Write-Host "[INFO] out:    $bundle"

# --- フルバックアップ作成（全refs） ---
& git -C $repo bundle create "$bundle" --all | Out-Null
Write-Host "[OK] bundle created" -ForegroundColor Green

# --- 検証（必要なら） ---
if ($Verify) {
  & git -C $repo bundle verify "$bundle"
}

# --- メタ情報を併置（復元の手がかり） ---
$heads = (& git -C $repo for-each-ref --format "%(refname:short)|%(objectname:short)" refs/heads/)
$tags  = (& git -C $repo for-each-ref --format "%(refname:short)|%(objectname:short)" refs/tags/)
$metaObj = [pscustomobject]@{
  created_at_utc = (Get-Date).ToUniversalTime().ToString("s") + 'Z'
  repo          = $repo
  branch        = $branch
  head          = $head
  bundle        = (Resolve-Path $bundle).Path
  include       = 'refs/* (all branches & tags)'
  heads         = $heads
  tags          = $tags
}
$metaObj | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $meta
Write-Host "[OK] meta: $meta" -ForegroundColor Green

# --- 復元のメモを出力（クリック一発で再利用できるよう明確化） ---
@"
# Restore from bundle (例)

## A) 新規クローン（最も簡単）
git clone ""$bundle"" <dest_dir>
cd <dest_dir>
git checkout main   # 必要なブランチへ切替

## B) 既存/空ディレクトリへ取り込み
git init <dest_dir>
git -C <dest_dir> fetch ""$bundle"" ""refs/*:refs/*""
git -C <dest_dir> checkout main
"@ | Set-Content -Encoding UTF8 ([IO.Path]::ChangeExtension($bundle, '.RESTORE.txt'))

Write-Host "[DONE] full backup ready." -ForegroundColor Cyan
