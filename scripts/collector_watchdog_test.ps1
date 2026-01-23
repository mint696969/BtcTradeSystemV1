# path: ./scripts/collector_watchdog_test.ps1
# desc: Collector Supervisor(Watchdog) フェーズ1検証用ワンショット起動スクリプト。
#       ENV固定 → stale lock安全掃除 → Watchdog起動 → ログ確認、を1コマンドで再現する。

[CmdletBinding()]
param(
  # ダミーCollectorで監視ロジックのみ検証
  [switch]$Dummy,

  # 明示停止（Ctrl+C 以外で止めたい場合）
  [switch]$Once
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "[test] collector_watchdog_test.ps1 start" -ForegroundColor Cyan

# === 正準パス（Phase1固定） ===
$ROOT = 'C:\BtcTradeSystem'
$env:BTC_TS_CONFIG_DIR = 'E:\btc_ts\config'
$env:BTC_TS_DATA_DIR   = 'E:\btc_ts\data'
$env:BTC_TS_LOGS_DIR   = 'E:\btc_ts\logs'
$env:PYTHONPATH        = Join-Path $ROOT 'btcts_next\src'

# === 事前チェック ===
$req = @(
  $env:BTC_TS_CONFIG_DIR,
  $env:BTC_TS_DATA_DIR,
  $env:BTC_TS_LOGS_DIR,
  $env:PYTHONPATH
)
foreach ($p in $req) {
  if (-not (Test-Path $p)) {
    Write-Host "[test] create dir $p" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $p | Out-Null
  }
}

$btctsInit = Join-Path $env:PYTHONPATH 'btcts\__init__.py'
if (-not (Test-Path $btctsInit)) {
  throw "btcts not found in PYTHONPATH: $btctsInit"
}

# === stale lock の安全掃除（起動前のみ） ===
$statusPath = Join-Path $env:BTC_TS_DATA_DIR 'collector\status.json'
$lockPath   = "$statusPath.lock"
if (Test-Path $lockPath) {
  try {
    $st = Get-Content $statusPath -Raw | ConvertFrom-Json
    $ts = if ($st.ts_unix) { [double]$st.ts_unix } elseif ($st.ts) { [double]$st.ts } else { 0 }
    $age = (Get-Date).ToUniversalTime() - [DateTime]::UnixEpoch.AddSeconds($ts)
    if ($age.TotalSeconds -gt 120) {
      Write-Host "[test] remove stale status.lock (age=${[int]$age.TotalSeconds}s)" -ForegroundColor Yellow
      Remove-Item $lockPath -Force
    } else {
      Write-Host "[test] status.lock is fresh (skip remove)" -ForegroundColor Gray
    }
  } catch {
    Write-Host "[test] cannot evaluate status.lock, keep it" -ForegroundColor DarkYellow
  }
}

# === Watchdog 起動 ===
$wd = Join-Path $ROOT 'scripts\watchdog_collector.ps1'
if (-not (Test-Path $wd)) {
  throw "watchdog_collector.ps1 not found"
}

$arg = @()
if ($Dummy) { $arg += '-UseDummyCollector' }

Write-Host "[test] start watchdog (Dummy=$Dummy)" -ForegroundColor Green

if ($Once) {
  pwsh -File $wd @arg
} else {
  pwsh -File $wd @arg
}

Write-Host "[test] watchdog exited" -ForegroundColor Cyan

# === 結果確認 ===
Write-Host "[test] supervisor log (tail)" -ForegroundColor Cyan
Get-Content (Join-Path $env:BTC_TS_LOGS_DIR 'supervisor_collector.log') -Tail 40
