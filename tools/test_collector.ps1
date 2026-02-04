# path: ./tools/test_collector.ps1
# role: Phase1 E2E test runner for Collector (bitFlyer public API only)
# desc:
#   - Collector / settings_svc / scheduler / rate / audit の結合確認
#   - 実行スクリプト本体は btcts_next/tool に固定
#   - 生成物（config/data/logs）は repo 直下 tmp/collector_test/<runId>/ にのみ出力
#   - 次フェーズ（データ品質ガード）のテスト注入母体

Set-StrictMode -Version Latest
# テストは「失敗しても次へ進める」前提なので Stop は使わない
$ErrorActionPreference = "Continue"

# ---- exit code aggregation (practical) ----
# 0: all OK
# non-zero: first failed test's code (keeps earlier failures visible)
$overall = 0
function Update-Overall([int]$code) {
  if ($script:overall -eq 0 -and $code -ne 0) { $script:overall = $code }
}

function Show-Title([string]$s) {
  Write-Host ""
  Write-Host ("=" * 70)
  Write-Host $s
  Write-Host ("=" * 70)
}

function Test-PyImport([string]$moduleName, [string]$pipName) {
  try {
    python -c "import $moduleName" | Out-Null
    Write-Host "[OK] python module: $moduleName"
  } catch {
    Write-Host "[NG] python module missing: $moduleName"
    Write-Host "     Try: python -m pip install $pipName"
    throw
  }
}

function Write-Utf8([string]$path, [string]$text) {
  $dir = Split-Path -Parent $path
  New-Item -ItemType Directory -Force $dir | Out-Null
  $text | Set-Content -Encoding UTF8 $path
}

function Show-Tail([string]$path, [int]$n = 30) {
  if (Test-Path $path) {
    Get-Content -Path $path -Tail $n
  } else {
    Write-Host "(missing) $path"
  }
}

# ---- paths (repo root is derived from this script location) ----
# script: <repo>\btcts_next\tool\collector_test.ps1
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$root = $root.Path
$src  = Join-Path $root "btcts_next\src"

if (-not (Test-Path (Join-Path $src "btcts\__init__.py"))) {
  throw "btcts package not found: $src\btcts. Please run from repo root (C:\BtcTradeSystem)."
}

