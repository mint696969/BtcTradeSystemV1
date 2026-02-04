# path: ./tools/test_phase1_cc_checks.ps1
# desc: Phase1の整合性チェック用ワンショット。Watchdogの stale lock 安全回収（status.json.lock）を“イベント根拠”で検証する（手入力パス排除）。

param(
  [ValidateSet('lock','audit')]
  [string]$Mode = 'lock',

  # audit観測：watchdog を回す秒数
  [ValidateRange(5, 600)]
  [int]$RunSec = 20,

  # audit観測で -UseDummyCollector を使うか（switch だと既定Trueが紛らわしいので bool にする）
  [bool]$UseDummyCollector = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Stop-Script([string]$Message) { throw $Message }

function Get-RepoRoot {
  $p = Resolve-Path -LiteralPath $PSScriptRoot
  (Resolve-Path -LiteralPath (Join-Path $p.Path '..')).Path
}

function Get-CollectorTestProcesses {
  param(
    [datetime]$Since = [datetime]::MinValue
  )

  # Win32_Process.CreationDate は WMI の日付形式なので Convert で DateTime にする
  Get-CimInstance Win32_Process |
    Where-Object {
      ($_.CommandLine -and (
        $_.CommandLine -like '*test_collector_entry.py*' -or
        $_.CommandLine -like '*watchdog_collector.ps1*'
      ))
    } |
    ForEach-Object {
      $cd = $null
      try { $cd = [System.Management.ManagementDateTimeConverter]::ToDateTime($_.CreationDate) } catch {}
      [pscustomobject]@{
        ProcessId    = $_.ProcessId
        Name         = $_.Name
        CommandLine  = $_.CommandLine
        CreatedAt    = $cd
      }
    } |
    Where-Object {
      ($null -eq $_.CreatedAt) -or ($_.CreatedAt -ge $Since)
    }
}

function Stop-CollectorTestProcesses {
  param(
    [datetime]$Since = [datetime]::MinValue,
    [switch]$WhatIf
  )

  $procs = @(Get-CollectorTestProcesses -Since $Since)
  if ($procs.Count -eq 0) { return 0 }

  foreach ($p in $procs) {
    Write-Host ("KILL pid={0} name={1}" -f $p.ProcessId, $p.Name)
    if (-not $WhatIf) {
      Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
  }
  return $procs.Count
}

function Invoke-CollectorTestGuarded {
  param(
    [int]$RunSec,
    [scriptblock]$StartWatchdogBlock,
    [switch]$PreClean
  )

  $t0 = Get-Date

  if ($PreClean) {
    Write-Host "[guard] pre-clean old test processes..."
    [void](Stop-CollectorTestProcesses -Since ([datetime]::MinValue))
  }

  try {
    & $StartWatchdogBlock
    Start-Sleep -Seconds $RunSec
  }
  finally {
    Write-Host "[guard] cleanup processes since $($t0.ToString('s'))..."
    [void](Stop-CollectorTestProcesses -Since $t0)
  }
}

function New-DirectoryIfMissing([string]$Path) {
  if ([string]::IsNullOrWhiteSpace($Path)) { Stop-Script 'empty path' }
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Get-FileTail([string]$Path, [int]$Lines = 60) {
  if (-not (Test-Path -LiteralPath $Path)) { return @("(missing) $Path") }
  try {
    Get-Content -LiteralPath $Path -Encoding UTF8 -Tail $Lines
  } catch {
    @("(read_failed) $Path : $($_.Exception.Message)")
  }
}

function Write-StatusFile([string]$StatusPath, [double]$TsUnix, [string]$Mode='RUNNING', [string]$Message='test') {
  $obj = [ordered]@{
    ts        = $TsUnix
    ts_unix   = $TsUnix
    ts_iso    = (Get-Date ([DateTime]::UnixEpoch.AddSeconds($TsUnix)) -AsUTC).ToString('yyyy-MM-ddTHH:mm:ssZ')
    mode      = $Mode
    message   = $Message
    last_error = ''
    items     = @()
  }
  ($obj | ConvertTo-Json -Depth 10) | Out-File -LiteralPath $StatusPath -Encoding UTF8 -Force
}

function New-LockFile([string]$LockPath) {
  "lock" | Out-File -LiteralPath $LockPath -Encoding UTF8 -Force
}

function Read-JsonLines([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return @() }
  $objs = @()
  foreach ($ln in (Get-Content -LiteralPath $Path -Encoding UTF8)) {
    if ([string]::IsNullOrWhiteSpace($ln)) { continue }
    try { $objs += ($ln | ConvertFrom-Json) } catch { }
  }
  return $objs
}

function Get-EventCount($Arr, [string]$Name) {
  # Where-Object の結果が単一オブジェクトの場合でも .Count が取れるように配列化
  @(@($Arr) | Where-Object { $_.event -eq $Name }).Count
}

# ---- ENV固定（既存設定は尊重。無ければ tmp/_phase1_env を使う） ----------
$repo = Get-RepoRoot
$envRoot = Join-Path $repo 'tmp\_phase1_env'

$cfgDirDefault  = Join-Path $repo 'config'
$dataDirDefault = Join-Path $envRoot 'data'
$logsDirDefault = Join-Path $envRoot 'logs'

New-DirectoryIfMissing $envRoot
New-DirectoryIfMissing $dataDirDefault
New-DirectoryIfMissing $logsDirDefault

if ([string]::IsNullOrWhiteSpace($env:BTC_TS_CONFIG_DIR)) {
  if (-not (Test-Path -LiteralPath $cfgDirDefault)) { Stop-Script "config dir not found: $cfgDirDefault" }
  $env:BTC_TS_CONFIG_DIR = $cfgDirDefault
}
if ([string]::IsNullOrWhiteSpace($env:BTC_TS_DATA_DIR)) { $env:BTC_TS_DATA_DIR = $dataDirDefault }
if ([string]::IsNullOrWhiteSpace($env:BTC_TS_LOGS_DIR)) { $env:BTC_TS_LOGS_DIR = $logsDirDefault }

if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
  $py = Join-Path $repo 'btcts_next\src'
  if (Test-Path -LiteralPath $py) { $env:PYTHONPATH = $py }
}

# ---- 対象 ---------------------------------------------------------------
$watchdog = Join-Path $repo 'scripts\watchdog_collector.ps1'
if (-not (Test-Path -LiteralPath $watchdog)) { Stop-Script "watchdog not found: $watchdog" }

$superLog  = Join-Path $env:BTC_TS_LOGS_DIR 'supervisor_collector.log'
$superJson = Join-Path $env:BTC_TS_LOGS_DIR 'supervisor_collector.jsonl'
$audJsonl  = Join-Path $env:BTC_TS_LOGS_DIR 'audit.jsonl'

$stPath = Join-Path $env:BTC_TS_DATA_DIR 'collector\status.json'
$stLock = "$stPath.lock"

New-DirectoryIfMissing (Split-Path -Parent $stPath)

# NOTE:
# 本スクリプトは「危険洗い出し」が目的のため、既存の監査ログ/監督ログを削除しない。
# （運用証跡の破壊を防ぎ、別プロセス混入も“差分抽出”で抑止する）
# lock モードでのみ status.json / lock をテスト用に上書きする。
if ($Mode -eq 'lock') {
  foreach ($p in @($stPath, $stLock)) {
    if (Test-Path -LiteralPath $p) {
      try { Remove-Item -LiteralPath $p -Force } catch { }
    }
  }
}

# watchdog.yaml が無い場合の既定 hang_timeout_sec=120（Watchdog仕様）
$hangSec = 120

$pwsh = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($pwsh)) { $pwsh = (Get-Command powershell -ErrorAction Stop).Source }

function Start-WatchdogForSeconds([int]$Seconds, [switch]$PreClean) {
  # NOTE: watchdog 停止だけでは子の python が残留するため、開始時刻以降に生成された
  # test_collector_entry.py / watchdog_collector.ps1 関連プロセスを必ず回収する。

  $t0 = Get-Date

  if ($PreClean) {
    Write-Host "[guard] pre-clean old test processes..."
    [void](Stop-CollectorTestProcesses -Since ([datetime]::MinValue))
  }

  # NOTE: $args は PowerShell の自動変数なので使用しない（PSScriptAnalyzer 警告回避）
  $argList = @('-NoProfile','-ExecutionPolicy','Bypass','-File', $watchdog)
  if ($UseDummyCollector) { $argList += '-UseDummyCollector' }

  $proc = $null
  try {
    $proc = Start-Process -FilePath $pwsh -PassThru -WindowStyle Hidden -ArgumentList $argList
    Start-Sleep -Seconds $Seconds
  }
  finally {
    # 1) watchdog 本体を止める
    try {
      if (($null -ne $proc) -and (-not $proc.HasExited)) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
      }
    } catch { }

    Start-Sleep -Milliseconds 300

    # 2) 子の python を回収する（今回開始以降に生成された分）
    Write-Host "[guard] cleanup processes since $($t0.ToString('s'))..."
    [void](Stop-CollectorTestProcesses -Since $t0)

    Start-Sleep -Milliseconds 300
  }
}

