# path: scripts/git/git_rp_list.ps1
# desc: 復元ポイントの総合一覧（rp-* タグ＋差分ZIP／フルbundle）を“従来表示”で最新順に表示。外部 BtcTradeSystemV1_git を走査

param(
  [string]$RpRoot   = "$env:USERPROFILE\BtcTradeSystemV1_git\git_rp",   # rp差分ZIPルート
  [string]$FullRoot = "$env:USERPROFILE\BtcTradeSystemV1_git\git_full", # フルbundleルート
  [int]   $Limit    = 10,                                               # 表示件数（latest 10）
  [switch]$Details,                                                     # 追加情報（rp: +/-, full: head/branch）
  [switch]$ShowTree,                                                    # ルートツリー表示
  [switch]$OpenRoot,                                                    # ルートを開く
  [switch]$NoPause                                                      # 終了待ちを無効化
)

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

function Get-ZipEntryText([string]$zipPath, [string]$entryName) {
  Add-Type -AssemblyName 'System.IO.Compression.FileSystem' -ErrorAction SilentlyContinue | Out-Null
  $fs = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
  try {
    $e = $fs.Entries | Where-Object { $_.FullName -ieq $entryName }
    if (-not $e) { return $null }
    $sr = New-Object System.IO.StreamReader($e.Open(), [Text.Encoding]::UTF8)
    try { return $sr.ReadToEnd() } finally { $sr.Dispose() }
  } finally { $fs.Dispose() }
}

# --- git 前提 & ルート ---
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git not found' }
$repo = Find-RepoRoot $PSScriptRoot
if (-not $repo) { throw 'No git repository found' }

# ===== rp-*（タグ） + 差分ZIP索引 =====
$tags = & git -C $repo tag --list 'rp-*'
$zipIndex = @{}
if (Test-Path $RpRoot) {
  Get-ChildItem -LiteralPath $RpRoot -Recurse -Filter *.zip -File | ForEach-Object {
    $base = Split-Path $_.DirectoryName -Leaf
    $name = [IO.Path]::GetFileNameWithoutExtension($_.Name)
    $zipIndex[$name] = [pscustomobject]@{ zip=$_.FullName; base=$base }
  }
}

$rpItems = @()
foreach ($t in $tags) {
  if (-not $t) { continue }
  $iso  = (& git -C $repo log -1 --format='%cI' $t) 2>$null
  $date = if ($iso) { [datetime]::Parse($iso) } else { Get-Date 0 }
  $shaS = (& git -C $repo rev-parse --short $t).Trim()
  $subj = (& git -C $repo log -1 --format='%s' $t).Trim()

  $memo = $subj
  $z = $zipIndex[$t]
  if ($z) {
    $metaText = Get-ZipEntryText -zipPath $z.zip -entryName 'metadata.json'
    if ($metaText) {
      try {
        $m = $metaText | ConvertFrom-Json
        if ($m.memo) { $memo = $m.memo }
        if ($Details -and $m.stats) {
          $memo = "{0} (files:{1} +{2}/-{3})" -f $memo, $m.stats.files_changed, $m.stats.insertions, $m.stats.deletions
        }
      } catch {}
    }
  }

  $rpItems += [pscustomobject]@{
    kind = 'RP'; date = $date; sha = $shaS; name = $t; memo = $memo
  }
}

# ===== FULL（bundle） =====
$fullItems = @()
if (Test-Path $FullRoot) {
  Get-ChildItem -LiteralPath $FullRoot -Recurse -Filter *.bundle -File | ForEach-Object {
    $b = $_
    $metaPath = [IO.Path]::ChangeExtension($b.FullName, '.json')
    $d = $b.LastWriteTime; $headS=''; $branch=''

    if (Test-Path $metaPath) {
      try {
        $mj = Get-Content $metaPath -Raw | ConvertFrom-Json
        if ($mj.created_at_utc) { $d = [datetime]::Parse($mj.created_at_utc) }
        $headS  = $mj.head; $branch = $mj.branch
      } catch {}
    }

    $detail = ""
    if ($Details -and $headS) { $detail = "(head:{0} branch:{1})" -f $headS, $branch }

    $fullItems += [pscustomobject]@{
      kind='FULL'; date=$d; sha=$headS; name=$b.BaseName; memo=$detail
    }
  } # end: ForEach-Object

  # ■重複抑止：同じ BaseName が複数ある場合は、日時の新しい1件だけ残す
  $fullItems = $fullItems | Sort-Object date -Descending
  $fullItems = $fullItems | Group-Object name | ForEach-Object { $_.Group | Select-Object -First 1 }
} # end: if (Test-Path $FullRoot)

# ===== マージして最新順 =====
$all = @($rpItems + $fullItems) | Sort-Object date -Descending | Select-Object -First $Limit

# ===== 画面出力（従来風1行） =====
"== Restore Points (rp-* / full)  (latest $Limit) =="
foreach ($x in $all) {
  $dt = $x.date.ToString('yyyy-MM-dd  HH:mm:ss')
  $sha = if ($x.sha) { $x.sha } else { '--------' }
  if ($x.kind -eq 'RP') {
    "{0}  {1,-8} - Restore Point {2} - {3}" -f $dt, $sha, $x.name, $x.memo | Out-Host
  } else {
    $extra = if ([string]::IsNullOrWhiteSpace($x.memo)) { "" } else { " - " + $x.memo }
    ("{0}  {1,-8} - Full Backup  {2}{3}" -f $dt, $sha, $x.name, $extra) | Out-Host
  }
}

if ($ShowTree) {
  ""
  if (Test-Path $RpRoot) {
    "[RpRoot]  $RpRoot"; "(base/tag.zip)"
    Get-ChildItem -LiteralPath $RpRoot | Sort-Object Name | ForEach-Object {
      $b = $_.Name
      $zips = Get-ChildItem -LiteralPath $_.FullName -Filter *.zip -ErrorAction SilentlyContinue
      "  - $b"; foreach ($z in $zips) { "      └─ $($z.BaseName).zip" }
    } | Out-Host
  }
  if (Test-Path $FullRoot) {
    ""; "[FullRoot] $FullRoot"; "(bundle + meta.json)"
    Get-ChildItem -LiteralPath $FullRoot -Recurse -Filter *.bundle -File | Sort-Object Directory,Name |
      ForEach-Object { "  - $($_.Directory.Name)\$($_.BaseName).bundle" } | Out-Host
  }
}

if ($OpenRoot) {
  if (Test-Path $RpRoot)   { Start-Process $RpRoot }
  if (Test-Path $FullRoot) { Start-Process $FullRoot }
}

if (-not $NoPause) {
  ""; "Press any key to exit..."
  $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
}
