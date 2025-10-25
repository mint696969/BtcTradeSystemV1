# path: ./scripts/refactor/dash_ui_reorg.ps1
# desc: ダッシュボードUI/設定の構成整理（スキャン/適用）: 参照洗い出し→安全なリネーム計画→defaults配置移行→復元点作成
[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
param(
  [ValidateSet('scan','apply')]
  [string]$Mode = 'scan',
  [string]$RepoRoot = (Resolve-Path '.').Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- 定義（パス） ---
$DashDir          = Join-Path $RepoRoot 'btc_trade_system/features/dash'
$SettingsDir      = Join-Path $RepoRoot 'btc_trade_system/features/settings'
$SettingsSections = Join-Path $SettingsDir 'sections'
$ConfigUiDir      = Join-Path $RepoRoot 'btc_trade_system/config/ui'
$ConfigExDir      = Join-Path $RepoRoot 'btc_trade_system/config/exchanges'
$SecretsPath      = Join-Path $RepoRoot 'config/secrets.exchanges.yaml'
$TmpDir           = Join-Path $RepoRoot 'tmp/refactor_phase0'
New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null

# --- 補助: 出力ユーティリティ ---
function Write-Plan {
  param([string]$Title,[object]$Data)
  $jsonPath = Join-Path $TmpDir ("$Title.json")
  $Data | ConvertTo-Json -Depth 6 | Out-File -FilePath $jsonPath -Encoding UTF8
  Write-Host "[plan] $Title -> $jsonPath"
}

function Test-Exists {
  param([string]$Path)
  return (Test-Path -LiteralPath $Path)
}

# --- 1) スキャン（UIファイル位置／参照洗い出し） ---
$scan = [ordered]@{}
$scan.repoRoot = $RepoRoot
$scan.time = (Get-Date).ToString('s')

# 候補: 旧ファイル名
$oldAudit = Get-ChildItem -Path $DashDir -Recurse -Filter 'ui_audit.py' -ErrorAction SilentlyContinue
$oldHealth = Get-ChildItem -Path $DashDir -Recurse -Filter 'ui_health.py' -ErrorAction SilentlyContinue

$scan.uiFiles = [ordered]@{
  audit_ui_py  = $oldAudit.FullName
  health_ui_py = $oldHealth.FullName
}

# 参照検索（repo全体）
$codeGlobs = @('*.py','*.ps1','*.md','*.yml','*.yaml')
$refPatterns = @('\baudit_ui\b','\bhealth_ui\b')
$refHits = @()
foreach ($glob in $codeGlobs) {
  $paths = Get-ChildItem -Path $RepoRoot -Recurse -Include $glob -File -ErrorAction SilentlyContinue
  if ($paths) {
    $refHits += Select-String -Path $paths.FullName -Pattern $refPatterns -SimpleMatch:$false -AllMatches -ErrorAction SilentlyContinue |
      ForEach-Object {
        [pscustomobject]@{
          Path  = $_.Path
          Line  = $_.Line.Trim()
          Match = ($_.Matches.Value -join ',')
        }
      }
  }
}
$scan.refHits = $refHits

# ターゲット名
$targetAudit = if ($oldAudit) { Join-Path $oldAudit.DirectoryName 'ui_audit.py' } else { Join-Path $DashDir 'ui_audit.py' }
$targetHealth = if ($oldHealth) { Join-Path $oldHealth.DirectoryName 'ui_health.py' } else { Join-Path $DashDir 'ui_health.py' }

$scan.renamePlan = @()
if ($oldAudit)  { $scan.renamePlan += [pscustomobject]@{ src=$oldAudit.FullName;  dst=$targetAudit;  exists=(Test-Exists $targetAudit) } }
if ($oldHealth) { $scan.renamePlan += [pscustomobject]@{ src=$oldHealth.FullName; dst=$targetHealth; exists=(Test-Exists $targetHealth) } }

# --- 2) 設定フォルダの将来構成チェック ---
$scan.configPlan = [ordered]@{
  make_dirs = @($ConfigUiDir, $ConfigExDir, $SettingsSections)
  ui_defaults_candidates = @()
}
$legacyDefaults = Get-ChildItem -Path (Join-Path $RepoRoot 'btc_trade_system/config') -Recurse -Directory -Filter 'ui_defaults' -ErrorAction SilentlyContinue
if ($legacyDefaults) {
  $scan.configPlan.ui_defaults_candidates = Get-ChildItem -Path $legacyDefaults.FullName -Filter '*.yaml' -File -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
}

# --- 3) 結果を保存 ---
Write-Plan -Title 'scan_report' -Data $scan

if ($Mode -eq 'scan') {
  Write-Host "\n[SCAN COMPLETE] 結果: $TmpDir/scan_report.json" -ForegroundColor Cyan
  Write-Host "- 参照件数: $($refHits.Count)"
  Write-Host "- リネーム候補: $($scan.renamePlan.Count) (ui_audit/ui_health)"
  Write-Host "- ui_defaults 候補: $($scan.configPlan.ui_defaults_candidates.Count)"
  return
}

# --- 4) APPLY フェーズ ---
Write-Host "[APPLY] 構成整理を適用します。" -ForegroundColor Yellow

# 4-0) Git 復元点（存在すれば既存スクリプト優先）
$rpScript = Join-Path $RepoRoot 'scripts/git/git_rp_make.ps1'
$rpName = "rp-$(Get-Date -Format 'yyyyMMdd_HHmmss')_phase0"
try {
  if (Test-Path $rpScript) {
    & $rpScript -TagName $rpName
  } else {
    # 最低限: Gitタグ（ブランチでも可）
    git rev-parse --is-inside-work-tree | Out-Null
    git add -A
    git commit -m "chore: pre-phase0 checkpoint"
    git tag $rpName
  }
  Write-Host "[OK] 復元点作成: $rpName"
} catch {
  Write-Warning "[WARN] 復元点の作成に失敗: $($_.Exception.Message)"
}

# 4-1) 必要ディレクトリ作成
foreach ($d in @($ConfigUiDir,$ConfigExDir,$SettingsDir,$SettingsSections)) {
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

# 4-2) 旧 ui_defaults → *.defaults.yaml へ移行
if ($legacyDefaults) {
  $files = Get-ChildItem -Path $legacyDefaults.FullName -Filter '*.yaml' -File -ErrorAction SilentlyContinue
  foreach ($f in $files) {
    $dst = Join-Path $ConfigUiDir (($f.BaseName) + '.defaults.yaml')
    if ($PSCmdlet.ShouldProcess($dst, "Copy defaults from $($f.Name)")) {
      Copy-Item -LiteralPath $f.FullName -Destination $dst -Force
    }
  }
}

# 4-3) UIファイルのリネーム（衝突回避）
foreach ($plan in $scan.renamePlan) {
  if ($plan.exists) {
    Write-Warning "[SKIP] 既に存在: $($plan.dst)"
    continue
  }
  if ($PSCmdlet.ShouldProcess($plan.dst, "Rename $($plan.src) -> $($plan.dst)")) {
    Rename-Item -LiteralPath $plan.src -NewName (Split-Path $plan.dst -Leaf)
  }
}

# 4-4) 最終レポート
$applyLog = [ordered]@{
  time = (Get-Date).ToString('s')
  rp   = $rpName
  created_dirs = @($ConfigUiDir,$ConfigExDir,$SettingsDir,$SettingsSections) | Where-Object { Test-Path $_ }
  renamed = $scan.renamePlan
}
Write-Plan -Title 'apply_result' -Data $applyLog
Write-Host "[APPLY COMPLETE] ログ: $TmpDir/apply_result.json" -ForegroundColor Green

