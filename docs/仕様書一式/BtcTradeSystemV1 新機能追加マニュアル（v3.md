BtcTradeSystemV1 新機能追加マニュアル（v3.0）

1. 機能追加の全体手順
   🔹 概要

新機能を追加する際は、独立したフォルダ構造と設定体系を持つ“1 機能 1 モジュール”方式で実装します。
UI・設定・defaults・current・監査が自動連携するため、ダッシュボード本体や設定 SVC に改修を加える必要はありません。

🔹 手順一覧
手順 内容 対応ディレクトリ 備考
① 機能フォルダの作成 btc*trade_system/features/<feature>/ 例：collector、health、audit_dev など
② defaults 設定作成 features/<feature>/config/<feature>\_def.yaml 既定設定を記述（詳細は後述）
③ UI タブの作成（必要時） features/dash/ui*<feature>.py ダッシュボード上の表示担当
④ 設定タブの作成（必要時） features/settings/set\_<feature>.py 設定画面で値編集を行う場合のみ
⑤ tabs.yaml へ登録 config/tabs.yaml 表示順・タイトル・有効/無効を設定
⑥ 動作確認と監査出力確認 logs/dev_audit.jsonl 書込・読込・リセット動作を検証
🔹 defaults（既定設定ファイル）

設置場所
btc_trade_system/features/<feature>/config/<feature>\_def.yaml

フォーマット例：

# path: ./btc_trade_system/features/collector/config/collector_def.yaml

# desc: データ収集機能（Collector）の既定設定

schema_rev: 1
interval_sec: 5
endpoints:

- exchange: bitflyer
  topic: board
  url: https://api.bitflyer.com/v1/getboard
  max_rps: 2
  burst: 4
  log_level: INFO

注意点

スキーマ外キーは禁止（SVC 側で破棄）

スキーマ変更時は schema_rev を更新

値は 最小限の正常動作を保証する設定 を記載

🔹 current（実効設定ファイル）

自動生成先
btc_trade_system/config/<feature>.yaml

保存形式
def との差分のみ（例：ユーザ変更値のみ保持）

外部同期運用（複数 PC 間）
環境変数 BTC_TS_CONFIG_DIR を指定することで、
同ディレクトリ内に current が作成される。

🔹 tabs.yaml の登録

設置場所
btc_trade_system/config/tabs.yaml

例：

order:

- main
- collector
- health
- audit_dev

tabs:
collector:
enabled: true
dashboard: true
settings: true
title_dash: "コレクター"
title_set: "収集設定"

dashboard：true → ui\_<key>.py を自動ロード

settings：true → set\_<key>.py を自動ロード

両方 false で非表示、または削除対象

未登録 key は UI 上に出ない

2. ダッシュボードヘッダーへのアラート表示
   🔹 概要

アラートは Streamlit のヘッダー部に alert_chip として出力される。
色・表示条件は dash.yaml 内 colors.alert_chip 設定に従う。

🔹 色定義（defaults 参照）
colors:
alert_chip:
warn:
fg: "#000000"
bg: "#FFF2CC"
crit:
fg: "#000000"
bg: "#FFCCCC"
urgent:
fg: "#FFFFFF"
bg: "#FF6666"

🔹 動的反映（SVC 提供関数）
from btc_trade_system.features.settings import settings_svc as S

palette = S.get_alert_palette()

# palette["crit"]["bg"] -> "#FFCCCC"

🔹 開発中にアラートを出す方法
import streamlit as st
st.markdown(
f"<div style='background:{palette['crit']['bg']};color:{palette['crit']['fg']};"
"padding:4px 12px;border-radius:8px;'>通信エラー発生</div>",
unsafe_allow_html=True,
)

🔹 永続的な色変更
S.save_palette({
"warn": {"fg": "#111111", "bg": "#FFFF99"},
"crit": {"fg": "#FFFFFF", "bg": "#FF0000"},
})

3. 開発監査ログ（dev_audit）出力仕様
   🔹 概要

すべての設定操作・内部処理は audit_dev.writer により自動記録される。
開発者はこのログを参照して異常検知・原因特定を行う。

🔹 出力先
D:\BtcTS_V1\logs\dev_audit.jsonl

🔹 代表的なイベント
イベント名 意味 トリガー
settings.write.<feature> 設定保存成功 save_yaml()
settings.default.apply.<feature> デフォルトリセット実施 reset_to_default()
settings.write.error.<feature> 保存失敗 I/O 例外発生
tabs.import_fail.<key> タブ UI import 失敗 dashboard 初期化時
🔹 出力形式（例）
{
"ts": "2025-11-11T01:23:45.678Z",
"mode": "BOOST",
"feature": "settings",
"event": "settings.write.collector",
"level": "INFO",
"payload": {
"changed_keys": ["interval_sec", "log_level"],
"path": "btc_trade_system/config/collector.yaml"
}
}

