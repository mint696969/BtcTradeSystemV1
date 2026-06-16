# path: ./tools/test_phase25_health_bundle.ps1
# desc: Runs the Phase 2.5 health verification bundle and prints optional live smoke steps.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $repoRoot 'btcts_next\src'))) {
  throw "repo root not detected from script path: $repoRoot"
}

$env:BTC_TS_REPO_ROOT = $repoRoot
$env:BTCTS_SRC = Join-Path $repoRoot 'btcts_next\src'

function Invoke-PythonScript {
  param(
    [Parameter(Mandatory = $true)][string]$RelativePath
  )

  $fullPath = Join-Path $repoRoot $RelativePath
  if (-not (Test-Path $fullPath)) {
    throw "missing test file: $RelativePath"
  }

  Write-Host "[RUN ] $RelativePath" -ForegroundColor Cyan
  & py -3 $fullPath
  if ($LASTEXITCODE -ne 0) {
    throw "failed: $RelativePath (exit=$LASTEXITCODE)"
  }
  Write-Host "[ OK ] $RelativePath" -ForegroundColor Green
}

$tests = @(
  'btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_signal_events_near_wall_persistence.py',
  'btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_event_usage_policy_contract.py',
  'btcts_next/src/btcts/market_engine/tests/test_orderbook_semantic_policy_resolution.py',
  'btcts_next/src/btcts/market_engine/tests/test_live_orderbook_semantics_summary.py',
  'btcts_next/src/btcts/market_engine/tests/test_market_state_flow.py',
  'btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_semantic_usage.py',
  'btcts_next/src/btcts/apps/operator_ui/tests/test_market_state_bridge.py',
  'btcts_next/src/btcts/apps/operator_ui/tests/test_market_summary_service.py'
)

$started = Get-Date
$passed = New-Object System.Collections.Generic.List[string]

foreach ($test in $tests) {
  Invoke-PythonScript -RelativePath $test
  $passed.Add($test) | Out-Null
}

$elapsed = (Get-Date) - $started
Write-Host ''
Write-Host '=== PHASE 2.5 HEALTH BUNDLE OK ===' -ForegroundColor Green
Write-Host ("passed: {0}" -f $passed.Count)
Write-Host ("elapsed_sec: {0:N1}" -f $elapsed.TotalSeconds)

Write-Host ''
Write-Host 'Optional live smoke:' -ForegroundColor Yellow
Write-Host '$env:BTCTS_MARKET_ENGINE_SMOKE_SECONDS = 30'
Write-Host '$env:BTCTS_MARKET_ENGINE_SMOKE_INTERVAL_SEC = 1'
Write-Host '$env:BTCTS_MARKET_ENGINE_SMOKE_CLEAN_ROOT = 1'
Write-Host 'py -3 .\tools\run_market_engine_runtime_smoke.py'
