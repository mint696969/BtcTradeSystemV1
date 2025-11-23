BtcTradeSystem V1 — 収集器完成までのロードマップ（最新版）

🚩 Completed（本日までに完了したタスク）
✔ RateController v2（collector_rate.py）

last_rate_limited_ts の導入

get_exchange_state() の新設

Soft-limit 判定（token / cooldown / penalty）

Hard-limit 判定（429）

外部アクセス用スナップショット API 完備

Safety に倒れない実装に再構成

✔ collector_status v2 拡張

rate ブロックを status.json スキーマに追加

rate_state.json の読み取り口 \_read_rate_state() の新設

状態マージ処理追加

✔ 情報収集ドメイン設計仕様書 v2（全面改訂）

全章再構成

Soft-limit ＝ warn, Hard-limit ＝ crit の明文化

Exchanges / Endpoints / Scheduler / Status / Health / Audit の統合

将来の GPT 解析仕様も含めた正式版に昇格

🎯 Next Actions（次に着手すべきタスク）

これは直ちに着手可能な “最短経路” です。

① Scheduler → rate_state.json 書き出しの実装（最優先）

RateController.get_exchange_state() を scheduler から参照

取引所ごとの rate 状態を JSON 化

Soft-limit（warn）／Hard-limit（crit）を boolean で書き出し

👉 collector の完全動作に必須

② Health → Rate 評価（warn/crit）ロジック追加

status.json の rate を読む

soft_limit → WARN

hard_limit → CRIT

health_svc の evaluate() 内に組み込み

👉 ダッシュボード連携に必須

③ Dashboard → alert chip 反映（warn / crit）

health のレベル分類をそのまま header chips に送出

warn ＝黄色、crit ＝赤

urgent は rate では使わないと明記

👉 UI 完成の最終パーツ

🧭 Phase Roadmap（収集器完成までの工程表）
Phase 1：Rate 制御の完成

Scheduler に rate_state 書き出し

Status との統合確認

Soft-limit / Hard-limit が正しく JSON に乗るかを確認

Phase 2：Health 統合

status.rate の検証

warn/crit 判定

health.json の consistent 化

Phase 3：Dashboard Alert

header chip に warn / crit 出力

デモアラートと衝突しないよう調整

UI の視覚性確認

Phase 4：Exchanges（取引所登録機能）

exchanges_def.yaml の正式構造確定

公式 max_rps × safety_ratio の設定

endpoint リストの管理機能

Phase 5：Endpoint SLA（target_interval）再点検

priority と組み合わせた最適な巡回設定

ビットフライヤーの注文系と収集系の競合調整

今後の新エンドポイント追加準備

Phase 6：Audit（Ops 運用監査）の完成

429 / wait_ms 統計

endpoint 成功/失敗ログ

rate-state の推移グラフ化（将来拡張）

collector の稼働監視基盤の安定化

🎌 最後：収集器完成の Definition of Done

以下 6 点を満たした時点で「Collector V1 完成」とする：

RateController が Soft-limit / Hard-limit を正確に判定し保護が働く

Scheduler がすべての API 呼び出しを RateController 経由で実行する

rate_state.json → collector_status.json → health → dashboard の流れが確立

warn / crit の alert chip が自動的に表示される

Exchanges / Endpoints が config に正しく登録される基盤が整う

Audit が collector の運用状態を保存し続ける

これで BtcTradeSystem V1 の Collector は“設計面・運用面とも完成状態” になる。