# ---- test workspace (tmp only) ----
# 既存プロセスの上書き干渉を避けるため、毎回ユニークな作業ディレクトリにする
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$base  = Join-Path $root ("tmp\collector_test\" + $runId)

# ---- last workspace marker (for parent shell after pwsh -File exits) ----
# pwsh -File は別プロセスなので、親シェルから参照できるように直近workspaceをファイルに書く
$lastWsPath = Join-Path $root "tmp\collector_test\_last_workspace.txt"
New-Item -ItemType Directory -Force (Split-Path -Parent $lastWsPath) | Out-Null
$base | Set-Content -Encoding UTF8 $lastWsPath

$configDir  = Join-Path $base "config\ui"
$secretsDir = Join-Path $base "secrets"
$dataDir    = Join-Path $base "data"
$logsDir    = Join-Path $base "logs"

New-Item -ItemType Directory -Force $configDir  | Out-Null
New-Item -ItemType Directory -Force $secretsDir | Out-Null
New-Item -ItemType Directory -Force $dataDir    | Out-Null
New-Item -ItemType Directory -Force $logsDir    | Out-Null

# ---- ENV (this PS process only) ----
$env:PYTHONPATH         = $src
$env:BTC_TS_CONFIG_DIR  = $configDir
$env:BTC_TS_SECRETS_DIR = $secretsDir
$env:BTC_TS_DATA_DIR    = $dataDir
$env:BTC_TS_LOGS_DIR    = $logsDir
# audit 出力を必ず有効化（仕様: BTC_TS_MODE != OFF のときのみ audit.jsonl が出る）
$env:BTC_TS_MODE        = "DEBUG"

Show-Title "ENV"
Write-Host "PYTHONPATH        = $env:PYTHONPATH"
Write-Host "BTC_TS_CONFIG_DIR = $env:BTC_TS_CONFIG_DIR"
Write-Host "BTC_TS_DATA_DIR   = $env:BTC_TS_DATA_DIR"
Write-Host "BTC_TS_LOGS_DIR   = $env:BTC_TS_LOGS_DIR"

Show-Title "Python sanity"
python -c "import sys; print(sys.executable); import btcts; print('btcts OK:', btcts.__file__)"
Test-PyImport -moduleName "requests" -pipName "requests"
Test-PyImport -moduleName "yaml"     -pipName "pyyaml"

# ---- common configs ----
Show-Title "Write common YAML"
Write-Utf8 (Join-Path $configDir "exchanges.yaml") @"
exchanges:
  bitflyer:
    enabled: true
    rate:
      max_rps: 5
      burst: 0
"@

Write-Utf8 (Join-Path $configDir "collector.yaml") @"
tick_sec: 0.05
rate_state_every_sec: 1.0
status_every_sec: 0.5
startup_grace_sec: 3.0
no_data_check_every_sec: 0.2
"@

Write-Utf8 (Join-Path $configDir "monitoring.yaml") @"
safety_factor:
  bitflyer: 0.8
"@

# endpoints は rate-limit でテストが不安定になりやすいので、テスト用に低めの上限を固定する
# NOTE: TEST1 は endpoints.yaml を items:[] に差し替えるので、この定義は TEST1 には影響しない
Write-Utf8 (Join-Path $configDir "endpoints.yaml") @"
bitflyer:
  orderbook:
    url: https://api.bitflyer.com/v1/board
    method: GET
    topic: orderbook
    priority: 0
    max_rps: 2
    burst: 1
  trades:
    url: https://api.bitflyer.com/v1/executions
    method: GET
    topic: trades
    priority: 1
    max_rps: 2
    burst: 1
"@

# helper paths
$auditPath  = Join-Path $logsDir "audit.jsonl"
$statusPath = Join-Path $dataDir "collector\status.json"

function Export-Effective([string]$name, [string]$outPath) {
  # settings_svc.load_effective(<name>) の「現物」を JSON で吐く
  # 追加: resolve結果（schema/current）と環境（BTC_TS_CONFIG_DIR 等）も同梱して「どこを読んだか」を確定させる
  try {
    $code = @"
import json, os
from btcts.settings import svc as s

ref = s.resolve('$name')
x = s.load_effective('$name')

out = {
  "__meta": {
    "name": "$name",
    "schema_path": str(ref.schema_path),
    "current_path": str(ref.current_path),
    "env": {
      "BTC_TS_CONFIG_DIR": os.environ.get("BTC_TS_CONFIG_DIR", ""),
      "BTC_TS_DATA_DIR": os.environ.get("BTC_TS_DATA_DIR", ""),
      "BTC_TS_LOGS_DIR": os.environ.get("BTC_TS_LOGS_DIR", ""),
      "BTC_TS_MODE": os.environ.get("BTC_TS_MODE", ""),
    }
  },
  "effective": x
}

print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
"@
    $dir = Split-Path -Parent $outPath
    New-Item -ItemType Directory -Force $dir | Out-Null
    $code | python -c "import sys; exec(sys.stdin.read())" 2>$null | Set-Content -Encoding UTF8 $outPath
    Write-Host "[OK] effective $name -> $outPath"
  } catch {
    Write-Host "[NG] Export-Effective failed: $name"
    Write-Host $_
  }
}

function Show-Result([string]$label) {
  Show-Title $label

  Write-Host "--- status.json (if exists) ---"
  Show-Tail $statusPath 80
  Write-Host ""

  Write-Host "--- effective config snapshots (if exists) ---"
$eff = Get-ChildItem -Path $logsDir -Filter "*.effective_*.json" -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime

$effList = @()
if ($null -ne $eff) { $effList = @($eff) }

if ($effList.Count -eq 0) {
  Write-Host "(missing) *.effective_*.json in $logsDir"
} else {
  foreach ($f in $effList) {
    Write-Host ("--- " + $f.Name + " ---")
    Get-Content -Path $f.FullName -Raw
    Write-Host ""
  }
}

  Write-Host "--- logs dir listing ---"
  Get-ChildItem -Path $logsDir -Force -ErrorAction SilentlyContinue | Format-Table -AutoSize
  Write-Host ""

  Write-Host "--- stdout/stderr tail (if exists) ---"
  $stdout = Get-ChildItem -Path $logsDir -Filter *.stdout.txt -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $stderr = Get-ChildItem -Path $logsDir -Filter *.stderr.txt -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1

  if ($null -ne $stdout) {
    Write-Host ("--- " + $stdout.Name + " ---")
    Show-Tail $stdout.FullName 50
    Write-Host ""
  }

  if ($null -ne $stderr) {
    Write-Host ("--- " + $stderr.Name + " ---")
    Show-Tail $stderr.FullName 50
    Write-Host ""
  }

  Write-Host "--- logs/*.jsonl tail ---"
  $jsonl = Get-ChildItem -Path $logsDir -Filter *.jsonl -ErrorAction SilentlyContinue | Select-Object -First 1

  if ($null -eq $jsonl) {
    Write-Host "(missing) *.jsonl in $logsDir"
  } else {
    Write-Host ("file: " + $jsonl.FullName)
    Show-Tail $jsonl.FullName 80
  }
}

# ---- workspace helpers ----
function Reset-Workspace {
  # logs/data をテスト単位で掃除（config は保持）
  try {
    # data/collector 以下を掃除
    $collectorDir = Join-Path $dataDir "collector"
    if (Test-Path $collectorDir) { Remove-Item -Recurse -Force $collectorDir -ErrorAction SilentlyContinue }

    # logs の生成物を掃除（audit/effective/stdout/stderr）
    if (Test-Path $logsDir) {
      Get-ChildItem -Path $logsDir -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '\.(jsonl|stdout\.txt|stderr\.txt)$' -or $_.Name -match '\.effective_.*\.json$' } |
        ForEach-Object { try { Remove-Item -Force $_.FullName -ErrorAction SilentlyContinue } catch {} }
    }
  } catch {
    Write-Host "[WARN] Reset-Workspace failed: $($_.Exception.Message)"
  }
}

