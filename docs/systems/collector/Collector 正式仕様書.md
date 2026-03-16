# Collector vNext 正式仕様書

（BtcTradeSystem / btcts_next / current official spec）

## 0. この文書の位置づけ
本書は **現行の Collector vNext (`btcts/collector_vnext/`) の正式仕様書** である。

目的は以下の 3 つである。
- 現行実装と運用契約を 1 本の文書で把握できるようにする
- 旧 Collector 仕様と vNext 記録設計 Draft の情報を、現行仕様として再整理する
- 後続 GPT / 人間が「どれが今の正本か」で迷わない状態を作る

本書を正本とし、以下の文書は補助資料とする。
- `Collector 記録設計 vNext.md`
  - 設計思想・将来拡張・未実装を含む補助資料
- 旧 `Collector 正式仕様書.md`
  - 本書へ置き換える

---

## 1. Collector vNext の定義
Collector vNext は、bitFlyer BTC/JPY 市場データを
- Raw
- Compact
- Canonical
の 3 層で記録し、将来の
- UI
- Replay
- Research
- Feature
- AI
- Strategy Sandbox
へ接続可能な **Event Capture System / 記録基盤** である。

Collector vNext は分析や判断を担当しない。
責務は、**市場イベントと収集状態を、順序・出自・品質情報付きで正しく・安全に記録すること** に限定される。

---

## 2. 主目的
### 2.1 市場データの継続取得
- board snapshot
- executions
- WebSocket board
- WebSocket executions
を継続取得する。

### 2.2 運用事故を避ける
- 多重起動防止
- state / health の分離
- soft-fail / degraded の段階管理
- API レート制御の可視化
により「動いているように見える事故」を避ける。

### 2.3 下流の共通入力源になる
- Replay
- Research
- UI
- 将来の戦略 / AI
に対して、共通の入力基盤を提供する。

---

## 3. 現在の収集対象
### 3.1 対象取引所 / 銘柄
- exchange: `bitflyer`
- symbol: `BTC_JPY`
- market: `spot`

### 3.2 REST
- board snapshot
- executions

### 3.3 WebSocket
- board_ws
- executions_ws

---

## 4. 記録レイヤ構成
### 4.1 Raw Layer
目的:
- 原本保全
- forensic
- parser / canonicalizer 再処理

保存先例:
- `data/collector_raw/exchange=bitflyer/symbol=BTC_JPY/channel=board_snapshot/date=YYYY-MM-DD/part-00001.jsonl`
- `data/collector_raw/exchange=bitflyer/symbol=BTC_JPY/channel=executions_ws/date=YYYY-MM-DD/part-00001.jsonl`

### 4.2 Compact Layer
目的:
- Operator UI
- 軽量監視
- board signal / compact snapshot の保存

保存先例:
- `data/collector_compact/exchange=bitflyer/symbol=BTC_JPY/topic=board_snapshot/date=YYYY-MM-DD/part-00001.jsonl`
- `data/collector_compact/exchange=bitflyer/symbol=BTC_JPY/topic=board_signals_ws/date=YYYY-MM-DD/part-00001.jsonl`

### 4.3 Canonical Layer
目的:
- Replay
- Research
- Feature / AI 入力
- 共通の正準入力

保存先例:
- `data/market_data/exchange=bitflyer/symbol=BTC_JPY/type=market.trade/date=YYYY-MM-DD/part-00001.jsonl`
- `data/market_data/exchange=bitflyer/symbol=BTC_JPY/type=market.orderbook.snapshot/date=YYYY-MM-DD/part-00001.jsonl`

---

## 5. 記録原則
### 5.1 3層分離
UI 向け縮約と研究向け正準を分離する。

### 5.2 append-only
すべての主記録は JSONL append-only を原則とする。

### 5.3 collector は判断しない
Collector 本体に戦略判断・市場判断は入れない。

### 5.4 事実と収集状態の両方を記録する
市場データだけでなく、collector 側の状態・stream の状態も重要なデータとみなす。

### 5.5 soft-fail を隠さない
不完全さ・warn・quality 低下は隠さず state / audit / record に残す。

---

## 6. 共通 record envelope
Collector vNext の record は共通 envelope を持つ。

### 6.1 現在の共通フィールド
- `schema_version`
- `record_type`
- `record_id`
- `collector_id`
- `collector_role`
- `host_name`
- `session_id`
- `stream_session_id`
- `exchange`
- `market`
- `symbol`
- `instrument_id`
- `channel`
- `transport`
- `source_event_id`
- `source_sequence`
- `sequence_id`
- `exchange_ts`
- `collector_ts`
- `ingest_ts`
- `event_ts`
- `quality_flags`
- `is_partial`
- `is_reconstructed`
- `confidence_score`
- `payload`

