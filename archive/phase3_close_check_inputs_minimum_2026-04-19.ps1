# path: ./archive/phase3_close_check_inputs_minimum_2026-04-19.ps1
# desc: Archived PowerShell utility or regression script.

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SrcRoot = Join-Path $RepoRoot 'btcts_next\src'
$PythonExe = 'python'

$env:PYTHONPATH = $SrcRoot

$CompileTargets = @(
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\market_summary.py'
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\prediction_liquidity_board_history.py'
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\prediction_regime_turning_point.py'
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\prediction_system_input.py'
    'btcts_next\src\btcts\processing\l4_consumer_models\shared\prediction_scenario_builder.py'
    'btcts_next\src\btcts\replay\replay_prediction_artifacts.py'
    'btcts_next\src\btcts\replay\prediction_evaluation_entry.py'
)

$TestGroups = @(
    @{
        Name = 'live_shared_input_owners'
        Targets = @(
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_market_summary_builder.py'
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_liquidity_board_history.py'
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_regime_turning_point.py'
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_system_input.py'
        )
    }
    @{
        Name = 'scenario_core_minimum_input'
        Targets = @(
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_system_contract.py'
            'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_scenario_builder.py'
        )
    }
    @{
        Name = 'replay_input_compatibility'
        Targets = @(
            'btcts_next\src\btcts\replay\tests\test_replay_prediction_artifacts.py'
            'btcts_next\src\btcts\replay\tests\test_prediction_evaluation_entry.py'
            'btcts_next\src\btcts\replay\tests\test_replay_runner_prediction_artifacts.py'
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
Write-Host 'phase3 close check - minimum inputs for collection + processing + prediction entry'
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

Write-Host "`n[3/3] interpretation guide" -ForegroundColor Yellow
if ($Failures.Count -eq 0) {
    Write-Host 'Interpretation:' -ForegroundColor Green
    Write-Host '- minimum live shared input owners are structurally available' -ForegroundColor Green
    Write-Host '- Scenario Core can be built from the current minimum input family' -ForegroundColor Green
    Write-Host '- replay side can consume the same minimum prediction-entry family without structural break' -ForegroundColor Green
} else {
    Write-Host 'Interpretation:' -ForegroundColor Red
    Write-Host '- a failed group indicates minimum-input blockage for Phase 3 close' -ForegroundColor Red
    Write-Host '- fix only the blocker-level issue; do not widen scope during close judgement' -ForegroundColor Red
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