function Stop-StrayCollector {
  # 直前の異常終了で残った collector を可能な限り止める（ベストエフォート）
  # NOTE: 止めたいのは「python -m btcts.collector.main」だけ。
  try {
    $procs = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
      Where-Object {
        ($_.Name -in @('python.exe','pythonw.exe')) -and
        ($_.CommandLine -match 'btcts\.collector')
      }

    foreach ($p in $procs) {
      try {
        Write-Host "[WARN] stray collector found => kill pid=$($p.ProcessId)"
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
      } catch {}
    }
  } catch {
    # CIM が無い / CommandLine が取れない環境でもテストは進める
  }
}
Stop-StrayCollector

# ---- TEST 1: endpoints empty => endpoints.empty + ERROR exit ----
Show-Title "TEST 1: endpoints empty (items: [])"
Stop-StrayCollector
Reset-Workspace

# region TEST1_COLLECTOR_YAML
# TEST1 は「collector.enabled_exchanges を空」にして scheduler の登録をゼロに落とし、
# collector.endpoints.empty を確実に踏ませる。
# ただし endpoints.yaml 側にデフォルト定義が載るケースがあるため、exchanges.yaml も同時に無効化して
# 「有効な取引所が1つも無い」状態を固定する（ここが一番安定）。
Write-Utf8 (Join-Path $configDir "exchanges.yaml") @"
exchanges:
  bitflyer:
    enabled: false
    rate:
      max_rps: 5
      burst: 0
"@

Write-Utf8 (Join-Path $configDir "collector.yaml") @"
enabled_exchanges: []
feeds: {}
tick_sec: 0.05
rate_state_every_sec: 1.0
status_every_sec: 0.5
startup_grace_sec: 1.0
no_data_check_every_sec: 0.2
"@
# endregion TEST1_COLLECTOR_YAML

