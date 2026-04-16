# path: ./tmp/03_L4_SHARED_CONSUMER_MODELS_SPEC_2026-04-09.md
# desc: L4 Shared Consumer Models Spec (merged current-truth sync after Phase 2 / 2.5 closeout)

更新日: 2026-04-14
位置づけ: 現行 mainline に合わせた L4 shared / consumer adapter 統合仕様
対象: `btcts_next/src/btcts/processing/l4_consumer_models/`, `btcts_next/src/btcts/apps/operator_ui/`, `btcts_next/src/btcts/market_engine/`

---

## 1. この仕様書の目的
本仕様書は、L4 を **second L3 にしない shared-first 層** として整理し、current implementation と今後の拡張余地を一箇所で読めるようにするための文書である。

ここでは次の 5 点を明確にする。

1. L4 は何の owner か
2. `market_summary` の current truth は何か
3. contract-first bundle として何が直接受けられるか
4. shared / adapter / bridge の責務はどこで切るか
5. 次にどの bundle を shared-first で増やすか

---

## 2. 結論
L4 は **shared-first の shape owner** である。

### L4 がやること
- L3 truth を consumer 利用向けの shared bundle に束ねる
- shared bundle を consumer 固有の thin adapter へ渡す
- 複数 consumer で再利用できる read model を育てる

### L4 がやらないこと
- 新しい market meaning を定義する
- trust / continuity / pressure / wall の owner になる
- UI wording を持つ
- page layout / CSS / refresh 秒数を持つ
- execution orchestration の owner になる

### 現状の一言
L4 は未展開ではない。2026-04-14 時点では、`market_summary` を中核に **summary-first mainline contract bundle** が mainline に入っており、さらに `health_digest` の current-state shared path まで到達している段階である。

---

## 3. 現行 L4 配置

### shared
- `btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py`
- `btcts_next/src/btcts/processing/l4_consumer_models/shared/health_digest.py`

### operator_ui thin adapter
- `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py`
- `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/health_digest_adapter.py`

### UI 側接続
- `btcts_next/src/btcts/apps/operator_ui/market_state_service.py`
- `btcts_next/src/btcts/apps/operator_ui/health_data_service.py`
- `btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py`
- `btcts_next/src/btcts/apps/operator_ui/components/health_digest_bridge.py`

旧説明にあった

- 「L4 package 未展開」
- 「market_summary は次フェーズで作る」
- 「operator_ui adapter は skeleton だけ」
- 「health_digest は将来の話」

という表現は、現行 mainline には合わない。

---

## 4. current L4 flow
現行の shared-first 経路は次である。

```text
market_state row
  ↓
L4 shared builder
  build_market_summary()
  ↓
L4 operator_ui thin adapter
  market_summary_widget_model()
  market_summary_status_payload()
  ↓
UI bridge
  market_state_bridge.py
  ↓
components / page
```

Health current-state line は次である。

```text
collector_state / market_state row / runtime summaries
  ↓
L4 shared builder
  build_health_digest()
  ↓
L4 operator_ui thin adapter
  health digest widget key / payload shaping
  ↓
UI bridge
  health_digest_bridge.py
  ↓
components / page
```

これらの経路は、

- L3 truth を直接 UI にばらまかず
- L4 shared で一度 bundle 化し
- adapter で consumer 都合の薄変換を行う

という shared-first の原則に沿っている。

---

## 5. `market_summary` shared bundle

## 5.1 current shared contract
`btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py` には、少なくとも次の実体がある。

- `MarketSummary`
- `MarketSummaryBuildInput`
- `build_market_summary()`

### 主な field 群
- identity / provenance
  - `summary_type`
  - `exchange`
  - `symbol_raw`
  - `market_uid`
  - `source_kind`
  - `source_series_id`
- time / freshness
  - `event_ts`
  - `age_sec`
  - `freshness`
  - `is_stale`
- interpretation core
  - `trust_state`
  - `continuity_state`
  - `interpretation_bucket`
  - `interpretation_reason`
- headline / summary
  - `market_state_label`
  - `participation_state`
  - `liquidity_bias`
- semantic side
  - `semantic_summary_source`
  - `semantic_contract_source`
  - `semantic_meaning_version`
  - `semantic_observer_status`
  - `semantic_observer_present`
  - `semantic_usage_summary_present`
  - `semantic_contract_rows_present`
  - `semantic_contract_rows_count`
  - `semantic_runtime_wiring_status`
  - `semantic_total_rows`
  - `semantic_active_event_count`
  - `semantic_mapped_event_count`
  - `semantic_unknown_event_count`
  - `semantic_event_family_distribution`
  - `semantic_trust_bucket_distribution`
  - `semantic_interpretation_bucket_distribution`
  - `semantic_consumer_distribution`
  - `semantic_usage_contract_rows`