### 6.2 意味
これにより以下を統一的に追える。
- どの collector 実行か
- どの stream か
- どの順序か
- いつのイベントか
- 品質はどうか

---

## 7. ID / session / ordering
### 7.1 session_id
Collector 1 回の smoke / cycle を識別する。

例:
- `collector_main-sess-...`

### 7.2 stream_session_id
個別 stream / 接続単位を識別する。

例:
- `collector_main-stream-bitflyer-board_ws-...`

### 7.3 sequence_id
collector 側の連番であり、Replay 上の正準順序キーの一つとなる。

### 7.4 record_id
collector 側で生成する各 record 固有 ID。

---

## 8. record_type taxonomy
### 8.1 現在使う主 record_type
- `market.trade`
- `market.orderbook.snapshot`
- `market.orderbook.diff`
- `market.liquidity.signal`
- `stream.started`

### 8.2 現在 taxonomy 上は定義されているが、全面活用ではないもの
- `stream.stopped`
- `stream.reconnected`
- `stream.heartbeat`
- `stream.gap_detected`
- `stream.resync_started`
- `stream.resync_completed`
- `quality.validation`
- `system.provider_error`

※ これらは将来契約として保持しているが、現時点で全てが常時出力されるとは限らない。

---

## 9. 時刻設計
Collector vNext は単一 `ts` ではなく、複数 timestamp を持つ。

### 9.1 現在の主要 timestamp
- `exchange_ts`
- `collector_ts`
- `ingest_ts`
- `event_ts`

### 9.2 原則
- exchange 起点と collector 起点の時刻を混同しない
- 順序は `event_ts` と `sequence_id` の両方で補助する

---

## 10. path 設計
### 10.1 Raw
`data/collector_raw/exchange=<exchange>/symbol=<symbol>/channel=<channel>/date=<YYYY-MM-DD>/part-00001.jsonl`

### 10.2 Compact
`data/collector_compact/exchange=<exchange>/symbol=<symbol>/topic=<topic>/date=<YYYY-MM-DD>/part-00001.jsonl`

### 10.3 Canonical
`data/market_data/exchange=<exchange>/symbol=<symbol>/type=<record_type>/date=<YYYY-MM-DD>/part-00001.jsonl`

### 10.4 現時点の注記
- 日付 partition は実装済み
- `part-00001.jsonl` 固定であり、本格ローテーションは未実装

---

## 11. trade 記録設計（現行）
### 11.1 原則
Canonical Layer では原則 `1 trade = 1 event`。

### 11.2 現在の代表 payload 項目
- `trade_id`
- `side`
- `price`
- `size`
- `notional`
- `liquidity_role`

### 11.3 現時点の注記
- payload 内の `trade_id` は保持している
- envelope 側 `source_event_id` への全面反映は今後の改善余地あり

---

## 12. orderbook 記録設計（現行）
### 12.1 主 record_type
- `market.orderbook.snapshot`
- `market.orderbook.diff`

### 12.2 現時点の状態
- snapshot 系は主力として安定稼働
- diff / continuity / lineage の契約は育成中
- 文書上の理想契約（prev_snapshot_id / continuity_state など）は全面固定ではない

### 12.3 運用上の重要点
- board 系は collector の主軸
- weekly 中も board 主軸が維持されることを重要視する

---

## 13. stream control / collector state の扱い
市場イベントだけでなく、collector 側の状態も重要な記録対象とする。

### 13.1 実装済みの代表例
- `stream.started`
- `status.json`
- `health.json`
- `daemon_health.json`
- `checkpoint.json`
- `rate_state.json`

### 13.2 意味
- collector の進行状況
- degraded / warning
- replay / research 側の信頼性判断
に使う。

---

## 14. state ファイル
保存先:
- `state/collector_vnext/`

### 14.1 status.json
用途:
- 現在状態の人間向け一次表示

代表項目:
- `mode`
- `message`
- `session_id`
- `stream_session_id`
- `consecutive_failures`
- `last_error`
- `last_success_ts`
- `ws_trades_warn_streak`
- `rate_control`

### 14.2 health.json
用途:
- app / smoke の実収集 health

代表項目:
- `ok`
- `status`
- `checks`

### 14.3 daemon_health.json
用途:
- daemon 側の継続運転 health

代表項目:
- `cycle_no`
- `interval_sec`
- `consecutive_failures`
- `last_success_ts`
- `ws_trades_warn_streak`
- `rate_control`

### 14.4 checkpoint.json
用途:
- 進行位置の確認

代表項目:
- `last_sequence_id`
- `last_channel`
- `last_symbol`
- `last_exchange`

### 14.5 rate_state.json
用途:
- API レート制御状態の正準 state

