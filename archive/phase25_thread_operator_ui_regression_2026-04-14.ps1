# path: ./archive/phase25_thread_operator_ui_regression_2026-04-14.ps1
# desc: Archived PowerShell utility or regression script.

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SrcRoot = Join-Path $RepoRoot 'btcts_next\src'
$PythonExe = 'python'

$env:PYTHONPATH = $SrcRoot

$CompileTargets = @(
    'btcts_next\src\btcts\apps\operator_ui\health_data_service.py'
    'btcts_next\src\btcts\apps\operator_ui\app.py'
    'btcts_next\src\btcts\apps\operator_ui\texts\common.py'
    'btcts_next\src\btcts\apps\operator_ui\views\health_page.py'
    'btcts_next\src\btcts\apps\operator_ui\components\market_state_bridge.py'
    'btcts_next\src\btcts\apps\operator_ui\components\market_monitor_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\market_monitor.py'
    'btcts_next\src\btcts\apps\operator_ui\components\market_signal_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_operator_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\agent_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_signal_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_signal_panel.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_reasoning_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_reasoning_panel.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_conversation_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_conversation_panel.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_market_summary_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_market_summary_panel.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_operator_panel.py'
    'btcts_next\src\btcts\apps\operator_ui\components\strategy_state_panel.py'
    'btcts_next\src\btcts\apps\operator_ui\components\agent_panels.py'
    'btcts_next\src\btcts\apps\operator_ui\components\warroom_alert_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\warroom_header_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\warroom_header.py'
    'btcts_next\src\btcts\apps\operator_ui\components\risk_monitor_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\risk_monitor_panel.py'
    'btcts_next\src\btcts\apps\operator_ui\components\market_regime_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\market_regime_panel.py'
    'btcts_next\src\btcts\apps\operator_ui\components\trade_flow_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\trade_flow_monitor.py'
    'btcts_next\src\btcts\apps\operator_ui\components\liquidity_pressure_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\liquidity_pressure_panel.py'
    'btcts_next\src\btcts\apps\operator_ui\components\warroom_timeline_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\warroom_timeline.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_health_data_service_health_digest.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_health_data_service_semantic_usage.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_health_digest_bridge.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_health_page_snapshot_bundle_helpers.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_live_shell_refresh_plan.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_state_bridge.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_monitor_logic.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_monitor_state_summary_bundle.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_signal_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_signal_state_adopters.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_signal_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_reasoning_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_conversation_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_market_summary_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_reasoning_prediction_snapshot.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_market_summary_prediction_snapshot.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_signal_prediction_snapshot.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_operator_prediction_snapshot.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_strategy_state_prediction_snapshot.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_agent_panels_prediction_snapshot.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_risk_monitor_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_regime_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_trade_flow_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_liquidity_pressure_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_warroom_alert_state_live_signal_context.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_warroom_header_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_warroom_timeline_state.py'
)

$TestTargets = @(
    'btcts_next\src\btcts\apps\operator_ui\tests\test_health_data_service_health_digest.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_health_data_service_semantic_usage.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_health_digest_bridge.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_health_page_snapshot_bundle_helpers.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_live_shell_refresh_plan.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_state_bridge.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_monitor_logic.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_monitor_state_summary_bundle.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_signal_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_signal_state_adopters.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_signal_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_reasoning_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_conversation_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_market_summary_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_risk_monitor_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_market_regime_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_trade_flow_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_liquidity_pressure_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_warroom_alert_state_live_signal_context.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_warroom_header_state.py'
    'btcts_next\src\btcts\apps\operator_ui\tests\test_warroom_timeline_state.py'
)

$Failures = New-Object System.Collections.Generic.List[string]
$Successes = New-Object System.Collections.Generic.List[string]

function Resolve-TargetPath {
    param([string]$RelativePath)
    return Join-Path $RepoRoot $RelativePath
}

function Invoke-CheckedCommand {
    param(
        [string]$Kind,
        [string]$RelativePath,
        [scriptblock]$Action
    )

    $FullPath = Resolve-TargetPath $RelativePath
    if (-not (Test-Path $FullPath)) {
        $Failures.Add("[$Kind][missing] $RelativePath") | Out-Null
        Write-Host "MISSING  $Kind  $RelativePath" -ForegroundColor Red
        return
    }

    Write-Host "RUN      $Kind  $RelativePath" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) {
        $Failures.Add("[$Kind][failed] $RelativePath") | Out-Null
        Write-Host "FAILED   $Kind  $RelativePath" -ForegroundColor Red
        return
    }

    $Successes.Add("[$Kind] $RelativePath") | Out-Null
    Write-Host "OK       $Kind  $RelativePath" -ForegroundColor Green
}

Write-Host "=" * 72
Write-Host "phase25 thread operator_ui regression bundle"
Write-Host "repo root : $RepoRoot"
Write-Host "pythonpath: $env:PYTHONPATH"
Write-Host "=" * 72

Write-Host "`n[1/2] py_compile targets" -ForegroundColor Yellow
foreach ($Target in $CompileTargets) {
    Invoke-CheckedCommand -Kind 'compile' -RelativePath $Target -Action {
        & $PythonExe -m py_compile $FullPath
    }
}

Write-Host "`n[2/2] focused tests" -ForegroundColor Yellow
foreach ($Target in $TestTargets) {
    Invoke-CheckedCommand -Kind 'test' -RelativePath $Target -Action {
        & $PythonExe $FullPath
    }
}

Write-Host "`n" + ("=" * 72)
Write-Host ("successes: {0}" -f $Successes.Count)
Write-Host ("failures : {0}" -f $Failures.Count)

if ($Failures.Count -gt 0) {
    Write-Host "`nFAILED ITEMS" -ForegroundColor Red
    foreach ($Item in $Failures) {
        Write-Host "- $Item" -ForegroundColor Red
    }
    exit 1
}

Write-Host "`nALL GREEN" -ForegroundColor Green
exit 0
