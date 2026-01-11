# path: ./tmp/test_settings_full.ps1
# desc: 設定タブ全体と dev_audit / BOOST スナップショットの総合チェック用テストスクリプト

param(
    [int]$Tail = 400
)

# リポ直下へ移動
Set-Location $PSScriptRoot
Set-Location ..

# ルート推定
$logsRoot = $env:BTC_TS_LOGS_DIR
if (-not $logsRoot) {
    $logsRoot = 'D:\BtcTS_V1\logs'
}

$configRoot = $env:BTC_TS_CONFIG_DIR
if (-not $configRoot) {
    $configRoot = Join-Path (Get-Location) 'btc_trade_system\config'
}

$devAudit  = Join-Path $logsRoot 'dev_audit.jsonl'
$boostJson = Join-Path $logsRoot 'boost_snapshot.json'
$handover  = Join-Path $logsRoot 'handover_gpt.txt'

Write-Host "=== ROOTS ===" -ForegroundColor Cyan
Write-Host "CONFIG_ROOT: $configRoot"
Write-Host "LOGS_ROOT  : $logsRoot"
Write-Host ""

#--------------------------------------
# A. dev_audit settings.* イベント
#--------------------------------------
Write-Host "=== A. dev_audit settings.* イベント (tail $Tail) ===" -ForegroundColor Yellow

if (Test-Path $devAudit) {
    Write-Host "-- A-1 settings.write / settings.default.apply --" -ForegroundColor Green
    Get-Content $devAudit -Tail $Tail |
      Select-String -Pattern '"settings\.write\.|settings\.default\.apply\.' -SimpleMatch

    Write-Host ""
    Write-Host "-- A-2 settings.*.(try|done) （出てこないのが理想） --" -ForegroundColor Green
    Get-Content $devAudit -Tail $Tail |
      Select-String -Pattern '"settings\.(.+?)\.(try|done)\."' -SimpleMatch

    Write-Host ""
    Write-Host "-- A-3 settings.* かつ ERROR/WARN を含む行 --" -ForegroundColor Green
    Get-Content $devAudit -Tail $Tail |
      Select-String -Pattern '"settings\..+?"' -SimpleMatch |
      Select-String -Pattern '"ERROR"|"WARN"' -SimpleMatch
}
else {
    Write-Host "dev_audit.jsonl が見つかりません: $devAudit" -ForegroundColor Red
}

#--------------------------------------
# B. CONFIG スナップショット
#--------------------------------------
Write-Host ""
Write-Host "=== B. CONFIG スナップショット ===" -ForegroundColor Yellow

$areas = @('main','dash','collector','health','monitoring')

foreach ($a in $areas) {
    switch ($a) {
        'main'       { $file = 'main.yaml' }
        'dash'       { $file = 'dash.yaml' }
        'collector'  { $file = 'collector.yaml' }
        'health'     { $file = 'health.yaml' }
        'monitoring' { $file = 'monitoring.yaml' }
        default      { $file = "$a.yaml" }
    }

    $path = Join-Path $configRoot $file
    Write-Host ""
    Write-Host "--- [$a] $path ---" -ForegroundColor Green
    if (Test-Path $path) {
        Get-Content $path
    }
    else {
        Write-Host "NO FILE" -ForegroundColor DarkGray
    }
}

#--------------------------------------
# C. BOOST スナップショット (boost_snapshot.json)
#--------------------------------------
Write-Host ""
Write-Host "=== C. BOOST スナップショット (boost_snapshot.json) ===" -ForegroundColor Yellow

if (Test-Path $boostJson) {
    try {
        $snapRaw = Get-Content $boostJson -Raw
        $snap    = $snapRaw | ConvertFrom-Json

        Write-Host "-- C-1 env / paths --" -ForegroundColor Green
        if ($snap.env) {
            $snap.env | Format-List | Out-String | Write-Host
        }
        if ($snap.paths) {
            $snap.paths | Format-List | Out-String | Write-Host
        }

        Write-Host "-- C-2 settings / config 関連フィールド (あれば) --" -ForegroundColor Green
        if ($snap.settings) {
            $snap.settings | Format-List | Out-String | Write-Host
        }

        Write-Host "-- C-3 旧実装や不要キーワードのチェック --" -ForegroundColor Green
        $snapRaw |
          Select-String -Pattern 'settings_svc_deprecated|features\.dash\.settings_svc|ui_defaults/monitoring\.yaml' |
          ForEach-Object { $_.Line } |
          Write-Host
    }
    catch {
        Write-Host "boost_snapshot.json の解析に失敗: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "boost_snapshot.json が見つかりません: $boostJson" -ForegroundColor DarkGray
}

#--------------------------------------
# D. handover_gpt.txt 中の旧設定実装キーワード
#--------------------------------------
Write-Host ""
Write-Host "=== D. handover_gpt.txt 内の旧設定実装キーワード ===" -ForegroundColor Yellow

if (Test-Path $handover) {
    Get-Content $handover |
      Select-String -Pattern 'settings_svc_deprecated|features\.dash\.settings_svc|ui_defaults/monitoring\.yaml' |
      ForEach-Object { $_.Line } |
      Write-Host
}
else {
    Write-Host "handover_gpt.txt は見つかりません（logs 直下想定）" -ForegroundColor DarkGray
}
