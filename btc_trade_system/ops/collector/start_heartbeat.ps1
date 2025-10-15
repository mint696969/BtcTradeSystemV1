# path: ./btc_trade_system/ops/collector/start_heartbeat.ps1
# desc: LeaderLock 心拍の単独起動（DEBUG/DIAG 用）。副作用は locks/status のみ。

param(
  [int]$IntervalSec = [int]($env:BTC_TS_HEARTBEAT_SEC ?? 10),
  [int]$StaleSec = 30,
  [switch]$Background    # バックグラウンド起動する場合に指定
)

$ErrorActionPreference = "Stop"

# --- 1) リポ/実行環境の自己同定 -----------------------------------------
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot  = Resolve-Path (Join-Path $scriptDir "..\..\..")
Set-Location $repoRoot

# venv Python 解決（なければシステム python）
$py = ".\.venv\Scripts\python.exe"; if (-not (Test-Path $py)) { $py = "python" }

# DATA/LOGS 実効パス
function _pp($p){ if(Test-Path $p){(Get-Item $p).FullName}else{ $p } }
$DATA = if ($env:BTC_TS_DATA_DIR) { $env:BTC_TS_DATA_DIR } else { Join-Path (Get-Location) "data" }
$LOGS = if ($env:BTC_TS_LOGS_DIR) { $env:BTC_TS_LOGS_DIR } else { Join-Path (Get-Location) "logs" }
$hbLogDir = Join-Path $LOGS "collector"
New-Item -ItemType Directory -Force $hbLogDir | Out-Null

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$outLog = Join-Path $hbLogDir "heartbeat.$ts.out.log"
$errLog = Join-Path $hbLogDir "heartbeat.$ts.err.log"

Write-Host "[HB] Repo   =" (Get-Location).Path
Write-Host "[HB] DATA   =" (_pp $DATA)
Write-Host "[HB] LOGS   =" (_pp $LOGS)
Write-Host "[HB] Intvl  =" $IntervalSec "sec  | Stale =" $StaleSec "sec"

# --- 2) 実行コマンド ------------------------------------------------------
$mod = ".\btc_trade_system\features\collector\worker\heartbeat.py"
$argList = @($mod, "--stale", "$StaleSec")
if ($env:BTC_TS_HEARTBEAT_SEC -eq $null -and $IntervalSec){
  $argList += @("--interval", "$IntervalSec")
}

if ($Background) {
  Write-Host "[HB] start (background) ->" $outLog
  $p = Start-Process -FilePath $py -ArgumentList $argList `
       -RedirectStandardOutput $outLog -RedirectStandardError $errLog `
       -WindowStyle Hidden -PassThru
  Write-Host "[HB] PID =" $p.Id
  Write-Host "[HB] OUT =" $outLog
  Write-Host "[HB] ERR =" $errLog
} else {
  Write-Host "[HB] start (foreground)"
  & $py @argList *>> $outLog
}

Write-Host "[HB] done"
