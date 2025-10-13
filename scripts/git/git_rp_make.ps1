# path: scripts/git/git_rp_make.ps1
# desc: Make a Git "Restore Point" tag (rp_YYYYMMDD_HHMMSS). Snapshot commit by default.

param(
  [bool]$Commit = $true   # ← 既定でコミットON（忘れても安全）
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
