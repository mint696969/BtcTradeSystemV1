# path: ./tools/phase1_smoke_collector.ps1
# desc: Collectorのスモークテスト（起動→status/audit確認）を自動化する。

[CmdletBinding()]
param(
  [int]$DurationSec = 600
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\phase1_env.ps1"

Write-Host "Smoke start: ${DurationSec}s" -ForegroundColor Cyan
Write-Host "status: $(Join-Path $env:BTC_TS_DATA_DIR 'collector\status.json')" -ForegroundColor DarkCyan
Write-Host "audit : $(Join-Path $env:BTC_TS_LOGS_DIR 'audit.jsonl')" -ForegroundColor DarkCyan

# 退避（証明ログを混ぜない）
$ts = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$arch = Join-Path $env:BTC_TS_LOGS_DIR "_archive\$ts"
New-Item -ItemType Directory -Force -Path $arch | Out-Null
foreach ($f in @("audit.jsonl")) {
  $p = Join-Path $env:BTC_TS_LOGS_DIR $f
  if (Test-Path $p) { Move-Item $p (Join-Path $arch $f) -Force }
}

# Collector 起動（Ctrl+Cで止めてもOK）
$deadline = (Get-Date).AddSeconds($DurationSec)
$job = Start-Job -ScriptBlock {
  python -m btcts.collector.main
}

while ((Get-Date) -lt $deadline) {
  $sp = Join-Path $env:BTC_TS_DATA_DIR "collector\status.json"
  if (Test-Path $sp) {
    try {
      $j = Get-Content $sp -Raw | ConvertFrom-Json
      $m = $j.mode
      $t = $j.ts_unix
      "{0} mode={1} ts_unix={2}" -f (Get-Date).ToUniversalTime().ToString("HH:mm:ss"), $m, $t
    } catch {}
  }
  Start-Sleep -Seconds 5
}

Write-Host "Smoke time reached. Stop collector (Ctrl+C in its window if running foreground) / or stop job." -ForegroundColor Yellow
Stop-Job $job -Force | Out-Null
Remove-Job $job | Out-Null