代表項目:
- `items.<exchange>.mode`
- `eff_max_rps`
- `wait_ms`
- `last_429_ts`
- `last_retry_after_sec`
- `reason`

---

## 15. Audit
保存先:
- `logs/audit.jsonl`

### 15.1 現在の代表イベント
- `collector_vnext.board_snapshot.completed`
- `collector_vnext.rest_trades.completed`
- `collector_vnext.ws_trades.completed`
- `collector_vnext.ws_trades.failed`
- `collector_vnext.ws_board.completed`
- `collector_vnext.ws_board.failed`
- `collector_vnext.run_smoke.completed`

### 15.2 目的
- 後追い調査
- 健全性確認
- GPT / 人間の原因解析

---

## 16. 実行モード
### 16.1 単発 smoke
コマンド:
- `tools/run_collector_vnext.ps1`

用途:
- 短時間確認
- qualification
- 手動確認

### 16.2 daemon
コマンド:
- `tools/run_collector_vnext_daemon.ps1`

用途:
- 継続運転
- 24h / weekly test

特徴:
- loop 実行
- state 更新
- health 更新
- audit 継続出力

---

## 17. 多重起動防止
### 17.1 実装
- `collector_vnext/lock.py`
- lock file + pid 生存確認

### 17.2 契約
1 本目 daemon 起動中に 2 本目を起動した場合、
- `already_running: true`
で拒否する。

### 17.3 意義
- 過去にあった多重起動によるデータ汚染を防ぐ

---

## 18. WebSocket 劣化判定
### 18.1 基本方針
- `ws_board` は主軸であり hard-fail 寄り
- `ws_trades` は単発 timeout を即全体障害扱いしない

### 18.2 現在の運用項目
- `ws_trades_warn_streak`

### 18.3 意味
- 単発 timeout = soft fail / warn
- 連続 warn = 段階的劣化
- 全停止とは別扱い

---

## 19. API レート制御（現行最小導入）
### 19.1 現在の対象
まず REST 経路を対象に導入している。
- board REST
- executions REST

### 19.2 現在の状態
- `RateController` を vNext 用 runtime で薄く再利用
- `rate_state.json` へ現在状態を出力
- `status.json` / `daemon_health.json` に要約を出力
- `Retry-After` の通り道あり
- 429 時の入口あり

### 19.3 現在の可視化項目
- `mode: NORMAL / WARN / CRIT`
- `eff_max_rps`
- `wait_ms`
- `last_429_ts`
- `last_retry_after_sec`
- `reason`

### 19.4 注意
- 429 実地時の長時間挙動は継続観測対象
- 週間テスト時点では「最小導入版」である

---

## 20. BTC_TS_MODE と severity の分離
### 20.1 BTC_TS_MODE
- `NORMAL / DEBUG / BOOST`
- 監査・観測密度モード

### 20.2 rate severity
- `NORMAL / WARN / CRIT`
- レート制御 / 状態評価 / UI バッジ用語彙

### 20.3 原則
両者を混同しない。
同じ `NORMAL` でも意味が違うため、別フィールド・別概念として扱う。

---

## 21. Replay / Research / UI 接続
Collector vNext の Canonical / Compact 出力は、すでに以下と接続されている。
- Operator UI
- Replay
- Research
- Strategy sandbox 周辺

Collector vNext は単なる取得器ではなく、後段システムの入力基盤である。

---

## 22. 現時点で安定しているもの
- REST board
- REST trades
- WS board
- 3層書き込み
- state / health / checkpoint
- daemon 単一起動防止
- weekly qualification 通過済みの基本運転

---

## 23. 現時点で継続観測中のもの
- `ws_trades` の断続 timeout
- 長時間運転時の劣化判定の自然さ
- 429 実地時の rate control 動作
- より高度な continuity / lineage 契約
- source_event_id の活用強化
- file rotation / part 分割

---

## 24. Collector vNext に入れないもの
Collector 本体に以下を入れない。
- 市場判断
- 戦略判断
- AI commentary
- spoof 判定などの高次判断

これらは Derived / Research / Feature / AI 層で扱う。

---

## 25. 開発・運用上の注意
- skip を success 扱いにしない
- 事実を捨てない
- state / audit / data の契約を壊さない
- board 主軸を維持する
- weekly 中は本体ロジックを原則変更しない

---

## 26. legacy との関係
旧 `btcts/collector/` は legacy collector であり、構造も責務も vNext と異なる。
旧 Collector 仕様は参考資料としてのみ扱い、現行の正本は本書とする。

---

## 27. まとめ
Collector vNext は、

**市場イベントと収集状態を、順序・出自・品質情報付きで 3 層記録し、UI / Replay / Research / AI の土台となる現行記録基盤**

として定義される。

本書を Collector vNext の正式仕様の正本とする。
