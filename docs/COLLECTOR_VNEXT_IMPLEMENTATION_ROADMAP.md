# Collector vNext 実装ロードマップ（Draft）

## 0. 目的
Collector 記録設計 vNext を、既存 Collector の安定性を維持しながら段階導入するための実装順を定義する。

本ロードマップの原則:
- 記録設計を先に固定する
- 既存 UI は Compact Layer を読むことで破壊を避ける
- 将来の Replay / Feature / AI / Research は Canonical Layer を読む
- Raw Layer は原本保全を最優先とする

---

## Phase A: スキーマ固定と共通基盤
### 目的
Collector vNext の土台を先に固定し、後戻りコストを消す。

### 実装項目
1. 共通 record envelope 導入
   - schema_version
   - record_type
   - record_id
   - collector_id
   - collector_role
   - session_id
   - stream_session_id
   - exchange / market / symbol / instrument_id
   - channel / transport
   - source_event_id / source_sequence / sequence_id
   - exchange_ts / collector_ts / ingest_ts / event_ts
   - quality_flags / is_partial / is_reconstructed / confidence_score

2. ID / sequence 発行基盤
   - collector 内 sequence_id 発行器
   - session_id / stream_session_id 発行器
   - record_id 生成規約

3. path / part 分割基盤
   - Raw / Compact / Canonical の 3 層パス生成
   - 日付 partition
   - part ローテーション規約

4. schema governance 雛形
   - record_type 一覧
   - required / optional 整理
   - version 管理方針

### 完了条件
- 新レイヤでも最低限書き込める
- 旧形式から vNext 形式へ移る骨格ができる

---

## Phase B: Raw Layer 導入
### 目的
原本保全を開始し、将来の再処理余地を確保する。

### 実装項目
1. REST raw payload 保存
   - response body（可能な限りそのまま）
   - request metadata
   - provider metadata
   - status / error information

2. WebSocket raw message 保存
   - subscribe / unsubscribe / reconnect / heartbeat を含む
   - raw frame or parsed raw message

3. stream_control record 導入
   - stream_started
   - stream_stopped
   - stream_reconnected
   - gap_detected
   - gap_recovered
   - resync_started / completed
   - snapshot_refreshed
   - sequence_reset
   - provider_error
   - heartbeat

### 完了条件
- 「何を受け取ったか」が raw に完全に残る
- stream 状態が市場イベントと同時間軸で追える

---

## Phase C: Compact Layer 移行
### 目的
既存 UI を壊さずに新設計へ接続する。

### 実装項目
1. 現行 orderbook compact を vNext envelope 付きに移行
2. 現行 trades compact を vNext envelope 付きに移行
3. 既存 UI が読む path / schema の互換維持
4. product_code 依存を symbol / instrument_id 前提へ寄せる

### 完了条件
- WarRoom UI が引き続き動作する
- Compact が「UI 専用縮約データ」として役割分離される

---

## Phase D: Canonical Layer 基礎
### 目的
Replay / Feature / Research の正準入力を作る。

### 実装項目
1. trade canonicalization
   - 1 trade = 1 event
   - source_event_id / side / price / size / notional

2. orderbook_snapshot canonicalization
   - snapshot_id
   - bids / asks
   - best_bid / best_ask / spread / mid

3. orderbook_diff canonicalization
   - base_snapshot_id
   - diff_seq_start / diff_seq_end
   - changes[] with op=add/update/remove

4. provenance / quality 反映
   - confidence_score
   - quality_flags
   - validation_state

### 完了条件
- Canonical Layer を Replay / Feature の起点にできる

---

## Phase E: WebSocket Collector 実装
### 目的
流動性中心分析に必要なリアルタイム粒度を確保する。

### 実装項目
1. bitFlyer WebSocket provider
   - trades stream
   - board diff stream
   - 必要なら snapshot refresh

2. reconnect / resubscribe / backfill 方針
3. stream_session 単位管理
4. REST と WS の併走方針
   - REST = safety net / periodic snapshot
   - WS = main realtime feed

### 完了条件
- orderbook diff / trades を realtime 取得できる
- reconnect / gap / resync が記録される

---

## Phase F: OrderBook Reconstruction 前提の continuity 実装
### 目的
板再構成できるデータにする。

### 実装項目
1. lineage 項目追加
   - snapshot_id
   - prev_snapshot_id
   - base_snapshot_id
   - continuity_state
   - is_gap_fill
   - is_resync
   - rebuild_required

2. gap / resync 反映ロジック
3. continuity watermark
   - last_contiguous_sequence
   - last_snapshot_id

### 完了条件
- どこまで連続した板かを機械判定できる
- rebuild 入力として十分になる

---

## Phase G: Multi-exchange / Multi-market 対応骨格
### 目的
将来の為替・金・株式・他金融商品へ広げられる基盤にする。

### 実装項目
1. instrument_id 正準規約
2. market / venue / symbol normalization
3. provider interface の共通化
4. source-specific field と canonical field の分離

### 完了条件
- bitFlyer 専用構造から脱却する
- 新しい取引所 / 商品を追加しやすくなる

---

## Phase H: Research 接続
### 目的
研究速度を一気に上げる。

### 実装項目
1. Canonical -> Parquet 変換ジョブ
2. DuckDB クエリテンプレ
3. level row 化変換
4. Replay cursor 用 read path

### 完了条件
- 研究・検証・比較の速度が上がる
- JSONL 原本を壊さず分析層を追加できる

---

## Phase I: Replay / Feature 接続
### 目的
Collector vNext を上位機能へ接続する。

### 実装項目
1. orderbook rebuilder
2. replay read model
3. liquidity feature extraction
   - orderflow imbalance
   - liquidity delta
   - wall pressure
   - sweep / absorption の入口特徴量

### 完了条件
- Collector が Replay / Feature / AI の直接的な土台になる

---

## Raw Layer 方針（重要決定）
Raw Layer は REST payload / WebSocket message を可能な限りそのまま残す。

### 理由
- parser / canonicalizer 改良余地を残せる
- forensic に強い
- exchange 固有バグや仕様変更を検証できる
- 再処理のたびに collector を走らせ直さなくてよい

### 注意
- secrets は保存しない
- 認証付き private API 情報は別途ポリシーを設ける
- raw は「そのまま保存」を優先するが、PII / secret は除外する

---

## 優先順位まとめ
### 最優先
- Phase A
- Phase B
- Phase E
- Phase F

### 次点
- Phase C
- Phase D
- Phase G

### その次
- Phase H
- Phase I
