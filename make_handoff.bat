@echo off
setlocal EnableExtensions

REM === One-Click Handoff (safe & simple) ===
REM ルート直下に置いてダブルクリックで実行
REM 引数1つ目はタグ用メモ（例: make_handoff.bat "nightly handoff"）

REM オプション
set "AUTO_RP=1"
REM rp-* 自動タグ: 1=ON / 0=OFF

set "GIT_COMMITS=30"
REM 直近コミット出力数

set "INCLUDE_GIT_SCRIPTS=0"
REM scripts\git 同梱: 1=ON / 0=OFF

REM メモ（引数1で上書き）
set "RP_MEMO=%~1"
if "%RP_MEMO%"=="" set "RP_MEMO=handoff one-click"

REM ルート（このbatの場所）
set "ROOT=%~dp0"

REM ps1 を -File で直接実行
set "PS1=%ROOT%scripts\handoff\make_handoff.ps1"

set "ARGS="
if "%AUTO_RP%"=="1" set "ARGS=%ARGS% -AutoRpTag -RpMemo \"%RP_MEMO%\""
if "%INCLUDE_GIT_SCRIPTS%"=="1" set "ARGS=%ARGS% -IncludeGitScripts"
set "ARGS=%ARGS% -GitCommits %GIT_COMMITS%"

echo.
echo [Handoff] %PS1% %ARGS%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %ARGS%

echo.
echo (完了していれば「OK: ...Handoff_YYYYMMDD_HHMM.zip」が表示されます)
echo.
pause
endlocal
