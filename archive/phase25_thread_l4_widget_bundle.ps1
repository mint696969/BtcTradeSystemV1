# path: ./archive/phase25_thread_l4_widget_bundle.ps1
# desc: Archived PowerShell utility or regression script.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$srcRoot = Join-Path $repoRoot 'btcts_next\src'

if (-not (Test-Path $srcRoot)) {
  throw "src root not found: $srcRoot"
}

$env:PYTHONPATH = $srcRoot

$script:Failures = New-Object System.Collections.Generic.List[string]
$script:Passes = New-Object System.Collections.Generic.List[string]

function Invoke-CompileFile {
  param(
    [Parameter(Mandatory = $true)][string]$RelativePath
  )

  $fullPath = Join-Path $repoRoot $RelativePath
  if (-not (Test-Path $fullPath)) {
    $script:Failures.Add("compile::missing::$RelativePath") | Out-Null
    Write-Host ("[MISS] {0}" -f $RelativePath) -ForegroundColor Red
    return
  }

  Write-Host ("[PILE] {0}" -f $RelativePath) -ForegroundColor DarkYellow
  & python -m py_compile $fullPath
  if ($LASTEXITCODE -ne 0) {
    $script:Failures.Add("compile::$RelativePath") | Out-Null
    Write-Host ("[FAIL] {0}" -f $RelativePath) -ForegroundColor Red
    return
  }

  $script:Passes.Add("compile::$RelativePath") | Out-Null
  Write-Host ("[ OK ] {0}" -f $RelativePath) -ForegroundColor Green
}

function Invoke-PythonScript {
  param(
    [Parameter(Mandatory = $true)][string]$RelativePath
  )

  $fullPath = Join-Path $repoRoot $RelativePath
  if (-not (Test-Path $fullPath)) {
    $script:Failures.Add("test::missing::$RelativePath") | Out-Null
    Write-Host ("[MISS] {0}" -f $RelativePath) -ForegroundColor Red
    return
  }

  Write-Host ("[RUN ] {0}" -f $RelativePath) -ForegroundColor Cyan
  & python $fullPath
  if ($LASTEXITCODE -ne 0) {
    $script:Failures.Add("test::$RelativePath") | Out-Null
    Write-Host ("[FAIL] {0}" -f $RelativePath) -ForegroundColor Red
    return
  }

  $script:Passes.Add("test::$RelativePath") | Out-Null
  Write-Host ("[ OK ] {0}" -f $RelativePath) -ForegroundColor Green
}

$compileGroups = @(
  @{
    Name = 'l4_shared_and_adapter'
    Files = @(
      'btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py',
      'btcts_next/src/btcts/processing/l4_consumer_models/shared/health_digest.py',
      'btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py',
      'btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/health_digest_adapter.py',
      'btcts_next/src/btcts/processing/l4_consumer_models/tests/test_market_summary_builder.py',
      'btcts_next/src/btcts/processing/l4_consumer_models/tests/test_health_digest_builder.py',
      'btcts_next/src/btcts/processing/l4_consumer_models/tests/test_health_digest_adapter.py'
    )
  },
  @{
    Name = 'operator_ui_market_summary'
    Files = @(
      'btcts_next/src/btcts/apps/operator_ui/components/market_summary_presenter.py',
      'btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_market_summary_service.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_market_summary_presenter.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_market_state_bridge.py'
    )
  },
  @{
    Name = 'operator_ui_health_digest'
    Files = @(
      'btcts_next/src/btcts/apps/operator_ui/health_data_service.py',
      'btcts_next/src/btcts/apps/operator_ui/components/health_digest_bridge.py',
      'btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py',
      'btcts_next/src/btcts/apps/operator_ui/components/health_detail_panels.py',
      'btcts_next/src/btcts/apps/operator_ui/components/health_chart_panels.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_semantic_usage.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_health_digest.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_digest_bridge.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_top_panels_digest_caption.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_detail_panels_digest_caption.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_chart_panels_semantic_observer_caption.py'
    )
  },
  @{
    Name = 'operator_ui_market_monitor'
    Files = @(
      'btcts_next/src/btcts/apps/operator_ui/components/market_monitor_presenter.py',
      'btcts_next/src/btcts/apps/operator_ui/texts/warroom.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_market_monitor_presenter.py'
    )
  }
)

$testGroups = @(
  @{
    Name = 'l4_shared_and_adapter'
    Tests = @(
      'btcts_next/src/btcts/processing/l4_consumer_models/tests/test_market_summary_builder.py',
      'btcts_next/src/btcts/processing/l4_consumer_models/tests/test_health_digest_builder.py',
      'btcts_next/src/btcts/processing/l4_consumer_models/tests/test_health_digest_adapter.py'
    )
  },
  @{
    Name = 'operator_ui_market_summary'
    Tests = @(
      'btcts_next/src/btcts/apps/operator_ui/tests/test_market_summary_service.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_market_summary_presenter.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_market_state_bridge.py'
    )
  },
  @{
    Name = 'operator_ui_health_digest'
    Tests = @(
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_semantic_usage.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_health_digest.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_digest_bridge.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_top_panels_digest_caption.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_detail_panels_digest_caption.py',
      'btcts_next/src/btcts/apps/operator_ui/tests/test_health_chart_panels_semantic_observer_caption.py'
    )
  },
  @{
    Name = 'operator_ui_market_monitor'
    Tests = @(
      'btcts_next/src/btcts/apps/operator_ui/tests/test_market_monitor_presenter.py'
    )
  }
)

$started = Get-Date

Write-Host '=== THREAD L4 / WIDGET / CAPTION BUNDLE START ===' -ForegroundColor Magenta
Write-Host ("repoRoot={0}" -f $repoRoot)
Write-Host ("PYTHONPATH={0}" -f $env:PYTHONPATH)

foreach ($group in $compileGroups) {
  Write-Host ''
  Write-Host ("=== COMPILE: {0} ===" -f $group.Name) -ForegroundColor Yellow
  foreach ($file in $group.Files) {
    Invoke-CompileFile -RelativePath $file
  }
}

foreach ($group in $testGroups) {
  Write-Host ''
  Write-Host ("=== TEST: {0} ===" -f $group.Name) -ForegroundColor Cyan
  foreach ($test in $group.Tests) {
    Invoke-PythonScript -RelativePath $test
  }
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
Write-Host 'THREAD L4 / WIDGET / CAPTION BUNDLE OK' -ForegroundColor Green
exit 0
