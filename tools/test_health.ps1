# path: ./tools/test_health.ps1
# desc: Health の動作確認用ワークスペースを生成し、ENV を固定して Streamlit(UI) を起動するテストスクリプト。

param(
  [ValidateSet('OK','WARN','CRIT','ERROR')]
  [string]$Case = 'OK',

  # age_sec を明示指定したい場合（未指定なら Case から自動決定）
  [Nullable[double]]$AgeSec = $null,

  # run.ps1 を起動しない（生成とENV設定だけ）
  [switch]$NoRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-Timestamp {
  return (Get-Date).ToString('yyyyMMdd_HHmmss')
}

function New-DirIfMissing([string]$Path) {
  if (-not (Test-Path $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

# ルート（C:\BtcTradeSystem）をスクリプト位置から自動推定
# tools\test_health.ps1 を前提：親 = C:\BtcTradeSystem
$root = Split-Path -Parent $PSScriptRoot

$repo = Join-Path $root 'btcts_next'
$pyCandidates = @(
  (Join-Path $root '.venv\Scripts\python.exe'),
  'python'  # 最後はPATHに頼る（CI/他PCで有効）
)

if (-not (Test-Path $repo)) {
  throw "repo not found: $repo"
}

$py = $null
foreach ($c in $pyCandidates) {
  if ($c -eq 'python') { $py = $c; break }
  if (Test-Path $c) { $py = $c; break }
}
if (-not $py) {
  throw "python not found. tried: $($pyCandidates -join ', ')"
}

$ts = New-Timestamp
$ws = Join-Path 'C:\BtcTradeSystem\tmp\health_test' $ts

$cfg = Join-Path $ws 'config\ui'
$data = Join-Path $ws 'data'
$logs = Join-Path $ws 'logs'

New-DirIfMissing $cfg
New-DirIfMissing $data
New-DirIfMissing $logs
New-DirIfMissing (Join-Path $data 'collector')

# -----------------------------------------------------------------------------
# ENV固定（このスクリプトの最大の目的）
# -----------------------------------------------------------------------------
$env:PYTHONPATH        = Join-Path $repo 'src'
$env:BTC_TS_CONFIG_DIR = $cfg
$env:BTC_TS_DATA_DIR   = $data
$env:BTC_TS_LOGS_DIR   = $logs

# -----------------------------------------------------------------------------
# monitoring.yaml（テスト用）
#   - UI/Health は load_yaml('monitoring') で BTC_TS_CONFIG_DIR 配下を見る想定
# -----------------------------------------------------------------------------
$monitoringPath = Join-Path $cfg 'monitoring.yaml'

# 既定値：Case に応じて age_sec を変える
if ($null -eq $AgeSec) {
  switch ($Case) {
    'OK'    { $AgeSec = 0.5 }
    'WARN'  { $AgeSec = 12.0 }
    'CRIT'  { $AgeSec = 35.0 }
    'ERROR' { $AgeSec = 0.5 }
  }
}

$monitoringYaml = @(
  'schema_rev: 1'
  'thresholds:'
  '  default:'
  '    age_sec: { warn: 10.0, crit: 30.0 }'
  '    retries: { warn: 1, crit: 3 }'
  'recovery:'
  '  back_to_normal_min_ok: 3'
) -join "`n"

Set-Content -Path $monitoringPath -Value $monitoringYaml -Encoding UTF8

# -----------------------------------------------------------------------------
# status.json（テスト用）
#   - age_sec を直接与えて WARN/CRIT を確実に発生させる
# -----------------------------------------------------------------------------
$statusPath = Join-Path $data 'collector\status.json'

$nowUtc = (Get-Date).ToUniversalTime()
$tsUnix = [double]([DateTimeOffset]$nowUtc).ToUnixTimeMilliseconds() / 1000.0
$tsIso = $nowUtc.ToString('yyyy-MM-ddTHH:mm:ssZ')

$mode = if ($Case -eq 'ERROR') { 'ERROR' } else { 'RUNNING' }
$message = if ($mode -eq 'ERROR') { 'collector error' } else { 'scheduler running endpoints=1' }
$lastError = if ($mode -eq 'ERROR') { 'simulated error for health test' } else { '' }

$item = [ordered]@{
  exchange = 'bitflyer'
  topic    = 'orderbook'
  age_sec  = [double]$AgeSec
  last_ok  = $tsIso
  cause    = if ($mode -eq 'ERROR') { 'simulated_error' } else { $null }
  notes    = if ($mode -eq 'ERROR') { 'This is a test-only status.json' } else { $null }
  retries  = if ($Case -eq 'WARN') { 2 } else { 0 }
}

$status = [ordered]@{
  mode      = $mode
  message   = $message
  last_error= $lastError
  ts        = $tsUnix
  ts_iso    = $tsIso
  ts_unix   = $tsUnix
  items     = @($item)
}

($status | ConvertTo-Json -Depth 10) | Set-Content -Path $statusPath -Encoding UTF8

# -----------------------------------------------------------------------------
# audit.jsonl（テスト用：最小）
# -----------------------------------------------------------------------------
$auditPath = Join-Path $logs 'audit.jsonl'

$trace = [guid]::NewGuid().ToString('N')
$procId = $PID
$hostName = $env:COMPUTERNAME

$events = @()
$events += [ordered]@{ ts=$tsIso; mode='DEBUG'; event='collector.main.start'; feature='collector'; level='INFO'; actor=''; site=''; trace_id=$trace; payload=@{pid=$procId}; meta=@{pid=$procId; host=$hostName} }
if ($mode -eq 'ERROR') {
  $events += [ordered]@{ ts=$tsIso; mode='DEBUG'; event='collector.main.error'; feature='collector'; level='CRIT'; actor=''; site=''; trace_id=$trace; payload=@{err=$lastError}; meta=@{pid=$procId; host=$hostName} }
} else {
  $events += [ordered]@{ ts=$tsIso; mode='DEBUG'; event='collector.endpoint.ok'; feature='collector'; level='INFO'; actor=''; site=''; trace_id=$trace; payload=@{exchange='bitflyer'; topic='orderbook'; bytes=900; elapsed_ms=250}; meta=@{pid=$procId; host=$hostName} }
}

$events | ForEach-Object { ($_ | ConvertTo-Json -Compress) } | Set-Content -Path $auditPath -Encoding UTF8

# -----------------------------------------------------------------------------
# 確認出力
# -----------------------------------------------------------------------------
Write-Host "Workspace : $ws"
Write-Host "CONFIG    : $env:BTC_TS_CONFIG_DIR"
Write-Host "DATA      : $env:BTC_TS_DATA_DIR"
Write-Host "LOGS      : $env:BTC_TS_LOGS_DIR"
Write-Host "monitoring: $monitoringPath"
Write-Host "status    : $statusPath"
Write-Host "audit     : $auditPath"
Write-Host "Case      : $Case (age_sec=$AgeSec)"

# load_yaml が実際に見るパスを Python で確定表示
& $py -c "from btcts.settings import load_yaml_with_path; r=load_yaml_with_path('monitoring'); p=r[1] if isinstance(r, tuple) else getattr(r,'path',None); print('load_yaml(monitoring) =>', p)" | Write-Host

if ($NoRun) {
  Write-Host 'NoRun specified: workspace generated; not launching UI.'
  exit 0
}

# UI起動（Health タブで OK/WARN/CRIT を確認）
Push-Location 'C:\BtcTradeSystem'
try {
  .\scripts\run.ps1
}
finally {
  Pop-Location
}
