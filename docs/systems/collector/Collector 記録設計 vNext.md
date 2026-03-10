# Collector 記録設計 vNext（正式項目案 / Draft）

## 0. 文書目的
本書は BtcTradeSystem NEXT における Collector の最終記録設計を定義する。

本設計は以下を同時に満たすことを目的とする。

- 24/365 の安定収集
- 将来の Replay / Research / Feature / AI / Strategy Sandbox / Execution への拡張容易性
- orderbook reconstruction を前提とした deterministic な市場再構成
- multi-collector / shadow collector / canonical merge への対応
- UI 向け軽量データと研究向け高忠実度データの分離

Collector は判断ロジックを持たない。
Collector の責務は、将来の判断に必要な事実と収集状態を、順序・出自・品質情報付きで記録することである。

---

## 1. 基本原則

### 1.1 Record raw facts before interpretation
取得した事実は解釈前に保存する。

### 1.2 Event ordering is first-class
イベント順序は第一級情報として扱う。

### 1.3 Collector stream state is also data
市場イベントだけでなく、collector 側の stream 状態も同じく記録対象とする。

### 1.4 Every record carries provenance
すべてのレコードは出自情報を持つ。

### 1.5 Rebuild must be deterministic
Replay / orderbook rebuild は deterministic でなければならない。

### 1.6 UI-friendly data and research-grade data must be separated
UI 向け縮約データと研究向け高忠実度データを分離する。

### 1.7 Schema evolution must be explicit
schema 変更は version を通じて明示的に行う。

### 1.8 Quality uncertainty must be preserved
不完全さ・欠損・再構成・信頼度低下は隠さず残す。

---

## 2. 記録レイヤ構成
Collector の出力は 3 層に分ける。

### 2.1 Raw Layer
目的:
- 原本保存
- forensic
- replay source
- parser / rebuild / canonicalizer 改善時の再処理

性質:
- append-only
- 可能な限り source 事実に近い
- source metadata を落とさない

### 2.2 Compact Layer
目的:
- WarRoom UI
- 軽量監視
- 直近状況の高速把握

性質:
- UI 向けに縮約
- 既存の orderbook / trades 参照系を移行しやすい
- 研究原本にはしない

### 2.3 Canonical Layer
目的:
- Replay
- Feature Engine
- Strategy Sandbox
- Research
- AI 入力
- multi-collector merge

性質:
- 順序・品質・lineage を持つ
- replay/read path の正準入力
- raw から再生成可能

---

## 3. レコード共通必須フィールド
すべてのレコードは以下の共通フィールドを持つ。

- `schema_version`
- `record_type`
- `record_id`
- `collector_id`
- `collector_role`
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

### 3.1 フィールド定義
#### schema_version
例:
- `collector.vnext.raw`
- `collector.vnext.compact`
- `collector.vnext.canonical`

#### record_type
例:
- `trade`
- `orderbook_snapshot`
- `orderbook_diff`
- `stream_control`
- `quality_event`

#### record_id
各レコード固有 ID。

#### collector_id
collector 識別子。例: `collector_A`

#### collector_role
例:
- `production`
- `shadow`
- `research`

#### session_id
collector プロセス起動単位のセッション ID。

#### stream_session_id
個別 stream / connection 単位のセッション ID。

#### market
例:
- `spot`
- `futures`
- `options`

#### instrument_id
将来の multi-market / multi-exchange を見据えた正準 instrument 識別子。

#### channel
例:
- `board_snapshot`
- `board_diff`
- `executions`

#### transport
例:
- `rest`
- `ws`

#### source_event_id
取引所由来のイベント ID。trade id 等。

#### source_sequence
取引所提供 sequence。存在しない場合は null 可。

#### sequence_id
collector 側の正準イベント連番。Replay の正順キー。

#### exchange_ts
取引所上でのイベント時刻。

#### collector_ts
collector が受信した時刻。

#### ingest_ts
永続化直前の時刻。

#### event_ts
内部順序構築に使用する正準時刻。

#### quality_flags
品質フラグ配列。
例:
- `missing_exchange_ts`
- `out_of_order`
- `gap_after_reconnect`
- `duplicate_source_event`
- `partial_snapshot`
- `clock_skew_high`

#### is_partial
部分データかどうか。

#### is_reconstructed
再構成データかどうか。