4. ひな型／テンプレート集
   🔹 新機能フォルダ構成
   btc_trade_system/
   features/
   myfeature/
   **init**.py
   config/
   myfeature_def.yaml
   myfeature_core.py

🔹 ui\_<key>.py テンプレート

# path: ./btc_trade_system/features/dash/ui_myfeature.py

# desc: MyFeature のダッシュボードビュー

import streamlit as st

def render():
st.subheader("MyFeature ダッシュボード")
st.info("ここに状態表示やアラートを出します")

🔹 set\_<key>.py テンプレート

# path: ./btc_trade_system/features/settings/set_myfeature.py

# desc: MyFeature の設定画面

import streamlit as st
from btc_trade_system.features.settings import settings_svc as S

def render():
cfg = S.load_yaml("myfeature")
st.text_input("ログレベル", key="log_level", value=cfg.get("log_level", "INFO"))
if st.button("保存"):
new_cfg = {"log_level": st.session_state["log_level"]}
S.save_yaml("myfeature", {**cfg, **new_cfg})
st.success("保存しました")

🔹 defaults YAML 雛形

# path: ./btc_trade_system/features/myfeature/config/myfeature_def.yaml

# desc: MyFeature の既定設定

schema_rev: 1
log_level: INFO
params:
retries: 3
timeout: 5

🔹 tabs.yaml 追記例
order:

- main
- myfeature
- audit_dev

tabs:
myfeature:
enabled: true
dashboard: true
settings: true
title_dash: "マイ機能"
title_set: "マイ機能設定"

🔹 動作確認ポイント

起動後に新タブが表示される

設定変更が保存される

logs/dev_audit.jsonl に settings.write.<key> が出力される

current YAML に差分のみが記録される

---

set\_**\***.py の責務と実装要領
目的

機能ごとの「設定 UI」を提供するセクション実装ファイル。

表示値は def + current の合成で初期化、保存時は def との差分のみを current に原子的保存。

既定に戻す（リセット）は current を {} にするだけで、表示は def に戻る。

保存先の feature key は set\_\*.py 側で決める（ダッシュボードから受け取った target キーと必ずしも一致しない想定）。

ファイル配置・命名

置き場所: btc*trade_system/features/settings/set*<feature>.py

1 行目コメント（必須）: # path: ./btc*trade_system/features/settings/set*<feature>.py

2 行目コメント（必須）: # desc: <機能名> の設定 UI（差分保存・既定リセット対応）

依存モジュール

読み書き: from . import settings_svc as S

共通 UI: from . import ui_common as U

表示フレームワーク: import streamlit as st

公開エントリ

def render() -> None: を必ず実装する（Hub が動的に render() を呼ぶ）。

画面初期化の原則

初回描画で merged = S.load_yaml(<feature>) を取得
→ merged は def ⊕ current（深い後勝ち）。

UI ウィジェットの初期値は st.session_state に保持（未保存値は Hub がセクション単位で破棄）。

典型例（擬似コード）:

\_FEATURE = "dash" # ← 保存先のキーをこのファイルが決める

def \_ensure_state_from(merged: dict) -> None:
st.session_state.setdefault("set.dash.title", merged.get("title", "BtcTradeSystem V1")) # 以降、必要な項目を session_state に setdefault

def \_collect_ui() -> dict:
return {
"title": st.session_state.get("set.dash.title"), # 以降、UI で編集した値から “表示どおりの合成値” を再構成
}

def render() -> None:
merged = S.load_yaml(\_FEATURE)
\_ensure_state_from(merged) # フォーム部品の描画（on_change で \_\_settings_changed=True を立てるのが推奨） # フッターの三点ボタン（閉じる／デフォルト／保存）

ボタン群（閉じる／デフォルト／保存）

U.render_section_controls(prefix, on_default, on_save, key_base=...) を使用（二段チェック付き）。

希望動作（本仕様）

閉じる: 変更を破棄し設定モーダルを閉じる（Hub が該当セクションの session_state を破棄）。

デフォルト: S.reset_to_default(<feature>) を呼び、モーダルは閉じずに即時反映（Hub 側で \_\_settings_dirty=True → ダッシュが 1 回だけ再描画）。

保存: S.save_yaml(<feature>, \_collect_ui()) を呼び、モーダルは閉じずに即時反映（同上）。