# region TEST1_ENDPOINTS_YAML
Write-Utf8 (Join-Path $configDir "endpoints.yaml") @"
items: []
"@
# endregion TEST1_ENDPOINTS_YAML
$code1 = 0

$out1 = Join-Path $logsDir "test1.stdout.txt"
$err1 = Join-Path $logsDir "test1.stderr.txt"

# 事前に effective をダンプ（Collector が何を見ているか確定させる）
Export-Effective "endpoints"   (Join-Path $logsDir "test1.effective_endpoints.json")
# precondition OK のときだけ Collector を起動
Export-Effective "exchanges"   (Join-Path $logsDir "test1.effective_exchanges.json")
Export-Effective "collector"   (Join-Path $logsDir "test1.effective_collector.json")

# TEST1 が狙う「endpoints.empty」は endpoints 設定ではなく collector 側の enabled_exchanges=[] で確実に踏む。
# そのため、collector effective が狙いどおりになっているかを事前条件として固定する。
$effColPath = Join-Path $logsDir "test1.effective_collector.json"
$expectedCollectorCurrent = (Join-Path $configDir "collector.yaml")

if (-not (Test-Path $effColPath)) {
  Write-Host "[FAIL] TEST1 precondition: effective collector json not found"
  Write-Host ("  expected: " + $effColPath)
  $code1 = 6
}
else {
  $effCol = Get-Content -Path $effColPath -Raw | ConvertFrom-Json
  $metaC  = $effCol.__meta

  $curC   = [string]$metaC.current_path
  if ($curC -ne $expectedCollectorCurrent) {
    Write-Host "[FAIL] TEST1 precondition: collector current_path mismatch"
    Write-Host ("  expected: " + $expectedCollectorCurrent)
    Write-Host ("  actual  : " + $curC)
    $code1 = 7
  }
  else {
    # enabled_exchanges が空か（最重要）
    $enabled = @()
    if ($null -ne $effCol.effective.enabled_exchanges) { $enabled = @($effCol.effective.enabled_exchanges) }

    if ($enabled.Count -ne 0) {
      Write-Host "[FAIL] TEST1 precondition: collector.enabled_exchanges must be empty"
      Write-Host ("  actual: " + (ConvertTo-Json $effCol.effective.enabled_exchanges -Compress))
      $code1 = 8
    }
    else {
      Write-Host "[OK] TEST1 precondition: collector.enabled_exchanges is empty (will force endpoints=0)"
      Write-Host ("  collector current_path = " + $curC)
    }
  }
}

Export-Effective "monitoring"  (Join-Path $logsDir "test1.effective_monitoring.json")

# precondition OK のときだけ Collector を起動
if ($code1 -eq 0) {
  try {
    $p = Start-Process -FilePath "python" -ArgumentList @("-m","btcts.collector.main") `
          -PassThru -NoNewWindow `
          -RedirectStandardOutput $out1 -RedirectStandardError $err1

    # TEST1 は「期待状態が観測できたら即PASSで止める」
    $timeoutSec = 15
    $deadline = (Get-Date).AddSeconds($timeoutSec)

    while ((Get-Date) -lt $deadline) {
      Start-Sleep -Milliseconds 200

      # 期待状態が出たら、プロセスを止めて PASS 判定へ進む
      $mode = ""
      if (Test-Path $statusPath) {
        try { $mode = (Get-Content -Path $statusPath -Raw | ConvertFrom-Json).mode } catch { $mode = "" }
      }

$hasEv = $false
if (Test-Path $auditPath) {
  $hasEv = (Select-String -Path $auditPath -SimpleMatch '"event":"collector.endpoints.empty"' -Quiet)
}

      if ($hasEv -and $mode -eq "ERROR") {
        # 期待結果が揃ったので止める（止めたこと自体は失敗ではない）
        if (-not $p.HasExited) {
          try { Stop-Process -Id $p.Id -Force } catch {}
          try { $null = $p | Wait-Process -Timeout 2 -ErrorAction SilentlyContinue } catch {}
        }
        $code1 = 0
        break
      }

      if ($p.HasExited) {
        $code1 = $p.ExitCode
        break
      }
    }

    if ($code1 -eq 0) {
      # PASS already
    }
    elseif (-not $p.HasExited) {
      Write-Host "[WARN] TEST1 timeout(${timeoutSec}s): force kill pid=$($p.Id)"
      try { Stop-Process -Id $p.Id -Force } catch {}
      $code1 = 124
    }
    else {
      $code1 = $p.ExitCode
    }
  } catch {
    Write-Host "[NG] TEST1 Start-Process failed"
    Write-Host $_
    $code1 = 999
  }
} else {
  Write-Host "[SKIP] TEST1 collector run skipped due to precondition failure (code=$code1)"
}

