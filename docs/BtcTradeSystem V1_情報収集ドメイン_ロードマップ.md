BtcTradeSystem V1 — 情報収集ドメイン 開発ロードマップ（共有版）

最終更新：{日付を適宜更新}

🎯 全体目的と前提
項目 内容
主目的 情報収集の完全性・正確性・健全性・可監査性を確立する。以後の AI 学習・自動売買の信頼基盤。
運用構成 当面はメイン PC 単体。将来、収集専用 PC ＋ NAS 構成に拡張。
開発姿勢 「急がば回れ」方針。小さく積み上げ、確実に動くものを段階的に固定。
最重視 データ欠損ゼロ／異常検知の確実性／信号系の再現性／監査と可視化。
🧱 フェーズ構成（全体像）
フェーズ 名称 概要 目的達成の指標
Phase 1 Collector 基盤構築 データ取得・保存・status.json・rate 制御の安全化 欠損率ゼロ／I/O 破損ゼロ／429 制御正常動作
Phase 2 Health システム 健全性の可視化・自動制御・並び替え・閾値設定 age_sec・cause 表示／閾値変更反映／自動制御動作
Phase 3 Ops-Audit 運用監査（DQ・Resource・Timeline） DQ/Resource レポ出力／イベント整合確認
Phase 4 可視化/信号評価 S/H デュアルチャネル、価格重ね、評価ウィンドウ グラフ上で提案 → 約定 → 評価が可視化
Phase 5 Collector↔Health 連携・運用安定化 長時間安定運転テスト（8–12 h） 連続稼働／再起動後の整合性／status 連携維持
Phase 6 学習準備と拡張 良質データ抽出・AI 前処理連携 S-only + 良 H 抽出／学習フォーマット出力
Phase 7 NAS 連携・多台化 Leader/Sync/Failover 機構 2 台構成で整合・欠損ゼロで稼働
Phase 8 長期運用・最適化 適応型レート制御（B 昇格）／監査自動化 情報利得学習・自律調整・週次監査自動出力
⚙️ Phase 1：Collector 基盤構築
タスク一覧

collector_status.py — 最終形 status.json 生成（原子的更新・監査可能形式）

collector_rate.py — 取引所ごとのバケット制御（429/Retry-After 対応、ヒステリシス）

collector_io.py — CSV/JSONL I/O の安全化（fsync・temp 置換）

collector_control.py — ファイルキュー制御 I/F（slow_down/restart/stop）

collector_scheduler.py — 周期・WS/REST 切替管理

collector_entry.py — プロセス起動・終了・PID ロック

成果物

正確な status.json

取引所別 429 制御動作ログ

audit log: I/O 書込確認レコード

🩺 Phase 2：Health システム構築
タスク一覧

ui_health.py — 健全性カード表示（OK/WARN/CRIT）

health_eval.py — 外因/内因判定ロジック（SLO/閾値適用）

set_health.py — 並び替え・閾値・自動アクション設定（プリセット＋ Custom）

health_actions.py — Collector 制御発行（slow_down 等）

成果物

Health タブに取引所別カード表示

閾値変更が即反映

自動制御が Collector に伝播

📊 Phase 3：Ops-Audit 構築
タスク一覧

ops_audit_writer.py — イベント記録（再起動・降格・閾値変更）

ops_audit_reports.py — DQ/Resource/Timeline 集計ロジック

ui_ops_audit.py — レポート可視化（CSV/PNG 出力）

成果物

DQ レポート (欠損率/連続欠損/SLA 違反率)

Resource レポート (API 呼出回数/降格時間)

Timeline レポート (重要イベント時系列)

📈 Phase 4：信号評価と可視化
タスク一覧

signal/order/fill スキーマ確定（S/H チャネル共通）

グラフ描画（価格＋マーカー＋評価窓）

フィルタ／リプレイ UI（channel/side/model 等）

良い H 抽出処理 (H & eval.hit → 学習候補)

成果物

S/H 重ね表示・評価ウィンドウ

良 H 抽出ファイル (CSV/JSON)

エクスポート機能 (PNG/CSV)

🔁 Phase 5：連携・長時間テスト

Health⇄Collector 連携の耐久性テスト（8–12 h 連続運転）

status.json 整合性・age_sec 推移・429 復帰時間の検証

再起動・停止・制御命令の整合性確認

🧠 Phase 6：学習準備とデータ整形

S-only ＋ 良 H データの統合抽出

学習フォーマット出力（JSONL / Parquet）

特徴量／ラベル化処理の雛形を作成

🧩 Phase 7：NAS 連携・多台構成

Leader ロック／Stale 検出／冪等同期処理

Sync ログ・NAS 切替検証

Secondary → Primary 自動同期の原子性テスト

⚡ Phase 8：適応型レート制御・運用最適化

B-1/B-2 情報利得メトリック導入（Collector 側に組込）

Ops-Audit と連携し報酬関数を定義

適応制御（B-3 以降）の段階導入

週次／月次レポート自動生成

🧾 管理ルールと進行運用
区分 内容
変更提案 1 ファイル 1 キャンバス・① 追加 ② 差替 ③ 削除フォーマット必須
ファイル命名 機能接頭辞（collector*/health*/ops*audit* 等）＋短く一意
Secrets 常時マスク、保存は暗号化。コピーはワンショットのみ。
ログ/監査 すべて Ops-Audit へ自動記録。
ドキュメント 各 Phase 完了ごとに仕様書へ追記。バージョン管理を明示。
✅ 現時点での合意事項（要約）

レート制御は取引所ごと（B 最終目標、C で運転し B-1/B-2 常時計測）。

Collector 独立稼働。Dashboard タブなし、設定は設定タブで管理。

Health 表示タブ＋設定タブ（二段構成、並び替え可）。

数値入力はプリセット＋ Custom。

Ops-Audit 初期出力は DQ → Resource → Timeline。

S/H 分離設計、学習は S-only ＋ 良 H 抽出。

すべての変更は Ops-Audit に記録。
