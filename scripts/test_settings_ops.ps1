# path: ./tmp/test_settings_ops.ps1
# desc: 設定モーダルの保存/デフォルト動作を dev_audit と設定ファイルから一括チェックする簡易ツール

param(
    [string]$Areas = "main,dash,collector,health,monitoring",
    [int]$Tail = 300
)

Set-Location $PSScriptRoot
Set-Location ..

$logsRoot = $env:BTC_TS_LOGS_DIR
if (-not $logsRoot) { $logsRoot = 'D:\BtcTS_V1\logs' }

$configRoot = $env:BTC_TS_CONFIG_DIR
if (-not $configRoot) { $configRoot = Join-Path (Get-Location) 'btc_trade_system\config' }

$devAudit = Join-Path $logsRoot 'dev_audit.jsonl'

Write-Host "=== CONFIG ROOT ===" -ForegroundColor Cyan
Write-Host $configRoot
Write-Host "=== LOGS ROOT ===" -ForegroundColor Cyan
Write-Host $logsRoot
Write-Host ""

# A. dev_audit の settings.* イベント
if (Test-Path $devAudit) {
    Write-Host "=== dev_audit: settings.default/apply + settings.write (tail $Tail) ===" -ForegroundColor Yellow
    Get-Content $devAudit -Tail $Tail |
      Select-String -Pattern '"settings\.write\.|settings\.default\.apply\.' -SimpleMatch

    Write-Host ""
    Write-Host "=== dev_audit: settings.*.(try|done)（出てこないのが理想） ===" -ForegroundColor Yellow
    Get-Content $devAudit -Tail $Tail |
      Select-String -Pattern '"settings\.(.+?)\.(try|done)\."' -SimpleMatch
} else {
    Write-Host "dev_audit.jsonl が見つかりません: $devAudit" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== CONFIG FILE SNAPSHOT ===" -ForegroundColor Cyan

$areaList = $Areas.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }

foreach ($a in $areaList) {
    switch ($a) {
        "main"       { $file = "main.yaml" }
        "dash"       { $file = "dash.yaml" }
        "collector"  { $file = "collector.yaml" }
        "health"     { $file = "health.yaml" }
        "monitoring" { $file = "monitoring.yaml" }
        default      { $file = "$a.yaml" }
    }

    $path = Join-Path $configRoot $file
    Write-Host ""
    Write-Host "--- [$a] $path ---" -ForegroundColor Green
    if (Test-Path $path) {
        Get-Content $path
    } else {
        Write-Host "NO FILE" -ForegroundColor DarkGray
    }
}
