📘 BtcTradeSystemV1 新機能追加マニュアル GPT 統一版

ver. 2.0 — 2025-11-08 制定

🎯 目的

BtcTradeSystem V1 に新しい機能を追加する際、GPT が迷わず・破壊せず・一貫した構造で拡張できるようにする。
このマニュアル以外のルールは不要。以後すべての機能追加は本規約に従う。

🧩 基本原則

1 機能＝ 1 フォルダ構成
features/<key>/ 以下に必要なファイルを配置。

tabs.yaml が唯一の情報源
ダッシュボード／設定の表示・順序・有効状態は全てここで制御。

def/current 方式

既定値：features/<key>/config/<key>\_def.yaml

実値：CONFIG_DIR/ui/<key>.yaml（なければ初回保存で自動生成）

設定モーダルは折りたたみ式・セクション単位保存

展開 1 つ、他は自動折りたたみ。

保存／デフォルトのみ確認ダイアログ。

折りたたみ・閉じる・タブ移動時は未保存破棄。

監査は SVC 一元

settings.write.<key> / settings.default.apply.<key> / settings.write.error.<key> 等。

UI はクリックイベントのみ（例：settings.save_click.<key>）。

コード提出ルール

1 ファイル 1 キャンバス。

新規ファイルの先頭 2 行にコメントを必ず記載：

# path: ./btc*trade_system/features/<key>/set*<key>.py

# desc: <簡潔な説明>

コード指示は以下の形式：

① 追加 / ② 差し替え / ③ 削除
対象ファイル
指標コード行 or 範囲
コピペ可能な修正コード
🧱 構成テンプレート
btc*trade_system/
features/
<key>/
ui*<key>.py # ダッシュボード UI（任意）
set*<key>.py # 設定セクション UI（必須）
svc*<key>.py # I/O・処理ロジック（任意）
config/
<key>\_def.yaml # 既定値ファイル（必須）
schema.yaml # スキーマ（任意）
🗂️ tabs.yaml 追記例

- key: collector
  label: "コレクター"
  has_dashboard: true
  has_settings: true
  order: 30
  enabled: true

order 体系

0：main（固定）

10–180：可変（通常機能）

190：exchanges（取引所登録）

200：basic（初期設定）

has_dashboard / has_settings で表示先を制御。

module / settings_module は命名規約で自動解決するため省略可。

🧩 set\_.py の雛形

# path: ./btc*trade_system/features/settings/set*<key>.py

# desc: <key> の設定セクション UI（折りたたみ式）

import streamlit as st
from btc_trade_system.features.settings import settings_svc as svc

def render():
st.subheader("<ラベル>")
cfg = svc.load*yaml("<key>") # ← cfg は def ＋ current 合成済み
st.text_input("項目 A", value=cfg["項目 A"], key="set.<key>.A")
...
col1, col2, col3 = st.columns([1,1,1])
if col1.button("閉じる", key="close*<key>"):
st.session*state.pop(f"set.<key>", None)
if col2.button("デフォルト", key="default*<key>"):
svc.reset*to_default("<key>")
if col3.button("保存", key="save*<key>"):
new*data = {...} # UI 値収集
svc.save_yaml("<key>", new_data)
🧰 svc*.py の最小構成

# path: ./btc*trade_system/features/<key>/svc*<key>.py

# desc: <key> 設定の入出力処理（def/current 統合＋監査 emit）

from btc_trade_system.features.audit_dev import writer as W
from btc_trade_system.features.settings import settings_svc as base

def load_yaml():
return base.load_yaml("<key>")

def save_yaml(data):
base.save_yaml("<key>", data)
W.emit(f"settings.write.<key>", level="INFO", feature="<key>", payload={"changed_keys": list(data.keys())})
🧮 config/\_def.yaml の雛形
schema_rev: 1
項目 A: 100
項目 B: true
項目 C: "default text"
⚙️ 設定モーダル動作仕様（v2 確定版）

初期状態：最上部の basic セクションのみ展開。

折りたたみ／タブ移動／閉じる：未保存の変更は即時破棄（確認なし）。

保存／デフォルト：確認モーダル 1 段 → 実行。

ボタン：「閉じる／デフォルト／保存」をセクション最下部に配置。

一括保存は廃止。

監査：SVC が一元発火。

current 不在：初回保存で自動生成。

ロック：キー単位で .lock 管理。

保存形式：.tmp → fsync → replace。

config 読込先：ENV（BTC_TS_CONFIG_DIR）優先。なければ <repo>/data/config を自動生成。

🔍 新機能追加フローチャート

1️⃣ 新フォルダ作成 → features/<key>/
2️⃣ ui*<key>.py（任意）・set*<key>.py（必須）を作成
3️⃣ config/<key>\_def.yaml を作成
4️⃣ tabs.yaml に <key> を追記
5️⃣ 起動・タブ表示を確認
6️⃣ 設定変更 → 保存 → 再読込動作を確認
7️⃣ dev_audit.jsonl に settings.write.<key> が記録されていれば完了

✅ チェックリスト（出荷前）

