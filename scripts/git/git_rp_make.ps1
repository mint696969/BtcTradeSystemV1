# path: scripts/git/git_rp_make.ps1
# desc: 復元ポイント作成（rp-YYYYMMDD_HHmmss）。必要に応じてコミット・タグ付け・差分バックアップ（ZIP/フォルダ）を実施。

param(
  [switch]$Commit,                                      # 変更をコミットする（-Commit）
  [switch]$Diff,                                        # 差分バックアップを作る（-Diff）
  [string]$BaseTag,                                     # 差分の起点タグ（未指定なら直近の rp-* を自動採用）
  [string]$BackupRoot = "$env:USERPROFILE\BtcTradeSystemV1_git\git_rp",
  [switch]$Zip,                                         # 差分を ZIP にまとめる
  [string]$RpMemo                                       # メモ（任意）
)

# ---- 共通設定 ---------------------------------------------------------------
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::InputEncoding  = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference    = 'Stop'

function Halt([string]$msg) {
  Write-Host "ERROR: $msg" -ForegroundColor Red
  exit 1
}

function GitExec([string[]]$CmdArgs) {
  if (-not $CmdArgs -or $CmdArgs.Count -eq 0) {
    Halt "GitExec(): 引数が空です（内部バグ）。"
  }
  # PowerShell ネイティブ実行で確実に終了コードを拾う
  $cmd = "git " + ($CmdArgs -join ' ')
  Write-Verbose "[git] $cmd"
  $all = & git @CmdArgs 2>&1
  $code = $LASTEXITCODE
  if ($code -ne 0) {
    $txt = ($all | Out-String).Trim()
    Halt ("git {0} failed (exit={1}): {2}" -f ($CmdArgs -join ' '), $code, $txt)
  }
  return ($all | Out-String).Trim()
}

# ---- リポジトリルート検出 ---------------------------------------------------
$here = (Get-Location).Path
$repoRoot = $here
while (-not (Test-Path (Join-Path $repoRoot ".git"))) {
  $parent = Split-Path -Parent $repoRoot
  if (-not $parent -or $parent -eq $repoRoot) { Halt "ここは Git リポジトリではありません: $here" }
  $repoRoot = $parent
}
Set-Location $repoRoot

# ---- 変更の有無メモ ---------------------------------------------------------
$dirty = (GitExec @("status","--porcelain=v1"))
$hasDirty = -not [string]::IsNullOrWhiteSpace($dirty)
if ($hasDirty) { Write-Verbose "[git] working tree: DIRTY" }

# ---- コミット（任意） -------------------------------------------------------
$stamp = (Get-Date -Format 'yyyyMMdd_HHmmss')
$tag   = "rp-$stamp"
$memo  = if ($RpMemo) { $RpMemo } else { "" }

if ($Commit) {
  GitExec @("add","-A")
  $msg = "[RP:$stamp] $memo"
  # 空コミットも許可（--allow-empty）
  GitExec @("commit","-m",$msg,"--allow-empty")
}

# ---- タグ付け（常に実施） ---------------------------------------------------
GitExec @("tag","-a",$tag,"-m",("[RP:{0}] {1}" -f $stamp,$memo))

# ---- 差分バックアップ（任意） -----------------------------------------------
if ($Diff) {
  if (-not (Test-Path $BackupRoot)) { New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null }

  # BaseTag を決める：明示指定 > 自動（直近 rp-* のうち「今打ったタグ」を除く最新）
  $base = $BaseTag
  if (-not $base) {
    $tags = GitExec @("tag","--list","rp-*","--sort=-creatordate")
    $tagList = @()
    if (-not [string]::IsNullOrWhiteSpace($tags)) {
      $tagList = $tags -split "`r?`n" | Where-Object { $_ -and $_ -ne $tag }
    }
    if ($tagList.Count -gt 0) { $base = $tagList[0] }
  }

  if (-not $base) {
    Write-Host "[WARN] 差分の起点 rp-* が見つからないため、今回の実行はタグ作成のみです。" -ForegroundColor Yellow
  } else {
    $dest = Join-Path $BackupRoot ("{0}\{1}" -f $base, $tag)
    New-Item -ItemType Directory -Path $dest -Force | Out-Null

    # 参考情報を保存
    (GitExec @("status","--porcelain=v1")) | Out-File (Join-Path $dest "status.txt") -Encoding UTF8
    (GitExec @("log","-1","--pretty=fuller",$tag))   | Out-File (Join-Path $dest "commit_show.txt") -Encoding UTF8

    # 差分（バイナリ含む）— base..tag
    $patchPath = Join-Path $dest "diff_$($base)_to_$($tag).patch"
    # git のレンジ指定は 1 引数で渡す（別引数だと path 解釈される）
    $range    = "$base..$tag"
    $diffText = GitExec @("diff","--binary",$range)
    $diffText | Set-Content -Path $patchPath -Encoding UTF8

    if ($Zip) {
      $zipPath = "$dest.zip"
      if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
      Compress-Archive -Path (Join-Path $dest "*") -DestinationPath $zipPath -Force
      Remove-Item -Recurse -Force $dest
      Write-Host ("[ZIP] {0}" -f $zipPath) -ForegroundColor DarkGray
    }
  }
}

Write-Host ""
Write-Host ("OK: Restore Point -> {0}" -f $tag) -ForegroundColor Green
if ($memo) { Write-Host ("MEMO: {0}" -f $memo) -ForegroundColor DarkGray }
exit 0