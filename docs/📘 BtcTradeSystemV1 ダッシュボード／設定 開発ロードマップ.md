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
