# path: ./archive/phase25_thread_operator_ui_regression_2026-04-14_README.md
# desc: Archived note, specification, report, or reference document.

# phase25_thread_operator_ui_regression_2026-04-14

## 目的
このスレで進めた `operator_ui` 周辺の実装束について、`py_compile` と focused tests をまとめて実行する回帰確認用 PowerShell スクリプトです。

## 含めている範囲
- health 系の focused tests 一式（このスレで繰り返し green を取ったもの）
- market monitor / market state bridge の focused tests
- market signal shared owner と typed contract 波及先の state/adopter tests
- trade flow / liquidity pressure / warroom timeline の dedicated owner tests

## 実行方法
PowerShell で repo root から次を実行してください。

```powershell
powershell -ExecutionPolicy Bypass -File C:\BtcTradeSystem\tmp\phase25_thread_operator_ui_regression_2026-04-14.ps1
```

## 判定
- 全部 green の場合は `ALL GREEN` を表示して exit code 0
- 失敗が 1 件でもあれば失敗項目一覧を表示して exit code 1

## 使い方の意図
ここで fail が出たら、その fail を起点に修正へ戻る。
全部 green なら、この束は少なくとも focused regression 上は前進してよい、という判断に使う想定です。
