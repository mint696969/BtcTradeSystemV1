# path: ./tools/run_warroom_chart_engine.ps1
# desc: Managed runtime for WarRoom base chart engine: starts read-only localhost candle endpoint and updates L4 rolling candle store.

param(
  [string]$RawRoot = "D:\btc_ts_hot",
  [string]$CacheRoot = "D:\btc_ts_hot",
  [string]$HostName = "127.0.0.1",
  [int]$Port = 8765,
  [string]$Exchange = "bitflyer",
  [string]$Symbol = "FX_BTC_JPY",
  [int]$TimeframeSec = 60,
  [int]$RangeMinutes = 180,
  [int]$MaxFiles = 8,
  [int]$MaxTrades = 500000,
  [int]$LatestScanDays = 7,
  [int]$LatestScanFilesPerDay = 24,
  [int]$MaxCandles = 720,
  [int]$RetentionDays = 92,
  [string]$TimeframesSec = "60,300,900,1800,3600,86400",
  [int]$MaxBootstrapBytes = 335544320,
  [int]$IntervalSec = 5,
  [int]$MaxCycles = 0,
  [int]$MaxConsecutiveRefreshFailures = 12,
  [switch]$Once,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Py = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
  $Py = "python"
}

$SrcRoot = Join-Path $RepoRoot "btcts_next\src"
$Endpoint = "http://$HostName`:$Port/warroom/plain-candles/latest"
$HealthUrl = "http://$HostName`:$Port/health"
$StateDir = Join-Path $CacheRoot "state\warroom_chart_engine"
$StatusPath = Join-Path $StateDir "status.json"
$HealthPath = Join-Path $StateDir "health.json"
$RequestPath = Join-Path $StateDir "request.json"
$LockPath = Join-Path $StateDir "runtime.lock.json"
$env:PYTHONPATH = $SrcRoot
$env:WARROOM_PLAIN_CANDLE_CHART_ENDPOINT = $Endpoint

if ($IntervalSec -lt 2) {
  $IntervalSec = 2
}

