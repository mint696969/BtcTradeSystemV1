:: path: .\git_rp_make_diff.bat
:: desc: クリック一発で差分バックアップ付き復元ポイント作成（rp-タグ＋ZIP差分）

@echo off
setlocal
pushd "%~dp0"

set "PS1=.\scripts\git\git_rp_make.ps1"

:: メモ入力（空でもOK）
set "MEMO="
set /p MEMO=RestorePoint Memo (optional): 

:: pwsh 優先、なければ Windows PowerShell
where pwsh >nul 2>nul
if %ERRORLEVEL%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Commit -Diff -Zip -RpMemo "%MEMO%"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Commit -Diff -Zip -RpMemo "%MEMO%"
)

popd
endlocal