#### confidence_score
0.0-1.0 の範囲で記録信頼度を表す。

---

## 4. 時刻設計
Collector は単一 `ts` を廃し、複数 timestamp を採用する。

### 4.1 必須 timestamp
- `exchange_ts`
- `collector_ts`
- `ingest_ts`
- `event_ts`

### 4.2 推奨補助項目
- `exchange_ts_source`
- `clock_skew_ms`
- `ingest_latency_ms`

### 4.3 原則
- exchange 起点の時刻と collector 起点の時刻を混同しない
- 順序構築は `event_ts` と `sequence_id` の両方で担保する
- latency / skew は将来の quality engine と replay 検証の入力とする

---

## 5. ID / 順序 / lineage 設計

### 5.1 ID 種別
- `record_id`
- `source_event_id`
- `source_sequence`
- `sequence_id`
- `snapshot_id`
- `base_snapshot_id`
- `prev_snapshot_id`

### 5.2 原則
- source 由来 ID と collector 由来 ID を混ぜない
- replay 順序は `sequence_id` を正準とする
- diff 系イベントはどの snapshot に依存するかを明示する

---

## 6. Collector stream control event
市場イベントだけでなく、collector の stream 状態も canonical event として保存する。

### 6.1 record_type
- `stream_control`

### 6.2 event_name 例
- `stream_started`
- `stream_stopped`
- `stream_reconnected`
- `gap_detected`
- `gap_recovered`
- `resync_started`
- `resync_completed`
- `snapshot_refreshed`
- `sequence_reset`
- `heartbeat`
- `provider_error`
- `clock_drift_warning`

### 6.3 意義
- Replay 時に市場由来異常と collector 由来異常を区別できる
- orderbook rebuild の continuity 判定に利用できる
- audit と別に市場時間軸上の control event として扱える

---

## 7. Trade 記録設計

### 7.1 原則
- Canonical Layer では `1 trade = 1 event` を基本とする
- Compact Layer では UI 向けに一覧まとめを許容する

### 7.2 trade event 推奨フィールド
- `trade_id`
- `price`
- `size`
- `notional`
- `side`
- `aggressor_side`
- `maker_side`（取得可能なら）
- `exchange_ts`
- `source_sequence`
- `sequence_id`
- `match_count`（集約時のみ）
- `is_block_trade`（取得可能なら）

### 7.3 効果
- orderflow imbalance
- trade velocity
- sweep / absorption 解析
- deterministic replay

---

## 8. OrderBook 記録設計

### 8.1 record_type
- `orderbook_snapshot`
- `orderbook_diff`

### 8.2 snapshot 必須項目
- `snapshot_id`
- `depth`
- `bids`
- `asks`
- `best_bid`
- `best_ask`
- `mid`
- `spread`
- `snapshot_reason`
- `is_resync_snapshot`

### 8.3 diff 必須項目
- `base_snapshot_id`
- `diff_seq_start`
- `diff_seq_end`
- `changes`

### 8.4 changes の各要素
- `side`
- `price`
- `size`
- `op`
- `level_hint`
- `source_sequence`

### 8.5 op の定義
- `add`
- `update`
- `remove`

remove を曖昧な size=0 解釈に依存させない。

---

## 9. OrderBook Reconstruction 前提項目
板再構成のため、板系 record に以下を持たせる。

- `snapshot_id`
- `prev_snapshot_id`
- `base_snapshot_id`
- `rebuild_required`
- `continuity_state`
- `is_gap_fill`
- `is_resync`

### 9.1 continuity_state 例
- `continuous`
- `gap_detected`
- `resynced`
- `unknown`

---

## 10. 品質情報設計
品質情報は外部ログに閉じず、各 record に保持する。

### 10.1 必須
- `quality_flags`
- `confidence_score`
- `is_partial`
- `is_gap_fill`
- `is_reconstructed`
- `validation_state`

### 10.2 原則
- 不完全データは削除せず、低信頼として残す
- quality engine は raw を破壊せず、canonical に判断結果を反映する

---

## 11. Provenance 設計
各 record は出自を示す provenance を持つ。

### 11.1 必須/推奨項目
- `collector_id`
- `collector_role`
- `host`
- `process_id`
- `session_id`
- `stream_session_id`
- `provider_name`
- `provider_version`
- `transport`
- `channel`
- `endpoint`
- `request_id`
- `subscription_id`