- orderbook side
  - `orderbook_wiring_status`
  - `orderbook_contract_status_source`
  - `orderbook_persistence_observable`
  - `orderbook_summary_slots_present`
  - `orderbook_summary_slots_count`
  - `orderbook_near_wall_present`
  - `orderbook_support_present`
  - `orderbook_resistance_present`
  - `orderbook_persistence_present`
  - `orderbook_active_event_names`
  - `orderbook_active_event_count`
  - `orderbook_active_event_contracts`
- lightweight consumer tags
  - `notable_events`
  - `alert_candidates`
- diagnostics
  - `diagnostics`

## 5.2 この bundle の意味
`market_summary` は、2026-04-13 時点では **Phase 2 / 2.5 の summary-first mainline contract bundle** として読む方が current repo truth に近い。

単なる「市場状態の最小 shared summary」に留まらず、semantic / orderbook の wiring, provenance, counts, distributions, presence を additive に保持する shared mainline へ前進している。

### current reading
#### semantic side
- `semantic_summary_source`
- `semantic_contract_source`
- `semantic_meaning_version`
- `semantic_observer_status`
- `semantic_observer_present`
- `semantic_usage_summary_present`
- `semantic_contract_rows_present`
- `semantic_contract_rows_count`
- `semantic_runtime_wiring_status`
- `semantic_total_rows`
- `semantic_active_event_count`
- `semantic_mapped_event_count`
- `semantic_unknown_event_count`
- `semantic_event_family_distribution`
- `semantic_trust_bucket_distribution`
- `semantic_interpretation_bucket_distribution`
- `semantic_consumer_distribution`

#### orderbook side
- `orderbook_wiring_status`
- `orderbook_contract_status_source`
- `orderbook_persistence_observable`
- `orderbook_summary_slots_present`
- `orderbook_summary_slots_count`
- `orderbook_near_wall_present`
- `orderbook_support_present`
- `orderbook_resistance_present`
- `orderbook_persistence_present`
- `orderbook_active_event_names`
- `orderbook_active_event_count`
- `orderbook_active_event_contracts`

これらは、単なる notable tag や diagnostics ではなく、**shared bundle に載る mainline contract / shape field** として扱うのが正しい。

---

## 6. shared builder の責務
`build_market_summary()` がやるべきことは、shared shape の生成に限定する。

### やってよいこと
- source_kind の正規化
- event_ts / age_sec / freshness / is_stale の決定
- trust / continuity / interpretation 系 field の受け取り
- lightweight な notable / alert tag の付与
- diagnostics の引き継ぎ
- `semantic_usage_contract_rows` の正規化
- semantic / orderbook runtime field の additive 正規化
- `orderbook_semantics_summary.summary_slots_present` / `summary_slots_count` の shared shape への正規化
- `orderbook_semantics_summary.active_event_contracts` / `active_event_names` の shared shape への正規化
- `orderbook_persistence_observable` の shared shape への正規化

### やってはいけないこと
- UI wording 生成
- CSS / layout / card 順の決定
- market meaning の再判定
- execution 用 heavy signal の生成
- widget library 依存 shape の生成

shared builder は、meaning owner ではなく **shared read model builder** として保つ。

---

## 7. thin adapter の責務

## 7.1 current 実体
- `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py`
- `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/health_digest_adapter.py`

### current output
- `MarketSummaryWidgetModel`
- `market_summary_widget_model()`
- `market_summary_status_payload()`
- health digest widget key / payload shaping

## 7.2 adapter がやってよいこと
- field 名の consumer 向け変換
- `*_key` の付与
- placeholder fallback
- widget ごとの subset 切り出し
- status payload の flattening
- shared bundle の contract rows / slot presence / observer field を payload として通すこと

## 7.3 adapter がやってはいけないこと
- 新しい market meaning の生成
- trust / continuity / interpretation の再判定
- CSS class / layout grid / refresh 秒数の埋め込み
- wording の最終決定

原則として adapter は **meaning-unaware / consumer-aware** に保つ。

---

## 8. bridge / service 側の位置づけ

### `market_state_service.py`
- `market_state` から最新 row を読む
- diagnostics を作る
- `build_market_summary()` へ入力を組む

### `health_data_service.py`
- collector / market_state / runtime summary source を読む
- `build_health_digest()` へ入力を組む
- timeline / anomaly / page convenience line は現時点では service 側にも残る

### `market_state_bridge.py`
- shared bundle を読む
- thin adapter を通して UI 用 payload / widget model を返す
- UI 側 components と shared 経路をつなぐ

