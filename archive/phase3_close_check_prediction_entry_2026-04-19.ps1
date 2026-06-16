# path: ./archive/phase3_close_check_prediction_entry_2026-04-19.ps1
# desc: Archived PowerShell utility or regression script.

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SrcRoot = Join-Path $RepoRoot 'btcts_next\src'
$PythonExe = 'python'

$env:PYTHONPATH = $SrcRoot

$Targets = @(
    'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_system_contract.py',
    'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_scenario_builder.py',
    'btcts_next\src\btcts\processing\l4_consumer_models\tests\test_prediction_scenario_builder_replay_feedback_invalidation.py'
)

$Failures = @()

Write-Host ('=' * 80)
Write-Host 'phase3 close check - prediction entry core'
Write-Host ('=' * 80)

foreach ($t in $Targets) {
    $full = Join-Path $RepoRoot $t
    if (!(Test-Path $full)) {
        Write-Host "MISSING $t" -ForegroundColor Red
        $Failures += $t
        continue
    }

    Write-Host "RUN $t" -ForegroundColor Cyan
    & $PythonExe $full
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAIL $t" -ForegroundColor Red
        $Failures += $t
    } else {
        Write-Host "OK   $t" -ForegroundColor Green
    }
}

Write-Host ('=' * 80)

if ($Failures.Count -eq 0) {
    Write-Host "ALL GREEN - Prediction Entry is structurally valid" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAILURES:" -ForegroundColor Red
    $Failures | ForEach-Object { Write-Host "- $_" }
    exit 1
}
