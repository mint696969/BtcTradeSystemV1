# path: scripts/git/git_rp_make.ps1
# desc: Git 復元ポイント（rp-YYYYMMDD_HHmmss）を作成。必要に応じて差分バックアップ（ZIP）を外部保存先へ出力

param(
  [bool]  $Commit     = $true,                                      # 既定でコミットON（忘れても安全）
  [switch]$Diff,                                                      # ← 差分バックアップを作成する
  [string]$BaseTag,                                                   # ← 差分の起点タグ（未指定なら自動）
  [string]$BackupRoot = "$env:USERPROFILE\BtcTradeSystemV1_git\git_rp",  # ← 保存先ルート（リポ外固定）
  [bool]  $Zip       = $true                                         # ← 差分をZIP化（falseでディレクトリ展開）
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

function Get-LastRestorePointTag([string]$repoRoot, [string]$excludeTag) {
  $tags = & git -C $repoRoot tag --list "rp-*" | Sort-Object
  $cand = $tags | Where-Object { $_ -ne $excludeTag } | Select-Object -Last 1
  return $cand
}

function Parse-NameStatus($nameStatusLines) {
  $add=$mod=$del=$ren=$cpy=0
  foreach ($ln in $nameStatusLines) {
    if (-not $ln) { continue }
    $code = ($ln -split "\s+",2)[0]
    switch -regex ($code) {
      '^A' { $add++ }
      '^M' { $mod++ }
      '^D' { $del++ }
      '^R' { $ren++ }
      '^C' { $cpy++ }
    }
  }
  return [pscustomobject]@{ added=$add; modified=$mod; deleted=$del; renamed=$ren; copied=$cpy }
}

function Parse-Numstat($numstatLines) {
  $ins=0; $dels=0; $files=0
  foreach ($ln in $numstatLines) {
    if (-not $ln) { continue }
    $parts = $ln -split "\t"
    if ($parts.Count -ge 3) {
      $i = $parts[0]; $d = $parts[1]
      if ($i -match '^[0-9]+$') { $ins += [int]$i }
      if ($d -match '^[0-9]+$') { $dels += [int]$d }
      $files++
    }
  }
  return [pscustomobject]@{ insertions=$ins; deletions=$dels; files=$files }
}

function New-DiffBackup([string]$repoRoot, [string]$baseTag, [string]$headRef, [string]$destDir, [string]$memo, [switch]$Zip) {
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null
  $metaPath  = Join-Path $destDir "metadata.json"
  $diffList  = Join-Path $destDir "changed_files.txt"
  $patchPath = Join-Path $destDir "diff.patch"
  $filesDir  = Join-Path $destDir "files"
  New-Item -ItemType Directory -Force -Path $filesDir | Out-Null

  $range      = "$baseTag..$headRef"
  $nameStatus = & git -C $repoRoot diff --name-status $range
  $nameOnly   = & git -C $repoRoot diff --name-only  $range
  $numstat    = & git -C $repoRoot diff --numstat    $range

  # 一覧・パッチの保存
  $nameStatus | Out-File -FilePath $diffList -Encoding UTF8
  & git -C $repoRoot diff $range | Out-File -FilePath $patchPath -Encoding UTF8

  # 変更ファイルの現物コピー（削除ファイルは一覧のみ）
  foreach ($rel in $nameOnly) {
    $src = Join-Path $repoRoot $rel
    if (Test-Path -LiteralPath $src) {
      $dst = Join-Path $filesDir $rel
      New-Item -ItemType Directory -Force -Path (Split-Path $dst -Parent) | Out-Null
      Copy-Item -LiteralPath $src -Destination $dst -Force
    }
  }

  # 変更統計の算出
  $fileKinds = Parse-NameStatus $nameStatus
  $numStats  = Parse-Numstat   $numstat

  # メタデータ
  $headSha  = (& git -C $repoRoot rev-parse $headRef).Trim()
  $branch   = (& git -C $repoRoot rev-parse --abbrev-ref HEAD).Trim()
  $metaObj = [ordered]@{
    created_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    base_tag   = $baseTag
    head_ref   = $headRef
    head_sha   = $headSha
    branch     = $branch
    memo       = $memo
    stats      = [ordered]@{
      files_changed = $numStats.files
      insertions    = $numStats.insertions
      deletions     = $numStats.deletions
      kinds         = $fileKinds   # {added, modified, deleted, renamed, copied}
    }
  }
  $metaObj | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $metaPath

  # 人間向けサマリ
  $summary = @()
  $summary += "range: $range"
  $summary += "files_changed: $($numStats.files) (+$($numStats.insertions)/-$($numStats.deletions))"
  $summary += "added:$($fileKinds.added) modified:$($fileKinds.modified) deleted:$($fileKinds.deleted) renamed:$($fileKinds.renamed) copied:$($fileKinds.copied)"
  $summary -join "`r`n" | Set-Content -Encoding UTF8 (Join-Path $destDir 'SUMMARY.txt')

  if ($Zip) {
    $zipPath = "$destDir.zip"
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    Compress-Archive -Path (Join-Path $destDir "*") -DestinationPath $zipPath
    Write-Host ("[OK] Diff backup ZIP: {0}" -f $zipPath) -ForegroundColor Green
  } else {
    Write-Host ("[OK] Diff backup DIR: {0}" -f $destDir) -ForegroundColor Green
  }
}

try {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Halt "git not found. Please check PATH." }

  # repo ルート検出
  $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
  if (-not (Test-Path (Join-Path $repoRoot '.git'))) { $repoRoot = Find-RepoRoot $repoRoot }
  if (-not $repoRoot) { Halt "No git repository found. Put this script inside the project tree." }

  # 復元ポイントタグ名
  $tag  = "rp-{0:yyyyMMdd_HHmmss}" -f (Get-Date)

  # メモ入力
  Write-Host "Memo (optional): " -NoNewline
  $memo = Read-Host

  # 任意：コミット
  if ($Commit) {
    & git -C $repoRoot add -A 1>$null 2>$null
    & git -C $repoRoot commit -m "chore: snapshot for $tag" --no-verify 1>$null 2>$null
  }

  # タグ付け
  $msg = "Restore Point $tag" + ($(if ($memo) { " : $memo" } else { "" }))
  & git -C $repoRoot tag -a $tag -m $msg 2>$null
  if ($LASTEXITCODE -ne 0) { & git -C $repoRoot tag $tag 2>$null }

  # 差分バックアップ（任意）
  if ($Diff) {
    # 保存先（リポ外固定ルート配下へ）
    New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null

    # 差分の起点（明示 > 直近の rp-*）
    $base = if ($BaseTag) { $BaseTag } else { Get-LastRestorePointTag -repoRoot $repoRoot -excludeTag $tag }
    if (-not $base) {
      Write-Host "[WARN] 差分の起点となる rp-* タグが見つかりません。最初の実行はタグ作成のみになります。" -ForegroundColor Yellow
    } else {
      $dest = Join-Path $BackupRoot ("{0}\{1}" -f $base, $tag)
      New-DiffBackup -repoRoot $repoRoot -baseTag $base -headRef "HEAD" -destDir $dest -memo $memo -Zip:$Zip
    }
  }

  Write-Host ""; Write-Host ("OK: Restore Point -> {0}" -f $tag) -ForegroundColor Green
  if ($memo) { Write-Host ("MEMO: {0}" -f $memo) -ForegroundColor DarkGray }
  Wait-AnyKey; exit 0
}
catch { Halt ("Unhandled error: {0}" -f $_.Exception.Message) }