### `health_digest_bridge.py`
- shared digest / adapter output を current-state panel 群へつなぐ
- observer-only current-state line を UI に渡す

### 位置づけ
現時点では妥当である。bridge / service は rows や meaning の owner ではなく、**shared bundle を consumer へ渡す接続層**として読むのが正しい。

---

## 9. L4 の current limit
L4 は動いているが、全面完成ではない。

### 現在あるもの
- `market_summary` shared bundle
- operator_ui thin adapter
- UI bridge 経路
- contract-first rows の shared 受け取り
- orderbook summary slot presence の shared 受け取り
- current-state shared `health_digest` path
- `market_summary` / `health_digest` の shared-first mainline reuse line

### broader formalization がまだ open のもの
- `semantic_timeline_bundle`
- `liquidity_snapshot_bundle`
- prediction / decision 向け shared bundle
- execution signal 系 bundle
- `health_digest` の timeline / anomaly / broader split formalization

したがって、L4 は「未展開」ではなく、**`market_summary` を起点に mainline contract bundle を固定しつつ、`health_digest` current-state path まで到達済み**と表現するのが current truth に近い。

---

## 10. Health と L4 の関係
2026-04-13 時点では、Health の主入力は全面的に L4 に統一完了したとまでは言わないが、**current-state shared digest path reached** と読むのが current repo truth に近い。

### できていること
- Health は `market_state` の formal field を読める
- runtime observer として useful な可視化ができる
- shared consumer 側では `semantic_usage_contract_rows` と `orderbook_active_event_contracts` を直接受けられる
- `market_summary` は orderbook summary slot presence も受けられる
- `health_digest` は shared / adapter / bridge / current-state panel usage まで repo mainline に到達している

### carry-forward open
- Health 本体の broader input formalization
- `health_digest` timeline / anomaly split formalization
- broader wording / consumer expansion
- full formal completion と docs sync

### 方針
`health_digest` は future-only の bundle ではなく、**observer-only current-state shared digest path reached** と読んだうえで、broader split を additive-first に formal 化する。
observer-only 原則を崩して meaning owner を増やしてはならない。

---

## 11. contract boundary の current reading
shared consumer / UI / docs では次の 4 層を混同しないことが重要である。

1. `semantic_usage_summary`
   - aggregate observer summary
2. `semantic_usage_contract_rows`
   - event-family contract rows
3. `orderbook_summary_slots_present`
   - current row の summary slot presence
4. `orderbook_active_event_contracts`
   - currently active event-level rows

L4 `market_summary` は current mainline で 2 / 3 / 4 を直接受けられるが、1 と同一視してまとめてはいけない。
この境界整理が current docs sync の核心である。

---

## 12. 次に増やす bundle 候補
current roadmap と current stop point を踏まえると、次段の L4 bundle 候補は次の順が自然である。

1. summary / family rows / summary slots / active event rows の境界を崩さない wording 固定
2. broader formalization を前提にした observer-only の `health_digest`
3. orderbook semantics richer formal spec 固定後の `liquidity_snapshot_bundle`
4. prediction / decision contract を受ける shared bundle
5. `semantic_timeline_bundle`

ここで重要なのは、

- event usage / orderbook semantics の境界が曖昧なまま event-heavy bundle を増やさない
- live wiring contract の richer formal spec 前に orderbook semantics bundle を厚くしすぎない

ことである。

---

## 13. additive-first / compatibility
L4 shared は契約として育てる。

### ルール
- field は add を優先する
- rename / remove は deprecate を挟む
- breaking は shared でなく adapter 側で吸収する
- shared bundle は version を持てる設計を優先する

### 推奨 version field
- `bundle_version`
- `schema_version`
- `meaning_version`
- `producer_version`

---

## 14. shared に寄せる判断基準
次のどれかを満たすなら、まず shared を疑う。

- 2 consumer 以上で使う
- wording-free で再利用できる
- market truth を再定義せず shape だけ整えている
- timeline / digest / bundle として共有価値がある
- contract rows や summary slot presence を consumer 間で共通利用したい

逆に、次は shared に置かない。

- 文言
- 色
- CSS
- widget 固有の final input
- page 固有の並び順
- refresh 秒数

---

## 15. 一言
L4 は未展開ではない。
現在の mainline では `market_summary` を中核に shared-first の最小経路が既に成立している。
さらに 2026-04-13 時点では、semantic / orderbook の summary-first mainline contract bundle と `health_digest` current-state shared path が repo truth として読める。

今後は、meaning を増やさず shape を育てること、そして summary / family rows / summary slots / active event rows の境界を崩さずに bundle を増やすことが正しい進み方である。
