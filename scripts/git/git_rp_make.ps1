# path: scripts/git/git_rp_make.ps1
# desc: Make a Git "Restore Point" tag (rp_YYYYMMDD_HHmmss). Snapshot commit by default. (＋任意で差分バックアップ)

param(
  [bool]  $Commit     = $true,              # 既定でコミットON（忘れても安全）
  [switch]$Diff,                            # ← 差分バックアップを作成する
  [string]$BaseTag,                         # ← 差分の起点タグ（未指定なら自動）
  [string]$BackupRoot = "backup\\git_rp",   # ← 保存先ルート
  [switch]$Zip = $true                      # ← 差分をZIP化（falseでディレクトリ展開）
)

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::InputEncoding  = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference    = 'Stop'

function Wait-AnyKey {
  Write-Host ""
  Write-Host "Press any key to exit..." -ForegroundColor DarkGray
  $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown') | Out-Null
}

function Halt($msg) {
  if ($msg) { Write-Host $msg -ForegroundColor Yellow }
  Wait-AnyKey
  exit 1
}

try {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Halt "git not found. Please check PATH."
  }

# 1) repo ルート検出（親を遡って .git を探す／worktree にも対応）
function Find-RepoRoot([string]$start) {
  $cur = (Resolve-Path -LiteralPath $start).Path  # PathInfo -> string
  while ($true) {
    $gitPath = Join-Path -Path $cur -ChildPath '.git'
    if (Test-Path -LiteralPath $gitPath) { return $cur }
    $parent = Split-Path -Path $cur -Parent
    if ([string]::IsNullOrEmpty($parent) -or ($parent -eq $cur)) { break }
    $cur = $parent
  }
  return $null
}

# --- 直近の復元ポイントタグ（rp-...）を取得。今作ったタグは除外可 ---
function Get-LastRestorePointTag([string]$repoRoot, [string]$excludeTag) {
  $tags = & git -C $repoRoot tag --list "rp-*" | Sort-Object
  $cand = $tags | Where-Object { $_ -ne $excludeTag } | Select-Object -Last 1
  return $cand
}

# --- 差分バックアップの作成 ---
function New-DiffBackup([string]$repoRoot, [string]$baseTag, [string]$headRef, [string]$destDir, [string]$memo, [switch]$Zip) {
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null
  $metaPath = Join-Path $destDir "metadata.json"
  $diffList = Join-Path $destDir "changed_files.txt"
  $patchPath = Join-Path $destDir "diff.patch"
  $filesDir = Join-Path $destDir "files"
  New-Item -ItemType Directory -Force -Path $filesDir | Out-Null

  # 変更ファイル一覧（状態付き）
  $nameStatus = & git -C $repoRoot diff --name-status $baseTag..$headRef
  $nameOnly   = & git -C $repoRoot diff --name-only  $baseTag..$headRef

  # 一覧保存
  $nameStatus | Out-File -FilePath $diffList -Encoding UTF8

  # パッチ保存
  & git -C $repoRoot diff $baseTag..$headRef | Out-File -FilePath $patchPath -Encoding UTF8

  # 変更ファイルをワークツリーから採取（削除されたファイルは一覧のみ記録）
  foreach ($rel in $nameOnly) {
    $src = Join-Path $repoRoot $rel
    if (Test-Path -LiteralPath $src) {
      $dst = Join-Path $filesDir $rel
      New-Item -ItemType Directory -Force -Path (Split-Path $dst -Parent) | Out-Null
      Copy-Item -LiteralPath $src -Destination $dst -Force
    }
  }

  # メタデータ保存
  $headSha  = (& git -C $repoRoot rev-parse $headRef).Trim()
  $branch   = (& git -C $repoRoot rev-parse --abbrev-ref HEAD).Trim()
  $meta = [ordered]@{
    created_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    base_tag   = $baseTag
    head_ref   = $headRef
    head_sha   = $headSha
    branch     = $branch
    memo       = $memo
  } | ConvertTo-Json -Depth 3
  $meta | Out-File -FilePath $metaPath -Encoding UTF8

  if ($Zip) {
    $zipPath = "$destDir.zip"
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    Compress-Archive -Path (Join-Path $destDir "*") -DestinationPath $zipPath
    Write-Host ("[OK] Diff backup ZIP: {0}" -f $zipPath) -ForegroundColor Green
  } else {
    Write-Host ("[OK] Diff backup DIR: {0}" -f $destDir) -ForegroundColor Green
  }
}

# ルートはスクリプトから 2 階層上を優先（BtcTradeSystemV1 固定構成）
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not (Test-Path (Join-Path $repoRoot '.git'))) {
  # 念のためフォールバック探索
  $repoRoot = Find-RepoRoot $repoRoot
}
if (-not $repoRoot) {
  Halt "No git repository found. Put this script inside the project tree."
}

  # 2) タグ名
  $tag  = "rp-{0:yyyyMMdd_HHmmss}" -f (Get-Date)

  # 3) メモ入力（同じ行で入力／文字化け回避のため英語表示）
  Write-Host "Memo (optional): " -NoNewline
  $memo = Read-Host

# 4) 任意：コミット
if ($Commit) {
  & git -C $repoRoot add -A 1>$null 2>$null
  & git -C $repoRoot commit -m "chore: snapshot for $tag" --no-verify 1>$null 2>$null
}

# 5) タグ付け
$msg = "Restore Point $tag" + ($(if ($memo) { " : $memo" } else { "" }))
& git -C $repoRoot tag -a $tag -m $msg 2>$null
if ($LASTEXITCODE -ne 0) {
  & git -C $repoRoot tag $tag 2>$null
}

# 5.5) 差分バックアップ（任意）
if ($Diff) {
  # 差分の起点を決定（明示指定 > 直近の rp-* タグ）
  $base = if ($BaseTag) { $BaseTag } else { Get-LastRestorePointTag -repoRoot $repoRoot -excludeTag $tag }
  if (-not $base) {
    Write-Host "[WARN] 差分の起点となる rp-* タグが見つかりません。最初の実行はタグ作成のみになります。" -ForegroundColor Yellow
  } else {
    $dest = Join-Path $repoRoot (Join-Path $BackupRoot ("{0}\{1}" -f $base, $tag))
    New-DiffBackup -repoRoot $repoRoot -baseTag $base -headRef "HEAD" -destDir $dest -memo $memo -Zip:$Zip
  }
}

  # 6) 完了表示
  Write-Host ""
  Write-Host ("OK: Restore Point -> {0}" -f $tag) -ForegroundColor Green
  if ($memo) { Write-Host ("MEMO: {0}" -f $memo) -ForegroundColor DarkGray }
  Wait-AnyKey
  exit 0
}
catch {
  Halt ("Unhandled error: {0}" -f $_.Exception.Message)
}
