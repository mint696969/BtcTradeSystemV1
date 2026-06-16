# Collector 記録設計 vNext

最終更新: 2026-03-19  
対象: `btcts_next/src/btcts/collector_vnext/` / `btcts_next/src/btcts/market_engine/`

> [!NOTE]
> 本書は **Collector vNext の記録設計・拡張方針・実装手順** をまとめる補助資料である。  
> 現在の運用契約そのものは `Collector 正式仕様書.md` を正本とする。  
> 本書は、後続 GPT / 人間が「どこを触れば新取引所を追加できるか」「どのテストで何を確認すべきか」を判断できることを目的にしている。

---

## 0. 目的
Collector vNext の記録設計は、以下を両立するために存在する。
- append-only での事実保全
- 後段の Replay / Research / Market Engine / UI の共通入力化
- stream continuity / provenance / quality を後から解析できる構造
- 新しい取引所・新しい channel を安全に追加できる拡張性

Collector の原則は変わらない。

**Collector は判断しない。事実と収集状態を残す。**

---

## 1. 設計原則
### 1.1 事実優先
source payload と provider 情報を先に残す。  
解釈や review は後段で行う。

### 1.2 順序は第一級情報
`sequence_id`・`stream_session_id`・`event_ts` は再構成の土台である。

### 1.3 stream 状態もデータ
市場イベントだけでなく、`stream.started` / `stream.gap_detected` / `stream.resync_*` / `system.provider_error` をデータとして扱う。

### 1.4 provenance を落とさない
provider / transport / endpoint / session / stream session を残す。

### 1.5 append-only
raw / canonical は JSONL append-only を原則とする。

### 1.6 downstream 用の意味づけはレイヤ分離
高次判断は Collector に持ち込まない。  
後段の Layer3 review / Market Engine / Research で扱う。

---

## 2. 現行の実装レイヤ
### 2.1 Raw
- provider payload を保存
- forensic / replay source / transform 再処理用

### 2.2 Canonical
- 下流の正準入力
- market / stream control / provider error を同一 envelope で保持
- board continuity の主記録を持つ

### 2.3 State / Health / Audit
- `status.json`
- `health.json`
- `daemon_health.json`
- `checkpoint.json`
- `rate_state.json`
- `origin_status.json`
- audit event

### 2.4 Compact
現行正本では collector 主書き込みの主線ではない。  
必要なら別設計で復活させる。

---

## 3. Canonical 記録設計の中心
### 3.1 trade
`market.trade`

方針:
- 1 trade = 1 canonical event
- `source_event_id` に native id を入れられるものは入れる
- `integration_hint / dedupe_hint / completeness_hint / origin_hint` を payload に付与する

### 3.2 board snapshot / diff
- `market.orderbook.snapshot`
- `market.orderbook.diff`

現行 board canonical で重要な項目:
- `snapshot_id`
- `base_snapshot_id`
- `prev_event_id`
- `stream_event_no`
- `continuity_state`
- `rebuild_required`
- `is_gap_fill`
- `is_resync`
- `integration_hint`
- `dedupe_hint`
- `completeness_hint`
- `origin_hint`

### 3.3 stream control
- `stream.started`
- `stream.gap_detected`
- `stream.resync_started`
- `stream.resync_completed`
- `system.provider_error`

board_ws はこの control event を canonical に残す点が重要。  
後段の continuity 観測や rebuild review はこの記録を前提にできる。

---

## 4. continuity / lineage の現在地
### 4.1 現在の前進点
旧 Draft と比べて、現行実装は少なくとも以下を board canonical に持てる。
- `snapshot_id`
- `base_snapshot_id`
- `prev_event_id`
- `continuity_state`
- `rebuild_required`
- `is_resync`

### 4.2 まだ強化余地がある点
- すべての venue で同じ密度の control event を出せるわけではない
- explicit gap/resync が薄いサンプルもある
- `source_sequence` は venue 依存で弱いことがある

### 4.3 方針
Collector は continuity の **材料** を残す。  
その continuity をどう review するかは Layer3 / Market Engine 側の責務とする。

---

## 5. Collector と Market Engine の責務境界
### 5.1 Collector（Layer1 / Layer2 相当）
- 取引所事実を取得する
- provenance / session / sequence を付与する
- stream state を記録する
- canonical event を生成する
- board continuity の材料を残す

