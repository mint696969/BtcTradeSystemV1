BtcTradeSystemV1 新機能追加マニュアル v4

位置づけ

これは 「新規機能追加のためのマニュアル」 です。

いわゆる「開発ルール」ではなく、

新しいダッシュボードタブ・設定タブ・ヘッダーアラート・監査連携
を追加する際の 型・レシピ集 として使います。

主な読者は GPT であり、将来のセッションが迷子にならないための「設計書＋運用メモ」です。

0. 全体像
   0-1. 設定のレイヤ構造

デフォルト設定（リポジトリ内）

パスはおおよそ
btc_trade_system/features/<feature>/config/<area>\_def.yaml

変更しない限り Git で管理される「正準値」。

実行時設定（外部 CONFIG）

ルートは環境変数 BTC_TS_CONFIG_DIR
（なければ btc_trade_system/config をフォールバック）

ファイル名はおおよそ
<area>.yaml（例：main.yaml, dash.yaml, collector.yaml, health.yaml, monitoring.yaml）

差分だけ を保存する（def との差分）。

ファイルが存在しない場合は def のみが適用される（＝完全デフォルト）。
UI から [保存] したときだけ <area>.yaml が作成され、
先頭 2 行に

# path: ./btc_trade_system/config/<area>.yaml

# desc: <area> の外部設定（def との差分のみ保存）

というヘッダーが自動で付与される。
[デフォルト] 実行時は <area>.yaml 自体を削除し、def のみに戻す。

UI（設定モーダル）

btc*trade_system/features/settings/set*\*.py

settings_svc を通して

def + current の解決

差分保存 / 既定値復元

開発監査ログ（dev_audit.jsonl）
をまとめて扱う。

ダッシュボード / ヘッダー

btc_trade_system/config/tabs_def.yaml（正準）と、
CONFIG_ROOT/tabs.yaml（外部差分）でタブ構成を制御。
※ CONFIG_ROOT = BTC_TS_CONFIG_DIR があればそのパス、なければ btc_trade_system/config。
旧 config/ui/tabs\*.yaml は廃止済み。

dash_def.yaml / dash.yaml から

タイトル

ヘッダーアラート色

デモアラートの有無
を読んで UI を描画する。

開発監査（dev_audit）

logs/dev_audit.jsonl

モード（OFF / DEBUG / BOOST）や UI からの設定操作などが JSONL で記録される。

設定まわりでは settings.\* 系イベントを使う。

1. 新規機能追加チェックリスト（概要）

新しい「機能」を追加するときに、まず下のどれに当てはまるかを決める。

ダッシュボードの新タブ

例：健全性 タブ、開発監査 タブ

設定モーダルの新タブ

例：メイン設定、健全性 設定、初期設定

既存タブの中に新しい「設定セクション」を足す

例：健全性 設定 タブの中に「Slack 通知」セクションを追加

ヘッダーに新しいアラート要素を出す

例：collector の異常を「緊急／重大／注意」に集約してヘッダーに表示

開発監査に新しいイベントを追加

例：ある設定が保存されたときのメタ情報を残す

以降の章では、この順に「どのファイルをどう触るか」を整理する。

2. tabs.yaml / tabs_def.yaml（タブ登録）
   2-1. ファイルの役割

btc_trade_system/config/tabs_def.yaml

デフォルト定義。Git 管理される。

CONFIG_ROOT/tabs.yaml

上書き用。存在しなければ def のコピー相当。

※ CONFIG_ROOT = BTC_TS_CONFIG_DIR があればそのパス、
なければ btc_trade_system/config。
※ 旧 btc_trade_system/config/ui/tabs\*.yaml は廃止済み。

ユーザー（＝将来は UI）からの変更は基本こちら。

2-2. スキーマ（概略）
order:

- main
- health
- audit_dev
- set_dash # 例：設定専用タブ

tabs:
main:
enabled: true
dashboard: true # ui_main.py を使用
settings: "dash" # set_dash.py を使用
title_dash: "メイン"
title_set: "初期設定"

health:
enabled: true
dashboard: "health" # ui_health.py
settings: "health" # set_health.py
title_dash: "健全性"
title_set: "健全性 設定"

audit_dev:
enabled: true
dashboard: "audit_dev" # ui_audit_dev.py
settings: false
title_dash: "開発監査"
title_set: ""

ルール

order に書かれた順でダッシュボードタブが並ぶ。

tabs.<key>.dashboard

true → ui\_<key>.py

文字列 → ui\_<value>.py

false → ダッシュボードタブなし

tabs.<key>.settings

true → set\_<key>.py

文字列 → set\_<value>.py

false → 設定タブなし

title_dash / title_set

