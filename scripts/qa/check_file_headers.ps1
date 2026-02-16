# path: ./scripts/qa/check_file_headers.ps1
# desc: staged(コミット対象)の .py/.ps1/.md に # path/# desc が先頭2行にあるかを検査し、無ければ exit 1

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-StagedFiles {
  $out = & git diff --cached --name-only --diff-filter=ACMR
  if ($LASTEXITCODE -ne 0) { throw "git diff --cached failed" }
  return ($out | Where-Object { $_ -and ($_ -notmatch '^\s*$') })
}

function Has-Header([string]$fullPath) {
  if (-not (Test-Path -LiteralPath $fullPath)) { return $true } # 例: delete は対象外

  # バイナリっぽいのはスキップ（万一）
  try {
    $lines = @(Get-Content -LiteralPath $fullPath -TotalCount 2 -ErrorAction Stop)
  } catch {
    return $true
  }

  if ($lines.Count -lt 2) { return $false }

  # BOM対策
  $l1 = $lines[0] -replace '^\uFEFF',''
  $l2 = $lines[1] -replace '^\uFEFF',''

  $ok1 = ($l1 -match '^\s*#\s*path:\s+\./')
  $ok2 = ($l2 -match '^\s*#\s*desc:\s+.+')
  return ($ok1 -and $ok2)
}

$targets = @()
foreach ($rel in (Get-StagedFiles)) {
  $ext = [IO.Path]::GetExtension($rel).ToLowerInvariant()
  if ($ext -in @(".py",".ps1",".md")) {
    # hooks 実行場所に依存しないよう絶対パス化
    $full = Join-Path (Get-Location) $rel
    $targets += [pscustomobject]@{ Rel=$rel; Full=$full }
  }
}

if ($targets.Count -eq 0) { exit 0 }

$ng = @()
foreach ($t in $targets) {
  if (-not (Has-Header $t.Full)) { $ng += $t.Rel }
}

if ($ng.Count -gt 0) {
  Write-Host ""
  Write-Host "ERROR: Missing required file header (# path / # desc) at top 2 lines:" -ForegroundColor Red
  $ng | ForEach-Object { Write-Host ("  - " + $_) -ForegroundColor Red }
  Write-Host ""
  Write-Host "Fix: add at very top (line1/2):" -ForegroundColor Yellow
  Write-Host "  # path: ./<repo-relative>" -ForegroundColor Yellow
  Write-Host "  # desc: <what this file does>" -ForegroundColor Yellow
  Write-Host ""
  exit 1
}

exit 0


