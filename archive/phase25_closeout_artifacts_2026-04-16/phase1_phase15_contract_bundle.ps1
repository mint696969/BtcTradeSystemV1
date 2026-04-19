# path: ./archive/archive/phase25_closeout_artifacts_2026-04-16/phase1_phase15_contract_bundle.ps1
# desc: Archived PowerShell utility or regression script.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = 'C:\BtcTradeSystem'
$srcRoot = Join-Path $repoRoot 'btcts_next\src'

if (-not (Test-Path $srcRoot)) {
  throw "src root not found: $srcRoot"
}

$env:PYTHONPATH = $srcRoot

$script:Failures = New-Object System.Collections.Generic.List[string]
$script:Passes = New-Object System.Collections.Generic.List[string]

function Invoke-CompileGroup {
  param(
    [Parameter(Mandatory = $true)][string]$GroupName,
    [Parameter(Mandatory = $true)][string[]]$Files
  )

  Write-Host ''
  Write-Host ("=== COMPILE: {0} ===" -f $GroupName) -ForegroundColor Yellow

  foreach ($file in $Files) {
    Write-Host ("[PILE] {0}" -f $file) -ForegroundColor DarkYellow
    & python -m py_compile $file
    if ($LASTEXITCODE -ne 0) {
      $script:Failures.Add("compile::$GroupName::$file") | Out-Null
      Write-Host ("[FAIL] {0}" -f $file) -ForegroundColor Red
      return
    }
    $script:Passes.Add("compile::$GroupName::$file") | Out-Null
    Write-Host ("[ OK ] {0}" -f $file) -ForegroundColor Green
  }
}

function Invoke-TestGroup {
  param(
    [Parameter(Mandatory = $true)][string]$GroupName,
    [Parameter(Mandatory = $true)][string[]]$Tests
  )

  Write-Host ''
  Write-Host ("=== TEST: {0} ===" -f $GroupName) -ForegroundColor Cyan

  foreach ($test in $Tests) {
    Write-Host ("[RUN ] {0}" -f $test) -ForegroundColor DarkCyan
    & python $test
    if ($LASTEXITCODE -ne 0) {
      $script:Failures.Add("test::$GroupName::$test") | Out-Null
      Write-Host ("[FAIL] {0}" -f $test) -ForegroundColor Red
      return
    }
    $script:Passes.Add("test::$GroupName::$test") | Out-Null
    Write-Host ("[ OK ] {0}" -f $test) -ForegroundColor Green
  }
}

$compileGroups = @(
  @{
    Name = 'l3_event_usage_policy'
    Files = @(
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l3_market_semantics\event_usage_policy.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l3_market_semantics\orderbook\tests\test_event_usage_policy_contract.py'
    )
  },
  @{
    Name = 'market_state_runtime_contracts'
    Files = @(
      'C:\BtcTradeSystem\btcts_next\src\btcts\market_engine\market_state\live_orderbook_semantics.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\market_engine\market_state\projector.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\market_engine\tests\test_live_orderbook_semantics_summary.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\market_engine\tests\test_market_state_flow.py'
    )
  },
  @{
    Name = 'l4_shared_and_adapter'
    Files = @(
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\shared\market_summary.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\shared\health_digest.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\operator_ui\market_summary_adapter.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\operator_ui\health_digest_adapter.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\tests\test_market_summary_builder.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\tests\test_health_digest_builder.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\tests\test_health_digest_adapter.py'
    )
  },
  @{
    Name = 'operator_ui_health_and_bridge'
    Files = @(
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\health_data_service.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\components\health_chart_panels.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\components\health_digest_bridge.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\components\market_state_bridge.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_health_data_service_semantic_usage.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_health_chart_panels_semantic_observer_caption.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_health_data_service_health_digest.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_health_digest_bridge.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_market_summary_service.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_market_state_bridge.py'
    )
  }
)

$testGroups = @(
  @{
    Name = 'l3_event_usage_policy'
    Tests = @(
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l3_market_semantics\orderbook\tests\test_event_usage_policy_contract.py'
    )
  },
  @{
    Name = 'market_state_runtime_contracts'
    Tests = @(
      'C:\BtcTradeSystem\btcts_next\src\btcts\market_engine\tests\test_live_orderbook_semantics_summary.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\market_engine\tests\test_market_state_flow.py'
    )
  },
  @{
    Name = 'l4_shared_and_adapter'
    Tests = @(
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\tests\test_market_summary_builder.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\tests\test_health_digest_builder.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\processing\l4_consumer_models\tests\test_health_digest_adapter.py'
    )
  },
  @{
    Name = 'operator_ui_health_and_bridge'
    Tests = @(
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_market_summary_service.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_market_state_bridge.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_health_data_service_semantic_usage.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_health_chart_panels_semantic_observer_caption.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_health_data_service_health_digest.py',
      'C:\BtcTradeSystem\btcts_next\src\btcts\apps\operator_ui\tests\test_health_digest_bridge.py'
    )
  }
)

$started = Get-Date

Write-Host '=== PHASE 1 / 1.5 CONTRACT BUNDLE START ===' -ForegroundColor Magenta
Write-Host ("repoRoot={0}" -f $repoRoot)
Write-Host ("PYTHONPATH={0}" -f $env:PYTHONPATH)

foreach ($group in $compileGroups) {
  Invoke-CompileGroup -GroupName $group.Name -Files $group.Files
}

foreach ($group in $testGroups) {
  Invoke-TestGroup -GroupName $group.Name -Tests $group.Tests
}

$elapsed = (Get-Date) - $started

Write-Host ''
Write-Host '=== SUMMARY ===' -ForegroundColor Magenta
Write-Host ("passes={0}" -f $script:Passes.Count)
Write-Host ("failures={0}" -f $script:Failures.Count)
Write-Host ("elapsed_sec={0:N1}" -f $elapsed.TotalSeconds)

if ($script:Failures.Count -gt 0) {
  Write-Host ''
  Write-Host 'FAILED ITEMS:' -ForegroundColor Red
  foreach ($failure in $script:Failures) {
    Write-Host (" - {0}" -f $failure) -ForegroundColor Red
  }
  exit 1
}

Write-Host ''
Write-Host 'PHASE 1 / 1.5 CONTRACT BUNDLE OK' -ForegroundColor Green
exit 0
