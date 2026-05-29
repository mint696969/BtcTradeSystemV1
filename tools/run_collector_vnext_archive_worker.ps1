# path: ./tools/run_collector_vnext_archive_worker.ps1
# desc: Collector vNext archive worker を D hot / E cold 前提で起動する launcher。

$ErrorActionPreference = "Stop"

$repoRoot = "C:\BtcTradeSystem"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

$env:PYTHONPATH = Join-Path $repoRoot "btcts_next\src"

# D hot 正本
$env:BTC_TS_DATA_DIR = "D:\btc_ts_hot\data"
$env:BTC_TS_LOGS_DIR = "D:\btc_ts_hot\logs"
$env:BTCTS_STATE_ROOT = "D:\btc_ts_hot\state"

# 互換 bridge
$env:BTCTS_DATA_ROOT = $env:BTC_TS_DATA_DIR
$env:BTCTS_LOGS_ROOT = $env:BTC_TS_LOGS_DIR

# archive config
if (-not $env:BTCTS_ARCHIVE_COLD_ROOT) {
    $env:BTCTS_ARCHIVE_COLD_ROOT = "E:\btc_ts"
}
if (-not $env:BTCTS_ARCHIVE_SCAN_INTERVAL_SEC) {
    $env:BTCTS_ARCHIVE_SCAN_INTERVAL_SEC = "30"
}
if (-not $env:BTCTS_ARCHIVE_STABLE_AGE_SEC) {
    $env:BTCTS_ARCHIVE_STABLE_AGE_SEC = "3600"
}
if (-not $env:BTCTS_ARCHIVE_COPY_MIN_AGE_DAYS) {
    $env:BTCTS_ARCHIVE_COPY_MIN_AGE_DAYS = "1"
}
if (-not $env:BTCTS_ARCHIVE_GC_MIN_AGE_DAYS) {
    $env:BTCTS_ARCHIVE_GC_MIN_AGE_DAYS = "10"
}
if (-not $env:BTCTS_ARCHIVE_MAX_FILES_PER_CYCLE) {
    $env:BTCTS_ARCHIVE_MAX_FILES_PER_CYCLE = "64"
}
if (-not $env:BTCTS_ARCHIVE_MAX_BYTES_PER_CYCLE) {
    $env:BTCTS_ARCHIVE_MAX_BYTES_PER_CYCLE = "268435456"
}
if (-not $env:BTCTS_ARCHIVE_GC_ENABLED) {
    $env:BTCTS_ARCHIVE_GC_ENABLED = "true"
}
if (-not $env:BTCTS_ARCHIVE_GC_DRY_RUN) {
    $env:BTCTS_ARCHIVE_GC_DRY_RUN = "true"
}
if (-not $env:BTCTS_ARCHIVE_MAX_DELETE_FILES_PER_CYCLE) {
    $env:BTCTS_ARCHIVE_MAX_DELETE_FILES_PER_CYCLE = "32"
}
if (-not $env:BTCTS_ARCHIVE_MAX_DELETE_BYTES_PER_CYCLE) {
    $env:BTCTS_ARCHIVE_MAX_DELETE_BYTES_PER_CYCLE = "26843545600"
}

Write-Host "[archive-worker] repoRoot=$repoRoot"
Write-Host "[archive-worker] python=$pythonExe"
Write-Host "[archive-worker] hot_data=$env:BTC_TS_DATA_DIR"
Write-Host "[archive-worker] hot_logs=$env:BTC_TS_LOGS_DIR"
Write-Host "[archive-worker] hot_state=$env:BTCTS_STATE_ROOT"
Write-Host "[archive-worker] cold_root=$env:BTCTS_ARCHIVE_COLD_ROOT"
Write-Host "[archive-worker] scan_interval_sec=$env:BTCTS_ARCHIVE_SCAN_INTERVAL_SEC"
Write-Host "[archive-worker] stable_age_sec=$env:BTCTS_ARCHIVE_STABLE_AGE_SEC"
Write-Host "[archive-worker] copy_min_age_days=$env:BTCTS_ARCHIVE_COPY_MIN_AGE_DAYS"
Write-Host "[archive-worker] max_files_per_cycle=$env:BTCTS_ARCHIVE_MAX_FILES_PER_CYCLE"
Write-Host "[archive-worker] max_bytes_per_cycle=$env:BTCTS_ARCHIVE_MAX_BYTES_PER_CYCLE"
Write-Host "[archive-worker] gc_enabled=$env:BTCTS_ARCHIVE_GC_ENABLED"
Write-Host "[archive-worker] gc_dry_run=$env:BTCTS_ARCHIVE_GC_DRY_RUN"
Write-Host "[archive-worker] max_delete_files_per_cycle=$env:BTCTS_ARCHIVE_MAX_DELETE_FILES_PER_CYCLE"
Write-Host "[archive-worker] max_delete_bytes_per_cycle=$env:BTCTS_ARCHIVE_MAX_DELETE_BYTES_PER_CYCLE"

& $pythonExe -m btcts.collector_vnext.archive.worker
exit $LASTEXITCODE