### 5.2 Market Engine onboarding / review（Layer3 相当）
- snapshot / diff の rebuild review
- overlap / gap 観測
- `allow_structural_use / observe_only / reanchor_required` の判断
- venue 固有の review posture 整理

### 5.3 原則
Collector は「使える / 使えない」を最終判断しない。  
Collector は **再判断できるだけの事実を残す**。

---

## 6. 新しい取引所を追加する方法
ここは後続 GPT / 人間向けの実務手順として重要。

### 6.1 追加対象を分解する
新取引所追加は、原則として以下を分離して考える。
1. config
2. provider
3. transform
4. venue adapter（board 系）
5. emit 導線
6. smoke / gate / diagnose テスト
7. 必要なら Market Engine profile

### 6.2 最小追加ポイント
#### config
- `collector_vnext/config.py`
- `enabled_exchanges`
- `symbol / instrument_id / market` の扱い整理

#### REST provider
追加例:
- `collector_vnext/providers/<exchange>_rest.py`

実装責務:
- endpoint を叩く
- request / response meta を返す
- `RestFetchResult` 相当の結果構造に揃える

#### WS provider
追加例:
- `collector_vnext/providers/<exchange>_ws.py`
- `collector_vnext/providers/<exchange>_ws_board.py`

実装責務:
- 生 message を返す
- received_ts / message meta / source_sequence を可能な範囲で埋める

#### transform
追加例:
- `collector_vnext/transforms/raw_to_canonical.py`
- `collector_vnext/transforms/raw_to_canonical_trades.py`
- `collector_vnext/transforms/ws_trade_to_canonical.py`
- `collector_vnext/transforms/ws_board_to_canonical.py`

実装責務:
- source payload を canonical payload に変換
- collector で高次判断をしない
- downstream が読むための最低限の payload 契約を守る

#### venue adapter（board）
追加例:
- `collector_vnext/venue_adapters/<exchange>_board.py`

実装責務:
- snapshot / delta / unknown 判定
- bids / asks の正規化
- venue 固有仕様の局所吸収

#### emit 導線
- `emit_rest.py`
- `emit_ws.py`
- 必要に応じて新しい emit module

実装責務:
- raw と canonical の両方に書く
- stream control event を必要に応じて書く
- provider error を canonical に落とす

### 6.3 board 追加時の実務ルール
board 系を追加するなら最低でも以下を考える。
- snapshot があるか
- delta があるか
- snapshot/delta の判別方法
- size=0 の意味
- venue sequence があるか
- continuity をどこまで collector が残せるか
- gap / resync をどう control event 化するか

### 6.4 取引所追加時に触るべきファイル一覧
現行 bitFlyer を雛形にする場合の主な参照先:
- `btcts_next/src/btcts/collector_vnext/providers/bitflyer_rest.py`
- `btcts_next/src/btcts/collector_vnext/providers/bitflyer_ws.py`
- `btcts_next/src/btcts/collector_vnext/providers/bitflyer_ws_board.py`
- `btcts_next/src/btcts/collector_vnext/venue_adapters/bitflyer_board.py`
- `btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py`
- `btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py`
- `btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py`
- `btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py`
- `btcts_next/src/btcts/collector_vnext/emit_rest.py`
- `btcts_next/src/btcts/collector_vnext/emit_ws.py`

---

## 7. 新しい取引所追加後の確認順
新規追加後は、いきなり weekly に行かない。

### 7.1 単発 smoke
- `tools/run_collector_vnext.ps1`
- `btcts.collector_vnext.app`

確認項目:
- raw が出る
- canonical が出る
- status / health が更新される

### 7.2 daemon
- `tools/run_collector_vnext_daemon.ps1`
- `btcts.collector_vnext.daemon`

確認項目:
- lock が効く
- daemon_health が更新される
- warn / degraded / stopped が自然

### 7.3 board continuity 系
board を追加した場合は必ず continuity / rebuild 診断を行う。
bitFlyer なら既存ツール群が参考になる。

---

## 8. 現在使う主要テストツール
### 8.1 Collector vNext 単体確認
- `tools/test_collector_vnext_invariants.py`
- `tools/test_collector_vnext_boundary_cleanup.py`
- `tools/test_collector_vnext_live_rate_control_gate.py`
- `tools/test_collector_vnext_live_diff_gate.py`