function Get-LineCount([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return 0 }
  try {
    # 大きいファイルでも比較的安全に行数だけ取る
    (Get-Content -LiteralPath $Path -Encoding UTF8 -ReadCount 5000 | Measure-Object -Line).Lines
  } catch { 0 }
}

function Read-JsonLinesFromOffset([string]$Path, [int]$SkipLines) {
  if (-not (Test-Path -LiteralPath $Path)) { return @() }
  $objs = @()
  $i = 0
  foreach ($ln in (Get-Content -LiteralPath $Path -Encoding UTF8)) {
    $i++
    if ($i -le $SkipLines) { continue }
    if ([string]::IsNullOrWhiteSpace($ln)) { continue }
    try { $objs += ($ln | ConvertFrom-Json) } catch { }
  }
  return $objs
}

function Get-LastWriteUtc([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return $null }
  try { (Get-Item -LiteralPath $Path).LastWriteTimeUtc } catch { $null }
}

if ($Mode -eq 'audit') {
  # ---- 実行前スナップ（差分抽出の起点） --------------------
  $auditSkip = Get-LineCount $audJsonl
  $superSkip = Get-LineCount $superJson

  $stBefore = Get-LastWriteUtc $stPath

  Start-WatchdogForSeconds -Seconds $RunSec -PreClean

  # ---- 差分だけ読む（他プロセス混入を最小化） --------------
  $audit = Read-JsonLinesFromOffset $audJsonl $auditSkip
  $events = Read-JsonLinesFromOffset $superJson $superSkip

  $sec = [Math]::Max(1, $RunSec)

  $rateState = Get-EventCount $audit 'collector.rate_state.write'
  $statusWr  = Get-EventCount $audit 'collector.status.write'
  $rateHold  = Get-EventCount $audit 'collector.rate.hold'
  $http429   = Get-EventCount $audit 'collector.http.429'

  # status.json の更新有無（監査イベント抑制が仕様でも、ファイル更新は進捗根拠になる）
  $stAfter = Get-LastWriteUtc $stPath
  $stTouched = ($null -ne $stBefore -and $null -ne $stAfter -and $stAfter -gt $stBefore)

  Write-Host ''
  Write-Host '=== phase1_cc_checks audit summary (risk scan) ==='
  Write-Host ("run_sec                          : {0}" -f $RunSec)
  Write-Host ("audit.jsonl new lines            : {0}" -f $audit.Count)
  Write-Host ("supervisor jsonl new lines       : {0}" -f $events.Count)
  Write-Host ''
  Write-Host ("collector.rate_state.write count : {0}  ({1}/sec)" -f $rateState, [Math]::Round($rateState / $sec, 3))
  Write-Host ("collector.status.write count     : {0}  ({1}/sec)  ※仕様で抑制され得る" -f $statusWr, [Math]::Round($statusWr / $sec, 3))
  Write-Host ("collector.rate.hold count        : {0}  ({1}/sec)" -f $rateHold, [Math]::Round($rateHold / $sec, 3))
  Write-Host ("collector.http.429 count         : {0}  ({1}/sec)" -f $http429,  [Math]::Round($http429 / $sec, 3))
  Write-Host ''
  Write-Host ("status.json touched              : {0}" -f $stTouched)
  if ($null -ne $stBefore) { Write-Host ("status.json mtime(before UTC)       : {0:o}" -f $stBefore) }
  if ($null -ne $stAfter)  { Write-Host ("status.json mtime(after  UTC)       : {0:o}" -f $stAfter) }

  # ---- 危険判定（仕様/バグの切り分けに使う） ----------------
  # 1) 監査イベントがゼロ：監査が死んでいる可能性（BTC_TS_MODEや初期化不備）
  if ($audit.Count -eq 0) {
    Write-Host ''
    Write-Host 'RISK: audit.jsonl に新規イベントがありません（監査無効/出力先違い/別プロセスなど）。'
  }

  # 2) status.json が更新されていない：Collector進捗が止まっている可能性（Watchdog hang検知にも影響）
  if (-not $stTouched) {
    Write-Host ''
    Write-Host 'RISK: status.json が更新されていません（Collector停止/出力先違い/権限/例外の可能性）。'
  }

  Write-Host ''
  Write-Host '--- supervisor_collector.log (tail) ---'
  (Get-FileTail $superLog 80) | ForEach-Object { Write-Host $_ }
  Write-Host ''
  Write-Host '--- supervisor_collector.jsonl (tail) ---'
  (Get-FileTail $superJson 80) | ForEach-Object { Write-Host $_ }
  Write-Host ''
  Write-Host '--- audit.jsonl (tail) ---'
  (Get-FileTail $audJsonl 120) | ForEach-Object { Write-Host $_ }
  Write-Host ''
  exit 0
}

