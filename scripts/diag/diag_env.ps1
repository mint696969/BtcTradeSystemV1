# path: ./scripts/diag/diag_env.ps1
# desc: リポ環境スモーク＆UI純読取チェック（apps/dashからの書込/削除APIの粗スキャンを含む）

param()

$ErrorActionPreference = "Stop"

# スクリプトディレクトリ
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# --- A. リポ自己同定（git優先 / フォールバック= ..\.. ） -------------
$repoRoot = $null
try {
  Push-Location $scriptDir
  $top = git rev-parse --show-toplevel 2>$null
  Pop-Location
  if ($LASTEXITCODE -eq 0 -and $top) { $repoRoot = $top.Trim() }
} catch { }

if (-not $repoRoot) {
  # scripts/diag から2階層上がリポルート想定
  $repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
}

Set-Location $repoRoot
Write-Host "[A-1] RepoRoot =" (Get-Location).Path

$branch = ""; $commit = ""
git rev-parse --is-inside-work-tree 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
  $branch = git branch --show-current
  $commit = git rev-parse --short HEAD
  Write-Host "[A-2] Git =" $branch $commit
} else {
  Write-Host "[A-2] Git = (not a git repo)"
}

# --- B. 実効パス ---------------------------------------------------------
function _pp($p){ if(Test-Path $p){(Get-Item $p).FullName}else{"(missing) $p"} }
$DATA = if ($env:BTC_TS_DATA_DIR) { $env:BTC_TS_DATA_DIR } else { Join-Path (Get-Location) "data" }
$LOGS = if ($env:BTC_TS_LOGS_DIR) { $env:BTC_TS_LOGS_DIR } else { Join-Path (Get-Location) "logs" }
Write-Host "[B-1] DATA =" (_pp $DATA)
Write-Host "[B-2] LOGS =" (_pp $LOGS)

# --- C. UI純読取チェック -----------------------------------------------
$targets = @(
  (Join-Path $repoRoot "btc_trade_system\apps"),
  (Join-Path $repoRoot "btc_trade_system\features\dash")
) | Where-Object { Test-Path $_ }

if (-not $targets) {
  Write-Host "[C] targets not found (btc_trade_system/apps or features/dash)"
} else {
  $patterns = @(
    'open\(.+[, ]+["' + "'" + ']w',  # open(...,"w")
    'open\(.+[, ]+["' + "'" + ']a',  # open(...,"a")
    '\.write\(', '\.writelines\(',
    'os\.remove\(', 'os\.rename\(',
    'Path\(.+\)\.write_text\(', 'Path\(.+\)\.write_bytes\('
  )
  foreach($t in $targets){
    $files = Get-ChildItem -Path $t -Recurse -Filter *.py -File -ErrorAction SilentlyContinue
    Write-Host "[C] scan target:" $t " files=" $files.Count
    foreach($pat in $patterns){
      Write-Host "  - pattern:" $pat
      $hit = $files | Select-String -Pattern $pat -Encoding UTF8
      if ($hit){ $hit | ForEach-Object { $_.Path + ":" + $_.LineNumber + " :: " + $_.Line.Trim() } }
      else { Write-Host "    (no match)" }
    }
  }
}

# --- D. ポート確認（null安全：既出の修正版） ---------------------------
$ports = 8501,8503
foreach ($p in $ports) {
  $m = netstat -ano | Select-String ":$p\s"
  if ($m) {
    $n = $m.ToString()
    $netPid = ($n -split "\s+")[-1]
    $proc = Get-Process -Id $netPid -ErrorAction SilentlyContinue
    Write-Host "[D-$p] LISTEN: PID=$netPid Name=$($proc.ProcessName)"
    try {
      $resp = curl.exe -s "http://localhost:$p/health" 2>$null
      if (-not $resp) { $resp = curl.exe -s "http://localhost:$p" 2>$null }
      if ($resp) { Write-Host "[D-$p] HTTP reachable (snippet):" ($resp.Substring(0,[Math]::Min(120,$resp.Length))) }
    } catch { Write-Host "[D-$p] HTTP probe failed" }
  } else {
    Write-Host "[D-$p] (no listener)"
  }
}

Write-Host "==== DONE (diag_env) ===="

# --- B. 実効パス ---------------------------------------------------------
function _pp($p){ if(Test-Path $p){(Get-Item $p).FullName}else{"(missing) $p"} }
$DATA = if ($env:BTC_TS_DATA_DIR) { $env:BTC_TS_DATA_DIR } else { Join-Path (Get-Location) "data" }
$LOGS = if ($env:BTC_TS_LOGS_DIR) { $env:BTC_TS_LOGS_DIR } else { Join-Path (Get-Location) "logs" }
Write-Host "[B-1] DATA =" (_pp $DATA)
Write-Host "[B-2] LOGS =" (_pp $LOGS)

# --- C. UI純読取チェック（書込/削除APIの粗スキャン） --------------------
$targets = @(
  "btc_trade_system\apps",
  "btc_trade_system\features\dash"
) | Where-Object { Test-Path $_ }

if (-not $targets) {
  Write-Host "[C] targets not found (apps/dash)"; 
} else {
  $patterns = @(
    'open\(.+[, ]+["' + "'" + ']w',  # open(...,"w")
    'open\(.+[, ]+["' + "'" + ']a',  # open(...,"a")
    '\.write\(', '\.writelines\(',
    'os\.remove\(', 'os\.rename\(',
    'Path\(.+\)\.write_text\(', 'Path\(.+\)\.write_bytes\('
  )
  foreach($t in $targets){
    $files = Get-ChildItem -Path $t -Recurse -Filter *.py -File -ErrorAction SilentlyContinue
    Write-Host "[C] scan target:" $t " files=" $files.Count
    foreach($pat in $patterns){
      Write-Host "  - pattern:" $pat
      $hit = $files | Select-String -Pattern $pat -Encoding UTF8
      if ($hit){ $hit | ForEach-Object { $_.Path + ":" + $_.LineNumber + " :: " + $_.Line.Trim() } }
      else { Write-Host "    (no match)" }
    }
  }
}

# --- D. ポート確認（null安全） ------------------------------------------
$ports = 8501,8503
foreach ($p in $ports) {
  $m = netstat -ano | Select-String ":$p\s"
  if ($m) {
    $n = $m.ToString()
    $netPid = ($n -split "\s+")[-1]
    $proc = Get-Process -Id $netPid -ErrorAction SilentlyContinue
    Write-Host "[D-$p] LISTEN: PID=$netPid Name=$($proc.ProcessName)"
    try {
      $resp = curl.exe -s "http://localhost:$p/health" 2>$null
      if (-not $resp) { $resp = curl.exe -s "http://localhost:$p" 2>$null }
      if ($resp) { Write-Host "[D-$p] HTTP reachable (snippet):" ($resp.Substring(0,[Math]::Min(120,$resp.Length))) }
    } catch { Write-Host "[D-$p] HTTP probe failed" }
  } else {
    Write-Host "[D-$p] (no listener)"
  }
}

Write-Host "==== DONE (diag_env) ===="