確認チェックは「未変更でもユーザーが任意で ON にできる」（自動で外さない）。

初回オープン／セクション切替時のみ安全のため OFF 初期化。

折りたたみ中（active=False）はチェックとボタンを無効化。

差分保存のしくみ（settings_svc 準拠）

読み込み: load_yaml(feature) → def ⊕ current。def に無いキーは無視（スキーマ外の混入防止）。

保存: save_yaml(feature, new_merged)

new_merged と def の差分だけを current に原子的保存。

変更なし保存 → current は {} になる（新規作成される場合も {}）。

既定: reset_to_default(feature) → current を {} にする。

いずれも Hub が監査出力（settings.write.<feature> / settings.default.apply.<feature>）を emit 済み。

アコーディオンで複数機能を同居させる場合

各パネル（機能）ごとに自分の feature key で save_yaml / reset_to_default を呼ぶ。

U.render_section_controls() をパネル単位で置くのが安全（誤更新の混入防止）。

セクションごとに prefix を分ける：例）"set.dash.", "set.health." …

Hub は prefix ごとの未保存値を個別に破棄可能。

即時反映の流れ

set\_\* で「保存／既定」ボタン押下 → 処理成功後に st.session_state["__settings_dirty"]=True を立てる。

Hub（settings.py）が \_\_settings_dirty を検知 → st.session_state["_dash_require_rerun"]=True をセットし再描画。

ダッシュ（dashboard.py）が \_dash_require_rerun を見て 1 回だけ rerun → 表示に即反映。

アクティブタブは active_tab により不変。

バリデーション・ガード

UI 入力は必ず set\_\* 側で妥当性チェック（色コード、数値範囲、選択肢など）。

スキーマ外キーは settings_svc 側で排除されるため、保存時にサニタイズされる（UI 側でもガード推奨）。

例外時は st.error() 表示＋保存しない。必要なら監査 emit を追加（W.emit(...)）。

監査

保存成功時：settings_svc.save_yaml() が内部で settings.write.<feature> を emit。

既定適用：settings.default.apply.<feature> を emit。

追加の独自監査が必要なら set\_\* 側で W.emit("settings.ui.<feature>....", payload=...) を任意に発火。

典型テンプレート（抜粋）

# path: ./btc_trade_system/features/settings/set_example.py

# desc: example の設定 UI（差分保存／既定リセット）

from **future** import annotations
import streamlit as st
from . import ui_common as U
from . import settings_svc as S

\_FEATURE = "example"
\_PREFIX = "set.example." # セッションキーの共通接頭辞
\_KEYBASE = "example.controls" # ボタン群の base key

def \_ensure_state_from(merged: dict) -> None:
st.session_state.setdefault(\_PREFIX + "threshold", (merged.get("threshold") or 0.5)) # 以降、必要分だけ setdefault

def \_collect_ui() -> dict:
return {
"threshold": float(st.session_state.get(\_PREFIX + "threshold", 0.5)),
}

def \_mark_changed():
st.session_state["__settings_changed"] = True

def render() -> None:
merged = S.load_yaml(\_FEATURE)
\_ensure_state_from(merged)

    val = st.slider("しきい値", 0.0, 1.0, key=_PREFIX + "threshold", on_change=_mark_changed)

    def _on_default():
        S.reset_to_default(_FEATURE)
    def _on_save():
        S.save_yaml(_FEATURE, _collect_ui())

    U.render_section_controls(
        prefix=_PREFIX, on_default=_on_default, on_save=_on_save,
        key_base=_KEYBASE, labels=("閉じる", "デフォルト", "保存"), active=True
    )

よくある落とし穴

保存先キーの誤り：ダッシュから渡る target は UI を開くためのキーであり、\*保存先の feature key は各 set\_ が定義\*\*すること。

未保存値の混入：prefix を機能ごとに分離しないと、他セクションの一時値が混ざる。

既定戻しの副作用：reset_to_default() は current を {} にするだけ。既定内容は def 由来なので、def ファイルが正しいことを前提にする。

差分の膨張：UI で def と同じ値に戻した項目は current から自然に消えるため、current は肥大化しない（本仕様のメリット）。

---

追記差分：新項目（パラメータ付き）を追加する標準手順
ポリシー（前提）

未知キーは保存・読込ともに破棄。したがって 新項目は必ず先に def に追加してから UI/処理を結線する。

current は def との差分のみを原子的保存。肥大化防止・多 PC 同期の再現性重視。

手順（例：health に responders.slack.\* を追加）

1. def スキーマを増やす（必須）

対象: btc_trade_system/features/health/config/health_def.yaml

