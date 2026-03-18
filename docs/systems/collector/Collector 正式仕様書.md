# Collector vNext 正式仕様書

最終更新: 2026-03-19  
対象実装: `btcts_next/src/btcts/collector_vnext/`

## 0. この文書の位置づけ
本書は **現行 Collector vNext 実装の正式仕様書** である。  
ここでいう正式仕様とは、実装済みコード・起動導線・出力物・運用前提に乖離しない現在契約を指す。

補助資料の役割分担は以下とする。
- `Collector 正式仕様書.md`
  - 現在の実装・運用契約の正本
- `Collector 記録設計 vNext.md`
  - 記録設計思想、将来拡張、取引所追加方法、テスト導線を含む設計補助資料

---

## 1. Collector vNext の定義
Collector vNext は、取引所市場データと収集状態を **append-only JSONL** と **state / health / audit** へ記録する記録基盤である。

現在の主責務は以下。
- bitFlyer BTC/JPY の smoke 収集
- raw / canonical への記録
- stream control event の記録
- state / health / checkpoint / daemon health / rate state の更新
- REST / WS の smoke qualification

Collector は戦略判断や市場判断を行わない。  
責務は **市場事実と収集状態を、順序・出自・品質情報付きで残すこと** に限定する。

---

## 2. 現在の実装スコープ
### 2.1 対象取引所・銘柄
- exchange: `bitflyer`
- market: `spot`
- symbol: `BTC_JPY`
- instrument_id: `bitflyer.spot.BTC_JPY`

### 2.2 現在の収集経路
REST:
- `/v1/board`
- `/v1/executions`

WebSocket:
- executions stream
- board stream
- board snapshot stream

### 2.3 現在の主な smoke 導線
- `tools/run_collector_vnext.ps1`
  - 単発 smoke
- `tools/run_collector_vnext_daemon.ps1`
  - ループ daemon
- `btcts.collector_vnext.app`
  - 1 qualification cycle 実行
- `btcts.collector_vnext.daemon`
  - loop / lock / state 更新付き daemon

---

## 3. レイヤ構成
現行 Collector vNext は **raw と canonical を正本として実装**している。

### 3.1 Raw Layer
目的:
- 原本保全
- forensic
- transform 再処理
- provider payload 保持

保存先:
- `BTCTS_DATA_ROOT/collector_raw/exchange=<exchange>/symbol=<symbol>/channel=<channel>/date=<YYYY-MM-DD>/part-00001.jsonl`

特徴:
- provider request / response meta を保持
- source payload を保持
- append-only

### 3.2 Canonical Layer
目的:
- downstream 共通入力
- Replay / Research / Market Engine への入力
- stream control / board continuity 記録

保存先:
- `BTCTS_DATA_ROOT/market_data/exchange=<exchange>/symbol=<symbol>/type=<record_type>/date=<YYYY-MM-DD>/part-00001.jsonl`

特徴:
- 共通 envelope を持つ
- orderbook snapshot / diff / trade / stream control を同一記録系で保持
- append-only

### 3.3 Compact Layer について
本日時点の `collector_vnext/` 正本実装は **Compact Layer を主書き込み先としては持たない**。  
Compact / UI 向け縮約は現行 Collector 正本の主要責務ではなく、必要に応じて後段で扱う。

---

## 4. 共通 envelope
実装上、`events.py` の `make_record()` が canonical / raw 共通 envelope を生成する。

### 4.1 現在の共通項目
- `schema_version`
- `schema_contract`（canonical のみ）
- `schema_contract_version`（canonical のみ）
- `payload_contract_version`（canonical のみ）
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

### 4.2 原則
- `event_ts` は `exchange_ts` 優先、なければ `collector_ts`
- collector 由来の `sequence_id` を全記録で持つ
- 品質低下は `quality_flags` / `confidence_score` で落とさず残す

---

## 5. record_type taxonomy
`collector_vnext/events.py` 上の現行 taxonomy は以下。

市場イベント:
- `market.trade`
- `market.orderbook.snapshot`
- `market.orderbook.diff`
- `market.liquidity.signal`

stream control:
- `stream.started`
- `stream.stopped`
- `stream.reconnected`
- `stream.heartbeat`
- `stream.gap_detected`
- `stream.resync_started`
- `stream.resync_completed`

品質 / 例外:
- `quality.validation`
- `system.provider_error`

### 5.1 現在よく出るもの
- `market.trade`
- `market.orderbook.snapshot`
- `market.orderbook.diff`
- `stream.started`
- `stream.gap_detected`
- `stream.resync_started`
- `stream.resync_completed`
- `system.provider_error`