🧾 付録：PowerShell チェックワンライナー
tabs.yaml 構文整合
$tabs=(Get-Content .\btc_trade_system\config\ui\tabs.yaml -Raw|ConvertFrom-Yaml)
$tabs.dashboard|Group-Object order|?{$_.Count -gt 1}
モジュール存在確認
$py=".\\.venv\\Scripts\\python.exe"; if(-not(Test-Path $py)){$py="python"}
$code=@'
import importlib,yaml
cfg=yaml.safe_load(open("btc_trade_system/config/ui/tabs.yaml",encoding="utf-8"))
for sect in ("dashboard","settings"):
  for it in cfg.get(sect,[]):
    m,v=it.get("module"),"render"
    try: getattr(importlib.import_module(m),v)
    except Exception as e: print("FAIL",sect,it["key"],e)
'@
$code|&$py -

---

付録: set\_**\***.py の末尾ボタン実装（統一規約）

対象: 設定タブ内の各機能セクション（例: set_health.py, set_collector.py, set_dash.py）
目的: 「閉じる／デフォルト／保存」ボタン＋確認ダイアログ＋即時反映（rerun）を共通モジュールで統一

1. 前提

共通 UI: btc_trade_system/features/settings/ui_common.py （UI.render_section_controls を使用）

セッションキーは set.<key>._ に統一
例: basic → set.basic._, health → set.health._, collector → set.collector._

一時値（未保存の入力値）は set.<key>.pending に集約

保存/デフォルト後は dirty フラグ＋ rerun によりダッシュボードへ即時反映

2. 実装手順（最小手順）

冒頭 import を追加

from btc_trade_system.features.settings import ui_common as UI

render() 内で実行ハンドラを定義

デフォルト適用時の処理（サービス層へ委譲）

保存時の処理（pending の取り出し →svc の保存関数）

セクション末尾に 共通フッター を 1 行で描画

UI.render_section_controls(
prefix="set.<key>", # 例: "set.basic", "set.health", "set.collector"
on_default=\_exec_default, # 実行ハンドラ（定義が無ければ None）
on_save=\_exec_save, # 実行ハンドラ（定義が無ければ None）
key_base="set.<key>.btn", # 例: "set.basic.btn"
labels=("閉じる","デフォルト","保存"),
confirm_message="◯◯ 設定を更新します。よろしいですか？"
)

既存の個別ボタン実装（st.button("閉じる") など）は削除（重複回避）

3. テンプレート（貼り替え用）

新規 set\_<key>.py を作る場合、以下を「render() の末尾」に挿入（ハンドラは上に定義）

# 実行ハンドラ（例）

def \_exec_default(): # 必要に応じて複数領域を既定化 # 例: settings_svc.reset_to_default("<area>")
pass

def \_exec_save(): # pending から値を取得して保存
values = st.session_state.get("set.<key>.pending")
if values is None:
st.toast("変更はありませんでした", icon="ℹ️")
return # 例: settings_svc.save_yaml("<area>", values) / 独自 commit(values)
pass

# 共通フッター

UI.render_section_controls(
prefix="set.<key>",
on_default=\_exec_default,
on_save=\_exec_save,
key_base="set.<key>.btn",
labels=("閉じる","デフォルト","保存"),
confirm_message="◯◯ 設定を更新します。よろしいですか？"
)

4. 具体例（抜粋）

basic（初期設定配色）:

prefix="set.basic"

\_exec_default() → settings_svc.reset_to_default("dash")

\_exec_save() → settings_svc.save_palette(palette_dict)

health:

prefix="set.health"

\_exec_default() → settings_svc.reset_to_default("health") と ("monitoring")

\_exec_save() → 既存 apply_pending()（health/monitoring 同時保存）

collector:

prefix="set.collector"

\_exec_default() → endpoints を“空定義”で保存（事故防止のため確認ダイアログ必須）

\_exec_save() → 既存 commit(values)（UI 順序を正としてそのまま保存）

5. 実装上の注意

pending の積み方: UI 入力の集約点で

st.session_state["set.<key>.pending"] = merged_values_dict

としておく（タブ切替＝未保存破棄はハブ側が set.<key>.\* を消す）

閉じる: 共通 UI が \_\_settings_open=False 設定 →set.<key>.\* 破棄 →st.rerun() を自動実行

確認ダイアログ: 共通 UI が「押下 → 確認 → 実行/キャンセル」の 2 段階を提供

即時反映: 実行後に dirty ＋ rerun を共通 UI が行うため、保存直後に UI へ反映

命名: prefix と key_base は必ず一致する階層に（例: set.health と set.health.btn）

不要コード: 旧「上部ボタン」系フック（on_save/on_default など）は撤去する

6. 検収チェックリスト

セッションキーが set.<key>.\* に統一されている

set.<key>.pending に未保存値が集約される

共通フッターで「閉じる／デフォルト／保存」が表示され、確認ダイアログを経由

保存直後にダッシュへ即時反映（色・タブ・表示の変化がすぐ出る）

タブ切替で未保存入力が破棄される

監査ログ（設定書込・デフォルト適用）が出る