responders:
slack:
enabled: false
webhook_url: "" # 機微は ENV/別ファイルに退避可
channel: "#ops"
min_level: "crit" # "warn" | "crit" | "urgent"

ルール

すべてのキーに「意図が分かる既定値」と「型」を与える（bool/int/str/list/dict）。

列挙は文字列で固定値にする（例: "warn"|"crit"|"urgent"）。

機微値（トークン等）は原則 ENV/外部安全ストアへ（空文字で占位）。

2. UI を結線（set_health.py）

cfg = settings_svc.load_yaml("health") の戻りに対し、上記キーを編集 UI にバインド。

保存は settings_svc.save_yaml("health", cfg_after_edit) を呼ぶだけ（SVC が差分抽出・未知キー破棄を実施）。

「閉じる/保存/デフォルト」ボタンは既定仕様どおり：

閉じる＝変更破棄・モーダル閉

デフォルト＝ reset_to_default("health")（current 空化）→ モーダルは閉じない（即時反映）

保存＝ save_yaml("health", merged_ui_dict) → モーダルは閉じない（即時反映）

3. 参照側（処理・表示）

参照は常に settings_svc.load_yaml("health") から同キーを読む。

既存コードに副作用を作らない範囲で、追加分の条件分岐・送出処理を実装。

4. 監査（自動）

保存成功で settings.write.health が emit（changed_keys, path を payload）。

仕様外キーが UI から来ても SVC が破棄（必要に応じ settings.drop_unknown.health を将来追加可）。

スキーマ設計チェックリスト

命名：lower_snake、短く意味明確に（min_ms, max_retries など）。

型：bool/int/float/str を明示。配列は空配列既定 [] を入れる。

数値範囲：UI 側で最小/最大を検証（保存ボタン活性条件に）。

列挙：UI はセレクト化。無効値は保存不可／既定へフォールバック。

機微：ENV/別ファイルに置き、def には空値で占位。

experimental：試験的パラメータは experimental: 配下に置けば、現行ポリシーでも保存・同期可能（のちに本キーへ昇格）。

よくある失敗と対処

def に入れずに保存 → 値が消える
→ 仕様どおり破棄。先に def へ追加してから UI を出す。

current が膨らむ
→ スキーマ外を残さないため基本的に起きない。旧版ファイルを人手で持ち込んだ場合は load_yaml がフィルタ。

型不一致
→ UI で型検証。不可なら保存ボタンを無効化。

スモーク（最短確認）
既知キーの保存
$env:PYTHONPATH = (Get-Location).Path
$py = ".\.venv\Scripts\python.exe"; if(-not(Test-Path $py)){ $py="python" }
@"
from btc_trade_system.features.settings import settings_svc as s
d = s.load_yaml("health"); orig = d.get("responders",{}).get("slack",{}).get("enabled")
d.setdefault("responders",{}).setdefault("slack",{})["enabled"] = True
s.save_yaml("health", d)
back = s.load_yaml("health")
print("ok_write:", back.get("responders",{}).get("slack",{}).get("enabled") is True)

# 戻す

d["responders"]["slack"]["enabled"] = bool(orig) if orig is not None else False
s.save_yaml("health", d)
"@ | Set-Content tmp/health_save_smoke.py -Encoding UTF8
& $py tmp/health_save_smoke.py

未知キーが残らない
@"
from btc*trade_system.features.settings import settings_svc as s
import yaml
d = s.load_yaml("health")
d["_unknown_param"] = 1
s.save_yaml("health", d)
*, path = s.get_paths("health")
cur = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
print("unknown_kept:", "\_unknown_param" in cur) # 期待: False
"@ | Set-Content tmp/health_unknown_drop.py -Encoding UTF8
& $py tmp/health_unknown_drop.py

ひな型
def（追記断片）
responders:
slack:
enabled: false
webhook_url: ""
channel: "#ops"
min_level: "crit" # "warn" | "crit" | "urgent"

UI（set_health.py 抜粋イメージ）
cfg = settings_svc.load_yaml("health")
slack = ((cfg.setdefault("responders", {})).setdefault("slack", {}))

enabled = st.checkbox("Slack 通知を有効化", value=bool(slack.get("enabled", False)))
channel = st.text_input("Slack チャンネル", value=slack.get("channel", "#ops"))
level = st.selectbox("最小レベル", ["warn","crit","urgent"], index=["warn","crit","urgent"].index(slack.get("min_level","crit")))

# 保存時

cfg["responders"]["slack"].update({"enabled": enabled, "channel": channel, "min_level": level})
settings_svc.save_yaml("health", cfg)