### 11.2 意義
- production / shadow の分離
- provider 差分比較
- collector 別品質評価
- failover / reconnect 分析

---

## 12. book 表現方針

### 12.1 Compact Layer
既存 UI 互換を重視し、配列形式を維持してよい。
例:
- `bids: [{price, size}, ...]`
- `asks: [{price, size}, ...]`

### 12.2 Canonical Layer
列指向分析や Parquet 変換を前提に、後で以下へ落とせる契約を持つ。
- `side`
- `price`
- `size`
- `level_index`
- `snapshot_id`

---

## 13. 保存パス方針

### 13.1 Raw Layer
`data/collector_raw/exchange=<exchange>/market=<market>/symbol=<symbol>/channel=<channel>/date=<YYYY-MM-DD>/part-xxxxx.jsonl`

### 13.2 Compact Layer
`data/collector_compact/exchange=<exchange>/symbol=<symbol>/topic=<topic>/date=<YYYY-MM-DD>/part-xxxxx.jsonl`

### 13.3 Canonical Layer
`data/market_data/exchange=<exchange>/symbol=<symbol>/type=<record_type>/date=<YYYY-MM-DD>/part-xxxxx.jsonl`

### 13.4 原則
- 日付 partition を持つ
- part 分割を前提とする
- symbol / type / channel を path に含める

---

## 14. ファイルローテーション方針
orderbook diff など高頻度データを想定し、1日1ファイル固定を避ける。

### 14.1 分割条件例
- file size
- line count
- time window

### 14.2 効果
- 破損時の影響局所化
- replay / transform / parquet 化の効率改善
- tail 読みの軽量化

---

## 15. 研究レイヤ接続方針
Collector primary write は JSONL append-only を維持する。
その上で別レイヤで以下へ変換する。

- Transformer
- Parquet
- DuckDB

### 15.1 方針
- Collector 本体に研究用 DB を直接混ぜない
- Canonical Layer は Parquet 化しやすい列契約を持つ
- 研究速度向上は transform 層で担保する

---

## 16. session 境界設計

### 16.1 必須
- `session_id`
- `stream_session_id`

### 16.2 意義
- 再接続前後の区別
- watchdog 再起動の区別
- stream reset / resync 判定

---

## 17. schema governance
Collector 記録設計は version 管理の対象とする。

### 17.1 管理対象
- `schema_version`
- record_type ごとの required / optional
- backward compatibility 方針
- migration 方針
- deprecation 方針

### 17.2 推奨
Collector 正式仕様書とは別に、record schema 専用仕様書を持つ。

---

## 18. 将来派生するが Collector では直接判定しないもの
以下は Collector 本体で判断せず、Derived / Feature / Research 層で生成する。

- `wall_created`
- `wall_removed`
- `liquidity_added`
- `liquidity_pulled`
- `sweep_detected`
- `absorption_detected`
- `refresh_detected`
- `spoof_suspected`
- regime 判定
- AI commentary

Collector はこれらの判定に必要な事実粒度を落とさないことに責任を持つ。

---

## 19. 推奨追加メタ情報
以下は強く推奨する。

- `heartbeat` event
- `last_contiguous_sequence`
- `last_snapshot_id`
- `expected_continuity` metadata
- `tombstone` / `remove` support
- symbol / side / venue normalization hints
- replay cursor 用最小キー (`event_ts`, `sequence_id`, `record_id`)

---

## 20. 実装優先順位（設計反映順）

### Tier S
- 共通必須フィールド導入
- 時刻 4 本化
- sequence / provenance 導入
- Raw / Compact / Canonical の三層化
- orderbook snapshot / diff 契約固定
- stream_control event 導入
- session / stream_session 導入

### Tier A
- lineage / continuity_state / gap/resync metadata
- quality_flags / confidence_score
- part 分割 / 新 path 体系
- trade 1 event 正準化

### Tier B
- parquet 変換前提の canonical 変換契約
- level row 化しやすい book 変換契約
- expected continuity / watermark 付与

---

## 21. Collector vNext の定義
Collector vNext は、単なる API 取得器ではない。

Collector vNext は

**市場イベントと収集状態を、順序・出自・品質情報付きで記録する Event Capture System**

として定義される。

この定義をもって、Replay / Liquidity Intelligence / Strategy Sandbox / Multi-Collector / AI / Research Layer の土台とする。
