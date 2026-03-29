# path: ./tools/run_collector_vnext_stack.ps1
# desc: Unified watchdog と archive worker を一緒に起動する stack launcher。

$ErrorActionPreference = "Stop"

$repoRoot = "C:\BtcTradeSystem"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

$watchdogScript = Join-Path $repoRoot "tools\run_collector_vnext_unified_watchdog.ps1"
$archiveScript = Join-Path $repoRoot "tools\run_collector_vnext_archive_worker.ps1"

$stateRoot = "D:\btc_ts_hot\state\collector_vnext"
$archiveStopRequestPath = Join-Path $stateRoot "archive_stop_request.json"

$env:PYTHONPATH = Join-Path $repoRoot "btcts_next\src"
$env:BTC_TS_DATA_DIR = "D:\btc_ts_hot\data"
$env:BTC_TS_LOGS_DIR = "D:\btc_ts_hot\logs"
$env:BTCTS_STATE_ROOT = "D:\btc_ts_hot\state"
$env:BTCTS_DATA_ROOT = $env:BTC_TS_DATA_DIR
$env:BTCTS_LOGS_ROOT = $env:BTC_TS_LOGS_DIR

function Write-ArchiveStopRequest {
    $dir = Split-Path $archiveStopRequestPath -Parent
    New-Item -ItemType Directory -Force -Path $dir | Out-Null

    $body = @{
        action = "stop"
        requested_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        requested_by = "collector_vnext_stack_launcher"
        reason = "stack_shutdown"
    } | ConvertTo-Json -Depth 8

    Set-Content -Path $archiveStopRequestPath -Value $body -Encoding UTF8
}

function Stop-ArchiveWorkerGracefully {
    param(
        [Parameter(Mandatory=$false)]
        $Process
    )

    try {
        Write-Host "[collector-stack] archive stop request -> $archiveStopRequestPath"
        Write-ArchiveStopRequest
    }
    catch {
        Write-Warning "[collector-stack] failed to write archive stop request: $($_.Exception.Message)"
    }

    if ($null -ne $Process) {
        try {
            if (-not $Process.HasExited) {
                if (-not $Process.WaitForExit(15000)) {
                    Write-Warning "[collector-stack] archive worker did not exit in 15s; forcing stop"
                    Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
                }
            }
        }
        catch {
            Write-Warning "[collector-stack] archive worker shutdown wait failed: $($_.Exception.Message)"
        }
    }
}

$archiveProc = $null

try {
    Write-Host "[collector-stack] repoRoot=$repoRoot"
    Write-Host "[collector-stack] python=$pythonExe"
    Write-Host "[collector-stack] stateRoot=$stateRoot"
    Write-Host "[collector-stack] starting archive worker..."

    $archiveProc = Start-Process `
        -FilePath "powershell" `
        -ArgumentList @(
            "-ExecutionPolicy", "Bypass",
            "-File", $archiveScript
        ) `
        -WorkingDirectory $repoRoot `
        -PassThru `
        -WindowStyle Normal

    Write-Host "[collector-stack] archive worker pid=$($archiveProc.Id)"
    Write-Host "[collector-stack] starting unified watchdog..."

    & powershell -ExecutionPolicy Bypass -File $watchdogScript
    $watchdogExitCode = $LASTEXITCODE

    Write-Host "[collector-stack] unified watchdog exited code=$watchdogExitCode"
    Stop-ArchiveWorkerGracefully -Process $archiveProc

    exit $watchdogExitCode
}
catch {
    Write-Warning "[collector-stack] exception: $($_.Exception.Message)"
    Stop-ArchiveWorkerGracefully -Process $archiveProc
    throw
}
finally {
    Stop-ArchiveWorkerGracefully -Process $archiveProc
}