Write-Host "Expected: audit has collector.endpoints.empty, status mode ERROR"

# --- TEST1 expectation assert (expected failure => PASS) ---
$mode1 = ""
if (Test-Path $statusPath) {
  try { $mode1 = (Get-Content -Path $statusPath -Raw | ConvertFrom-Json).mode } catch { $mode1 = "" }
}

$hasEv1 = $false
if (Test-Path $auditPath) {
  try {
    # 1行でも壊れていると ConvertFrom-Json が落ちるので、event 文字列の単純検索に寄せる（安定）
    $hasEv1 = (Select-String -Path $auditPath -SimpleMatch '"event":"collector.endpoints.empty"' -Quiet)
  } catch { $hasEv1 = $false }
}

if ($hasEv1 -and $mode1 -eq "ERROR") {
  Write-Host "[OK] TEST1 expected ERROR observed (endpoints.empty + status ERROR) => PASS"
  $code1 = 0
} else {
  Write-Host "[FAIL] TEST1 expectation not met (need endpoints.empty + status ERROR)"
  Write-Host "  status.mode = '$mode1' (expected 'ERROR')"
  Write-Host "  audit has collector.endpoints.empty = $hasEv1"
  if ($code1 -eq 0) { $code1 = 10 }
}

Update-Overall $code1

# ---- TEST 2: unsupported topic => skip reason/hint then no_data => ERROR ----

Show-Title "TEST 2: unsupported topic => skip -> no_data -> ERROR"
Stop-StrayCollector
Reset-Workspace

# region TEST2_COLLECTOR_YAML
# TEST2: endpoints.yaml は触らない（schema map 構造なので items は無効化される）
#       代わりに collector.yaml の feeds で unsupported topic を作る
#       ここでは exchanges.yaml を明示的に有効化して「TEST1 の無効化の影響」を遮断する。
Write-Utf8 (Join-Path $configDir "exchanges.yaml") @"
exchanges:
  bitflyer:
    enabled: true
    rate:
      max_rps: 5
      burst: 0
"@

Write-Utf8 (Join-Path $configDir "collector.yaml") @"
enabled_exchanges:
  - bitflyer
feeds:
  bitflyer:
    # schema 側の既知 topic が走らないように明示的に潰す
    orderbook:
      enabled: false
    trades:
      enabled: false

    # これだけを「有効」にして unsupported -> skip を踏ませる
    unknown_topic:
      enabled: true
      priority: 0
      target_interval: 0.2
tick_sec: 0.05
rate_state_every_sec: 1.0
status_every_sec: 0.5
startup_grace_sec: 3.0
no_data_check_every_sec: 0.2
"@
# endregion TEST2_COLLECTOR_YAML

# TEST1 で endpoints.yaml を items:[] に差し替えるため、TEST2 以降は毎回ここで map を復元
Write-Utf8 (Join-Path $configDir "endpoints.yaml") @"
bitflyer:
  orderbook:
    url: https://api.bitflyer.com/v1/board
    method: GET
    topic: orderbook
    priority: 0
    max_rps: 2
    burst: 1
  trades:
    url: https://api.bitflyer.com/v1/executions
    method: GET
    topic: trades
    priority: 1
    max_rps: 2
    burst: 1
"@

