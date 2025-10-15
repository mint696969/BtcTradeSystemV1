# path: ./tmp/repo_flatten/apply_plan.ps1
# desc: move_plan.json / shim_plan.json を用いた安全適用（RP作成→git mv→ヘッダ修正→簡易シム生成）

# Disable PSScriptAnalyzer warnings for non-approved verbs
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseApprovedVerbs','',Justification='Internal tooling script')]
param(
  [switch]$WhatIf,
  [string]$MovePlanPath = "./tmp/repo_flatten/move_plan.json",
  [string]$ShimPlanPath = "./tmp/repo_flatten/shim_plan.json",
  [switch]$SkipRP
)

Set-StrictMode -Version Latest

# --- repo root fix (workdir guard) ---
$scriptDir = Split-Path -Parent $PSCommandPath
# this script lives in ./tmp/repo_flatten/, so repo root = parent of ../
$RepoRoot  = (Resolve-Path (Join-Path $scriptDir '..\..')).Path
$OrigLoc   = Get-Location
Push-Location $RepoRoot
# --------------------------------------

$ErrorActionPreference = 'Stop'

function Ensure-File([string]$Path){ if(!(Test-Path $Path)){ throw "Not found: $Path" } }
function Read-Json([string]$Path){ Ensure-File $Path; (Get-Content $Path -Raw | ConvertFrom-Json) }

function Make-RestorePoint{
  if($SkipRP){ return }
  $rp = Join-Path -Path "." -ChildPath "scripts/git/git_rp_make.ps1"
  if(Test-Path $rp){
    Write-Host "[RP] creating restore point..."
    if($WhatIf){ Write-Host "WhatIf: & $rp -Commit -Diff -Zip -RpMemo 'repo_flatten apply'" }
    else { & $rp -Commit -Diff -Zip -RpMemo "repo_flatten apply" }
  } else {
    Write-Warning "[RP] scripts/git/git_rp_make.ps1 が見つかりません。手動で保存してください。"
  }
}

function Git-Mv-Safe([string]$Src,[string]$Dst){
  $srcFull = Join-Path $RepoRoot $Src
  $dstFull = Join-Path $RepoRoot $Dst
  $dstDir  = Split-Path -Parent $dstFull
  if(!(Test-Path $srcFull)){
    Write-Warning "[SKIP] git mv: source not found -> $Src"
    return
  }
  if(!(Test-Path $dstDir)){
    if($WhatIf){ Write-Host "WhatIf: mkdir $dstDir" }
    else { New-Item -ItemType Directory -Force -Path $dstDir | Out-Null }
  }
  $cmd = "git mv -v -- `"$Src`" `"$Dst`""
  if($WhatIf){ Write-Host "WhatIf: $cmd" } else { & git mv -v -- "$Src" "$Dst" }
}

function Update-Header-Path([string]$File,[string]$NewPath){
  $fileFull = Join-Path $RepoRoot $File
  if(!(Test-Path $fileFull)){ return }
  $lines = Get-Content $fileFull -Raw -Encoding UTF8 -ErrorAction SilentlyContinue | Out-String
  $updated = $false
  $out = $lines -split "\r?\n"
  if($out.Length -ge 1 -and $out[0] -match '^#\\s*path\\s*:\\s*'){
    $out[0] = "# path: ./$NewPath"; $updated = $true
  }
  $text = ($out -join "`n")
  if($updated){
    if($WhatIf){ Write-Host "WhatIf: update header in $File -> # path: ./$NewPath" }
    else { [IO.File]::WriteAllText($fileFull, $text, (New-Object System.Text.UTF8Encoding($false))) }
  }
}

function Apply-Moves($plan){
  foreach($kv in $plan.PSObject.Properties){
    $src = $kv.Name; $dst = $kv.Value
    Git-Mv-Safe $src $dst

    if($dst.ToLower().EndsWith('.py')){
      $dstFull = Join-Path $RepoRoot $dst
      if(Test-Path $dstFull){
        Update-Header-Path $dst $dst
      } else {
        Write-Warning "[SKIP] header update: not found after move -> $dst"
      }
    }
  }
}

function Write-Shims($shim){
  foreach($kv in $shim.PSObject.Properties){
    $initRel = $kv.Name
    $spec    = $kv.Value

    # 絶対パスで扱う（System32誤爆防止）
    $initFull = Join-Path $RepoRoot $initRel
    $dirFull  = Split-Path -Parent $initFull
    if(!(Test-Path $dirFull)){
      if($WhatIf){ Write-Host "WhatIf: mkdir $dirFull" }
      else { New-Item -ItemType Directory -Force -Path $dirFull | Out-Null }
    }

    $lines = @()
    $lines += "# path: ./$initRel"
    $lines += "# desc: 互換エクスポート（移行期間のみ使用）"
    $lines += "# NOTE: 移行完了後にこの __init__ は削除します"
    $lines += ""

    $props = @{}
    foreach($p in $spec.PSObject.Properties){ $props[$p.Name] = $true }

    if($props.ContainsKey('reexports_to')){
      $target = $spec.reexports_to
      $lines += "# reexports_to: $target"
      $lines += "# (実際の中身は機能側へ移設済み)"
    }

    if($props.ContainsKey('exports') -and $spec.exports){
      foreach($kv2 in $spec.exports.PSObject.Properties){
        $mod = $kv2.Value -replace '/', '.' -replace '\.py$',''
        $lines += "from ${mod} import *  # noqa: F401"
      }
    }

    if($props.ContainsKey('reexports') -and $spec.reexports){
      foreach($kv3 in $spec.reexports.PSObject.Properties){
        $mod = $kv3.Value -replace '/', '.' -replace '\.py$',''
        $lines += "from ${mod} import *  # noqa: F401"
      }
    }

    $content = ($lines -join "`n")
    if($WhatIf){ Write-Host "WhatIf: write $initRel (shim @ $initFull)" }
    else { [IO.File]::WriteAllText($initFull, $content, (New-Object System.Text.UTF8Encoding($false))) }
  }
}

try {
  $move = Read-Json $MovePlanPath
  $shim  = Read-Json $ShimPlanPath

  Make-RestorePoint
  Set-Location $RepoRoot

  Apply-Moves $move
  Write-Shims $shim

  Write-Host "[DONE] apply_plan completed. Use git status to review changes."
}
catch {
  Write-Error "[FAILED] $($_.Exception.Message)"
  throw
}
finally {
  if($OrigLoc){ Pop-Location }
}