それぞれダッシュボードタブ／設定タブのタイトル。

新規機能追加のパターン

ダッシュボードと設定が セット の場合
→ dashboard: "<feature>", settings: "<feature>" をペアで登録。

設定だけ欲しい場合
→ dashboard: false, settings: "<feature>"。

3. \*\_def.yaml の書き方
   3-1. 共通ルール

先頭 2 行は 必須 コメント。

# path: ./btc_trade_system/features/health/config/health_def.yaml

# desc: 健全性ビューのデフォルト設定（カード順・しきい値・色など）

YAML は 人間が読める ことを優先し、以下を守る。

key は英小文字＋ \_。

数値は単位を key 名に含める
（例：interval_sec, latency_ms, max_stale_s）。

論理値は true / false。

「外部 CONFIG 側」は 差分だけ 持つことが前提なので、
def 側は 完全な構造 を持たせる。

3-2. 例：health_def.yaml / monitoring_def.yaml

# health_def.yaml

auto_refresh:
enabled: false
interval_sec: 10

periods:

- 1m
- 5m
- 10m
- 30m
- 1h

age_thresholds_sec:
warn: 20.0
crit: 30.0

latency_ms:
warn: 400
crit: 1200

slo:
ticker:
max_stale_s: 5
orderbook:
max_stale_s: 6
trades:
max_stale_s: 5

order:

- bitflyer/orderbook
- bitflyer/trades

palette:
card_border:
ok: "#10b981"
warn: "#f59e0b"
crit: "#ef4444"
bar_fill:
ok: "#d1fae5"
warn: "#fef3c7"
crit: "#fee2e2"
card_fill:
ok: "#ecfdf5"
warn: "#fffbeb"
crit: "#fef2f2"

# monitoring_def.yaml

thresholds:
age_sec:
warn: 20
crit: 30
latency_ms:
warn: 400
crit: 1200

slo:
ticker:
max_stale_s: 5
orderbook:
max_stale_s: 6
trades:
max_stale_s: 5

palette: # health とほぼ同じ構造
card_border: ...
bar_fill: ...
card_fill: ...

ポイント

health.yaml と monitoring.yaml は 役割分担 しているが、
UI の都合上、片方にしかない値もある。
→ UI 側でミラーする（例：色パレットは両方に保存）。

今後、新たな sub-feature を追加する場合も 同じ構造 を踏襲する。

4. set\_\*.py の基本パターン
   4-1. 共通テンプレート

# path: btc_trade_system/features/settings/set_xxxx.py

# desc: 「XXXX」タブの設定 UI。I/O は settings_svc に委譲。

from **future** import annotations
import streamlit as st

from btc_trade_system.features.settings import settings_svc as S
from btc_trade_system.features.settings import ui_common as U

try:
import yaml # type: ignore
except Exception:
yaml = None

\_PREFIX = "set.xxxx" # session_state 用の接頭辞
\_FEATURE = "xxxx" # settings_svc.load_yaml/save_yaml 用エリア名
\_KEYBASE = "set.xxxx.btn" # セクションボタンの key ベース

def \_mark_changed() -> None:
st.session_state["__settings_changed"] = True

def \_read_cfg() -> dict:
try:
return S.load_yaml(\_FEATURE) or {}
except Exception:
return {}

def \_exec_default(): # 1) デフォルトへ戻す
S.reset_to_default(\_FEATURE)

    # 2) UI 上の入力をクリア
    U.discard_prefix(_PREFIX)
    st.session_state.pop(_PREFIX + ".pending", None)

    # 3) ダッシュボード側へ「再描画要求＋適用済み」通知
    st.session_state["_dash_require_rerun"] = True
    st.session_state.pop("__settings_changed", None)
    st.session_state["__settings_apply"] = True

def \_exec_save(): # 1) pending から差分を集約
p = st.session_state.get(\_PREFIX + ".pending") or {}
if not p:
return

    base = S.load_yaml(_FEATURE) or {}
    merged = _deep_merge(base, p)

    ok_f = getattr(S, "force_save_yaml", None)
    if callable(ok_f):
        ok = bool(ok_f(_FEATURE, merged))
    else:
        S.save_yaml(_FEATURE, merged)
        ok = True

    # 2) 成功時のみ UI 状態をクリーンに
    if ok:
        U.discard_prefix(_PREFIX)
        st.session_state.pop(_PREFIX + ".pending", None)
        st.session_state["_dash_require_rerun"] = True
        st.session_state["__settings_apply"] = True
        st.session_state.pop("__settings_changed", None)

