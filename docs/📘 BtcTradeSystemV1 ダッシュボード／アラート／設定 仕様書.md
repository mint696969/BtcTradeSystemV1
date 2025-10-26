📘 BtcTradeSystemV1 ダッシュボード／アラート／設定 仕様書

path: ./docs/spec_dashboard_settings.md
version: 1.0
last updated: 2025-10-25
author: SystemGPT (共同開発仕様統括)

1. 概要

本仕様書は、BtcTradeSystem V1 における
ダッシュボード構造・アラートシステム・設定モーダル・設定ファイル構成
を一元的に定義する。

目的は以下の3点。

機能追加時における UI／アラート／設定の設計基準統一

監査・警告・状態表示の共通ルール確立

将来的な機能分離／統合における再利用性の確保

2. ダッシュボード構造仕様
2.1 構成概要
Header（タイトル＋設定ボタン）
 └─ Tabs（Main / Health / Audit / Snapshot …）
     └─ Content（各タブの機能UI）

2.2 Header

左側：システムタイトル

右側：歯車（設定ボタン）

高さ最小・1行構成

背景：白

設定ボタン位置：最右端固定

2.3 Tabs
状態	背景	文字色	補足
非選択	薄灰 #F0F0F0	黒 #000000	折返しなし・スクロール対応
選択	白	黒	下線あり（underline_active: true）
警告（warn）	薄灰	濃黄 #CC9900	
重大（crit）	薄灰	赤 #FF0000	
緊急（urgent）	薄灰	赤 #FF0000	赤系ポップアップと連動

タブ数・順序・有効化は設定ファイル config/ui/tabs.yaml により制御。

初期表示タブは同ファイル内 initial に従う（通常 main）。

2.4 タブ登録レジストリ仕様

各タブは登録制で管理される。

tab = {
  key: str,             # 一意キー ("main", "health" など)
  label: str,           # 表示名（i18nキーでも可）
  render: callable,     # 描画関数
  get_status: callable, # 状態取得 normal|warn|crit|urgent
  enabled: bool         # tabs.yaml により上書き
}


ユーザーが新タブを追加する機能は提供しない。
開発時のみ登録可能とする。

3. アラートシステム仕様
3.1 概要

全アラートはタブ状態色＋緊急ポップアップにより通知。

種別：normal / warn / crit / urgent

優先順位：urgent > crit > warn > normal

各タブは自機能の状態を要約して severity を返す。

3.2 緊急ポップアップ

表示位置：画面右上

常時1ウィンドウ

内容：発生時刻（HH:MM:SS）＋要約＋「詳細」ボタン

消滅条件：

各 issue（事象）を「詳細」で開くとその事象のみ既読

全事象既読でウィンドウ自体が消滅

再表示：未既読がある状態でタブ遷移した場合に再ポップ

閉じる（×）：一時非表示（未既読が残れば再表示）

複数事象：下に積み、時刻順に表示

3.3 既読管理

粒度：事象単位

管理キー：{tab_key, issue_id}

保存先：一時セッションメモリ（永続化不要）

4. 設定モーダル仕様
4.1 構造

表示方式：ヘッダー右の歯車→モーダル（中央寄せ）

初期表示タブ：Basic

モーダル内タブ：

Basic / Exchanges / Monitoring / Network / Appearance / Backup / Paths

4.2 操作
操作	動作
Ctrl+S または「保存」	設定保存（即時反映）
Esc または「閉じる」	モーダルを閉じる
↺（復元）	個別キーを既定値に戻す（ホバー確認あり）
4.3 個別復元（↺）

各入力欄右に小ボタン（既定が存在する項目のみ）

クリック／ホバーで小ポップ確認

［戻す］／［キャンセル］

復元後5秒間アンドゥ可（右下スナックバー表示）

ログ：settings.<area>.reset_key を dev_audit に記録

セクション見出し右に「このセクションを既定に戻す」（確認モーダル付き）

4.4 設定保存

検証：型・必須キーのみ軽量検証（不正時は即エラー表示）

書込み：atomic replace（tmp→rename）＋fsync

