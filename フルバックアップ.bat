:: path: .\git_full_backup.bat
:: desc: クリック一発で git bundle によるフルバックアップを作成

@echo off
setlocal
set "ROOT=%~dp0"
set "PS1=%ROOT%scripts\git\git_full_backup.ps1"

where pwsh >nul 2>nul && set "PS=pwsh" || set "PS=powershell"
%PS% -NoProfile -ExecutionPolicy Bypass -File "%PS1%"

echo.
echo Done. (backup\git_full に .bundle / .json / .RESTORE.txt を作成)
echo.
pause
endlocal
