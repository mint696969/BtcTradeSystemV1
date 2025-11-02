# ダッシュボード\_アラート仕様書 vFinal（2025-11-01）

## 1. 目的 / スコープ

- 運用時の異常（レート制御・到達不能・板消失・急変など）を **ヘッダー右スロット**のチップで即時可視化。
- 開発時の警告は **左スロット（将来）** に分離（現在は未表示。必要時のみ表示）。
- クリック導線で **health（運用）/ audit（開発）** へ遷移できること。

## 2. 配置 / ファイル

- `btc_trade_system/features/dash/dashboard.py` … ヘッダー＆タブのハブ。
- `btc_trade_system/features/dash/styles/dashboard_header.css` … 見た目（チップ色/余白/行高）。
- 配色：`settings.get_alert_palette()` の戻り値を `:root` CSS 変数へ注入（`_inject_alert_palette_vars`）。

## 3. ヘッダー構造

- タイトル列 / チップ列 / ⚙️ 設定ギア。チップが 0 件なら **2 カラム**（タイトル/⚙️）。
- チップは最大 3 件 + `+n` 表示。重要度優先（`urgent > crit > warn`）。
- **詳細** ボタンをチップ列の直下に配置（最小差分）→ `_jump_health()` で health へ遷移。

## 4. 監査語彙（dev_audit.jsonl）

- タブ登録：`dash.tab.register` … payload: `{key, title}`（UI 表示候補の全件）
- タブ切替：`dash.tab.open` … payload: `{key, title}`（アクティブ＝並び先頭）
- 設定モーダル：`settings.open / settings.save_click / settings.close`（modal 入口で発火）

## 5. 遷移仕様

- 運用チップ（右スロット） → `health`（`st.session_state["active_tab"] = "health"; st.rerun()`）
- 開発チップ（左スロット：将来） → `audit`
- **tabs.yaml 初期タブより** `session_state.active_tab` を優先して並び替え（`preferred`）。

## 6. 設計ポリシー

- 見た目は CSS に委譲。Python 側は `:root` 変数注入のみ。
- チップは HTML スパン描画（クリック不可）。導線は最小差分で **直下のボタン**を使う。
- デモアラートは `?demo_alerts=1` または `st.session_state["demo_alerts"]` で有効化。

## 7. DoD（完了定義）

- WhatIf でヘッダー描画がエラーなく通る。
- 通常起動で `dash.tab.register / dash.tab.open / settings.*` が JSONL に出る。
- チップ 0 件時に余白が空かない（2 カラム動作）。

---

### Appendix A: 拡張点（将来）

- 左スロット Dev バッジ + `_jump_audit()` 実装。
- `tabs.yaml` に `module` 指定を許容し、`dashboard.py` で動的 import（登録不要化）。

### 追記情報

ダッシュボードのアラートチップへ“信号を出す”方法

完成状態のコードでは以下の契約で動いています（今回の zip で確認）：

表示側（ダッシュボード・ヘッダ）
dashboard.py のヘッダ描画で
\_\_render_alert_chips(alerts) のように alerts 配列を読み込んで表示。

設定側（set_main.py）
デモアラートのチェック ON/OFF や色変更など、
UI 操作時に st.session_state["_alerts"] を組み立てて格納しています。
その後 st.session_state["__settings_dirty"] = True を付けて、必要時に st.rerun()。

チップデータの形（概形）

st.session_state["_alerts"] = [
{"level": "urgent", "label": "緊急 Y", "fg": "#000000", "bg": "#FF6666"},
{"level": "critical", "label": "重大 X", "fg": "#000000", "bg": "#FFCCCC"},
{"level": "warn", "label": "注意 A", "fg": "#000000", "bg": "#FFF2CC"},
# 省略…
]

※ level/label/fg/bg は既存 UI に合わせる。カウントなどを足す場合は
{"count": 3} のように属性追加しても良い（描画側に反映が必要）。

新タブからアラートを出したいときは、
同じく st.session_state["_alerts"] を置き換えまたは追記してください。
（例：監視タブで閾値を超えたときに warn を追加…など）

alerts = st.session_state.get("\_alerts", [])
alerts.append({"level": "warn", "label": "しきい値超え", "fg": "#000", "bg": "#FFF2CC"})
st.session_state["_alerts"] = alerts
st.session_state["__settings_dirty"] = True
