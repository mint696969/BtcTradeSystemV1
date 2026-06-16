# path: ./archive/phase25_thread_l4_widget_bundle_README.md
# desc: Archived note, specification, report, or reference document.

# THREAD L4 / WIDGET / CAPTION BUNDLE

この bundle は、このスレで進めた以下の期待動作を focused に確認するための専用テスト実行スクリプトです。

## 目的

- L4 shared -> operator_ui adapter -> widget model -> presenter/caption -> bridge の整合確認
- `market_summary` と `health_digest` の追加 field が末端まで到達していることの確認
- presenter / caption の additive line が期待文字列を返すことの確認
- `market_state_bridge` / `health_digest_bridge` で payload と widget が期待 key を返すことの確認

## 含む範囲

- `market_summary`
  - shared
  - adapter
  - presenter
  - bridge
  - service
- `health_digest`
  - shared
  - adapter
  - data_service
  - top/detail/chart caption
  - bridge
- `market_monitor_presenter`
  - このスレで触った軽量 presenter 系の回帰確認

## 実行方法

PowerShell で repo root から実行:

```powershell
powershell -ExecutionPolicy Bypass -File .\tmp\phase25_thread_l4_widget_bundle.ps1
```

## 成功条件

- compile group が全件成功
- test group が全件 `ok`
- 最後に `THREAD L4 / WIDGET / CAPTION BUNDLE OK` が表示される

## 失敗時の見方

- `compile::...` は構文/参照崩れ
- `test::...` は期待動作の崩れ
- `FAILED ITEMS:` に失敗した相対パスが出るので、そのファイルだけ局所修正すればよいです
