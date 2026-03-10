# path: ./scripts/watchdog_collector.ps1
# desc: Collector を24/7運用するSupervisor。status.json(ts_unix)停滞/プロセス終了/no_data等を検知して kill→再起動（多重起動防止・バックオフ・ディスク安全弁込み）。

[CmdletBinding()]
param(
  # 省略時は $env:BTC_TS_CONFIG_DIR\watchdog.yaml を使用
  [string]$ConfigPath = "",

  # Phase1テスト用：ダミーCollectorを使う
  [switch]$UseDummyCollector
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function NowIso {
  (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
}

function New-DirectoryIfMissing([string]$Path) {
  if ([string]::IsNullOrWhiteSpace($Path)) { throw "Path is empty" }
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Read-YamlOrDefault([string]$Path) {
  # ConvertFrom-Yaml に依存しない（PowerShell標準で動く）簡易読込。
  # 仕様上、watchdog.yaml は「トップレベルの scalar + inline list」だけを許可する。

  $defaults = [ordered]@{
    schema_rev        = 1
    interval_sec      = 5
    hang_timeout_sec  = 120
    max_failures      = 5
    backoff_sec       = @(10,30,60,120,300)
    no_data_fail_limit= 5
    log_tail_lines    = 200
    free_gb_warn      = 20
    free_gb_stop      = 10
  }

  if (-not (Test-Path -LiteralPath $Path)) { return $defaults }

  $lines = Get-Content -LiteralPath $Path -Encoding UTF8
  if (-not $lines -or $lines.Count -eq 0) { return $defaults }

  $cfg = [ordered]@{}
  foreach ($k in $defaults.Keys) { $cfg[$k] = $defaults[$k] }

  foreach ($line0 in $lines) {
    $line = ($line0 -as [string]).Trim()
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    if ($line.StartsWith('#')) { continue }

    $m = [regex]::Match($line, '^(?<k>[A-Za-z0-9_]+)\s*:\s*(?<v>.*)$')
    if (-not $m.Success) { continue }

    $k = $m.Groups['k'].Value
    $v = $m.Groups['v'].Value.Trim()

    if (-not $cfg.Contains($k)) { continue } # 未知キーは無視（安全）

    # inline list: [10, 30, 60]
    if ($v.StartsWith('[') -and $v.EndsWith(']')) {
      $inner = $v.Substring(1, $v.Length-2)
      $arr = @()
      foreach ($p in ($inner -split ',')) {
        $s = $p.Trim()
        if ([string]::IsNullOrWhiteSpace($s)) { continue }
        $n = 0
        if ([int]::TryParse($s, [ref]$n)) { $arr += $n }
      }
      if ($k -eq 'backoff_sec') { $cfg[$k] = $arr }
      continue
    }

    # scalar（数値/文字列）
    $nInt = 0
    $nDbl = 0.0
    if ([int]::TryParse($v, [ref]$nInt)) { $cfg[$k] = $nInt; continue }
    if ([double]::TryParse($v, [ref]$nDbl)) { $cfg[$k] = $nDbl; continue }

    # quoted string を剥がす
    if (($v.StartsWith('"') -and $v.EndsWith('"')) -or ($v.StartsWith("'") -and $v.EndsWith("'"))) {
      $v = $v.Substring(1, $v.Length-2)
    }
    $cfg[$k] = $v
  }

  # 返り値を PSObject 化（既存コード互換）
  return [pscustomobject]$cfg
}

function Resolve-PyPathOrThrow {
  # 1) まずENVを尊重
  $v = [Environment]::GetEnvironmentVariable('PYTHONPATH')
  if (-not [string]::IsNullOrWhiteSpace($v)) { return $v }

  # 2) あなたの正準構成（確定パス）
  $cand1 = "C:\BtcTradeSystem\btcts_next\src"
  if (Test-Path -LiteralPath $cand1) { return $cand1 }

  # 3) スクリプト位置からの相対推定
  $cand2 = Join-Path -Path $PSScriptRoot -ChildPath "..\btcts_next\src"
  $cand2 = (Resolve-Path -LiteralPath $cand2 -ErrorAction SilentlyContinue).Path
  if (-not [string]::IsNullOrWhiteSpace($cand2) -and (Test-Path -LiteralPath $cand2)) { return $cand2 }

  throw "PYTHONPATH missing and auto-resolve failed. Set PYTHONPATH to '<repo>\btcts_next\src'."
}

function Join-PathSafe([string]$a, [string]$b) {
  if ([string]::IsNullOrWhiteSpace($a)) { return $b }
  if ([string]::IsNullOrWhiteSpace($b)) { return $a }
  return (Join-Path -Path $a -ChildPath $b)
}

function Get-DriveFreeGB([string]$AnyPath) {
  if ([string]::IsNullOrWhiteSpace($AnyPath)) { return $null }
  $root = [System.IO.Path]::GetPathRoot($AnyPath)
  if ([string]::IsNullOrWhiteSpace($root)) { return $null }
  $drive = Get-PSDrive -Name $root.Substring(0,1) -ErrorAction SilentlyContinue
  if (-not $drive) { return $null }
  return [math]::Round(($drive.Free / 1GB), 2)
}

function Open-Lock([string]$LockPath) {
  New-DirectoryIfMissing (Split-Path -Parent $LockPath)

  try {
    return [System.IO.File]::Open($LockPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
  } catch {
    # できる範囲で「誰が watchdog を動かしているか」を出す（原因特定用）
    try {
      $procs = Get-CimInstance Win32_Process -Filter "Name='pwsh.exe'" |
        Where-Object { $_.CommandLine -match 'watchdog_collector\.ps1' } |
        Select-Object ProcessId, CommandLine
      $hint = ($procs | ConvertTo-Json -Compress -Depth 5)
      throw "lock busy: $LockPath ; running_watchdogs=$hint"
    } catch {
      throw "lock busy: $LockPath"
    }
  }
}

function Write-Text([string]$Path, [string]$Text) {
  New-DirectoryIfMissing (Split-Path -Parent $Path)
  $Text | Out-File -LiteralPath $Path -Encoding UTF8 -Force
}
function Add-LogLine([string]$LogPath, [string]$Level, [string]$Msg, [hashtable]$Fields) {
  $ts = NowIso
  $line = "[$ts][$Level] $Msg"
  if ($Fields) {
    $kv = ($Fields.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ' '
    $line = "$line $kv"
  }
  New-DirectoryIfMissing (Split-Path -Parent $LogPath)
  Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

function Add-JsonlLine([string]$Path, [hashtable]$Obj) {
  New-DirectoryIfMissing (Split-Path -Parent $Path)
  $json = ($Obj | ConvertTo-Json -Depth 10 -Compress)
  Add-Content -LiteralPath $Path -Value $json -Encoding UTF8
}

function Read-Status([string]$StatusPath) {
  if (-not (Test-Path -LiteralPath $StatusPath)) { return $null }
  try {
    $raw = Get-Content -LiteralPath $StatusPath -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
    return ($raw | ConvertFrom-Json)
  } catch {
    return $null
  }
}

function Get-StatusTsUnix($StatusObj) {
  if (-not $StatusObj) { return $null }
  if ($StatusObj.PSObject.Properties.Name -contains 'ts_unix') { return [double]$StatusObj.ts_unix }
  if ($StatusObj.PSObject.Properties.Name -contains 'ts') { return [double]$StatusObj.ts }
  return $null
}

function Get-LastOkIso($StatusObj) {
  if (-not $StatusObj) { return $null }
  if (-not $StatusObj.items) { return $null }
  if ($StatusObj.items.Count -lt 1) { return $null }
  return $StatusObj.items[0].last_ok
}

function Test-BtctsImport([string]$PythonExe, [string]$PyPath, [string]$LogPath, [string]$JsonlPath) {
  # -c のワンライナーは PowerShell で壊れやすいため、複数行文字列で固定する
  $code = @"
import sys
sys.path.insert(0, r"$PyPath")
import btcts
print("OK", btcts.__file__)
"@

  $out = & $PythonExe -c $code 2>&1
  $txt = ($out -join ' ')

  if ($LASTEXITCODE -eq 0 -and ($txt -match '\bOK\b')) {
    Add-LogLine  $LogPath 'INFO' 'preflight.btcts.ok' @{ out=$txt }
    Add-JsonlLine $JsonlPath @{ ts=NowIso; level='INFO'; event='preflight.btcts.ok'; out=$txt }
    return $true
  }

  Add-LogLine  $LogPath 'ERROR' 'preflight.btcts.ng' @{ exit_code=$LASTEXITCODE; out=$txt }
  Add-JsonlLine $JsonlPath @{ ts=NowIso; level='ERROR'; event='preflight.btcts.ng'; exit_code=$LASTEXITCODE; out=$txt }
  return $false
}

function Start-Collector([string]$PythonExe, [string]$PyPath, [string]$ConfigDir, [string]$DataDir, [string]$LogsDir, [string]$LogPath, [string]$JsonlPath, [bool]$UseDummyCollector) {

    # 子プロセスへ渡す環境を「明示固定」して、手動起動との差・事故を無くす
  $envMap = @{}
  $envMap['PYTHONPATH']          = $PyPath
  $envMap['BTC_TS_CONFIG_DIR']   = $ConfigDir
  $envMap['BTC_TS_DATA_DIR']     = $DataDir
  $envMap['BTC_TS_LOGS_DIR']     = $LogsDir
  $envMap['PYTHONUNBUFFERED']    = '1'
  $envMap['PYTHONFAULTHANDLER']  = '1'
  if (-not (Test-BtctsImport -PythonExe $PythonExe -PyPath $PyPath -LogPath $LogPath -JsonlPath $JsonlPath)) {
    throw "preflight failed: btcts import"
  }

  Add-LogLine  $LogPath 'INFO' 'collector.start' @{ python=$PythonExe; py_path=$PyPath; config_dir=$ConfigDir; data_dir=$DataDir; logs_dir=$LogsDir }
  Add-JsonlLine $JsonlPath @{ ts=NowIso; level='INFO'; event='collector.start'; python=$PythonExe; py_path=$PyPath; config_dir=$ConfigDir; data_dir=$DataDir; logs_dir=$LogsDir }

  # Collectorの標準出力/標準エラーを確実に採取（exit_code=2 の理由をログで確定させる）
  $stdoutPath = Join-PathSafe $LogsDir 'collector_stdout.log'
  $stderrPath = Join-PathSafe $LogsDir 'collector_stderr.log'

if ($UseDummyCollector) {
  # Phase1テスト：ダミーCollector
  $dummyCandidates = @(
    (Join-Path $PSScriptRoot '..\tools\test_collector_entry.py')
  )
  $dummyScript = $null
  foreach ($c in $dummyCandidates) {
    if (Test-Path -LiteralPath $c) { $dummyScript = $c; break }
  }
  if (-not $dummyScript) {
    throw "dummy collector script not found. looked: $($dummyCandidates -join ', ')"
  }

  $pyArgs = @(
    $dummyScript
  )

  Add-LogLine  $LogPath 'INFO' 'collector.start.dummy' @{ script=$pyArgs[0] }
  Add-JsonlLine $JsonlPath @{ ts=NowIso; level='INFO'; event='collector.start.dummy'; script=$pyArgs[0] }

  # Phase1最終テストは再現性固定（危険系は FORCE 指定が必要）
  $envMap['BTC_TS_TEST_MODE'] = 'ok_then_hang'
  $envMap['BTC_TS_TEST_MODE_FORCE'] = $envMap['BTC_TS_TEST_MODE']

  $p = Start-Process -FilePath $PythonExe `
    -ArgumentList $pyArgs `
    -PassThru -WindowStyle Hidden `
    -Environment $envMap `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError  $stderrPath

} else {
  # 本番Collector（Start-Process は引数クォートが壊れやすいので -m を使う）
  $pyArgs = @('-m', 'btcts.collector.main')

  Add-LogLine  $LogPath 'INFO' 'collector.start.real' @{ module='btcts.collector.main'; mode='-m' }
  Add-JsonlLine $JsonlPath @{ ts=NowIso; level='INFO'; event='collector.start.real'; module='btcts.collector.main'; mode='-m' }

  $p = Start-Process -FilePath $PythonExe `
    -ArgumentList $pyArgs `
    -PassThru -WindowStyle Hidden `
    -Environment $envMap `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError  $stderrPath
}
return $p
}

function Stop-Collector([System.Diagnostics.Process]$Proc, [string]$LogPath, [string]$JsonlPath) {
  if (-not $Proc) { return }
  try {
    if (-not $Proc.HasExited) {
      Add-LogLine $LogPath 'WARN' 'collector.kill' @{ pid=$Proc.Id }
      Add-JsonlLine $JsonlPath @{ ts=NowIso; level='WARN'; event='collector.kill'; pid=$Proc.Id }
      Stop-Process -Id $Proc.Id -Force -ErrorAction SilentlyContinue
    }
  } catch {
    # ignore
  }
}

function Get-FileTailText([string]$Path, [int]$Lines = 80) {
  try {
    if (-not (Test-Path -LiteralPath $Path)) { return "" }
    $arr = Get-Content -LiteralPath $Path -Tail $Lines -Encoding UTF8 -ErrorAction SilentlyContinue
    if (-not $arr) { return "" }
    return ($arr -join "`n")
  } catch {
    return ""
  }
}

function Get-StatusRawText([string]$StatusPath) {
  try {
    if (-not (Test-Path -LiteralPath $StatusPath)) { return "" }
    return (Get-Content -LiteralPath $StatusPath -Raw -Encoding UTF8 -ErrorAction SilentlyContinue)
  } catch {
    return ""
  }
}

function Write-CollectorExitDiagnostics(
  [int]$ExitCode,
  [string]$StdoutPath,
  [string]$StderrPath,
  [string]$StatusPath,
  [string]$LogPath,
  [string]$JsonlPath
) {
  $stdoutTail = Get-FileTailText -Path $StdoutPath -Lines 120
  $stderrTail = Get-FileTailText -Path $StderrPath -Lines 120
  $statusRaw  = Get-StatusRawText -StatusPath $StatusPath

  Add-LogLine $LogPath 'WARN' 'collector.exit.diag' @{
    exit_code   = $ExitCode
    stdout_tail = ($stdoutTail -replace "`r?`n", ' <NL> ')
    stderr_tail = ($stderrTail -replace "`r?`n", ' <NL> ')
  }

  Add-JsonlLine $JsonlPath @{
    ts          = NowIso
    level       = 'WARN'
    event       = 'collector.exit.diag'
    exit_code   = $ExitCode
    stdout_tail = $stdoutTail
    stderr_tail = $stderrTail
    status_raw  = $statusRaw
  }
}

# ---- main ----

# 必須ENV（config/data/logs）を先に確定する（ConfigPath決定に必要）
function Resolve-EnvOrThrow([string]$Name) {
  $v = [Environment]::GetEnvironmentVariable($Name)
  if ([string]::IsNullOrWhiteSpace($v)) {
    throw "ENV missing: $Name"
  }
  return $v
}

$cfgDir  = Resolve-EnvOrThrow 'BTC_TS_CONFIG_DIR'
$dataDir = Resolve-EnvOrThrow 'BTC_TS_DATA_DIR'
$logsDir = Resolve-EnvOrThrow 'BTC_TS_LOGS_DIR'
$pyPath  = Resolve-PyPathOrThrow

# python 実体
$pythonExe = (Get-Command python -ErrorAction Stop).Source

# ConfigPath 省略時は ENV 正準から
if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
  $ConfigPath = Join-Path -Path $cfgDir -ChildPath 'watchdog.yaml'
}

# config 読み込み（ConfigPath確定後）
$cfg = Read-YamlOrDefault $ConfigPath

$cfgInterval = [int]$cfg.interval_sec
$hangSec      = [int]$cfg.hang_timeout_sec
$maxFails     = [int]$cfg.max_failures
$backoffs     = @($cfg.backoff_sec)
$noDataLimit  = [int]$cfg.no_data_fail_limit
$tailLines    = [int]$cfg.log_tail_lines
$tailLines | Out-Null  # reserved (Phase1では未使用だが設定として保持)
$freeWarn     = [double]$cfg.free_gb_warn
$freeStop     = [double]$cfg.free_gb_stop

$superLog  = Join-PathSafe $logsDir 'supervisor_collector.log'
$superJson = Join-PathSafe $logsDir 'supervisor_collector.jsonl'
$lockPath  = Join-PathSafe $logsDir 'watchdog.lock'
$pidPath   = Join-PathSafe $logsDir 'watchdog.pid'

$statusPath = Join-PathSafe (Join-PathSafe $dataDir 'collector') 'status.json'
$collectorStdoutPath = Join-PathSafe $logsDir 'collector_stdout.log'
$collectorStderrPath = Join-PathSafe $logsDir 'collector_stderr.log'

function Clear-StaleStatusLock([string]$StatusPath, [int]$HangSec, [string]$LogPath, [string]$JsonlPath) {
  $lockPath = "$StatusPath.lock"
  if (-not (Test-Path -LiteralPath $lockPath)) { return }

  $st = Read-Status $StatusPath
  $stTs = Get-StatusTsUnix $st
  if ($null -eq $stTs) {
    # statusが読めない/無い場合は安全側：消さない
    Add-LogLine  $LogPath 'WARN' 'lock.stale.check.skip' @{ lock=$lockPath; reason='no_status_ts' }
    Add-JsonlLine $JsonlPath @{ ts=NowIso; level='WARN'; event='lock.stale.check.skip'; lock=$lockPath; reason='no_status_ts' }
    return
  }

  $age = [math]::Max(0.0, (Get-Date).ToUniversalTime().Subtract([DateTime]::UnixEpoch.AddSeconds($stTs)).TotalSeconds)
  if ($age -lt $HangSec) {
    # まだ新しい＝稼働中の可能性が高いので消さない
    Add-LogLine  $LogPath 'INFO' 'lock.stale.not_old' @{ lock=$lockPath; age_sec=[math]::Round($age,1); hang_sec=$HangSec }
    Add-JsonlLine $JsonlPath @{ ts=NowIso; level='INFO'; event='lock.stale.not_old'; lock=$lockPath; age_sec=[math]::Round($age,1); hang_sec=$HangSec }
    return
  }

  try {
    Remove-Item -LiteralPath $lockPath -Force -ErrorAction Stop
    Add-LogLine  $LogPath 'WARN' 'lock.stale.removed' @{ lock=$lockPath; age_sec=[math]::Round($age,1); hang_sec=$HangSec }
    Add-JsonlLine $JsonlPath @{ ts=NowIso; level='WARN'; event='lock.stale.removed'; lock=$lockPath; age_sec=[math]::Round($age,1); hang_sec=$HangSec }
  } catch {
    Add-LogLine  $LogPath 'ERROR' 'lock.stale.remove_failed' @{ lock=$lockPath; err=$_.Exception.Message }
    Add-JsonlLine $JsonlPath @{ ts=NowIso; level='ERROR'; event='lock.stale.remove_failed'; lock=$lockPath; err=$_.Exception.Message }
  }
}

$lock = Open-Lock $lockPath
Write-Text $pidPath ("pid={0}`nstart_utc={1}`npython={2}`n" -f $PID, (NowIso), $pythonExe)

Add-LogLine  $superLog 'INFO' 'watchdog.start' @{ interval_sec=$cfgInterval; hang_timeout_sec=$hangSec; data_dir=$dataDir; logs_dir=$logsDir }
Add-JsonlLine $superJson @{ ts=NowIso; level='INFO'; event='watchdog.start'; interval_sec=$cfgInterval; hang_timeout_sec=$hangSec; data_dir=$dataDir; logs_dir=$logsDir }
# 起動時：過去クラッシュ等で残った status.lock を安全条件付きで掃除
Clear-StaleStatusLock -StatusPath $statusPath -HangSec $hangSec -LogPath $superLog -JsonlPath $superJson

$proc = $null
$consecutiveFails = 0
$consecutiveNoData = 0
$exitReason = 'unknown'

# Ctrl+C / セッション停止を「理由つきで」回収する
$stopRequested = $false
$cancelEventSub = $null
try {
  $cancelEventSub = Register-ObjectEvent -InputObject ([Console]) -EventName CancelKeyPress -Action {
    $Event.SourceEventArgs.Cancel = $true
    $script:exitReason = 'console.cancel'
    $script:stopRequested = $true
  }
} catch {
  $exitReason = 'cancel_hook_failed'
}

function Get-BackoffSeconds([int]$Fails, [object[]]$Backoffs) {
  if (-not $Backoffs -or $Backoffs.Count -eq 0) { return 10 }
  $i = [math]::Min([math]::Max($Fails - 1, 0), $Backoffs.Count - 1)
  return [int]$Backoffs[$i]
}

try {
  # 初回起動
  $proc = Start-Collector -PythonExe $pythonExe -PyPath $pyPath -ConfigDir $cfgDir -DataDir $dataDir -LogsDir $logsDir -LogPath $superLog -JsonlPath $superJson -UseDummyCollector ([bool]$UseDummyCollector)

  while ($true) {
  if ($stopRequested) {
    # Ctrl+C 等で止めたいときは、ここで理由つきで終了
    break
  }

    Start-Sleep -Seconds $cfgInterval
    Add-JsonlLine $superJson @{ ts=NowIso; level='DEBUG'; event='loop.tick' }
    Add-LogLine  $superLog  'DEBUG' 'loop.tick' @{}

    # ディスク安全弁（logsのドライブ）
    $freeGb = Get-DriveFreeGB $logsDir
    if ($null -ne $freeGb) {
      if ($freeGb -lt $freeStop) {
        $exitReason = 'guard.disk.stop'
        Add-LogLine $superLog 'ERROR' 'guard.disk.stop' @{ free_gb=$freeGb; stop_gb=$freeStop }
        Add-JsonlLine $superJson @{ ts=NowIso; level='ERROR'; event='guard.disk.stop'; free_gb=$freeGb; stop_gb=$freeStop }
        Stop-Collector $proc $superLog $superJson
        break
      } elseif ($freeGb -lt $freeWarn) {
        Add-LogLine $superLog 'WARN' 'guard.disk.warn' @{ free_gb=$freeGb; warn_gb=$freeWarn }
        Add-JsonlLine $superJson @{ ts=NowIso; level='WARN'; event='guard.disk.warn'; free_gb=$freeGb; warn_gb=$freeWarn }
      }
    }

    # プロセス終了検知
    if ($proc -and $proc.HasExited) {
      $consecutiveFails += 1
      Add-LogLine $superLog 'WARN' 'collector.exited' @{ exit_code=$proc.ExitCode; fails=$consecutiveFails }
      Add-JsonlLine $superJson @{ ts=NowIso; level='WARN'; event='collector.exited'; exit_code=$proc.ExitCode; fails=$consecutiveFails }

      Write-CollectorExitDiagnostics `
        -ExitCode $proc.ExitCode `
        -StdoutPath $collectorStdoutPath `
        -StderrPath $collectorStderrPath `
        -StatusPath $statusPath `
        -LogPath $superLog `
        -JsonlPath $superJson

      if ($consecutiveFails -ge $maxFails) {
        $exitReason = 'watchdog.stop.too_many_fails'
        Add-LogLine $superLog 'ERROR' 'watchdog.stop.too_many_fails' @{ fails=$consecutiveFails; max=$maxFails }
        Add-JsonlLine $superJson @{ ts=NowIso; level='ERROR'; event='watchdog.stop.too_many_fails'; fails=$consecutiveFails; max=$maxFails }
        break
      }

      $sleepSec = Get-BackoffSeconds $consecutiveFails $backoffs
      Add-LogLine $superLog 'INFO' 'backoff.sleep' @{ sec=$sleepSec }
      Add-JsonlLine $superJson @{ ts=NowIso; level='INFO'; event='backoff.sleep'; sec=$sleepSec }
      Start-Sleep -Seconds $sleepSec

      $proc = Start-Collector -PythonExe $pythonExe -PyPath $pyPath -ConfigDir $cfgDir -DataDir $dataDir -LogsDir $logsDir -LogPath $superLog -JsonlPath $superJson -UseDummyCollector ([bool]$UseDummyCollector)
      continue
    }

    # status監視（ハング検知）
    $st = Read-Status $statusPath
    $stTs = Get-StatusTsUnix $st
    if ($null -ne $stTs) {
      $age = [math]::Max(0.0, (Get-Date).ToUniversalTime().Subtract([DateTime]::UnixEpoch.AddSeconds($stTs)).TotalSeconds)

      # 成功観測：status.ts が新しい＝前進している → 連続失敗をリセット
      if ($age -lt $hangSec) {
        if ($consecutiveFails -ne 0) {
          Add-LogLine  $superLog 'INFO' 'fails.reset' @{ prev=$consecutiveFails }
          Add-JsonlLine $superJson @{ ts=NowIso; level='INFO'; event='fails.reset'; prev=$consecutiveFails }
        }
        $consecutiveFails = 0
      }

      if ($age -ge $hangSec) {
        $lastOk = Get-LastOkIso $st
        $consecutiveFails += 1
        Add-LogLine $superLog 'ERROR' 'collector.hang' @{ age_sec=[math]::Round($age,1); hang_sec=$hangSec; last_ok=$lastOk; fails=$consecutiveFails }
        Add-JsonlLine $superJson @{ ts=NowIso; level='ERROR'; event='collector.hang'; age_sec=[math]::Round($age,1); hang_sec=$hangSec; last_ok=$lastOk; fails=$consecutiveFails }

        Stop-Collector $proc $superLog $superJson

        if ($consecutiveFails -ge $maxFails) {
          $exitReason = 'watchdog.stop.too_many_fails'
          Add-LogLine $superLog 'ERROR' 'watchdog.stop.too_many_fails' @{ fails=$consecutiveFails; max=$maxFails }
          Add-JsonlLine $superJson @{ ts=NowIso; level='ERROR'; event='watchdog.stop.too_many_fails'; fails=$consecutiveFails; max=$maxFails }
          break
        }

        $sleepSec = Get-BackoffSeconds $consecutiveFails $backoffs
        Add-LogLine $superLog 'INFO' 'backoff.sleep' @{ sec=$sleepSec }
        Add-JsonlLine $superJson @{ ts=NowIso; level='INFO'; event='backoff.sleep'; sec=$sleepSec }
        Start-Sleep -Seconds $sleepSec

        $proc = Start-Collector -PythonExe $pythonExe -PyPath $pyPath -ConfigDir $cfgDir -DataDir $dataDir -LogsDir $logsDir -LogPath $superLog -JsonlPath $superJson -UseDummyCollector ([bool]$UseDummyCollector)
        continue
      }
    }

    # no_data 連続検知（status.messageに出る場合の保険）
    if ($st -and $st.PSObject.Properties.Name -contains 'message') {
      $msg = [string]$st.message
      if ($msg -match 'no_data' -or $msg -match 'startup grace') {
        $consecutiveNoData += 1
        Add-LogLine $superLog 'WARN' 'collector.no_data.detected' @{ count=$consecutiveNoData; limit=$noDataLimit }
        Add-JsonlLine $superJson @{ ts=NowIso; level='WARN'; event='collector.no_data.detected'; count=$consecutiveNoData; limit=$noDataLimit }
        if ($consecutiveNoData -ge $noDataLimit) {
          $exitReason = 'watchdog.stop.no_data_limit'
          Add-LogLine $superLog 'ERROR' 'watchdog.stop.no_data_limit' @{ count=$consecutiveNoData; limit=$noDataLimit }
          Add-JsonlLine $superJson @{ ts=NowIso; level='ERROR'; event='watchdog.stop.no_data_limit'; count=$consecutiveNoData; limit=$noDataLimit }
          Stop-Collector $proc $superLog $superJson
          break
        }
      } else {
        $consecutiveNoData = 0
      }
    }
  }
}
catch {
  $exitReason = 'exception'
  try {
    Add-LogLine  $superLog 'ERROR' 'watchdog.exception' @{ err=$_.Exception.Message }
    Add-JsonlLine $superJson @{ ts=NowIso; level='ERROR'; event='watchdog.exception'; err=$_.Exception.Message }
  } catch { }
  throw
}

finally {
  if ($exitReason -eq 'unknown') {
    $exitReason = 'loop.ended_or_external_stop'
  }

  try {
    Add-LogLine  $superLog 'INFO' 'watchdog.exit' @{ reason=$exitReason }
    Add-JsonlLine $superJson @{ ts=NowIso; level='INFO'; event='watchdog.exit'; reason=$exitReason }
  } catch { }

  try {
    if ($proc) {
      Stop-Collector $proc $superLog $superJson
      Start-Sleep -Milliseconds 500
    }
  } catch { }

  try { if ($lock) { $lock.Dispose() } } catch { }

    try {
    if ($cancelEventSub) {
      Unregister-Event -SubscriptionId $cancelEventSub.Id -ErrorAction SilentlyContinue
      Remove-Job -Id $cancelEventSub.Id -Force -ErrorAction SilentlyContinue
    }
  } catch { }

  # lock ファイルは「ロック用」なので、終了時は必ず消す（残すと混乱の元）
  try { Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue } catch { }

  try { Remove-Item -LiteralPath $pidPath -Force -ErrorAction SilentlyContinue } catch { }
}
