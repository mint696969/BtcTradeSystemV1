# path: ./tools/phase1_run_watchdog.ps1
# desc: Phase1 watchdog起動ラッパ（ENV正準化＋ログ退避）を実行する。
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\phase1_env.ps1"

# 証明ログを混ぜない（退避）
$ts = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$arch = Join-Path $env:BTC_TS_LOGS_DIR "_archive\$ts"
New-Item -ItemType Directory -Force -Path $arch | Out-Null
foreach ($f in @("supervisor_collector.jsonl","supervisor_collector.log")) {
  $p = Join-Path $env:BTC_TS_LOGS_DIR $f
  if (Test-Path $p) { Move-Item $p (Join-Path $arch $f) -Force }
}

pwsh -File (Join-Path $env:BTC_TS_CONFIG_DIR "..\..\scripts\watchdog_collector.ps1")