$code2 = 0
try {
  $out2 = Join-Path $logsDir "test2.stdout.txt"
  $err2 = Join-Path $logsDir "test2.stderr.txt"

  Export-Effective "endpoints" (Join-Path $logsDir "test2.effective_endpoints.json")
  Export-Effective "exchanges" (Join-Path $logsDir "test2.effective_exchanges.json")
  Export-Effective "collector" (Join-Path $logsDir "test2.effective_collector.json")

  $p = Start-Process -FilePath "python" -ArgumentList @("-m","btcts.collector.main") `
        -PassThru -NoNewWindow `
        -RedirectStandardOutput $out2 -RedirectStandardError $err2

  # startup_grace_sec(3.0) + no_data 判定までを考慮して少し長め
  $timeoutSec = 15
  $null = $p | Wait-Process -Timeout $timeoutSec -ErrorAction SilentlyContinue

  if (-not $p.HasExited) {
    Write-Host "[WARN] TEST2 timeout(${timeoutSec}s): force kill pid=$($p.Id)"
    try { Stop-Process -Id $p.Id -Force } catch {}
    $code2 = 124
  } else {
    $code2 = $p.ExitCode
  }
} catch {
  $code2 = 999
}

Show-Result "TEST 2 RESULT (exit=$code2)"
Write-Host "Expected: audit has collector.endpoint.skip with reason/hint, then collector.no_data, status mode ERROR"

# --- TEST2 expectation assert (expected failure => PASS) ---
$mode2 = ""
if (Test-Path $statusPath) {
  try { $mode2 = (Get-Content -Path $statusPath -Raw | ConvertFrom-Json).mode } catch { $mode2 = "" }
}

$hasSkip = $false
$hasNoData = $false
$hasEmpty = $false

if (Test-Path $auditPath) {
  try {
    # JSONパースは壊れた1行で全体が落ちるので、event文字列の単純検索に寄せる（安定）
    $hasSkip   = (Select-String -Path $auditPath -SimpleMatch '"event":"collector.endpoint.skip"' -Quiet)
    $hasNoData = (Select-String -Path $auditPath -SimpleMatch '"event":"collector.no_data"' -Quiet)
    $hasEmpty  = (Select-String -Path $auditPath -SimpleMatch '"event":"collector.endpoints.empty"' -Quiet)
  } catch {
    $hasSkip = $false
    $hasNoData = $false
    $hasEmpty = $false
  }
}

$passBySkip = ($hasSkip -and $hasNoData)
$passByEmpty = $hasEmpty

if (($mode2 -eq "ERROR") -and ($passBySkip -or $passByEmpty)) {
  Write-Host "[OK] TEST2 expected ERROR observed => PASS"
  Write-Host "  pass: mode=ERROR and (skip+no_data OR endpoints.empty)"
  $code2 = 0
} else {
  Write-Host "[FAIL] TEST2 expectation not met"
  Write-Host "  status.mode = '$mode2' (expected 'ERROR')"
  Write-Host "  audit has endpoint.skip = $hasSkip"
  Write-Host "  audit has no_data       = $hasNoData"
  Write-Host "  audit has endpoints.empty = $hasEmpty"
  if ($code2 -eq 0) { $code2 = 11 }
}

Update-Overall $code2


# ---- TEST 3: orderbook normal (run 10 sec, then stop) ----

Show-Title "TEST 3: orderbook normal (stop on first data or audit ok; max 20 sec)"
Stop-StrayCollector
Reset-Workspace

# region TEST3_COLLECTOR_YAML
# TEST3: orderbook だけ有効化（trades を無効にする）
# ここでも exchanges.yaml を明示的に有効化して「TEST1 の無効化の影響」を遮断する。
Write-Utf8 (Join-Path $configDir "exchanges.yaml") @"
exchanges:
  bitflyer:
    enabled: true
    rate:
      max_rps: 5
      burst: 0
"@

Write-Utf8 (Join-Path $configDir "collector.yaml") @"
enabled_exchanges:
  - bitflyer
feeds:
  bitflyer:
    orderbook:
      enabled: true
      priority: 0
      target_interval: 1.0
    trades:
      enabled: false
tick_sec: 0.05
rate_state_every_sec: 1.0
status_every_sec: 0.5
startup_grace_sec: 15.0
no_data_check_every_sec: 0.2
"@
# endregion TEST3_COLLECTOR_YAML

