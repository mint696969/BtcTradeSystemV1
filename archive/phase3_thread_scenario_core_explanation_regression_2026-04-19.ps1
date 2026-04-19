# path: ./archive/phase3_thread_scenario_core_explanation_regression_2026-04-19.ps1
# desc: Archived PowerShell utility or regression script.

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SrcRoot = Join-Path $RepoRoot 'btcts_next\src'
$PythonExe = 'python'

$env:PYTHONPATH = $SrcRoot

$CompileTargets = @(
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\prediction_system_contract.py'
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\prediction_system_input.py'
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\prediction_replay_feedback.py'
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\prediction_scenario_builder.py'
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\prediction_summary.py'
    'btcts_next\src\btcts\processing\l4_consumer_models\operator_ui\prediction_summary_adapter.py'
    'btcts_next\src\btcts\replay\prediction_evaluation_entry.py'
    'btcts_next\src\btcts\replay\prediction_evaluation_report.py'
    'btcts_next\src\btcts\replay\prediction_calibration_review.py'
    'btcts_next\src\btcts\replay\replay_prediction_feedback.py'
    'btcts_next\src\btcts\replay\replay_prediction_artifacts.py'
    'btcts_next\src\btcts\apps\operator_ui\components\prediction_summary_presenter.py'
    'btcts_next\src\btcts\apps\operator_ui\components\warroom_header_state.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_operator_display_payloads.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_operator_advisory.py'
    'btcts_next\src\btcts\apps\operator_ui\components\ai_operator_panel.py'
)

$TestGroups = @(
    @{
        Name = 'scenario_core_contracts'
        Targets = @(
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_system_contract.py'
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_system_input.py'
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_scenario_builder.py'
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_scenario_builder_replay_feedback_invalidation.py'
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_replay_feedback_builder.py'
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_summary_adapter.py'
        )
    }
    @{
        Name = 'replay_feedback_loop'
        Targets = @(
            'btcts_next\src\btcts\replay\tests\test_prediction_evaluation_entry.py'
            'btcts_next\src\btcts\replay\tests\test_prediction_evaluation_report.py'
            'btcts_next\src\btcts\replay\tests\test_prediction_calibration_review.py'
            'btcts_next\src\btcts\replay\tests\test_replay_runner_prediction_feedback_scenario_bridge.py'
            'btcts_next\src\btcts\replay\tests\test_replay_prediction_artifacts.py'
            'btcts_next\src\btcts\replay\tests\test_replay_runner_prediction_artifacts.py'
            'btcts_next\src\btcts\replay\tests\test_replay_runner_export_prediction_artifacts.py'
        )
    }
    @{
        Name = 'operator_ui_explanation_consumers'
        Targets = @(
            'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_operator_advisory.py'
            'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_operator_display_payloads.py'
            'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_operator_presenter.py'
            'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_operator_prediction_snapshot.py'
            'btcts_next\src\btcts\apps\operator_ui\tests\test_ai_reasoning_prediction_snapshot.py'
            'btcts_next\src\btcts\apps\operator_ui\tests\test_warroom_header_state.py'
        )
    }
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
        [string]$Label,
        [string]$RelativePath,
        [scriptblock]$Action
    )

    $script:FullPath = Resolve-TargetPath $RelativePath
    if (-not (Test-Path $script:FullPath)) {
        $Failures.Add("[$Kind][$Label][missing] $RelativePath") | Out-Null
        Write-Host "MISSING  $Kind  $Label  $RelativePath" -ForegroundColor Red
        return
    }

    Write-Host "RUN      $Kind  $Label  $RelativePath" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) {
        $Failures.Add("[$Kind][$Label][failed] $RelativePath") | Out-Null
        Write-Host "FAILED   $Kind  $Label  $RelativePath" -ForegroundColor Red
        return
    }

    $Successes.Add("[$Kind][$Label] $RelativePath") | Out-Null
    Write-Host "OK       $Kind  $Label  $RelativePath" -ForegroundColor Green
}

Write-Host ('=' * 80)
Write-Host 'phase3 scenario core + replay feedback + ai advisory explanation regression'
Write-Host "repo root : $RepoRoot"
Write-Host "pythonpath: $env:PYTHONPATH"
Write-Host ('=' * 80)

Write-Host "`n[1/3] py_compile targets" -ForegroundColor Yellow
foreach ($Target in $CompileTargets) {
    Invoke-CheckedCommand -Kind 'compile' -Label 'bundle' -RelativePath $Target -Action {
        & $PythonExe -m py_compile $script:FullPath
    }
}

Write-Host "`n[2/3] focused test groups" -ForegroundColor Yellow
foreach ($Group in $TestGroups) {
    Write-Host "`n--- group: $($Group.Name) ---" -ForegroundColor Magenta
    foreach ($Target in $Group.Targets) {
        Invoke-CheckedCommand -Kind 'test' -Label $Group.Name -RelativePath $Target -Action {
            & $PythonExe $script:FullPath
        }
    }
}

Write-Host "`n[3/3] bundle interpretation" -ForegroundColor Yellow
if ($Failures.Count -eq 0) {
    Write-Host 'Interpretation:' -ForegroundColor Green
    Write-Host '- Scenario Core contract / replay feedback / explanation consumer line are structurally consistent.' -ForegroundColor Green
    Write-Host '- This bundle is designed to catch boundary drift, not live-market quality.' -ForegroundColor Green
} else {
    Write-Host 'Interpretation:' -ForegroundColor Red
    Write-Host '- A failure here means boundary drift or expectation mismatch exists in the current mainline.' -ForegroundColor Red
    Write-Host '- Resolve the failed group before thread migration or further expansion.' -ForegroundColor Red
}

Write-Host "`n" + ('=' * 80)
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
