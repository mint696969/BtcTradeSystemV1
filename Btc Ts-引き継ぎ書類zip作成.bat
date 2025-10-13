@echo off
setlocal EnableExtensions

REM === One-Click Handoff (stable quoting) ===
REM ダブルクリック実行。引数1はタグ用メモ（例: "nightly handoff"）

REM オプション
set "AUTO_RP=1"                 REM rp-* 自動タグ: 1=ON / 0=OFF
set "GIT_COMMITS=30"            REM 直近コミット出力数
set "INCLUDE_GIT_SCRIPTS=0"     REM scripts\git 同梱: 1=ON / 0=OFF

REM メモ（引数1で上書き）
set "RP_MEMO=%~1"
if "%RP_MEMO%"=="" set "RP_MEMO=handoff one-click"

REM ルート（このbatの場所）
set "ROOT=%~dp0"
set "PS1=%ROOT%scripts\handoff\make_handoff.ps1"

REM 条件付きスイッチを分離して組み立て
set "ARG_AUTORP="
if "%AUTO_RP%"=="1" set "ARG_AUTORP=-AutoRpTag"

set "ARG_GITSCRIPTS="
if "%INCLUDE_GIT_SCRIPTS%"=="1" set "ARG_GITSCRIPTS=-IncludeGitScripts"

echo.
echo [Handoff] %PS1% %ARG_AUTORP% -RpMemo "%RP_MEMO%" %ARG_GITSCRIPTS% -GitCommits %GIT_COMMITS%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" ^
  %ARG_AUTORP% -RpMemo "%RP_MEMO%" %ARG_GITSCRIPTS% -GitCommits %GIT_COMMITS%

echo.
echo (完了していれば「OK: ...Handoff_YYYYMMDD_HHMM.zip」が表示されます)
echo.
pause
endlocal
