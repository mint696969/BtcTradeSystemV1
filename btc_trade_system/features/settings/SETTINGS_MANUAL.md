path: btc_trade_system/features/settings/SETTINGS_MANUAL.md
desc: 新規機能の設定タブを追加するための唯一の正準マニュアル（GPT 用）


BtcTradeSystem V1 – 設定機能 開発者向け統一マニュアル（v1）

1. 目的

本マニュアルは、BtcTradeSystem V1 の 設定機能（Settings） に関する
開発者向け統一仕様書（GPT 用） です。

新機能追加の際に必要となる以下をすべて網羅します。

set_XXXXX.py の雛形

XXXXX_def.yaml の雛形

設定タブ UI の構築規則

settings_svc API のルール

未知キー破棄スキーマルール

保存／デフォルト／破棄の動作仕様

開発監査(dev_audit)への出力規則

テストコードの書き方（smoke）

トラブルシューティング

2. 新規設定機能を作成する手順（全体像）

新規機能 KEY を foo とします。

STEP 1 — フォルダを作成
btc_trade_system/features/foo/
    ├── ui_foo.py        ← ダッシュボード用 UI（任意）
    ├── set_foo.py       ← 設定 UI（必須）
    └── config/
        └── foo_def.yaml ← 設定のデフォルト値（必須）

STEP 2 — tabs.yaml に登録

path: btc_trade_system/config/tabs.yaml

order:
  - main
  - foo

tabs:
  foo:
    enabled: true
    dashboard: true      # ui_foo.py を持つ場合
    settings: true       # set_foo.py を持つ場合
    title_dash: "Foo"
    title_set: "Foo 設定"

STEP 3 — def ファイル（foo_def.yaml）を作る

・UI設定項目はすべてここに定義される。
・未定義キーは settings_svc により破棄される（＝保存されない）。

雛形：

# path: btc_trade_system/features/foo/config/foo_def.yaml
# desc: Foo 機能のデフォルト設定。settings_svc の唯一の正準。

# 例: API関連
api:
  enabled: true
  max_rps: 5
  burst: 2

# UIに反映される値（任意）
ui:
  refresh_sec: 3.0
  theme: "light"

STEP 4 — set_foo.py を作る（雛形）
# path: btc_trade_system/features/settings/set_foo.py
# desc: Foo 設定タブの UI。read-only def + current を用いて描画する。

import streamlit as st
from btc_trade_system.features.settings import settings_svc

AREA = "foo"

def render():
    # def + current をマージした dict（未知キーは破棄）
    cfg = settings_svc.load_yaml(AREA) or {}

    st.subheader("Foo 設定")

    # --- UI 表示（例） ---
    cfg["api"]["enabled"] = st.checkbox("API 有効", value=cfg["api"]["enabled"])
    cfg["api"]["max_rps"] = st.number_input("max_rps", 1, 20, cfg["api"]["max_rps"])
    cfg["ui"]["theme"] = st.selectbox("テーマ", ["light", "dark"], index=0 if cfg["ui"]["theme"]=="light" else 1)
    
    return cfg

3. settings_svc API 仕様

位置：
btc_trade_system/features/settings/settings_svc.py

3.1 load_yaml(area)

def → current の順でマージして dict を返す

def にないキーは current にあっても破棄

ファイルが無い場合は def の内容のみを返す

3.2 save_yaml(area, data)

条件：

UIからの保存操作でのみ成功する（通常時）

スクリプトから保存する場合は
BTC_TS_ALLOW_SCRIPT_WRITE=1 が必要

動作：

def のキーに含まれない項目は 保存されない（unknown 破棄）

保存成否が開発監査へ出力される

3.3 force_save_yaml(area, data)

UIガード無視して保存可能

settings_svc 内部でのみ使用することを推奨

3.4 reset_to_default(area)

動作：

current 側の area.yaml を 空 {} にし保存

UIへ即反映（モーダルは閉じない）

4. 設定 UI の共通ルール（重要）
4.1 設定タブの表示

ダッシュボードのアクティブタブ KEY に対応する
set_<key>.py が存在する場合のみ、歯車ボタンが有効

4.2 ボタンの動作
● 閉じる（変更破棄）

モーダルを閉じる

変更内容は一切保存しない

● デフォルト

reset_to_default(area) を実行

モーダルを閉じない

現在のタブ内容のみ再読込して更新

開発監査に dev.settings.default.try / done が記録される

● 保存

save_yaml(area, cfg) を実行

モーダルを閉じない

反映後の cfg が即 UI に反映

unknown key は def.yaml の仕様により破棄

開発監査に dev.settings.write.try / done が記録される

5. 開発監査(dev_audit)への出力ルール

settings_svc 内部で emit:

dev.settings.write.try.<area>
dev.settings.write.done.<area>
dev.settings.write.error.<area>

dev.settings.default.try.<area>
dev.settings.default.done.<area>
dev.settings.default.error.<area>


payload に含まれる情報：

area（対象キー）

path（書き込んだ current 側の yaml パス）

ok（成功/失敗）

エラー内容（あれば）

6. 新規機能のテスト（最小 smoke）
6.1 force_save のスモーク
from btc_trade_system.features.settings import settings_svc as svc
cfg = svc.load_yaml("foo") or {}
cfg["api"]["enabled"] = False
print(svc.force_save_yaml("foo", cfg))

6.2 unknown キー破棄のテスト
cfg = svc.load_yaml("foo") or {}
cfg["_unknown"] = 1
svc.force_save_yaml("foo", cfg)

# 物理ファイルを読んで "_unknown" が無いことを確認

6.3 UI smoke（手動）

ダッシュで設定を開く

値を変更 → 保存

current/foo.yaml が生成されているか確認

デフォルト → 空 {} に戻るか

7. トラブルシューティング
● 歯車がグレーアウトする

tabs.yaml の settings:false

set_foo.py の import エラー

tabs_def と tabs.yaml の KEY mismatch

アクティブタブ KEY の判定ロジック不一致

● 設定が保存されない

UIガード：BTC_TS_ALLOW_SCRIPT_WRITE=1 が必要

settings_svc で unknown key が破棄されている

yaml が BOM 付き（※ UTF-8 BOM 禁止）

● 保存後 UI に反映されない

set_foo.render() が dict を返していない

settings.py 側で active_area の扱いがズレている

8. 付録：新規機能セット完全テンプレート
features/foo/
    ├── ui_foo.py
    ├── set_foo.py
    └── config/
         └── foo_def.yaml

tabs.yaml:
  foo:
    enabled: true
    dashboard: true
    settings: true

以上

このファイルは GPT が読むための唯一の正準マニュアル です。
拡張や修正があれば、必ずここを更新し、
すべての set_XXXXX.py / XXXXX_def.yaml と整合性を保ってください。