function Get-NowIsoUtc {
  return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Write-JsonFile {
  param([string]$Path, [object]$Payload)
  $dir = Split-Path -Parent $Path
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  $Payload | ConvertTo-Json -Depth 16 | Set-Content -Path $Path -Encoding UTF8
}

function Read-JsonFile {
  param([string]$Path)
  if (-not (Test-Path $Path)) { return $null }
  try { return Get-Content -Path $Path -Raw -Encoding UTF8 | ConvertFrom-Json } catch { return $null }
}

function ConvertTo-EndpointSummary {
  param([object]$Payload)
  if ($null -eq $Payload) { return $null }
  $summary = [ordered]@{
    ok = $Payload.ok
    version = $Payload.version
    server_version = $Payload.server_version
    server_role = $Payload.server_role
    endpoint_family = $Payload.endpoint_family
    exchange = $Payload.exchange
    symbol = $Payload.symbol
    timeframe_sec = $Payload.timeframe_sec
    candle_count = $Payload.candle_count
    meta = $Payload.meta
    gap_policy = $Payload.gap_policy
    read_only = $Payload.read_only
    broker_send_enabled = $Payload.broker_send_enabled
    order_intent_submitted = $Payload.order_intent_submitted
    ledger_append_allowed = $Payload.ledger_append_allowed
    prediction_invoked = $Payload.prediction_invoked
    classifier_invoked = $Payload.classifier_invoked
  }
  return $summary
}

function Write-ChartEngineStatus {
  param([string]$Mode, [string]$LastAction = "", [object]$Extra = $null)
  $payload = [ordered]@{
    ts = Get-NowIsoUtc
    last_seen_ts = Get-NowIsoUtc
    mode = $Mode
    last_action = $LastAction
    runtime_pid = $PID
    endpoint = $Endpoint
    raw_root = $RawRoot
    cache_root = $CacheRoot
    exchange = $Exchange
    symbol = $Symbol
    timeframe_sec = $TimeframeSec
    timeframes_sec = $TimeframesSec
    retention_days = $RetentionDays
    interval_sec = $IntervalSec
    gap_policy = "absent_candles_no_synthetic_null"
    version = "warroom_chart_engine_runtime.2026_07_07.v1_ui_managed_l4_runtime"
    layer = "L4_CONSUMER_MODEL_OPERATOR_UI_RUNTIME"
    candle_store_module = "btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store"
    append_boundary = "update_state.source_part_file+byte_offset"
    duplicate_policy = "resume_from_update_state_no_reaggregate_processed_trades"
    initial_build_policy = "backfill_or_bootstrap_must_adopt_source_offset_before_live_append"
    read_only_source = $true
    broker_send_enabled = $false
    order_intent_submitted = $false
    prediction_invoked = $false
    classifier_invoked = $false
  }
  $endpointSummary = ConvertTo-EndpointSummary -Payload $Extra
  if ($null -ne $endpointSummary) {
    $payload.extra = $endpointSummary
    if ($endpointSummary.Contains("meta") -and $null -ne $endpointSummary["meta"]) {
      $payload.last_endpoint_meta = $endpointSummary["meta"]
      $payload.latest_candle_end_ts_utc = $endpointSummary["meta"].end_ts_utc
    }
    if ($endpointSummary.Contains("candle_count") -and $null -ne $endpointSummary["candle_count"]) {
      $payload.candle_count = $endpointSummary["candle_count"]
    }
  }
  Write-JsonFile -Path $StatusPath -Payload $payload
}

function Write-ChartEngineHealth {
  param([bool]$Ok, [string]$Reason = "", [object]$Extra = $null)
  Write-JsonFile -Path $HealthPath -Payload ([ordered]@{
    ts = Get-NowIsoUtc
    ok = $Ok
    reason = $Reason
    runtime_pid = $PID
    endpoint = $Endpoint
    extra = (ConvertTo-EndpointSummary -Payload $Extra)
    read_only_source = $true
    broker_send_enabled = $false
    order_intent_submitted = $false
    prediction_invoked = $false
    classifier_invoked = $false
  })
}

function Clear-RequestFile {
  if (Test-Path $RequestPath) { Remove-Item -Force $RequestPath -ErrorAction SilentlyContinue }
}

function Get-RequestedAction {
  $request = Read-JsonFile -Path $RequestPath
  if ($null -eq $request) { return "" }
  $action = ([string]($request.action)).Trim().ToLowerInvariant()
  if ($action -in @("safe_stop", "stop", "stop_stack")) {
    Write-ChartEngineStatus -Mode "STOP_REQUESTED" -LastAction "safe_stop_requested" -Extra $request
    Clear-RequestFile
    return "safe_stop"
  }
  if ($action -eq "restart") {
    Write-ChartEngineStatus -Mode "RESTART_REQUESTED" -LastAction "restart_requested" -Extra $request
    Clear-RequestFile
    return "restart"
  }
  return ""
}

Write-Host "[warroom-chart-engine] repo=$RepoRoot"
Write-Host "[warroom-chart-engine] python=$Py"
Write-Host "[warroom-chart-engine] endpoint=$Endpoint"
Write-Host "[warroom-chart-engine] raw_root=$RawRoot cache_root=$CacheRoot"
Write-Host "[warroom-chart-engine] candle_store_retention_days=$RetentionDays timeframes_sec=$TimeframesSec gap_policy=absent_candles_no_synthetic_null"
Write-Host "[warroom-chart-engine] state_dir=$StateDir"
Write-Host "[warroom-chart-engine] interval_sec=$IntervalSec max_cycles=$MaxCycles once=$Once"
Write-Host "[warroom-chart-engine] read_only=true broker_send_enabled=false order_intent_submitted=false prediction_invoked=false classifier_invoked=false"
Write-Host "[warroom-chart-engine] ui_trigger_enabled=false streamlit_invoked=false"

if ($DryRun) {
  Write-Host "[warroom-chart-engine] dry_run=true"
  Write-Host "[warroom-chart-engine] would start server: $Py -m btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server --host $HostName --port $Port --cache-root $CacheRoot --exchange $Exchange --symbol $Symbol --timeframe-sec $TimeframeSec --max-candles $MaxCandles"
  Write-Host "[warroom-chart-engine] would update rolling candle store every $IntervalSec sec with btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store"
  Write-Host "[warroom-chart-engine] would write status=$StatusPath health=$HealthPath request=$RequestPath lock=$LockPath"
  Write-Host "[warroom-chart-engine] append_boundary=update_state.source_part_file+byte_offset duplicate_policy=resume_from_update_state_no_reaggregate_processed_trades"
  exit 0
}

$ServerJob = $null
$StartedServer = $false
$StopRequested = $false
$RuntimeFailed = $false
$LastRuntimeError = ""
$ConsecutiveRefreshFailures = 0
$LastEndpointPayload = $null

function Test-ChartEngineHealth {
  try {
    $health = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 2 -UseBasicParsing
    return [bool]$health.ok
  } catch {
    return $false
  }
}

function Start-ChartDataServer {
  if (Test-ChartEngineHealth) {
    Write-Host "[warroom-chart-engine] existing server detected: $HealthUrl"
    Write-ChartEngineStatus -Mode "RUNNING" -LastAction "existing_server_detected"
    return
  }
  $script:ServerJob = Start-Job -Name "warroom_chart_data_server" -ScriptBlock {
    param($RepoRoot, $Py, $SrcRoot, $HostName, $Port, $CacheRoot, $Exchange, $Symbol, $TimeframeSec, $MaxCandles)
    Set-Location $RepoRoot
    $env:PYTHONPATH = $SrcRoot
    & $Py -m btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server `
      --host $HostName `
      --port $Port `
      --cache-root $CacheRoot `
      --exchange $Exchange `
      --symbol $Symbol `
      --timeframe-sec $TimeframeSec `
      --max-candles $MaxCandles
  } -ArgumentList $RepoRoot, $Py, $SrcRoot, $HostName, $Port, $CacheRoot, $Exchange, $Symbol, $TimeframeSec, $MaxCandles
  $script:StartedServer = $true
  Write-Host "[warroom-chart-engine] server job started id=$($ServerJob.Id)"

  $ready = $false
  for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    if (Test-ChartEngineHealth) {
      $ready = $true
      break
    }
    if ($ServerJob.State -eq "Failed" -or $ServerJob.State -eq "Completed") {
      Receive-Job $ServerJob -ErrorAction SilentlyContinue | Write-Host
      throw "chart data server stopped before health became ready: state=$($ServerJob.State)"
    }
  }
  if (-not $ready) {
    Receive-Job $ServerJob -ErrorAction SilentlyContinue | Write-Host
    throw "chart data server health timeout: $HealthUrl"
  }
  Write-Host "[warroom-chart-engine] server healthy: $HealthUrl"
  Write-ChartEngineStatus -Mode "RUNNING" -LastAction "server_started"
}

function Stop-ChartDataServer {
  if ($script:StartedServer -and $null -ne $script:ServerJob) {
    Write-Host "[warroom-chart-engine] stopping server job id=$($script:ServerJob.Id)"
    Stop-Job $script:ServerJob -ErrorAction SilentlyContinue | Out-Null
    Remove-Job $script:ServerJob -Force -ErrorAction SilentlyContinue | Out-Null
    $script:StartedServer = $false
    $script:ServerJob = $null
  }
}

function Invoke-RefreshOnce {
  & $Py -m btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store `
    --raw-root $RawRoot `
    --store-root $CacheRoot `
    --exchange $Exchange `
    --symbol $Symbol `
    --timeframes-sec $TimeframesSec `
    --retention-days $RetentionDays `
    --max-days $LatestScanDays `
    --max-bootstrap-bytes $MaxBootstrapBytes
  if ($LASTEXITCODE -ne 0) {
    throw "warroom candle store update failed exit_code=$LASTEXITCODE"
  }
}

try {
  New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
  if (Test-Path $RequestPath) {
    Write-Host "[warroom-chart-engine] clearing stale startup request: $RequestPath"
    Clear-RequestFile
  }
  Write-JsonFile -Path $LockPath -Payload ([ordered]@{ pid = $PID; started_at = Get-NowIsoUtc; command = "tools/run_warroom_chart_engine.ps1"; endpoint = $Endpoint })
  Write-ChartEngineStatus -Mode "STARTING" -LastAction "runtime_starting"
  Write-ChartEngineHealth -Ok $true -Reason "starting"
  Start-ChartDataServer

  $cycle = 0
  while ($true) {
    $action = Get-RequestedAction
    if ($action -eq "safe_stop") {
      $StopRequested = $true
      break
    }
    if ($action -eq "restart") {
      Write-Host "[warroom-chart-engine] restart requested"
      Stop-ChartDataServer
      Start-ChartDataServer
      Write-ChartEngineStatus -Mode "RUNNING" -LastAction "runtime_restarted"
    }

    $cycle += 1
    Write-Host "[warroom-chart-engine] refresh cycle=$cycle start=$(Get-Date -Format o)"
    try {
      Invoke-RefreshOnce
      $script:ConsecutiveRefreshFailures = 0
    } catch {
      $script:ConsecutiveRefreshFailures += 1
      $message = $_.Exception.Message
      Write-Host "[warroom-chart-engine] refresh failed consecutive=$($script:ConsecutiveRefreshFailures)/$MaxConsecutiveRefreshFailures error=$message" -ForegroundColor Yellow
      Write-ChartEngineStatus -Mode "DEGRADED" -LastAction "refresh_cycle_failed" -Extra $script:LastEndpointPayload
      Write-ChartEngineHealth -Ok $false -Reason "refresh_cycle_failed consecutive=$($script:ConsecutiveRefreshFailures)/$MaxConsecutiveRefreshFailures error=$message" -Extra $script:LastEndpointPayload
      if ($script:ConsecutiveRefreshFailures -ge $MaxConsecutiveRefreshFailures) {
        throw "warroom candle store refresh failure threshold reached consecutive=$($script:ConsecutiveRefreshFailures) last_error=$message"
      }
      Start-Sleep -Seconds $IntervalSec
      continue
    }
    try {
      $payload = Invoke-RestMethod -Uri "${Endpoint}?max_candles=$MaxCandles&timeframe_sec=$TimeframeSec" -TimeoutSec 5 -UseBasicParsing
      Write-Host "[warroom-chart-engine] endpoint ok=$($payload.ok) candles=$($payload.candle_count) end=$($payload.meta.end_ts_utc)"
      $script:LastEndpointPayload = $payload
      Write-ChartEngineStatus -Mode "RUNNING" -LastAction "refresh_cycle_ok" -Extra $payload
      Write-ChartEngineHealth -Ok ([bool]$payload.ok) -Reason "endpoint_check" -Extra $payload
    } catch {
      Write-Host "[warroom-chart-engine] endpoint check failed: $($_.Exception.Message)" -ForegroundColor Yellow
      Write-ChartEngineHealth -Ok $false -Reason "endpoint_check_failed: $($_.Exception.Message)"
    }
    if ($Once -or ($MaxCycles -gt 0 -and $cycle -ge $MaxCycles)) {
      break
    }
    Start-Sleep -Seconds $IntervalSec
  }
} catch {
  $script:RuntimeFailed = $true
  $script:LastRuntimeError = $_.Exception.Message
  Write-ChartEngineStatus -Mode "ERROR" -LastAction "runtime_error" -Extra $script:LastEndpointPayload
  Write-ChartEngineHealth -Ok $false -Reason $script:LastRuntimeError -Extra $script:LastEndpointPayload
  throw
} finally {
  Stop-ChartDataServer
  if ($script:RuntimeFailed) {
    Write-ChartEngineStatus -Mode "ERROR" -LastAction "runtime_error_preserved" -Extra $script:LastEndpointPayload
    Write-ChartEngineHealth -Ok $false -Reason $script:LastRuntimeError -Extra $script:LastEndpointPayload
  } elseif ($StopRequested) {
    Write-ChartEngineStatus -Mode "STOPPED" -LastAction "safe_stop_completed" -Extra $script:LastEndpointPayload
    Write-ChartEngineHealth -Ok $true -Reason "safe_stop_completed" -Extra $script:LastEndpointPayload
  } else {
    Write-ChartEngineStatus -Mode "STOPPED" -LastAction "runtime_exit" -Extra $script:LastEndpointPayload
    Write-ChartEngineHealth -Ok $true -Reason "runtime_exit" -Extra $script:LastEndpointPayload
  }
  Remove-Item -Force $LockPath -ErrorAction SilentlyContinue
}

exit 0
