# path: ./tools/phase3_run_main.ps1
# desc: Phase3A統合runner（Main PC）。watchdog_collector + derived/quality runner を常駐させ、日次 evidence_pack を生成する。

[CmdletBinding()]
param(
  [ValidateSet('NORMAL','DEBUG','BOOST')]
  [string]$Mode = 'NORMAL',

  # 省略時は 24h 動作（運用では 720h=30日 など）
  [double]$DurationHours = 24,

  # 1回だけ起動確認（watchdog/derivedを起動→evidence_pack実行→終了）
  [switch]$Once
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function NowIso { (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }

function New-DirIfMissing([string]$Path) {
  if ([string]::IsNullOrWhiteSpace($Path)) { throw "Path is empty" }
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Resolve-RepoRoot {
  $root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..') | Select-Object -ExpandProperty Path
  return $root
}

function Resolve-EnvOrDefault([string]$Name, [string]$Default) {
  $v = [Environment]::GetEnvironmentVariable($Name)
  if ([string]::IsNullOrWhiteSpace($v)) { return $Default }
  return $v
}

function Add-Jsonl([string]$Path, [hashtable]$Obj) {
  New-DirIfMissing (Split-Path -Parent $Path)
  $Obj.ts = NowIso
  $json = ($Obj | ConvertTo-Json -Depth 10 -Compress)
  Add-Content -LiteralPath $Path -Value $json -Encoding UTF8
}

function Open-Lock([string]$LockPath) {
  New-DirIfMissing (Split-Path -Parent $LockPath)
  try {
    return [System.IO.File]::Open($LockPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
  } catch {
    throw "lock busy: $LockPath"
  }
}

function Start-ChildPwsh {
  param(
    [Parameter(Mandatory)][string]$Name,
    [Parameter(Mandatory)][string]$FilePath,
    [string[]]$ChildArgs = @(),
    [Parameter(Mandatory)][hashtable]$EnvMap,
    [Parameter(Mandatory)][string]$StdoutPath,
    [Parameter(Mandatory)][string]$StderrPath
  )

  $pwsh = (Get-Command pwsh -ErrorAction Stop).Source
  $argList = @('-NoProfile','-ExecutionPolicy','Bypass','-File', $FilePath) + $ChildArgs

  New-DirIfMissing (Split-Path -Parent $StdoutPath)
  New-DirIfMissing (Split-Path -Parent $StderrPath)

  $p = Start-Process -FilePath $pwsh `
    -ArgumentList $argList `
    -PassThru -WindowStyle Hidden `
    -Environment $EnvMap `
    -RedirectStandardOutput $StdoutPath `
    -RedirectStandardError  $StderrPath

  return $p
}

function Find-RunningPwshScript {
  param(
    [Parameter(Mandatory)][string]$ScriptPath
  )

  $full = (Resolve-Path -LiteralPath $ScriptPath).Path
  $escaped = [regex]::Escape($full)

  $p = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Name -match '^pwsh(\.exe)?$' -and
      $_.CommandLine -match $escaped
    } |
    Sort-Object ProcessId |
    Select-Object -First 1

  return $p
}

function Invoke-EvidencePackOnce {
  param(
    [Parameter(Mandatory)][string]$PythonExe,
    [Parameter(Mandatory)][hashtable]$EnvMap,
    [Parameter(Mandatory)][string]$JsonlPath
  )

  Add-Jsonl $JsonlPath @{ level='INFO'; event='evidence_pack.start' }

  $out = & $PythonExe -m btcts.derived.evidence_pack 2>&1
  $txt = ($out -join "`n")

  if ($LASTEXITCODE -eq 0) {
    Add-Jsonl $JsonlPath @{ level='INFO'; event='evidence_pack.ok'; output=$txt }
    return $true
  } else {
    Add-Jsonl $JsonlPath @{ level='ERROR'; event='evidence_pack.fail'; exit_code=$LASTEXITCODE; output=$txt }
    return $false
  }
}

function Invoke-SoakReportOnce {
  param(
    [Parameter(Mandatory)][string]$PythonExe,
    [Parameter(Mandatory)][string]$RepoRoot,
    [Parameter(Mandatory)][string]$JsonlPath,
    [double]$Hours = 168
  )

  Add-Jsonl $JsonlPath @{ level='INFO'; event='soak_report.start'; hours=$Hours }

  Push-Location $RepoRoot
  try {
    $out = & $PythonExe 'tools\phase3_soak_report.py' --hours $Hours 2>&1
    $txt = ($out -join "`n")

    if ($LASTEXITCODE -eq 0) {
      Add-Jsonl $JsonlPath @{ level='INFO'; event='soak_report.ok'; hours=$Hours; output=$txt }
      return $true
    } else {
      Add-Jsonl $JsonlPath @{ level='ERROR'; event='soak_report.fail'; hours=$Hours; exit_code=$LASTEXITCODE; output=$txt }
      return $false
    }
  } finally {
    Pop-Location
  }
}

function TodayUtcKey { (Get-Date).ToUniversalTime().ToString('yyyyMMdd') }

function Get-DirSizeBytes([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return 0 }
  $sum = 0L
  try {
    Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { $sum += $_.Length }
  } catch { }
  return $sum
}

function Get-DriveFreeBytes([string]$AnyPathOnDrive) {
  try {
    $root = [IO.Path]::GetPathRoot((Resolve-Path -LiteralPath $AnyPathOnDrive).Path)
    $d = Get-PSDrive -Name $root.TrimEnd('\', ':') -ErrorAction Stop
    return [int64]$d.Free
  } catch {
    return -1
  }
}

function GB([int64]$bytes) {
  if ($bytes -lt 0) { return -1 }
  return [math]::Round($bytes / 1GB, 3)
}

function Invoke-DiskGuard {
  param(
    [Parameter(Mandatory)][string]$LogsDir,
    [Parameter(Mandatory)][string]$DataDir,
    [int]$MaxLogsGB = 200,
    [int]$MaxDataGB = 1500,
    [int]$MinFreeGB = 200
  )

  $logsB = Get-DirSizeBytes $LogsDir
  $dataB = Get-DirSizeBytes $DataDir
  $freeB = Get-DriveFreeBytes $LogsDir

  $logsGB = GB $logsB
  $dataGB = GB $dataB
  $freeGB = GB $freeB

  $level = 'INFO'
  $reasons = @()

  if ($logsGB -ge $MaxLogsGB) { $level = 'WARN'; $reasons += "logs>=${MaxLogsGB}GB" }
  if ($dataGB -ge $MaxDataGB) { $level = 'WARN'; $reasons += "data>=${MaxDataGB}GB" }
  if ($freeGB -ge 0 -and $freeGB -le $MinFreeGB) { $level = 'CRIT'; $reasons += "free<=${MinFreeGB}GB" }

  $msg = ($reasons -join ', ')
  return @{ level=$level; msg=$msg; logs_gb=$logsGB; data_gb=$dataGB; free_gb=$freeGB }
}

function Invoke-NasSync {
  param(
    [Parameter(Mandatory)][string]$NasRoot,
    [Parameter(Mandatory)][string]$LogsDir,
    [Parameter(Mandatory)][string]$DataDir,
    [Parameter(Mandatory)][string]$JsonlPath
  )

  if ([string]::IsNullOrWhiteSpace($NasRoot)) { return }
  if (-not (Test-Path -LiteralPath $NasRoot)) {
    Add-Jsonl $JsonlPath @{ level='WARN'; event='nas.sync.skip'; reason='nas_root_not_found'; nas_root=$NasRoot }
    return
  }

  $dstLogs = Join-Path $NasRoot 'logs'
  $dstData = Join-Path $NasRoot 'data'
  New-DirIfMissing $dstLogs
  New-DirIfMissing $dstData

  $rc = (Get-Command robocopy -ErrorAction SilentlyContinue)
  if (-not $rc) {
    Add-Jsonl $JsonlPath @{ level='WARN'; event='nas.sync.skip'; reason='robocopy_not_found' }
    return
  }

  Add-Jsonl $JsonlPath @{ level='INFO'; event='nas.sync.start'; nas_root=$NasRoot }

  # 実行中ログ/ロック/一時ファイルは除外して sharing violation を避ける
  $excludeLogs = @(
    'phase3_runner.jsonl',
    'watchdog_stdout.log',
    'watchdog_stderr.log',
    'derived_stdout.log',
    'derived_stderr.log',
    'derived_runner.lock',
    'derived_runner.pid',
    'watchdog.lock',
    'watchdog.pid',
    '*.lock',
    '*.pid'
  )

  $args1 = @(
    $LogsDir, $dstLogs,
    '/E','/XO','/FFT','/Z','/R:1','/W:1','/NFL','/NDL','/NP',
    '/XF'
  ) + $excludeLogs

  $args2 = @(
    $DataDir, $dstData,
    '/E','/XO','/FFT','/Z','/R:1','/W:1','/NFL','/NDL','/NP'
  )

  & robocopy @args1 | Out-Null
  $c1 = $LASTEXITCODE
  & robocopy @args2 | Out-Null
  $c2 = $LASTEXITCODE

  # robocopy は 0-7 が成功扱い
  $ok = (($c1 -lt 8) -and ($c2 -lt 8))

  Add-Jsonl $JsonlPath @{
    level     = $(if ($ok) { 'INFO' } else { 'WARN' })
    event     = 'nas.sync.done'
    ok        = $ok
    code_logs = $c1
    code_data = $c2
  }
}

# ---- main ----
$repoRoot = Resolve-RepoRoot

$env:PYTHONPATH  = (Join-Path $repoRoot 'btcts_next\src')
$env:BTC_TS_MODE = $Mode

$logsDir = Resolve-EnvOrDefault 'BTC_TS_LOGS_DIR' (Join-Path $repoRoot 'btcts_next\logs')
$dataDir = Resolve-EnvOrDefault 'BTC_TS_DATA_DIR' (Join-Path $repoRoot 'btcts_next\data')
$cfgDir  = Resolve-EnvOrDefault 'BTC_TS_CONFIG_DIR' (Join-Path $repoRoot 'btcts_next\config\ui')
$secDir  = Resolve-EnvOrDefault 'BTC_TS_SECRETS_DIR' (Join-Path $repoRoot 'btcts_next\secrets')

$env:BTC_TS_LOGS_DIR    = $logsDir
$env:BTC_TS_DATA_DIR    = $dataDir
$env:BTC_TS_CONFIG_DIR  = $cfgDir
$env:BTC_TS_SECRETS_DIR = $secDir

New-DirIfMissing $logsDir
New-DirIfMissing $dataDir
New-DirIfMissing $cfgDir

$phase3Dir   = Join-Path $logsDir 'phase3'
$runnerJsonl = Join-Path $phase3Dir 'phase3_runner.jsonl'
$lockPath    = Join-Path $phase3Dir 'phase3_runner.lock'
$pidPath     = Join-Path $phase3Dir 'phase3_runner.pid'

New-DirIfMissing $phase3Dir

$lock = Open-Lock $lockPath
"pid=$PID`nstart_utc=$(NowIso)`nmode=$Mode`nlogs_dir=$logsDir`ndata_dir=$dataDir`nconfig_dir=$cfgDir`n" | Set-Content -Encoding UTF8 $pidPath

Add-Jsonl $runnerJsonl @{ level='INFO'; event='phase3.start'; repo_root=$repoRoot; mode=$Mode; logs_dir=$logsDir; data_dir=$dataDir; config_dir=$cfgDir }

$pythonExe = (Get-Command python -ErrorAction Stop).Source

$childEnv = @{}
$childEnv['PYTHONPATH']         = $env:PYTHONPATH
$childEnv['BTC_TS_MODE']        = $env:BTC_TS_MODE
$childEnv['BTC_TS_LOGS_DIR']    = $env:BTC_TS_LOGS_DIR
$childEnv['BTC_TS_DATA_DIR']    = $env:BTC_TS_DATA_DIR
$childEnv['BTC_TS_CONFIG_DIR']  = $env:BTC_TS_CONFIG_DIR
$childEnv['BTC_TS_SECRETS_DIR'] = $env:BTC_TS_SECRETS_DIR

$watchdogScript = Join-Path $repoRoot 'scripts\watchdog_collector.ps1'
$derivedScript  = Join-Path $repoRoot 'tools\phase2_run_derived.ps1'

if (-not (Test-Path -LiteralPath $watchdogScript)) { throw "missing: $watchdogScript" }
if (-not (Test-Path -LiteralPath $derivedScript))  { throw "missing: $derivedScript" }

$watchdogOut = Join-Path $phase3Dir 'watchdog_stdout.log'
$watchdogErr = Join-Path $phase3Dir 'watchdog_stderr.log'
$derivedOut  = Join-Path $phase3Dir 'derived_stdout.log'
$derivedErr  = Join-Path $phase3Dir 'derived_stderr.log'

$watchdogExternal = $false
$existingWatchdog = Find-RunningPwshScript -ScriptPath $watchdogScript

if ($existingWatchdog) {
  $watchdogExternal = $true
  $watchdogProc = $null
  Add-Jsonl $runnerJsonl @{ level='INFO'; event='watchdog.attach_existing'; pid=$existingWatchdog.ProcessId; script=$watchdogScript }
} else {
  $watchdogProc = Start-ChildPwsh -Name 'watchdog' -FilePath $watchdogScript -ChildArgs @() -EnvMap $childEnv -StdoutPath $watchdogOut -StderrPath $watchdogErr
  Add-Jsonl $runnerJsonl @{ level='INFO'; event='watchdog.spawn'; pid=$watchdogProc.Id; script=$watchdogScript }
}

$dur = [math]::Max(0.1, [double]$DurationHours)
$derivedArgs = @('-Mode', $Mode, '-DurationHours', $dur)
if ($Once) {
  $derivedArgs = @('-Mode', $Mode, '-Once')
}

$derivedProc = Start-ChildPwsh -Name 'derived' -FilePath $derivedScript -ChildArgs $derivedArgs -EnvMap $childEnv -StdoutPath $derivedOut -StderrPath $derivedErr
Add-Jsonl $runnerJsonl @{ level='INFO'; event='derived.spawn'; pid=$derivedProc.Id; script=$derivedScript; args=($derivedArgs -join ' ') }

$lastPackDay = ''

try {
  if ($Once) {
    Invoke-EvidencePackOnce -PythonExe $pythonExe -EnvMap $childEnv -JsonlPath $runnerJsonl | Out-Null
    Invoke-SoakReportOnce -PythonExe $pythonExe -RepoRoot $repoRoot -JsonlPath $runnerJsonl -Hours 24 | Out-Null
    Add-Jsonl $runnerJsonl @{ level='INFO'; event='phase3.stop.once' }
    return
  }

  $deadline = (Get-Date).ToUniversalTime().AddHours($dur)

  while ((Get-Date).ToUniversalTime() -lt $deadline) {
    Start-Sleep -Seconds 5

    if (-not (Get-Variable -Scope Script -Name lastGuardTs -ErrorAction SilentlyContinue)) {
      $script:lastGuardTs = (Get-Date).ToUniversalTime().AddYears(-1)
    }
    if (((Get-Date).ToUniversalTime() - $script:lastGuardTs).TotalSeconds -ge 60) {
      $dg = Invoke-DiskGuard -LogsDir $logsDir -DataDir $dataDir -MaxLogsGB 200 -MaxDataGB 1500 -MinFreeGB 200
      Add-Jsonl $runnerJsonl @{ level=$dg.level; event='disk.guard'; msg=$dg.msg; logs_gb=$dg.logs_gb; data_gb=$dg.data_gb; free_gb=$dg.free_gb }
      $script:lastGuardTs = (Get-Date).ToUniversalTime()
    }

    if (-not (Get-Variable -Scope Script -Name lastNasSyncTs -ErrorAction SilentlyContinue)) {
      $script:lastNasSyncTs = (Get-Date).ToUniversalTime().AddYears(-1)
    }
    if (((Get-Date).ToUniversalTime() - $script:lastNasSyncTs).TotalSeconds -ge 300) {
      $nasRoot = $env:BTC_TS_NAS_ROOT
      if (-not [string]::IsNullOrWhiteSpace($nasRoot)) {
        Invoke-NasSync -NasRoot $nasRoot -LogsDir $logsDir -DataDir $dataDir -JsonlPath $runnerJsonl
      }
      $script:lastNasSyncTs = (Get-Date).ToUniversalTime()
    }

    if (-not $watchdogExternal -and $watchdogProc -and $watchdogProc.HasExited) {
      Add-Jsonl $runnerJsonl @{ level='WARN'; event='watchdog.exited'; exit_code=$watchdogProc.ExitCode }
      $watchdogProc = Start-ChildPwsh -Name 'watchdog' -FilePath $watchdogScript -ChildArgs @() -EnvMap $childEnv -StdoutPath $watchdogOut -StderrPath $watchdogErr
      Add-Jsonl $runnerJsonl @{ level='INFO'; event='watchdog.respawn'; pid=$watchdogProc.Id }
    }

    if ($derivedProc -and $derivedProc.HasExited) {
      Add-Jsonl $runnerJsonl @{ level='WARN'; event='derived.exited'; exit_code=$derivedProc.ExitCode }
      $derivedProc = Start-ChildPwsh -Name 'derived' -FilePath $derivedScript -ChildArgs @('-Mode',$Mode,'-DurationHours',1) -EnvMap $childEnv -StdoutPath $derivedOut -StderrPath $derivedErr
      Add-Jsonl $runnerJsonl @{ level='INFO'; event='derived.respawn'; pid=$derivedProc.Id }
    }

    $day = TodayUtcKey
    if ($day -ne $lastPackDay) {
      $ok = Invoke-EvidencePackOnce -PythonExe $pythonExe -EnvMap $childEnv -JsonlPath $runnerJsonl
      $lastPackDay = $day
      Add-Jsonl $runnerJsonl @{ level='INFO'; event='evidence_pack.done'; day=$day; ok=$ok }
    }
  }

  Add-Jsonl $runnerJsonl @{ level='INFO'; event='phase3.stop.duration'; duration_hours=$dur }
  Invoke-SoakReportOnce -PythonExe $pythonExe -RepoRoot $repoRoot -JsonlPath $runnerJsonl -Hours 168 | Out-Null

} catch {
  Add-Jsonl $runnerJsonl @{ level='ERROR'; event='phase3.exception'; err=$_.Exception.Message }
  try {
    Invoke-SoakReportOnce -PythonExe $pythonExe -RepoRoot $repoRoot -JsonlPath $runnerJsonl -Hours 24 | Out-Null
  } catch { }
  throw
} finally {
  try {
    if ($derivedProc -and -not $derivedProc.HasExited) {
      Stop-Process -Id $derivedProc.Id -Force -ErrorAction SilentlyContinue
    }
  } catch {}

  try {
    if (-not $watchdogExternal -and $watchdogProc -and -not $watchdogProc.HasExited) {
      Stop-Process -Id $watchdogProc.Id -Force -ErrorAction SilentlyContinue
    }
  } catch {}

  try { if ($lock) { $lock.Dispose() } } catch {}
  try { Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue } catch {}
  try { Remove-Item -LiteralPath $pidPath  -Force -ErrorAction SilentlyContinue } catch {}

  Add-Jsonl $runnerJsonl @{ level='INFO'; event='phase3.exit' }
}