### 5.2 注記
`market.liquidity.signal` は taxonomy には存在するが、Collector vNext の主線機能として常時出力しているわけではない。

---

## 6. セッション / 順序 / ID
### 6.1 session_id
collector 実行単位のセッション ID。  
`run_smoke()` では `make_session_id()` を用いる。

### 6.2 stream_session_id
接続・channel 単位のセッション ID。  
例:
- `collector_main-stream-bitflyer-board_snapshot-...`
- `collector_main-stream-bitflyer-board_ws-...`
- `collector_main-stream-bitflyer-executions_ws-...`

### 6.3 sequence_id
collector 側の正準連番。  
Raw / Canonical / stream control すべてで付与される。

### 6.4 record_id
`make_record_id()` により collector 側で生成する一意 ID。

---

## 7. REST 収集仕様
### 7.1 board snapshot
実装:
- `providers/bitflyer_rest.py::fetch_board`
- `emit_rest.py::emit_rest_board_snapshot`

Raw:
- provider / endpoint / request_meta / response_meta / source_payload を保存

Canonical:
- `canonical_board_snapshot()` を通して `market.orderbook.snapshot` を出力
- `snapshot_id`
- `base_snapshot_id`
- `integration_hint`
- `dedupe_hint`
- `completeness_hint`
- `origin_hint`
を付与

### 7.2 executions
実装:
- `providers/bitflyer_rest.py::fetch_executions`
- `emit_rest.py::emit_rest_trades`

Canonical:
- `canonical_trades()` を通して **1 trade = 1 canonical record** を出力
- `source_event_id` には `trade_id` を反映
- `integration_hint / dedupe_hint / completeness_hint / origin_hint` を付与

---

## 8. WebSocket 収集仕様
### 8.1 executions_ws
実装:
- `providers/bitflyer_ws.py`
- `emit_ws.py::emit_ws_trade_smoke`
- `transforms/ws_trade_to_canonical.py`

Canonical:
- `market.trade`
- `source_event_id = trade_id`
- `source_sequence = provider 由来 sequence（取得できる範囲）`
- realtime provenance を `origin_hint` に記録

### 8.2 board_ws
実装:
- `providers/bitflyer_ws_board.py`
- `venue_adapters/bitflyer_board.py`
- `emit_ws.py::emit_ws_board_smoke`
- `transforms/ws_board_to_canonical.py`

board adapter の役割:
- snapshot / delta の判別
- bid / ask level の正規化
- venue 仕様の局所吸収

Canonical board の重要項目:
- `stream_event_no`
- `snapshot_id`
- `base_snapshot_id`
- `prev_event_id`
- `continuity_state`
- `rebuild_required`
- `is_gap_fill`
- `is_resync`
- `integration_hint`
- `dedupe_hint`
- `completeness_hint`
- `origin_hint`

### 8.3 明示 control event
board_ws は現在、以下の control event を canonical に出力できる。
- `stream.started`
- `stream.gap_detected`
- `stream.resync_started`
- `stream.resync_completed`
- `system.provider_error`

この点は旧仕様より前進しており、board continuity 観測の正本は現行実装側にある。

---

## 9. 品質情報
現行 quality 実装は `quality.py` と emit 系に分かれる。

### 9.1 現在の扱い
- `validate_board_payload()`
- `flags_for_missing_exchange_ts()`
- `confidence_from_flags()`

### 9.2 原則
- 欠損を捨てず `quality_flags` へ落とす
- `confidence_score` は低下として記録する
- collector が高次判断を確定しない

---

## 10. state / health / checkpoint / logs
state 系の主保存先:
- `BTCTS_STATE_ROOT/collector_vnext/`

### 10.1 `status.json`
用途:
- 現在状態の一次表示

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

### 10.2 `health.json`
用途:
- 単発 smoke 実行の health

### 10.3 `daemon_health.json`
用途:
- daemon ループ状態の health
- `cycle_no`
- `interval_sec`
- `consecutive_failures`
- `ws_trades_warn_streak`
- `rate_control`

### 10.4 `checkpoint.json`
用途:
- last processed の目安保存
- `last_sequence_id`
- `last_channel`
- `last_symbol`
- `last_exchange`

### 10.5 `rate_state.json`
用途:
- REST rate control 状態の正本
- `summary_state`
- `engaged`
- `reason`
- `wait_ms`
- `util_ratio`
- `last_429_ts`
- `recovery_phase`

### 10.6 origin status
board_ws origin audit 用の補助 state として `write_origin_status()` が使われる。

---

## 11. daemon / lock / degraded 運用
### 11.1 daemon
実装:
- `collector_vnext/daemon.py`