### 8.2 board sequence / rebuild / audit
- `tools/test_collector_vnext_board_ws_sequence.py`
- `tools/test_collector_vnext_board_ws_rebuild.py`
- `tools/test_collector_vnext_board_ws_rebuild_diagnose.py`
- `tools/test_collector_vnext_board_ws_rebuild_long.py`
- `tools/test_collector_vnext_board_ws_compare_diagnose.py`
- `tools/test_collector_vnext_board_ws_best_mismatch_audit.py`
- `tools/test_collector_vnext_board_ws_best_mismatch_trace.py`
- `tools/test_collector_vnext_board_internal_risk_audit.py`

### 8.3 Market Engine 接続確認
- `tools/export_market_engine_onboarding_input.py`
- `tools/run_market_engine_onboarding.py`
- `tools/test_market_engine_onboarding_rebuild_accuracy.py`
- `tools/test_market_engine_short_soak_gate.py`
- `tools/run_market_engine_runtime_smoke.py`

### 8.4 テストツールの読み方
- `run_*.py / run_*.ps1`
  - 正式導線 / smoke 実行
- `test_*_gate.py`
  - 最低条件の確認
- `test_*_diagnose.py`
  - 原因解析用
- `test_*_audit.py`
  - 品質観測 / 監査用
- `test_*_rebuild*.py`
  - board continuity / rebuild 観測用

---

## 9. 現在の Market Engine 側との接続点
Collector の canonical board / trade は、現在 Market Engine onboarding / runtime に接続されている。

### 9.1 onboarding 側
- `market_engine/onboarding/runner.py`
- `bitflyer_rebuild_review.py`
- `bitflyer_review_policy.py`

### 9.2 実装上の意味
Collector は以下を残せばよい。
- snapshot / diff / control event
- provenance
- continuity 材料
- payload の事実

review / rebuild 品質判定は Market Engine 側で行う。

---

## 10. bitFlyer board の現時点の設計理解
Collector 正本としての理解は次。
- snapshot は safer baseline / truth anchor 候補
- diff は board continuity の材料
- explicit gap / resync control event を collector が残せる範囲で残す
- best mismatch 単独で collector が diff を否定しない

この「使えるかどうか」の判断は Market Engine review 側へ渡す。

---

## 11. schema / contract の現在地
### 11.1 実装済みで強いもの
- 共通 envelope
- canonical schema contract fields
- raw / canonical path 契約
- board control event の canonical 記録

### 11.2 まだ将来強化余地のあるもの
- file rotation の実体実装
- multi-exchange の本格 config 化
- venue ごとの richer source_sequence 利用
- Compact Layer の再定義

---

## 12. 今後の拡張方針
### 12.1 Collector でやること
- 事実を増やす
- continuity 材料を増やす
- provenance を増やす

### 12.2 Collector でやらないこと
- venue quality の最終判定
- structural use / reanchor の最終判断
- AI commentary
- strategy ロジック

### 12.3 役割分担
- Collector
  - capture / normalize / record
- Market Engine onboarding / review
  - evaluate / review / bridge
- Runtime profile
  - venue posture を runtime 正本へ反映

---

## 13. 実務メモ: 仕様更新時の確認順
この文書や正式仕様書を更新する際は、最低限以下を現物確認する。
1. `collector_vnext/events.py`
2. `collector_vnext/app.py`
3. `collector_vnext/daemon.py`
4. `collector_vnext/emit_rest.py`
5. `collector_vnext/emit_ws.py`
6. `collector_vnext/writer.py`
7. `collector_vnext/paths.py`
8. `collector_vnext/providers/*`
9. `collector_vnext/venue_adapters/*`
10. 関連する `tools/test_*` / `tools/run_*`

仕様書は会話ベースで更新せず、必ず現物コード確認ベースで更新する。

---

## 14. まとめ
Collector 記録設計 vNext の要点は、

**事実・順序・出自・stream 状態を落とさず append-only で残し、後段の review / rebuild / AI / research が再解釈できるようにすること**

である。

新しい取引所を追加するときも、Collector は判断を増やすのではなく、
- provider
- transform
- venue adapter
- emit
- control event
- テスト導線
を整えることで拡張する。

本書はそのための設計補助資料とする。