# ---- lock テスト（イベント根拠） -----------------------------------------
Write-StatusFile -StatusPath $stPath -TsUnix ([double]([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())) -Message 'fresh'
New-LockFile -LockPath $stLock
Start-WatchdogForSeconds -Seconds 6 -PreClean

$oldTs = [double]([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() - ($hangSec + 10))
Write-StatusFile -StatusPath $stPath -TsUnix $oldTs -Message 'stale'
New-LockFile -LockPath $stLock
Start-WatchdogForSeconds -Seconds 6

$events = Read-JsonLines $superJson
$notOld = ($events | Where-Object { $_.event -eq 'lock.stale.not_old' }).Count
$removed = ($events | Where-Object { $_.event -eq 'lock.stale.removed' }).Count

Write-Host ''
Write-Host '=== phase1_cc_checks summary ==='
Write-Host ("repo             : {0}" -f $repo)
Write-Host ("DATA_DIR          : {0}" -f $env:BTC_TS_DATA_DIR)
Write-Host ("LOGS_DIR          : {0}" -f $env:BTC_TS_LOGS_DIR)
Write-Host ("CONFIG_DIR        : {0}" -f $env:BTC_TS_CONFIG_DIR)
Write-Host ("PYTHONPATH        : {0}" -f $env:PYTHONPATH)
Write-Host ''
Write-Host ("lock.stale.not_old count : {0} (expected >= 1)" -f $notOld)
Write-Host ("lock.stale.removed count : {0} (expected >= 1)" -f $removed)

if ($notOld -lt 1) { Stop-Script "FAIL: lock.stale.not_old not observed" }
if ($removed -lt 1) { Stop-Script "FAIL: lock.stale.removed not observed" }

Write-Host ''
Write-Host 'PASS: stale-lock safety behavior observed via watchdog events.'
Write-Host ''
Write-Host '--- supervisor_collector.log (tail) ---'
(Get-FileTail $superLog 80) | ForEach-Object { Write-Host $_ }
Write-Host ''
Write-Host '--- supervisor_collector.jsonl (tail) ---'
(Get-FileTail $superJson 80) | ForEach-Object { Write-Host $_ }
Write-Host ''
Write-Host '--- audit.jsonl (tail) ---'
(Get-FileTail $audJsonl 80) | ForEach-Object { Write-Host $_ }
Write-Host ''



