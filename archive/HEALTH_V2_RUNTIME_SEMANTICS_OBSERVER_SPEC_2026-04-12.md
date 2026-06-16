# path: ./archive/HEALTH_V2_RUNTIME_SEMANTICS_OBSERVER_SPEC_2026-04-12.md
# desc: Archived note, specification, report, or reference document.

# Health v2 Runtime Semantics Observer Specification

更新日: 2026-04-12
位置づけ: 仕様書候補（tmp 作業台配置）
対象: Phase 2.5 `Health v2 runtime semantics observer`

---

## 1. この仕様書の結論
本仕様は、Health v2 runtime semantics observer が

- 何を観測対象とするか
- 何を observer の責務とするか
- 何をしてはいけないか
- どの field を current stable line とみなすか

を固定するためのものである。

この仕様は **observer target set と境界定義に関しては仕様書として固定可能** である。
一方で、`health_digest` の timeline / anomaly split や broader wording expansion は本仕様の外側にある carry-forward open とする。

---

## 2. 目的
Health v2 は、L3 / market_state / shared L4 / operator_ui adapter をまたいで outward に出てくる runtime semantics contract を、

- summary-first
- observer-only
- wording-light
- owner 境界を壊さない

という条件で監視する。

Health v2 の役割は「意味の再計算」ではなく、**正本 contract の生存確認と観測性の可視化** である。

---

## 3. 責務
### 3.1 Health v2 がやること
Health v2 observer は、次を行う。

1. runtime wiring が outward まで届いているかを見る
2. summary field が揃っているかを見る
3. active event contract rows が outward に届いているかを見る
4. persistence が absent なのか not-observable なのかを分けて見る
5. shared `health_digest` 経由の current-state observer 情報を表示する

### 3.2 Health v2 がやらないこと
Health v2 observer は、次を行ってはならない。

1. market meaning を再計算すること
2. near wall / support / resistance / persistence を独自推定すること
3. L3 / L4 の owner になること
4. UI convenience のために contract gap を黙って埋めること
5. wording の都合で summary / family-row / active-event-row の粒度を混同すること

---

## 4. 設計原則
### 4.1 summary-first
observer は、まず summary field を見る。
row-level 詳細は observer-only な補助確認として扱う。

### 4.2 observer-only
Health は observer であり owner ではない。
意味の生成・補完・変換の正本になってはならない。

### 4.3 additive-first
既存 outward contract を壊す変更ではなく、additive な field で拡張する。

### 4.4 wording-light
observer wording は、意味の解釈ではなく contract 状態の可視化に留める。

### 4.5 no second L3
Health / L4 / adapter / widget のどこも second L3 になってはならない。

---

## 5. current primary target set
Health v2 observer の primary target set は、以下の 3 群で固定する。

1. semantic runtime contract summary
2. orderbook runtime summary
3. shared `health_digest` current-state payload / widget keys

---

## 6. semantic runtime contract summary の stable target
### 6.1 必須 observer target
以下を current stable line とする。

- `wiring_status`
- `observer_present`
- `usage_summary_present`
- `contract_rows_present`
- `contract_rows_count`
- `source_series_present`
- `freshness`

### 6.2 semantic usage summary の stable target
以下を summary-first observer target とする。

- `source_kind`
- `contract_source`
- `meaning_version`
- `observer_status`
- `active_event_count`
- `mapped_event_count`
- `unknown_event_count`
- `event_family_distribution`
- `trust_bucket_distribution`
- `interpretation_bucket_distribution`
- `consumer_distribution`

### 6.3 observer-only 補助 target
以下は補助確認に使ってよい。

- `layer3_semantic_usage_rows` の count
- `active_event_contracts` から読める active version / trust / interpretation / consumer

ただし、これらは summary の代替にしてはならない。

---

## 7. orderbook runtime summary の stable target
### 7.1 必須 observer target
以下を current stable line とする。

- `contract_status_source`
- `wiring_status`
- `freshness`
- `present_count`
- `summary_slots_present`
- `active_event_count`
- `active_event_names`
- `active_event_contracts`
- `persistence_observable`

### 7.2 summary slot presence target
以下を slot presence observer target とする。

- `near_wall_present`
- `support_present`
- `resistance_present`
- `persistence_present`

### 7.3 observer-only diagnostics
以下は observer-only diagnostics として扱う。

- `near_wall_side`
- `support_side`
- `resistance_side`
- `persistence_event_name`
- `persistence_side`

---

## 8. persistence の読み分け
### 8.1 必須原則
Health v2 は、次を混同してはならない。

