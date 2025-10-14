# path: scripts/git/git_restore_from_bundle.ps1
# desc: 直近または指定の .bundle からワンショットで復元（clone or fetch）

param(
  [string]$Bundle,                          # 省略時は backup\git_full の最新 .bundle
  [string]$Dest,                            # 省略時は %TEMP%\restore_<timestamp>
  [ValidateSet("clone","fetch")] [string]$Mode = "clone",
  [string]$Branch = "main"
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# ルート検出
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
$repo = Find-RepoRoot $PSScriptRoot
if (-not $repo) { throw "ここは Git リポジトリではありません。" }

# git 存在確認
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git が見つかりません。PATH を確認してください。"
}

# 最新 bundle 自動解決
if (-not $Bundle) {
  $b = Get-ChildItem -LiteralPath (Join-Path $repo "backup\git_full") -Filter *.bundle |
       Sort-Object LastWriteTime | Select-Object -Last 1
  if (-not $b) { throw "backup\git_full に .bundle が見つかりません。" }
  $Bundle = $b.FullName
}

# デフォルト宛先
if (-not $Dest) {
  $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $Dest = Join-Path $env:TEMP ("restore_" + $stamp)
}

Write-Host "[INFO] bundle: $Bundle"
Write-Host "[INFO] mode  : $Mode"
Write-Host "[INFO] dest  : $Dest"

if (Test-Path $Dest) {
  Write-Host "[WARN] 既存の宛先を削除します: $Dest" -ForegroundColor Yellow
  Remove-Item $Dest -Recurse -Force
}

switch ($Mode) {
  "clone" {
    git clone "$Bundle" "$Dest"
    git -C "$Dest" checkout "$Branch"
  }
  "fetch" {
    New-Item -ItemType Directory -Force -Path "$Dest" | Out-Null
    git -C "$Dest" init
    git -C "$Dest" fetch "$Bundle" "refs/*:refs/*"
    git -C "$Dest" checkout "$Branch"
  }
}

git -C "$Dest" log -1 --oneline
Write-Host "[DONE] restore ok -> $Dest" -ForegroundColor Cyan