機能:
- 一定間隔で `app.main()` を反復実行
- 失敗回数を管理
- `status.json` / `daemon_health.json` を更新
- warn streak と rate summary を引き継ぐ

### 11.2 単一起動防止
実装:
- `collector_vnext/lock.py`

契約:
- daemon 起動時に lock を取得
- 既に稼働中なら `already_running=true` で拒否

### 11.3 degraded 判定
現行方針:
- `ws_board` 失敗は強めに扱う
- `ws_trades` は warn streak で段階評価
- `rate_state` は別 severity として保持

---

## 12. レート制御
実装:
- `rate_runtime.py`
- `VNextRateRuntime`

対象:
- 現在は主に REST 側

効果:
- `acquire()` / `note_request_sent()` / `on_success()` / `on_429()`
- `rate_state.json` への状態保存
- status / daemon health への summary 反映

注記:
- 現在は最小導入版
- 長時間・実地 429 の観測は継続対象

---

## 13. 現在の path 契約
### 13.1 Raw
`<BTCTS_DATA_ROOT>/collector_raw/exchange=<exchange>/symbol=<symbol>/channel=<channel>/date=<YYYY-MM-DD>/part-00001.jsonl`

### 13.2 Canonical
`<BTCTS_DATA_ROOT>/market_data/exchange=<exchange>/symbol=<symbol>/type=<record_type>/date=<YYYY-MM-DD>/part-00001.jsonl`

### 13.3 注記
- 現在の writer は `part-00001.jsonl` 固定
- rotation policy は config に存在するが、writer 側の part 分割は未反映

---

## 14. 現在の起動方法
### 14.1 単発 smoke
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\run_collector_vnext.ps1
```

### 14.2 daemon
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\run_collector_vnext_daemon.ps1
```

### 14.3 主要環境変数
- `BTCTS_DATA_ROOT`
- `BTCTS_LOGS_ROOT`
- `BTCTS_STATE_ROOT`
- `BTCTS_COLLECTOR_ID`
- `BTCTS_COLLECTOR_ROLE`
- `BTCTS_HOST_NAME`
- `BTCTS_ENABLED_EXCHANGES`
- `BTCTS_ENABLED_STREAMS`
- `BTCTS_MARKET`
- `BTCTS_SYMBOL`
- `BTCTS_INSTRUMENT_ID`
- `BTCTS_WS_SSL_VERIFY`
- `BTCTS_LOOP_INTERVAL_SEC`
- `BTCTS_MAX_FAILURES`
- `BTCTS_FAILURE_BACKOFF_SEC`

---

## 15. 現在のテスト / 診断導線
実装と一緒に保守すべき主なツール:
- `tools/test_collector_vnext_invariants.py`
- `tools/test_collector_vnext_boundary_cleanup.py`
- `tools/test_collector_vnext_live_diff_gate.py`
- `tools/test_collector_vnext_live_rate_control_gate.py`
- `tools/test_collector_vnext_board_ws_sequence.py`
- `tools/test_collector_vnext_board_ws_rebuild.py`
- `tools/test_collector_vnext_board_ws_rebuild_diagnose.py`
- `tools/test_collector_vnext_board_ws_best_mismatch_audit.py`
- `tools/test_collector_vnext_board_ws_compare_diagnose.py`
- `tools/test_collector_vnext_board_internal_risk_audit.py`

### 15.1 運用上の読み方
- smoke / gate ツールは「最低条件が壊れていないか」を確認する
- diagnose / audit ツールは board continuity や diff 品質を深掘りする
- 仕様書を更新するときは、関連ツールの前提も同時に確認する

---

## 16. Collector に入れないもの
Collector 本体には以下を入れない。
- 市場判断
- 戦略判断
- spoof 判定などの高次解釈
- AI commentary

これらは Derived / Research / Market Engine / AI レイヤで扱う。

---

## 17. 現在の強みと未完了事項
### 17.1 現在の強み
- raw / canonical の共通 envelope
- board_ws continuity 系 control event
- state / health / daemon health / checkpoint / rate state 分離
- lock による多重起動防止
- smoke と gate の導線が揃っている

### 17.2 未完了事項
- writer の part rotation 実装
- multi-exchange の本格拡張
- Compact Layer の正式復活が必要なら別途設計
- 実地 429 長時間運用の蓄積

---

## 18. まとめ
Collector vNext の現行正本は、

**bitFlyer BTC/JPY の市場イベントと stream 状態を raw / canonical / state 系へ記録し、後段の Replay / Research / Market Engine の土台となる記録基盤**

である。

本書は現行実装の正式仕様の正本とする。
