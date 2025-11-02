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

## 追記情報

① いまの実装（完成状態）と最初の合意仕様の差分

結論：ほぼ合意仕様どおりです。実装上の“キー”と“責務の分担”を明示します。

モーダルの上部ボタン（閉じる／デフォルト／保存）

表示は features/settings/settings.py 内のトップバーで描画。

どのタブでも共通ボタンを押すが、実処理は「アクティブなタブのモジュール」に委譲。

現状タブ「初期設定」は features/settings/set_main.py が担当。

set_main.py は on_default()（既定適用）と on_save()（保存）のハンドラ関数を公開。

「デフォルト」ボタンの活性/非活性判定は そのタブの“既定ファイルが存在するか” で決める。

いまは settings_svc.has_default() → config/ui/basic_def.yaml の存在チェック。

モーダルのタブ切替・再入（初期タブ記憶）

最後に開いたタブは st.session_state["__settings_last_tab"] に保存。

歯車から再度開くときはここを読んで同じタブから復元。

デモアラートのチェック（“1 回ズレ”はロールバック前に解消済み）

set_main.py 内でチェック ON/OFF のその場反映を実装。

UI からの変更で st.session_state["__settings_dirty"] = True を立て、必要時 st.rerun()。

カラーパレット（今回のみ反映／デフォルト／保存）

UI 編集はセッション上の作業コピーで持ち、

「デフォルト」＝ basic_def.yaml を読んで作業コピーに反映（ファイルは書き換えない）

「保存」＝ basic.yaml へ書き出し（safe/atomic）

保存処理は features/settings/settings_svc.py の save_palette() で tmp→ 置換のアトミック書込。

YAML の実体

既定：btc_trade_system/config/ui/basic_def.yaml

保存先：btc_trade_system/config/ui/basic.yaml

※今回は main.yaml への改名は撤回（ロールバック）なので参照は basic 系で統一。

② 新しい「機能タブ」を追加する手順（完全版）

追加は 3 点セットで考えると安全・速いです。

2-A. 設定モーダルの新タブ（例：キー名 "alerts"）を足す

モジュールを作成
btc_trade_system/features/settings/set_alerts.py（新規）

必須：render()（タブの UI 本体）、on_default()、on_save() の 3 関数

任意：supports_default()（デフォルトが無いタブは False を返す）

# path: btc_trade_system/features/settings/set_alerts.py

# desc: 設定モーダル「監査/アラート」タブの UI と処理フック

from **future** import annotations
import streamlit as st
from . import settings_svc as svc # 既存の I/O ヘルパを流用

TAB_KEY = "alerts" # ← settings.py 側と合わせる

def supports_default() -> bool: # 既定ファイルを持たないタブは False を返す
return False

def render():
st.subheader("監査/アラート 設定") # 例）閾値入力など
warn = st.number_input("WARN 閾値", min_value=0, value=10, key=f"{TAB_KEY}\_warn")
crit = st.number_input("CRIT 閾値", min_value=0, value=50, key=f"{TAB_KEY}\_crit") # UI で値が動いたらダーティフラグ
if st.session_state.get("**settings_open"):
st.session_state["**settings_dirty"] = True

def on_default(): # 既定なし → 何もしない（トーストだけ）
st.toast("このタブは既定値がありません。", icon="ℹ️")

def on_save(): # 例）svc.save_alerts() を実装して保存（下の 2-C 参照）
data = dict(
warn=st.session_state.get(f"{TAB_KEY}\_warn"),
crit=st.session_state.get(f"{TAB_KEY}\_crit"),
)
svc.save_alerts(data) # 新規 I/O を自作
st.toast("保存しました。", icon="✅")

ハブへ登録
features/settings/settings.py（既存）に インポートとタブ登録を追加。
（キャンバスの現行コードに合わせて、該当箇所へ“キーとタイトル”を 1 行追加）

# settings.py（該当ブロック）

from . import set_main
from . import set_health
from . import set_audit
from . import set_alerts # ← 追加

TABS = {
"main": ("初期設定", set_main),
"health": ("健全性", set_health),
"audit": ("監査", set_audit),
"alerts": ("アラート", set_alerts), # ← 追加
}

以降は 共通トップバーが自動で
TABS[active_key][1].on_default() / .on_save() を呼びます。
supports_default() があれば、それを使って「デフォルト」ボタンの活性状態も自動制御されます（無ければ True とみなす → 必要なら False を返す関数を用意）。

2-B. ダッシュボード側（タブ一覧の見出し）に“説明導線”を足す場合

既存の薄い入口は features/dash/ui_settings.py。
新タブの説明やショートカットを足したい場合は、ここに説明テキストとボタンを追加し、
押下で st.session_state["__settings_open"]=True と \_\_settings_last_tab="alerts" をセットします。

# ui_settings.py（既存の render() 内で）

if st.button("アラート設定を開く", use_container_width=True):
st.session_state["__settings_open"] = True
st.session_state["__settings_last_tab"] = "alerts"
st.toast("設定 → アラート タブを開きます。", icon="ℹ️")

2-C. 設定ファイルへの I/O が必要なら settings_svc.py に“薄い関数”を追加

既存の save_palette() と同じ書式で、小粒のヘルパを生やします。

例：config/ui/alerts.yaml に保存したい場合

# settings_svc.py（末尾などに追加）

from pathlib import Path
import json, os, tempfile
import yaml # 既存の import に揃える

UI_DIR = REPO_ROOT / "btc_trade_system" / "config" / "ui"
ALERTS_PATH = UI_DIR / "alerts.yaml"

def save_alerts(data: dict):
UI_DIR.mkdir(parents=True, exist_ok=True)
tmp = ALERTS_PATH.with_suffix(".yaml.tmp")
with open(tmp, "w", encoding="utf-8") as f:
yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
os.replace(tmp, ALERTS_PATH)

def load_alerts() -> dict:
if ALERTS_PATH.exists():
with open(ALERTS_PATH, "r", encoding="utf-8") as f:
return yaml.safe_load(f) or {}
return {}

これで set_alerts.py から svc.save_alerts() / svc.load_alerts() を呼べます。
既定ファイルを持たせたい場合は alerts_def.yaml を用意し、
supports_default() で alerts_def.yaml の存在を見て True/False を返せば OK。

付録：実務メモ（壊さないための“型”）

各タブは最小 3 関数

render()：UI 描画（ここで session_state を読んで編集し、dirty を立てる）

on_default()：既定適用（既定ファイルが無いならトーストで終了）

on_save()：保存（atomic 書込。保存後は st.rerun() で即反映）

supports_default()：既定ファイル有無を返す（無いタブは False）

トップバーは一切ロジックを持たない

アクティブタブのモジュールに委譲するだけ（＝壊れにくい）

I/O は settings_svc.py に寄せる

1 タブ 1 ファイルを基本に、\*\_def.yaml を用意するかどうかで
「デフォルト」ボタンの有無（活性/非活性）を決める