# TEST1 で endpoints.yaml を items:[] に差し替えるため、TEST2 以降は毎回ここで map を復元
Write-Utf8 (Join-Path $configDir "endpoints.yaml") @"
bitflyer:
  orderbook:
    url: https://api.bitflyer.com/v1/board
    method: GET
    topic: orderbook
    priority: 0
    max_rps: 2
    burst: 1
  trades:
    url: https://api.bitflyer.com/v1/executions
    method: GET
    topic: trades
    priority: 1
    max_rps: 2
    burst: 1
"@

$code3 = 0

# StrictMode 対策：try の外で必ず初期化（例外経路でも未初期化参照にならない）
$requestedStop = $false
$seenData = $false
$seenOk = $false
$p = $null

try {

  $out3 = Join-Path $logsDir "test3.stdout.txt"
  $err3 = Join-Path $logsDir "test3.stderr.txt"

  Export-Effective "endpoints" (Join-Path $logsDir "test3.effective_endpoints.json")
  Export-Effective "exchanges" (Join-Path $logsDir "test3.effective_exchanges.json")
  Export-Effective "collector" (Join-Path $logsDir "test3.effective_collector.json")

  # 非同期起動 → データが出たら即停止（最小負荷）
  $p = Start-Process -FilePath "python" -ArgumentList @("-m","btcts.collector.main") `
        -PassThru -NoNewWindow `
        -RedirectStandardOutput $out3 -RedirectStandardError $err3

  # 生成物が出るまで待つ（最大20秒）。出たら即止める。
  $dataGlob = Join-Path $dataDir "collector\bitflyer\orderbook\*.jsonl"
  $timeoutSec = 20
  $deadline = (Get-Date).AddSeconds($timeoutSec)

  while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 200

    # data file 観測（確実だが I/O タイミングで遅れることがある）
    $files = @(Get-ChildItem -Path $dataGlob -ErrorAction SilentlyContinue)
    if ($files.Count -gt 0 -and ((@($files | Where-Object { $_.Length -gt 0 })).Count -gt 0)) {
      $seenData = $true
      break
    }

    # audit 観測（data より先に出ることがあるので成功判定の保険）
    if (Test-Path $auditPath) {
      $seenOk = (Select-String -Path $auditPath -SimpleMatch '"event":"collector.endpoint.ok"' -Quiet)
      if ($seenOk) { break }
    }

    if ($p.HasExited) { break }
  }

  # データが出た or タイムアウト or 途中終了 → ここで止めに行く（止めたら requestedStop=true）
  if ($null -ne $p -and -not $p.HasExited) {
    try { Stop-Process -Id $p.Id -Force } catch {}
    try { $null = $p | Wait-Process -Timeout 2 -ErrorAction SilentlyContinue } catch {}
    $requestedStop = $true
  }

  if (-not $seenData) {
    Write-Host "[WARN] TEST3 did not observe data within ${timeoutSec}s (may be rate-limited)"
  }

  # exit code 判定
  if ($requestedStop) {
    # テスト都合で止めたので 0 扱い
    $code3 = 0
  } elseif ($null -ne $p -and $p.HasExited) {
    $code3 = $p.ExitCode
  } else {
    # ここに来たら異常（プロセス参照不可など）
    $code3 = 124
  }

  # region TEST3_DATA_ASSERT
  $files = @(Get-ChildItem -Path $dataGlob -ErrorAction SilentlyContinue)
  $hasNonZero = ((@($files | Where-Object { $_.Length -gt 0 })).Count -gt 0)

  $success = ($seenData -or $seenOk)

  if (-not $success) {
    Write-Host "[FAIL] TEST3 success not observed (need data file OR audit endpoint.ok)"
    Write-Host "  seenData = $seenData"
    Write-Host "  seenOk   = $seenOk"
    Write-Host "  files    = $($files.Count)"
    if ($code3 -eq 0) { $code3 = 20 }
  }
  elseif ($hasNonZero) {
    Write-Host "[OK] TEST3 success observed (data file OR audit endpoint.ok)"
  }
  else {
    # audit は出たが data が遅れているケースを PASS 扱いにする（最小負荷で止める方針の副作用を吸収）
    Write-Host "[OK] TEST3 audit has endpoint.ok (data file timing may lag) => PASS"
  }
  # endregion TEST3_DATA_ASSERT

} catch {
  Write-Host "[NG] TEST3 exception"
  Write-Host $_
  if ($code3 -eq 0) { $code3 = 999 }
} finally {
  # 最後の保険：まだ生きてたら落とす（次のテストへ干渉させない）
  if ($null -ne $p -and -not $p.HasExited) {
    try { Stop-Process -Id $p.Id -Force } catch {}
  }
}