保存対象：config/ui/*.yaml の該当項目のみ

4.5 監査

設定保存／復元／順序変更すべて logs/dev_audit.jsonl に記録

イベント名例：

settings.basic.update

settings.network.reset_key

settings.tabs.update_order

5. 設定ファイル構成
./btc_trade_system/config/
  ui/
    basic.yaml / basic.defaults.yaml
    tabs.yaml / tabs.defaults.yaml
    network.yaml / network.defaults.yaml
    monitoring.yaml / monitoring.defaults.yaml
    appearance.yaml / appearance.defaults.yaml
  exchanges/
    registry.yaml / registry.defaults.yaml
./config/
  secrets.exchanges.yaml

5.1 読み込みルール

読み込み順序：defaults → current（後勝ちマージ）

書込み：current のみ更新

defaults は不変（リセット参照用）

5.2 共通キー規則
キー	内容
schema_rev	スキーマ版
meta.last_updated	最終更新日時（任意）
colors.*	HTMLカラーコード
time.format	24h / ampm
time.display	HH:MM:SS
underline_active	bool（タブ下線）
6. 運用ルール

defaults を直接変更しない。

既定値更新は新バージョン時のみ。

監査を常時有効化。

すべての設定変更／復元を dev_audit に記録。

ファイル名・フォルダ構成を固定。

config/ui/* および config/exchanges/* は絶対パスを基準にロード。

開発時拡張ポリシー

新タブ追加時は ui_.py を dash/ 配下に追加し、config/ui/ に必要設定を追加。

既存スキーマと矛盾する場合は schema_rev を上げる。

互換性

schema_rev の不一致時は defaults から再生成。

バックアップ／復元

Backup タブで zip 生成、既定復元確認後 apply。

7. 更新履歴
Ver	Date	Author	Summary
1.0	2025-10-25	SystemGPT	初版（ダッシュボード／アラート／設定仕様確定）

以上を正式仕様とし、次工程「ロードマップ（設定完成までの作業予定）」に引き継ぐ。


===============================================================================


📘 BtcTradeSystemV1 ダッシュボード／設定 開発ロードマップ

path: ./docs/roadmap_dashboard_settings.md
version: 1.0
last updated: 2025-10-25
author: SystemGPT（共同開発計画書）

1. 目的と現状

本ロードマップは、
「ダッシュボード（ハブ）と設定（モーダル）」を安全かつ確実に完成させるための短期開発計画である。

現状は以下の状態にある：

項目	状態
ダッシュボード構造仕様	v1.1 決定済み（凍結）
設定モーダル仕様	確定（個別復元＋ホバー確認＋アンドゥ対応）
Health／監査との接続	保留（後フェーズ）
コード状態	UI骨格あり、開発監査完成、Dashboard一部構成済み
2. フェーズ構成（短期ゴール）
フェーズ	内容	目的
A	Header + Tabs 実装	UI基盤確立（ハブ構造／状態色切替）
B	Settings モーダル実装	設定画面起動／構造確定（Basic開始）
C	Basic 設定タブ実装	色・言語・時間設定＋個別復元機能
D	監査／ポップアップ確認	dev_audit出力／urgent挙動確認

💡 フェーズD以降（Health・Collector連携）は次期ロードマップにて扱う。

3. フェーズ別タスク詳細
🟩 Phase A — Header & Tabs（ハブ基盤）
タスク	ファイル	概要	テスト観点
A1	features/dash/ui_main.py	ヘッダー・タブのベースUI作成	タブ色変化／クリック切替動作
A2	features/dash/dashboard.py	レジストリ登録制導入	order/enabledの適用
A3	config/ui/tabs.yaml	並び順・有効化のYAML読み込み	有効タブのみ描画確認
A4	(内部)	normal/warn/crit/urgentの状態反映ロジック	色切替／スタイル整合性確認

完了条件

全タブの切替が安定動作

色／下線表示が仕様通り

tabs.yaml の変更が即時反映

🟦 Phase B — Settings モーダル実装
タスク	ファイル	概要	テスト観点
B1	features/settings/modal_settings.py	モーダル起動枠／Basic初期表示	歯車クリックで開閉
B2	features/settings/modal_sections.py	機能別タブ構造生成	各セクション見出し確認
B3	UI	保存（Ctrl+S／ボタン）／閉じる（Esc）実装	即時反映／再起動不要
B4	共通	入力バリデーション実装	無効カラーコード警告
B5	共通	dev_audit への記録	settings.*.update 出力

完了条件

Basic 初期表示／タブ遷移正常

保存が即時反映（YAML更新）

監査ログ出力確認

🟨 Phase C — Basic 設定タブ実装
タスク	ファイル	概要	テスト観点
C1	features/settings/sections/basic.py	言語／色／時刻入力欄作成	入力UI整列／ラベル表示
C2	同上	色入力をHTMLカラーコード対応	変更即反映
C3	同上	個別復元（↺）＋確認ポップ＋5秒アンドゥ	戻す／キャンセル／Undo確認
C4	同上	検証と保存	defaults→currentマージ動作確認

完了条件

各項目の変更が即時反映

↺復元＋確認ポップ正常

dev_audit に reset_key 記録あり

🟥 Phase D — 監査・ポップアップ連携確認
タスク	ファイル	概要	テスト観点
D1	features/audit_dev/writer.py	settings更新イベント監査連携	audit.jsonl に出力
D2	features/dash/ui_main.py	urgentポップアップの表示連携	試験的トリガで表示確認
D3	共通	既読管理（issue_id単位）	既読→個別消去動作

完了条件

監査出力が整合

ポップアップが1ウィンドウで積み上げ

既読単位で再ポップ制御

4. テスト＆確認チェックリスト
項目	確認内容	OK条件
タブ切替	色・下線の切替	全状態正常
Basic 保存	設定変更→YAML更新	即反映／再起動不要
↺復元	ホバー確認→戻す	defaults値と一致
Undo	5秒以内操作で復帰	値が元通り
dev_audit	settings更新記録	JSONL出力確認
urgentポップ	複数積層・個別既読	再表示正常
5. 完了条件と引継ぎ基準

すべてのフェーズA～Dを通過し、

dashboard.py 起動でUI完全動作

config/ui/*.yaml が正常読書き可能

監査・ポップアップが仕様通り

Health/Audit連携以降は次ロードマップに引き継ぐ。

✅ これをもって設定モーダル完成までの短期開発計画（v1.0）とする。
すべての仕様変更は docs/spec_dashboard_settings.md に追記・履歴管理を行う。