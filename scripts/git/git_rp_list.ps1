# path: scripts/git/git_rp_list.ps1
# desc: List Restore Points (rp-*) - works with both annotated & lightweight tags.

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = 'Stop'

function Wait-AnyKey {
  Write-Host ""
  Write-Host "Press any key to exit..." -ForegroundColor DarkGray
  $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown') | Out-Null
}

function Halt($msg) {
  if ($msg) { Write-Host $msg -ForegroundColor Yellow }
  Wait-AnyKey
  exit 1
}

try {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Halt "git is not found. Please check PATH."
  }

  # 1) Detect repo root via git (works with worktree, etc.)
  $here = $PSScriptRoot
  $top  = (& git -C $here rev-parse --show-toplevel 2>$null)
  if (-not $top) {
    $maybe = Split-Path -Parent (Split-Path -Parent $here)
    $top   = (& git -C $maybe rev-parse --show-toplevel 2>$null)
  }
  if (-not $top) { Halt "Could not locate a Git repo. Check script location." }

  Write-Host "== Restore Points (rp-*)  (latest 10) ==" -ForegroundColor Cyan

  # 2) List tags (newest first)
  $lines = & git -C $top for-each-ref `
    --sort=-taggerdate `
    --format="%(taggerdate:iso)|%(objectname:short)|%(refname:short)|%(contents:subject)" `
    "refs/tags/rp-*"
  if ($LASTEXITCODE -ne 0) {
    $msg = "Failed to run 'git for-each-ref':`n" + ($lines | Out-String)
    Halt $msg
  }

  if (-not $lines) {
    Write-Host "(No Restore Points yet.)"
    Wait-AnyKey
    exit 0
  }

  # 3) Print up to 10 lines nicely
  ($lines | Select-Object -First 10) | ForEach-Object {
    $parts = $_ -split '\|', 4
    if ($parts.Count -ge 3) {
      $ts   = $parts[0]; if ($ts.Length -ge 19) { $ts = $ts.Substring(0,19) }
      $hash = $parts[1]
      $ref  = $parts[2] -replace '^refs/tags/', ''
      $memo = if ($parts.Count -ge 4 -and $parts[3]) { $parts[3] } else { "" }

      # 「Restore Point <tag> …」「<tag> : …」「<tag> - …」など重複前置きを取り除く
      $refEsc = [Regex]::Escape($ref)
      if ($memo -match "^\s*(?:Restore\s+Point\s+)?$refEsc\s*(?:[-:]\s*)?(.*)$") {
        $memo = $matches[1]
      }
      $memo = $memo.Trim()

      if ([string]::IsNullOrWhiteSpace($memo)) {
        # コメントが空なら末尾の「 - 」を出さない
        $line = "{0}  {1,-7}  - Restore Point {2}" -f $ts, $hash, $ref
      } else {
        $line = "{0}  {1,-7}  - Restore Point {2} - {3}" -f $ts, $hash, $ref, $memo
      }
      Write-Host $line

    }
  }

  Wait-AnyKey
  exit 0
}
catch {
  Halt ("Unhandled error: {0}" -f $_.Exception.Message)
}