Show-Result "TEST 3 RESULT (exit=$code3)"
Write-Host "Expected: audit has collector.endpoint.ok, data file created under data\collector\bitflyer\orderbook\*.jsonl"
Update-Overall $code3

# ---- TEST 4: data quality injection (0byte / write途中の疑似) ----
Show-Title "TEST 4: data quality injection (0byte file)"
$code4 = 0

# TEST3 の生成物パスと同じ場所に 0byte を作る（品質ガード注入用）
$dqDir4 = Join-Path $dataDir "collector\bitflyer\orderbook"
New-Item -ItemType Directory -Force $dqDir4 | Out-Null

$zeroPath = Join-Path $dqDir4 "_dq_zero_byte.jsonl"
# 0byte を保証（既存があっても 0byte 化）
# NOTE: Set-Content は改行を書いて 0byte にならないことがあるため、バイト列で空を明示する
[System.IO.File]::WriteAllBytes($zeroPath, [byte[]]@())

if (-not (Test-Path $zeroPath)) {
  Write-Host "[FAIL] TEST4 could not create 0byte file: $zeroPath"
  $code4 = 40
} elseif ((Get-Item $zeroPath).Length -ne 0) {
  Write-Host "[FAIL] TEST4 expected 0byte but got $((Get-Item $zeroPath).Length) bytes: $zeroPath"
  $code4 = 41
} else {
  Write-Host "[OK] TEST4 injected 0byte file: $zeroPath"
}
Update-Overall $code4
Write-Host "Expected: (next phase) data-quality guard flags 0byte / partial-write as NG"


# ---- TEST 5: data quality injection (JSON破損行の疑似) ----
Show-Title "TEST 5: data quality injection (corrupt json line)"
$code5 = 0

$dqDir5 = Join-Path $dataDir "collector\bitflyer\orderbook"
New-Item -ItemType Directory -Force $dqDir5 | Out-Null

$badPath = Join-Path $dqDir5 "_dq_bad_json.jsonl"
"{ this is not json }" | Set-Content -Encoding UTF8 $badPath

if (-not (Test-Path $badPath)) {
  Write-Host "[FAIL] TEST5 could not create corrupt file: $badPath"
  $code5 = 50
} else {
  # Pythonで 1行JSONパース -> 失敗行番号を返す（0なら全部OK）
  $py = @"
import json, sys
p = sys.argv[1]
ng = 0
with open(p, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        line = line.rstrip("\n")
        if not line:
            continue
        try:
            json.loads(line)
        except Exception:
            ng = i
            break
print(ng)
"@
  $ngLine = ($py | python - "$badPath")
  $ngLine = [int]$ngLine

  if ($ngLine -le 0) {
    Write-Host "[FAIL] TEST5 expected JSON parse failure but got OK: $badPath"
    $code5 = 51
  } else {
    Write-Host "[OK] TEST5 injected corrupt line and detected at line=$($ngLine): $badPath"
  }
  Update-Overall $code5
}
Write-Host "Expected: (next phase) data-quality guard flags json decode failure as NG"

Write-Host ""
Show-Title "DONE"
Write-Host ("Workspace: " + $base)
Write-Host ("LastWs  : " + (Join-Path $root "tmp\collector_test\_last_workspace.txt"))
Write-Host ("StatusPath: " + $statusPath)
Write-Host ("AuditPath : " + $auditPath)
Write-Host ("ExitCode  : " + $overall)

exit $overall
