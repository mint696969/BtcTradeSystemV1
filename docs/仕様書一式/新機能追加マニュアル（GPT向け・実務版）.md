新機能追加マニュアル（GPT 向け・実務版）

リポジトリ前提：C:\Users\mint777\BtcTradeSystemV1（以降「repo」）
既存基盤：features/dash/dashboard.py（タブハブ）、features/settings/settings.py（設定ハブ）、features/settings/settings*svc.py（設定 I/O）。
コンフィグ方針 A：current YAML はリポ内 btc_trade_system/config/ui/*.yaml に保存し、\_\_def.yaml（既定）は追跡し、\*.yaml（current）は .gitignore 済み。

0. 命名・配置の絶対ルール

1 機能 = 1 ディレクトリ（例：btc_trade_system/features/<key>/）

ダッシュボードの各タブ UI は features/dash/ui\_<key>.py に置く

ダッシュボードは自動で ui\_<key>.py を import し、render() を呼ぶ

render() は 必須

機能の既定設定は features/<key>/config/<key>\_def.yaml

上書き保存（current）は config/ui/<key>.yaml に自動生成（settings_svc.save_yaml()）

タブの並び・有効化は config/ui/tabs.yaml（なければ tabs_def.yaml が既定）

予約キー：main=0（メイン）、基本設定はダッシュボードのタブを作らず 設定側で右端に置く（キー：basic などを後述の設定ハブで制御）

1. 新しい機能タブを追加する手順（例：signals）
   1-1. 既定設定（任意）

# path: btc_trade_system/features/signals/config/signals_def.yaml

schema_rev: 1
enabled: true
thresholds:
buy: 0.7
sell: 0.7

1-2. タブ登録（並び・有効化）

# path: btc_trade_system/config/ui/tabs.yaml

order: [main, health, audit, signals] # 並びに signals を追加
enabled:
signals: true
initial: main

1-3. タブ UI 本体

# path: btc_trade_system/features/dash/ui_signals.py

# desc: 「signals」タブの UI。dashboard が render() を呼ぶ。

import streamlit as st
from btc_trade_system.features.settings import settings_svc as S

def render():
cfg = S.load_yaml("signals") # def + current（current 優先）の浅いマージ
st.subheader("🚦 シグナル")
st.write({k: cfg.get(k) for k in ("enabled","thresholds")}) # …ここに表やグラフ、操作などを実装…

1-4. 動作チェック（ワンライナー）
$py = ".\.venv\Scripts\python.exe"; if(-not(Test-Path $py)){ $py="python" }
@'
import importlib
m = importlib.import*module("btc_trade_system.features.dash.dashboard")
cfg = m.\_load_tabs_cfg()
print("ORDER =", cfg["order"])
print("ENABLED =", [k for k,v in cfg["enabled"].items() if v])
for k in ["main","health","audit","signals"]:
name=f"btc_trade_system.features.dash.ui*{k}"
try: importlib.import_module(name); print("OK", name)
except Exception as e: print("NG", name, e.**class**.**name**)
'@ | & $py -

2. 機能別の「設定タブ」を追加する（設定モーダル内）

設定ハブ：features/settings/settings.py（既存）。
方式：薄いハブに“機能の設定パネル”をぶら下げる。
例として signals の設定パネルを作る。

2-1. 設定パネル（機能側）

# path: btc_trade_system/features/signals/settings_panel.py

# desc: 設定モーダル内の「signals」タブの UI 部品

import streamlit as st
from btc_trade_system.features.settings import settings_svc as S

KEY = "signals"

def render_settings():
st.write("⚙️ シグナル設定")
cfg = S.load_yaml(KEY)
col1, col2 = st.columns([1,1], gap="small")
with col1:
en = st.toggle("有効化", value=bool(cfg.get("enabled", True)), key=f"{KEY}\_enabled")
with col2:
buy = st.number_input("買いしきい値", min_value=0.0, max_value=1.0,
value=float(cfg.get("thresholds",{}).get("buy",0.7)), step=0.05,
key=f"{KEY}\_th_buy")
sell = st.number_input("売りしきい値", min_value=0.0, max_value=1.0,
value=float(cfg.get("thresholds",{}).get("sell",0.7)), step=0.05,
key=f"{KEY}\_th_sell")

    if st.button("保存", type="primary", key=f"{KEY}_save"):
        new_cfg = S.load_yaml(KEY)  # def+current を再読込してから上書き
        new_cfg["enabled"] = en
        new_cfg.setdefault("thresholds",{})["buy"]  = buy
        new_cfg.setdefault("thresholds",{})["sell"] = sell
        S.save_yaml(KEY, new_cfg)
        st.success("保存しました（repo/config/ui/ へ current 反映済み）")

2-2. 設定ハブに“面”を登録（ここだけハブ側を追記）

# path: btc_trade_system/features/settings/settings.py

# 既存の設定タブ構築の中で signals を 1 面として追加（例）

from btc_trade_system.features.signals import settings_panel as signals_panel

# …既存の設定タブ配列に追加…

# tabs = st.tabs(["初期設定", "…", "signals"]) のような構成箇所で：

with tabs[<signals のインデックス>]:
signals_panel.render_settings()

メモ：将来は features 側から “登録フック” を自動探索する方式にも拡張可（現状は明示追記）。

3. ヘッダーの「アラート」を出す・消す

ダッシュボードのヘッダーは st.session_state["_alerts"] を見て、最大 3 個のチップを表示。
レベルは warn | crit | urgent。表示順は urgent > crit > warn。

3-1. 追加（どこからでも OK）
import streamlit as st

def add_alert(label: str, level: str = "warn"):
a = st.session_state.get("\_alerts", [])
a.append({"label": label, "level": level})
st.session_state["_alerts"] = a

# 例：新規データの異常検知時

add_alert("Bybit レート制限", "crit")
add_alert("OKX 接続不安定", "warn")

3-2. クリア（手動で）
st.session_state["_alerts"] = [] # 全消し

# or: st.session_state["_alerts"] = [x for x in st.session_state["_alerts"] if x["label"]!="…"]

既にダッシュボードは settings_svc.get_alert_palette() に従って配色を注入済み。
色の編集は「設定 → 初期設定（basic/dash）」から実施 → dash.yaml に保存。

4. 設定 I/O の使い方（共通ユーティリティ）
   from btc_trade_system.features.settings import settings_svc as S

# 読み（def + current の浅いマージ／current 優先）

cfg = S.load_yaml("<key>")

# 既定だけ

def_cfg = S.load_def_yaml("<key>")

# 保存（current を原子的更新）

S.save_yaml("<key>", cfg)

def 探索順：features/<key>/config/<key>\_def.yaml → config/ui/<key>\_def.yaml

current 保存先：config/ui/<key>.yaml（.gitignore 済み）

ダッシュボード配色：S.get_alert_palette()、一時適用：S.apply_palette_once()、既定復元：S.reset_palette_to_default()、永続保存：S.save_palette(picks)。

5. 最終チェック用ワンライナー

A. 構文＋インポート健全性

$py = ".\.venv\Scripts\python.exe"; if(-not(Test-Path $py)){ $py="python" }
@'
import compileall, importlib
ok = compileall.compile_dir(r".", quiet=1); print("COMPILE_OK=",bool(ok))
for m in [
"btc_trade_system.features.dash.dashboard",
"btc_trade_system.features.settings.settings",
"btc_trade_system.features.settings.settings_svc",
"btc_trade_system.features.dash.ui_main",
"btc_trade_system.features.dash.ui_health",
"btc_trade_system.features.dash.ui_audit",
"btc_trade_system.features.dash.ui_signals", # 追加タブ例
]:
try: importlib.import_module(m); print("IMPORT_OK", m)
except Exception as e: print("IMPORT_NG", m, e.**class**.**name**)
'@ | & $py -

B. タブ設定の最終合成

@'
import importlib
m = importlib.import_module("btc_trade_system.features.dash.dashboard")
c = m.\_load_tabs_cfg()
print("ORDER =", c["order"])
print("ENAB =", [k for k,v in c["enabled"].items() if v])
print("INIT =", c["initial"])
'@ | & $py -

6. 運用メモ（落とし穴回避）

ui\_<key>.py に 必ず render() を実装（無いと情報メッセージが出るだけで何も描画されない）

tabs.yaml の不整合（キー未実装・重複）は壊れないが紛らわしいので整理すること

_\_def.yaml は追跡対象、_.yaml（current）は追跡除外（誤コミット防止）

既定／current の検索ポリシーは settings_svc に統一（独自 I/O を作らない）

## 付録 A：以後の追加ルール（ゼロ改修で足すための超要点）

目的：新機能を追加しても dashboard.py と settings.py を原則いじらない。
追加は「機能フォルダ＋ tabs.yaml 記述」だけで完結させる。

A. ダッシュボードのタブ追加ルール

置き場所：btc*trade_system/features/dash/ui*<key>.py

必須：render() 関数（引数なしで OK）

タブ登録：btc_trade_system/config/ui/tabs.yaml に追記

order: [main, health, audit, <key>] # 並び順
enabled:
main: true
health: true
audit: true
<key>: true
initial: main

ラベル表記（設定モーダル側）：

既定は キー名そのまま（例: <key>）。

日本語表示にしたい場合だけ、features/settings/settings.py の \_LABELS に任意で追記（編集不要運用を優先するならスキップ可）。

並び順の“概念番号”ルール（参照用）：

main=0（固定）、health=50、audit=100、初期設定=200（設定モーダルのみ／自動付与）

実際の制御は tabs.yaml.order の配列順で行います（番号はドキュメント上の基準）。

動作チェック（ワンライナー）
$py = ".\.venv\Scripts\python.exe"; if(-not(Test-Path $py)){ $py="python" }
@'
import importlib
m = importlib.import_module("btc_trade_system.features.dash.dashboard")
cfg = m.\_load_tabs_cfg()
print("ORDER =", cfg["order"])
print("ENABLED_KEYS =", [k for k,v in cfg["enabled"].items() if v])
'@ | & $py -

B. 設定タブ追加ルール（必要な機能だけ）

優先候補（上から順に探索、最初に見つかったものを採用）

btc*trade_system/features/settings/set*<key>.py ← 推奨

btc_trade_system/features/<key>/settings_ui.py

btc_trade_system/features/<key>/config/settings_ui.py（将来用）

実装インターフェース（あるものだけ呼ばれる）

def render(): ...
def on_save(): ...
def on_default(): ...
def supports_default() -> bool: # 省略時は未対応扱い
return True

初期設定タブ（200）は常に自動追加：set_dash.py が描画されます。
→ 新機能の設定タブは「必要な機能のみ」追加すれば OK。

設定タブ解決チェック（ワンライナー）
$py = ".\.venv\Scripts\python.exe"; if(-not(Test-Path $py)){ $py="python" }
@'
import importlib
from btc_trade_system.features.settings import settings as S
for k in ["main","health","audit","<key>"]:
print(k, "->", S.\_resolve_settings_module(k))
'@ | & $py -

C. 機能内の“既定値”と“現在値”の置き方（保存ポリシ）

既定値（def）：機能フォルダ内に持つ

btc_trade_system/features/<key>/config/<key>\_def.yaml

現在値（current）：リポ内の共通場所に自動保存

btc_trade_system/config/ui/<key>.yaml

.gitignore で …/config/ui/_.yaml を無視、_\_def.yaml は管理対象（既に設定済み）

読み順：def → current（浅いマージ）。current が無ければ def のみで動作。

このポリシは settings_svc.py の get_paths()/load_yaml()/save_yaml() が面倒を見ます。

D. 追加時の最短レシピ（チェックリスト）

features/dash/ui\_<key>.py を作成し、render() を実装。
（必要に応じて features/<key>/... にロジックや静的ファイルを配置）

config/ui/tabs.yaml の order と enabled に <key> を追記。
initial は基本 main のまま。

設定が要る場合のみ：features/settings/set\_<key>.py を作成し、上記 I/F を実装。
既定値は features/<key>/config/<key>\_def.yaml に置く。

PowerShell のワンライナーで import 解決／タブ設定を検証（上記 A/B のコマンド）。

Streamlit を再起動 → ダッシュボードのタブ／設定モーダルが自動で反映されていることを確認。

E. 触らないファイル

btc_trade_system/features/dash/dashboard.py

btc_trade_system/features/settings/settings.py

これらは自動解決のハブです。新機能追加では原則編集不要。
日本語ラベルだけ変えたい場合のみ、\_LABELS に追記（任意）。

F. よくある質問

Q. ラベルを日本語にしたいけど、settings.py を触りたくない
A. 現状はキー名表示になります。将来、tabs.yaml へ labels: マップを拡張予定（仕様書 TODO）。今は必要になった時だけ \_LABELS に追加してください。

Q. on_default() 未実装で「デフォルト」ボタンはどうなる？
A. supports_default() が False（または未実装）なら自動で無効化されます。

## 追記：機能追加の絶対ルール（ダッシュボード／設定／配色）

1. タブ ID と並び順（固定規約）

タブ ID は一意の番号で昇順に並ぶ。重複禁止。

予約:

0: main（メイン）

50: health（健全性）

100: audit（開発監査）

200: dash（初期設定・右端固定。ダッシュボード側タブは持たない）

表示ラベルは tabs.yaml 側で ID→ キー → ラベルに解決（詳細は次項）。

tabs.yaml（ユーザー編集可能）

# path: ./btc_trade_system/config/ui/tabs.yaml # current（Git 追跡外）

# def は tabs_def.yaml（同ディレクトリ）に置く

order: [main, health, audit] # 表示順（ID の昇順で作るのが慣例）
enabled:
main: true
health: true
audit: true
initial: main

合成規則：tabs_def.yaml（既定）に tabs.yaml（現在値）を浅いマージで上書き。
参照優先度：ENV BTC_TS_CONFIG_DIR > <repo>/data/config/ui/ > <repo>/btc_trade_system/config/ui/

2. 設定画面の自動連携（設定サブタブの解決規約）

設定 UI はキー名から実装モジュールを自動解決する。探索順は以下：

btc*trade_system/features/<key>/set*<key>.py

btc*trade_system/features/settings/set*<key>.py

見つからなければなし（そのキーは設定タブに出ない）

例：

health → features/health/set_health.py があればそれを表示

なければ features/settings/set_health.py を探す

どちらも無ければ設定タブに「健全性」は出ない

set\_\* モジュールの期待 I/F（最小）

# 必須：この設定サブタブを表示する本体

def render():
"""Streamlit で設定 UI を描画する。保存／デフォルト復元などは内部で実行。"""

# 任意：デフォルト復元ボタンの活性可否

def supports_default() -> bool:
return True # 既定ありなら True

# 任意：デフォルト復元が押された時の処理（dash_def.yaml 等に戻す）

def on_default():
"""current を書き戻し、必要なら st.rerun() かモーダルを閉じる。"""

# 任意：保存成功時に設定モーダルを閉じたい場合

def on_save(picks: dict) -> bool:
"""保存処理を行い、True を返したら呼び出し側でモーダルを閉じる。"""

すでに dash（初期設定）は
btc*trade_system/features/settings/set_dash.py に実装済み。
ここを雛形として新規機能の set*<key>.py を作ると早い。

3. 設定ファイルの配置と合成規約（def / current）

def（既定）：優先して機能フォルダ内に置ける

btc_trade_system/features/<key>/config/<key>\_def.yaml

無ければグローバル既定：btc_trade_system/config/ui/<key>\_def.yaml

current（現在値）：既定ではリポ内に保存（Git 追跡外）

btc_trade_system/config/ui/<key>.yaml

.gitignore で \*\_def.yaml を除き current は無視

読込優先度（解決ルート）

ENV: BTC_TS_CONFIG_DIR があれば /<key>.yaml

<repo>/data/config/ui/<key>.yaml があればそれ

<repo>/btc_trade_system/config/ui/<key>.yaml（本運用の current）

合成：def に current を浅いマージ（辞書は一段のみマージ）

すべて features/settings/settings_svc.py の
get_paths()/load_yaml()/save_yaml()/load_def_yaml() が担当。

4. アラート配色（dash.yaml）— 構造と適用順
   colors:
   alert_chip:
   warn: { fg: "#000000", bg: "#FFF2CC" }
   crit: { fg: "#000000", bg: "#FFCCCC" }
   urgent: { fg: "#FFFFFF", bg: "#FF6666" }

適用順：def → current → session override（一時適用）

API（settings_svc.py 提供）：

get_alert_palette()：最終パレットを返す

apply_palette_once(picks: dict)：セッション内だけ上書き

reset_palette_to_default()：セッション上書きを破棄し def 相当に戻す

save_palette(picks: dict)：dash.yaml（current）へ原子的保存

5. ダッシュボード側（タブ自動組立の原則）

dashboard.py は固定の薄い入口。やることは：

tabs_def.yaml + tabs.yaml を読み込み、order/initial/enabled を決定

キー →UI モジュール名は固定規約で import する
例：ui*<key> → btc_trade_system.features.dash.ui*<key>

存在しないキーは自動スキップ（コード変更不要）

表示ラベルは日本語対応：
main: メイン / health: 健全性 / audit: 開発監査 / dash: 初期設定
（必要があれば settings.py 側の \_LABELS マップを更新）

6. 新機能を作るときの最短手順（テンプレ）
   features/<key>/
   **init**.py
   ui*<key>.py # ダッシュボード表示（不要なら省略可）
   set*<key>.py # 設定タブ（不要なら作らない）
   config/<key>\_def.yaml # 既定値（必須推奨）

docs/ に機能仕様書テンプレを 1 枚（任意）

config/<key>\_def.yaml を最初に用意（必要なデフォルトだけ）

設定が必要なら set\_<key>.py を set_dash.py を真似して実装

supports_default()/on_default()/on_save() の 3 点は雛形通り

ダッシュボード表示が必要なら ui\_<key>.py を用意

tabs.yaml に order と enabled を追記（dashboard 側）

設定側でサブタブを出したい場合はファイル追加だけで OK（set\_<key>.py の有無で自動）

動作確認のワンライナー（PowerShell）：

$py = ".\.venv\Scripts\python.exe"; if(-not(Test-Path $py)){ $py="python" }
@'
import importlib

# 1) ダッシュボード UI の import 確認

for k in ["main","health","audit"]:
m = f"btc*trade_system.features.dash.ui*{k}"
try: importlib.import_module(m); print("UI OK ", m)
except Exception as e: print("UI NG ", m, e.**class**.**name**)

# 2) 設定タブ解決の確認

from btc_trade_system.features.settings import settings as S
for k in ["dash","health","audit","<key>"]:
r = getattr(S,"\_resolve_settings_module",lambda x:None)(k)
print(f"SETTINGS {k:8} ->", r)
'@ | & $py -

7. 運用ルール（変更不可）

dashboard/settings の薄い入口にロジックを置かない
画面描画は ui*\*、設定は set*\*、既定/現在値/保存は settings_svc.py

current YAML は Git 追跡外（.gitignore で管理）
→ 実運用の変更が誤コミットで壊れないようにするため

ENV や data/config/ui に current があれば自動優先
→ 将来のマルチマシン運用・外部ディレクトリ切替に備える

「新機能の追加＝その機能フォルダに完結」
→ 既存 dashboard.py / settings.py を一切編集しない方針

8. よくある質問

Q: デフォルトボタンがグレーになるのは？
A: 当該キーの \_def.yaml が解決できない、または supports_default() が False のとき。

Q: 保存後に設定モーダルを自動で閉じたい
A: set\_<key>.py の on_save() が True を返すと呼び出し側が閉じる（すでに dash は対応済み）。
