# desc: 復元ポイントからブランチを作って切り替え

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repo

Write-Host "== Restore Points (latest 20) ==" -ForegroundColor Cyan
$tags = (git tag --list "rp-*" --sort=-creatordate)
if (-not $tags) {
  Write-Host "（まだありません）"
} else {
  foreach ($t in ($tags | Select-Object -First 20)) {
    $msg = (git show -s --format="%ci %H %s" $t)
    Write-Host $msg
  }
}
Write-Host ""
Read-Host "Press Enter to exit..."
