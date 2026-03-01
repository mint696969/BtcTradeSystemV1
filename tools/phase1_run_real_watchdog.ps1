# path: ./tools/phase1_run_real_watchdog.ps1
# desc: Phase1実取引所用 watchdog 起動ラッパ（ログ退避など含む）。

[CmdletBinding()]
param(
  [string]$RepoRoot = "C:\BtcTradeSystem",
  [switch]$ArchiveLogs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ENV固定
. "$PSScriptRoot\phase1_env.ps1" -RepoRoot $RepoRoot -Mode "DEBUG"

# 証明ログを混ぜない（任意）
if ($ArchiveLogs) {
  $ts = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
  $arch = Join-Path $env:BTC_TS_LOGS_DIR "_archive\$ts"
  New-Item -ItemType Directory -Force -Path $arch | Out-Null

  foreach ($name in @("audit.jsonl","supervisor_collector.jsonl","supervisor_collector.log")) {
    $p = Join-Path $env:BTC_TS_LOGS_DIR $name
    if (Test-Path $p) { Move-Item $p (Join-Path $arch $name) -Force }
  }
  "archived -> $arch" | Write-Host
}

# watchdog起動（このPSはブロックする＝Ctrl+Cで停止）
pwsh -File (Join-Path $RepoRoot "scripts\watchdog_collector.ps1")