- `persistence_present = false`
- `persistence_observable = false`

### 8.2 読み方
- `persistence_present = false` は、current row に persistence summary slot が present でないことを表す
- `persistence_observable = false` は、比較不能や前状態不足などにより persistence 可否自体を判定できない状態を含みうる

### 8.3 UI / observer 表現への含意
Health observer は、absence と not-observable を分けて表示すること。

---

## 9. shared `health_digest` の stable target
### 9.1 widget keys
以下を current-state widget target とする。

- `freshness_key`
- `collector_mode_key`
- `api_mode_key`
- `ws_board_state_key`
- `ws_executions_state_key`
- `trust_key`
- `continuity_key`
- `interpretation_key`
- `semantic_wiring_key`
- `orderbook_wiring_key`
- `semantic_contract_rows_count`
- `orderbook_summary_slots_count`
- `active_event_count`

### 9.2 payload keys
以下を current-state payload target とする。

- `collector_runtime`
- `api_runtime`
- `ws_runtime`
- `market_runtime`
- `semantic_usage_summary_source`
- `semantic_usage_observer_status`
- `semantic_usage_runtime_wiring_status`
- `semantic_usage_contract_rows_count`
- `semantic_usage_contract_rows`
- `orderbook_runtime_wiring_status`
- `orderbook_summary_slots_count`
- `orderbook_summary_slots_present`
- `orderbook_active_event_contracts_count`
- `orderbook_active_event_contracts`
- `freshness`

### 9.3 役割分担
- shared bundle は wording-free current-state shape を持つ
- adapter は consumer-fit widget keys / payload shaping を持つ
- widget / view は rendering のみを持つ

---

## 10. observer caption / panel の stable line
### 10.1 top summary
top summary は、少なくとも次の軸を表示できること。

- collector: `mode`, `ok`, `runtime_kind`
- api: `mode`, `utilization`, `requests_60s`
- ws: `board_state`, `executions_state`, `board_freshness`, `executions_freshness`
- layer3: `semantic_rows`, `summary_slots`, `active_event_rows`

### 10.2 current state caption
current state caption は、少なくとも次を表示できること。

- `freshness`
- `semantic_rows`
- `summary_slots`
- `active_event_rows`

### 10.3 semantic observer caption
semantic observer caption は、少なくとも次を表示できること。

- `semantic_observer`
- `summary_source`
- `summary_contract`
- `summary_version`
- `family_rows`
- `active_events`
- `mapped_events`
- `family_dist`
- `active_versions`
- `trust_dist`
- `interpretation_dist`
- `consumers`
- `unknown_events`

---

## 11. Phase 2 minimal stable line との関係
Health v2 observer は、Phase 2 `live orderbook semantics runtime wiring contract` の current minimal stable line と整合しなければならない。

その current minimal stable line は次である。

1. `orderbook_semantics_contract_status`
2. `orderbook_semantics_summary`
3. `orderbook_persistence_observable`

Health v2 はこれらを observer 側の summary 表現に落とすが、owner になってはならない。

---

## 12. owner 境界
### 12.1 L3
市場意味の唯一 owner。

### 12.2 market_state
runtime outward の owner。

### 12.3 shared L4
reusable shared shape の owner。

### 12.4 operator_ui adapter
consumer-fit 変換の owner。

### 12.5 Health v2 observer
observer の owner。
意味の owner ではない。

---

## 13. 非ゴール
本仕様は次を確定しない。

- `health_digest` timeline bundle の最終 shape
- `health_digest` anomaly bundle の最終 shape
- broader wording expansion の最終文面
- full event-level formalization の最終完成形
- docs 全体の最終再編成

これらは carry-forward open とする。

---

## 14. current repo truth に基づく固定判断
本仕様は、少なくとも以下の repo truth とテスト根拠に基づいて固定できる。

- `health_chart_panels.py`
- `health_top_panels.py`
- `health_detail_panels.py`
- `health_digest_bridge.py`
- `test_health_chart_panels_semantic_observer_caption.py`
- `test_health_top_panels_digest_caption.py`
- `test_health_detail_panels_digest_caption.py`
- `test_health_digest_bridge.py`

したがって、本仕様は **手前ドラフトではなく、observer target set に関しては仕様書として固定可能** と判断する。

---

## 15. 一言
Health v2 runtime semantics observer の本質は、何かを賢く判断することではない。

- wiring が届いているか
- summary が揃っているか
- active event rows が outward に出ているか
- persistence が観測可能か

を、summary-first / observer-only で継続監視することである。

この線は、現時点で仕様書として固定してよい。
