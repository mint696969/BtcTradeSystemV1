@echo off
setlocal EnableExtensions

REM === One-Click Handoff (stable quoting) ===
REM ダブルクリック実行。引数1はタグ用メモ（例: "nightly handoff"）

REM オプション
set "AUTO_RP=1"                 REM rp-* 自動タグ: 1=ON / 0=OFF
set "GIT_COMMITS=30"            REM 直近コミット出力数
set "INCLUDE_GIT_SCRIPTS=0"     REM scripts\git 同梱: 1=ON / 0=OFF
REM 監査スナップショット（audit_snapshot.txt）を同梱するか
set "INCLUDE_AUDIT_SNAPSHOT=1"     REM 1=ON / 0=OFF
REM GPT向けサイズ（KB）予算
set "GPT_BUDGET_KB=800"
REM テスト出力（TMPを削除せず中身を確認）: 1=ON / 0=OFF
set "TEST_OUTPUT=0"
REM 監査末尾の行数（make_handoff.ps1 の -AuditTail）
set "AUDIT_TAIL=200"

REM メモ（引数1で上書き）
set "RP_MEMO=%~1"
if "%RP_MEMO%"=="" set "RP_MEMO=handoff one-click"

REM ルート（このbatの場所 = リポジトリ直下）
set "ROOT=%~dp0"
REM PowerShellスクリプトは scripts\handoff\ 配下
set "PS1=%ROOT%scripts\handoff\make_handoff.ps1"

if not exist "%PS1%" (
  echo [ERROR] not found: "%PS1%"
  pause
  exit /b 1
)

REM 実行シェル: pwsh があれば優先、無ければ従来の powershell
set "PS=powershell"
where pwsh >nul 2>nul && set "PS=pwsh"

REM 条件付きスイッチを分離して組み立て
set "ARG_AUTORP="
if "%AUTO_RP%"=="1" set "ARG_AUTORP=-AutoRpTag"

set "ARG_GITSCRIPTS="
if "%INCLUDE_GIT_SCRIPTS%"=="1" set "ARG_GITSCRIPTS=-IncludeGitScripts"

set "ARG_AUDITSNAP="
if "%INCLUDE_AUDIT_SNAPSHOT%"=="1" set "ARG_AUDITSNAP=-IncludeAuditSnapshot"

set "ARG_TESTOUT="
if "%TEST_OUTPUT%"=="1" set "ARG_TESTOUT=-TestOutput"

echo.
echo.
echo [Handoff] %PS% -NoProfile -ExecutionPolicy Bypass -File "%PS1%" ^
 %ARG_AUTORP% -RpMemo "%RP_MEMO%" %ARG_GITSCRIPTS% -GitCommits %GIT_COMMITS% ^
 %ARG_AUDITSNAP% -GptBudgetKB %GPT_BUDGET_KB% -AuditTail %AUDIT_TAIL% %ARG_TESTOUT%
echo.

pushd "%ROOT%"

%PS% -NoProfile -ExecutionPolicy Bypass -File "%PS1%" ^
  %ARG_AUTORP% -RpMemo "%RP_MEMO%" %ARG_GITSCRIPTS% -GitCommits %GIT_COMMITS% ^
  %ARG_AUDITSNAP% -GptBudgetKB %GPT_BUDGET_KB% -AuditTail %AUDIT_TAIL% %ARG_TESTOUT%

set "RC=%ERRORLEVEL%"
popd

if "%RC%"=="0" (
  echo.
  echo [OK] handoff completed. ZIP was created under docs\handoff (or tmp when TEST_OUTPUT=1).
) else (
  echo.
  echo [ERROR] handoff failed. RC=%RC%
)

echo.
echo (完了していれば「OK: ...CTX-YYYYMMDD_HHMM.zip」が PowerShell 側で表示されます)
echo.
pause
endlocal
exit /b %RC%
