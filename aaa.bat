:: path: .\git_rp_make_diff.bat
:: desc: クリック一発で差分バックアップ付き復元ポイント作成（rp-タグ＋ZIP差分）

@echo off
setlocal

REM ルート直下で実行される前提。場所に自信がない場合はこの行でルートへ移動:
pushd "%~dp0"

set "PS1=.\scripts\git\git_rp_make.ps1"

REM pwsh 優先、なければ Windows PowerShell
where pwsh >nul 2>nul
if %ERRORLEVEL%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Diff
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Diff
)

REM ps1 側で「Press any key...」を出すが、保険で pause も可
REM pause

popd
endlocal
