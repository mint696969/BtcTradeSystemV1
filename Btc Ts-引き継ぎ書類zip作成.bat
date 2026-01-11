@echo off
setlocal EnableExtensions

REM === One-Click Handoff ===
REM usage:
REM   cmd /c ".\Btc Ts-引き継ぎ書類zip作成.bat" "memo text"

set "REPO=%~dp0"
set "PS=pwsh"
set "PS1=%REPO%scripts\handoff\make_handoff.ps1"

set "AUTO_RP=1"
set "GIT_COMMITS=30"

set "RP_MEMO=%~1"
if "%RP_MEMO%"=="" set "RP_MEMO=handoff one-click"

set "ARG_AUTORP="
if "%AUTO_RP%"=="1" set "ARG_AUTORP=-AutoRpTag"

echo.
echo [Handoff] %PS% -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %ARG_AUTORP% -RpMemo "%RP_MEMO%" -GitCommits %GIT_COMMITS%
echo.

%PS% -NoProfile -ExecutionPolicy Bypass -File "%PS1%" ^
  %ARG_AUTORP% -RpMemo "%RP_MEMO%" -GitCommits %GIT_COMMITS%

echo.
echo (OK: ...\tmp\handoff\CTX-YYYYMMDD_HHMMSS.zip が表示されれば成功)
echo.
pause
endlocal
