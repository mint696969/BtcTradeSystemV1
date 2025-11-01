# ダッシュボード\_設定とタブ追加仕様書 vFinal（2025-11-01）

## 1. 目的 / スコープ

- 設定の入口とタブ追加手順を **GPT が迷わず実装できる粒度**で固定化。
- 将来の設定タブは `set_*****.py` 命名に統一。

## 2. 配置 / 役割

- **設定ハブ**：`btc_trade_system/features/settings/settings.py`

  - 入口 `settings_gear()`（ダイアログ優先、古い環境はサイドバーにフォールバック）。
  - タブ配列：`["初期設定", "健全性", "監査"]`。
  - 呼び出し：`set_main.render()` / `set_health.render()`。

- **初期設定タブ**：`btc_trade_system/features/settings/set_main.py`（I/F: `render()`）

  - 配色ピッカー、**今回のみ適用**、**デフォルト復元**、**保存（basic.yaml へ alert_palette）**。
  - 監査：`settings.apply_once / settings.restore_default / settings.save_click`。
  - I/O：`settings_svc.load_yaml` / `settings_svc.write_atomic` を必須使用。

- **健全性タブ**：`btc_trade_system/features/settings/set_health.py`（I/F: `render()`）

  - 説明・SLO ガイド・編集 UI（保存がある場合も `settings_svc` 経由）。

- **サービス層**：`btc_trade_system/features/settings/settings_svc.py`

  - YAML の安全読み書き、アトミック置換、既定値ロード。

## 3. 命名規則（決定）

- 設定タブ：`features/settings/set_*****.py`（例：`set_orders.py`、`set_alerts.py`）。
- ダッシュボード UI：`features/dash/ui_*****.py`（例：`ui_orders.py`）。

## 4. タブ追加（ダッシュボード）

1. `btc_trade_system/config/ui/tabs.yaml` に key を追加（`order/ enabled / initial`）。
2. `features/dash/ui_<key>.py` に `render()` を実装。
3. `dashboard.py` は **動的解決**で `btc_trade_system.features.dash.ui_<key>` を import して `render()` を起動（`_resolve_tab_module`）。

> ※現行は登録不要。将来 `module` 指定を tabs.yaml へ拡張する場合は importlib で上書き。

## 5. 監査／UI 連携

- タブ登録：`dash.tab.register`（表示対象分を全列挙）。
- タブ切替：`dash.tab.open`（アクティブ＝先頭）。
- 設定モーダル：`settings.open / settings.save_click / settings.close`。
- 遷移：`st.session_state["active_tab"]` を優先（`preferred`）→ 並び先頭に移動。

## 6. DoD（完了定義）

- WhatIf で依存無しに通る（import/パスエラーゼロ）。
- 通常起動で設定モーダルが表示され、`set_main` の 3 操作が動作。
- `dev_audit.jsonl` に `settings.* / dash.tab.*` が記録される。

---

### Appendix A: サンプル・スニペット

- 保存（basic.yaml：`alert_palette`）

```python
basic = settings_svc.load_yaml("basic.yaml") or {}
basic["alert_palette"] = pal_save
settings_svc.write_atomic("basic.yaml", yaml.safe_dump(basic, allow_unicode=True))
W.emit("settings.save_click", level="INFO", feature="settings", payload={"file":"basic.yaml","keys":["alert_palette"]})
```