def render():
if yaml is None:
st.error("PyYAML が見つかりません。`pip install pyyaml` を実行してください。")
return

    def_path, act_path = S.get_paths(_FEATURE)
    cfg = _read_cfg()

    st.subheader("設定（XXXX）")
    st.caption(f"適用対象（外部CONFIG）: {act_path.name} ／ 既定: {def_path.name}")

    # ↓ ここから UI 本体。値変更ごとに _mark_changed() を呼ぶ。
    ...

    # pending を組み立ててセッションに載せる
    pending = {
        # cfg 構造に対応させる
    }
    _old = st.session_state.get(_PREFIX + ".pending") or {}
    st.session_state[_PREFIX + ".pending"] = _deep_merge(_old, pending)

    # ボタン（閉じる／デフォルト／保存）
    U.render_section_controls(
        prefix=_PREFIX,
        on_default=_exec_default,
        on_save=_exec_save,
        key_base=_KEYBASE,
        labels=("閉じる", "デフォルト", "保存"),
        confirm_message="XXXX設定を更新します。よろしいですか？",
        audit_tag=None,   # settings_svc 側の監査だけにする
    )

from collections.abc import Mapping
def \_deep_merge(dst: dict, src: dict) -> dict:
for k, v in (src or {}).items():
if isinstance(v, Mapping) and isinstance(dst.get(k), Mapping):
\_deep_merge(dst[k], v)
else:
dst[k] = v
return dst

4-2. マルチエリア版（例：set_health.py）

1 つの UI で 複数エリア を扱う場合（例：health + monitoring）は：

pending を

pending = {
"health": {...},
"monitoring": {...},
}

という構造にする。

apply_pending() で

base_h = S.load_yaml("health") or {}
merged_h = \_deep_merge(base_h, p.get("health", {}) or {})
S.force_save_yaml("health", merged_h)

base_m = S.load_yaml("monitoring") or {}
merged_m = \_deep_merge(base_m, p.get("monitoring", {}) or {})
S.force_save_yaml("monitoring", merged_m)

のように エリアごとに保存 する。

UI 上では

どのエリアの値か を明示するコメントを残す。

読み取り時は「monitoring → health」のように フォールバック順 を決めておく。

4-3. よくある落とし穴

settings_svc の area 名と YAML ファイル名の対応を間違える。

例：S.load_yaml("monitor") と書いてしまい monitoring.yaml を読めない。

pending を 完全代入 してしまい、他セクションの値を消去する。

必ず \_deep_merge() でマージする。

reset_to_default() したあとに pending を消し忘れ、
次の保存で再び古い値が書き戻される。

st.radio 等の key を共有してしまい、別セクションと衝突する。

すべて set.<feature>.\* の名前空間に閉じ込める。

5. settings_svc API（実装前提）

ここでは GPT が知っていてよい前提 の API だけを整理する。

load_yaml(area: str) -> dict | None

def + current を解決して dict を返す。

save_yaml(area: str, diff: dict) -> None

差分を書き込む旧 API。
（内部で def を読み、差分を計算して <area>.yaml に保存）

force_save_yaml(area: str, merged: dict) -> bool

新 API。呼び出し側が「def + current + diff」までマージ済みの dict を渡す。

def との差分計算、atomic 書き込み、fsync、開発監査までを一括で実行。

成功なら True。

UI 経由の保存では、<area>.yaml には必ず

# path: ./btc_trade_system/config/<area>.yaml

# desc: <area> の外部設定（def との差分のみ保存）

というヘッダー 2 行が付き、その下に def との差分だけが YAML で書き出される。

reset_to_default(area: str) -> None

CONFIG_ROOT/<area>.yaml を物理削除する（ファイルが無ければ何もしない）。
その後は def のみが適用される（完全デフォルト状態）。

開発監査 settings.default.apply.<area> を記録する。

get_paths(area: str) -> tuple[Path, Path]

(def_path, current_path) を返す。

UI の caption 表示用に利用。

6. ダッシュボードヘッダーのアラート
   6-1. 方針

ヘッダーのアラートは、基本的に

どこかの機能 が「集約済みステータス」を
JSON または YAML で出力し、

features/dash/providers.py がそれを読んで

ui_main.py などがヘッダーに反映する

という流れになっている。

例：ヘルスカードからのアラート

features/health/health_svc.py が

age_sec / latency / SLO を評価し

status.json 的なファイルに
ok/warn/crit のレベルや理由を集約して書き出す。

providers.py でそれを読み、

「緊急」「重大」「注意」件数に変換。

ヘッダーでは「緊急 Y・重大 X・注意 A +1」のように表示。

6-2. 新しい機能からアラートを出すときの手順

ステータスの集約形式を決める。

例：

{
"feature": "collector",
"level": "crit", // ok | warn | crit | urgent
"reasons": ["bitflyer board stale", "bybit latency high"],
"updated_at": "2025-11-12T21:00:00Z"
}

集約ロジックを自分の機能側に実装する。

例：features/collector/collector_status.py など。

「個々のエラー」ではなく「人間に見せるべき要約」を作る。

providers.py にブリッジを追加する。

既存の provider（boards / health / audit_dev など）を参考に、
同じ構造で

def get_collector_alerts() -> AlertsSummary: ...

のような関数を追加。

ヘッダー UI 側でチップにマージする。

既存の alert 集約処理に collector 分を足す。

「どの機能の alert か」は tooltip や詳細画面で見せる。

重要

ここは仕様変更の余地が大きいため、
新しい機能を追加するときは 必ず現物コード（providers / ui_main）を確認し、同じパターンを踏襲すること。

「推測で実装しない」が原則。

7. 開発監査（dev_audit）連携
   7-1. 目的

大きく二つ：

GPT に状況を説明するための 開発用ログ。

「いつ」「どの設定を」「どの値に変えたか」を追跡するための 監査ログ。

ファイルは logs/dev_audit.jsonl（JSONL 形式）。

7-2. 主なフィールド（簡略）

標準的な 1 行はだいたいこんな形になる：

{
"ts": "2025-11-12T21:23:45.123Z",
"mode": "DEBUG",
"feature": "settings",
"event": "settings.write.health",
"level": "INFO",
"payload": {
"area": "health",
"fields": ["age_thresholds_sec.warn", "slo.ticker.max_stale_s"]
}
}

feature

設定系は "settings" を使う。

event

保存時：settings.write.<area>

既定値適用：settings.default.apply.<area>

それ以外は既存の命名規則に従う（collector._, health._ など）。

7-3. 新機能追加時の原則

自前で dev_audit を直接触らない。

I/O 周りは settings_svc / audit_dev.writer / io_safe などの既存ラッパーを必ず通す。

新しい設定エリアを作るときは、

force_save_yaml / reset_to_default が
自動で 適切な event 名 を出すようにする。

監査を追加したいときは、

既存の audit_dev.writer を調べ、

同じ payload 形式・同じ level を踏襲する。

7-4. 動作確認に使う PowerShell ワンライナー

# 直近 300 行から settings.\* 関連を抽出

$logs = $env:BTC_TS_LOGS_DIR; if(-not $logs){ $logs = 'D:\BtcTS_V1\logs' }
Get-Content (Join-Path $logs 'dev_audit.jsonl') -Tail 300 |
Select-String -Pattern '"settings\.write\.|settings\.default\.apply\.' -SimpleMatch

8. 実装パターン別メモ
   8-1. 「単純な設定タブ」追加（例：collector 設定）

features/collector/config/collector_def.yaml を用意。

set_collector.py を set_dash.py / set_health.py を参考に実装。

tabs_def.yaml / tabs.yaml に

collector:
enabled: true
dashboard: "collector" # 既にあれば
settings: "collector"
title_dash: "コレクタ"
title_set: "コレクタ設定"

を追加し、order に collector を追加。

動作確認：

UI で保存 → D:\BtcTS_V1\config\collector.yaml 更新

dev_audit に settings.write.collector が出ていること。

8-2. 1 つの設定タブに複数セクション（しきい値／カード順／色）

set_health.py の方式を基本とする：

st.radio でセクション切替（thresholds / order / palette）。

実際の UI は「選択中のセクション」だけ描画。

しかし pending の構築は常にフルセット で行う。

→ どのセクションから保存しても、全体の一貫性が保たれる。

デフォルトボタンの挙動：

すべての値を def に戻し、

モーダル内の表示も def 値に置き換える
（reset_to_default → UI.discard_prefix → 再描画）。

9. アンチパターンまとめ

場当たり的に どこかの YAML を直接 open().write() で書き換える。

ヘッダーアラートの仕様を 記憶だけで 再実装する。

set\_\* モジュールの中から st.experimental_rerun() を多用する。

再レンダー制御は settings.py / dashboard.py の責務。

session_state の key をグローバルにばら撒く。

必ず set.<feature>. プレフィックスに閉じ込める。

10. まとめ

新規機能を追加するときは：

\*\_def.yaml で def を定義する

set\_\*.py で UI と settings_svc のブリッジを書く

tabs_def.yaml / tabs.yaml へタブを登録

必要ならヘッダーアラートと dev_audit への経路を追加

迷ったときは必ず

set_dash.py

set_health.py

settings_svc.py

features/dash/providers.py

ui_main.py

の 現物コードを読んでから 実装すること。

このマニュアル自体も随時アップデートし、
「GPT が迷わず引き継げる最小限かつ十分な知識ベース」として維持していく。
