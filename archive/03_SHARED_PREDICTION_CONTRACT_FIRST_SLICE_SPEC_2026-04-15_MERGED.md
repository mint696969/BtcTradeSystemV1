# path: ./tmp/03_SHARED_PREDICTION_CONTRACT_FIRST_SLICE_SPEC_2026-04-15_MERGED.md
# desc: Phase 3 shared prediction contract first-slice merged spec anchored on market_summary with optional health_digest caution input.

更新日: 2026-04-15
位置づけ: `./tmp/` 正式仕様書候補 / Phase 3 entry first slice merged current-truth spec
対象: `market_summary` anchor と optional `health_digest` caution input を用いた shared-first prediction contract

---

## 1. この仕様書の目的
本仕様書は、Phase 3 の最初の 1 本目として切った
**shared prediction contract first slice**
の current repo truth を固定するための文書である。

ここで大事なのは、prediction を

- L3 meaning owner の再実装
- Health observer の拡張版
- decision / tactic / execution の先食い

として始めないことである。

最初の 1 slice は、あくまで

- shared-first
- wording-free
- evidence-first
- horizon-separated

な **prediction read model** として切る。

---

## 2. 結論
Phase 3 first slice は、`market_summary` を primary anchor にした
**PredictionSummary**
として切るのが最も安全である。

### first slice で扱うもの
- short horizon bias
- regime transition risk
- liquidity deterioration risk
- continuation likelihood
- mean-reversion likelihood
- caution level
- execution feasibility hint

### first slice で扱わないもの
- prediction observer UI
- decision recommendation
- tactic recommendation
- label / target contract
- execution bundle
- event-level full contract broader completion

### optional supporting input
- `health_digest` は **primary truth ではなく optional caution input** としてのみ使ってよい

---

## 3. owner boundary
### L3 が owner のままのもの
- trust / continuity / interpretation
- event usage meaning
- orderbook semantics meaning
- summary / family rows / active event rows の事実

### L4 が owner になるもの
- shared prediction shape
- prediction summary bundle
- evidence / provenance / confidence / horizon の整理

### Health が owner ではないもの
- prediction truth
- prediction bias
- tactic hint
- execution hint の最終 owner

### decision / execution がまだ owner でないもの
- action recommendation
- order placement
- entry / exit policy

---

## 4. input anchor
Phase 3 first slice の primary input anchor は `market_summary` とする。

### primary input
- `MarketSummary`

### optional supporting input
- `HealthDigest` current-state caution input

### 重要な原則
- direct raw L3 input を増やさない
- UI convenience payload を primary truth にしない
- `market_summary` にすでに載っている summary / family rows / summary slots / active event rows を再利用する
- `health_digest` は prediction truth を作るためではなく、**caution を補助的に上書き・引き上げる** ためにだけ使う

---

## 5. current repo truth
### 実装済み shared file
- `btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_summary.py`

### export
- `btcts_next/src/btcts/processing/l4_consumer_models/shared/__init__.py`

### focused test
- `btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_summary_builder.py`

### current object
- `PredictionSummary`
- `PredictionSummaryBuildInput`
- `build_prediction_summary(...)`

---

## 6. current shape
### top-level object
```text
PredictionSummary
  prediction_type
  prediction_version
  source_kind
  market_uid
  event_ts
  freshness
  is_stale
  horizon
  confidence
  caution_level
  short_horizon_bias
  continuation_likelihood
  mean_reversion_likelihood
  regime_transition_risk
  liquidity_deterioration_risk
  execution_feasibility_hint
  evidence
  diagnostics
```

### build input
```text
PredictionSummaryBuildInput
  market_summary
  health_digest (optional)
  source_kind
  horizon
```

---

## 7. field draft
### identity / provenance
- `prediction_type`
  - `shared_prediction_summary`
- `prediction_version`
  - `phase3.v1alpha1`
- `source_kind`
  - 既定値は `market_summary_anchor`
- `market_uid`
- `event_ts`
- `freshness`
- `is_stale`

### horizon
- `horizon`
  - `micro`, `short`

### confidence / caution
- `confidence`
  - 0.0〜1.0
- `caution_level`
  - `low`, `medium`, `high`, `blocked`

### core outputs
- `short_horizon_bias`
  - `bullish`, `bearish`, `neutral`, `unknown`
- `continuation_likelihood`
  - `low`, `medium`, `high`, `unknown`
- `mean_reversion_likelihood`
  - `low`, `medium`, `high`, `unknown`
- `regime_transition_risk`
  - `low`, `medium`, `high`, `unknown`
- `liquidity_deterioration_risk`
  - `low`, `medium`, `high`, `unknown`
- `execution_feasibility_hint`
  - `favorable`, `caution`, `unfavorable`, `unknown`

### evidence
- `summary_source`
- `semantic_runtime_wiring_status`
- `orderbook_wiring_status`
- `interpretation_bucket`
- `trust_state`
- `continuity_state`
- `semantic_active_event_count`
- `orderbook_active_event_count`
- `orderbook_summary_slots_present`
- `orderbook_persistence_observable`
- `notable_events`
- `alert_candidates`
- `health_digest_present`
- `health_freshness` (optional)
- `health_is_stale` (optional)
- `health_semantic_observer_status` (optional)
- `health_orderbook_wiring_status` (optional)

### diagnostics
- wording-free な debug-safe field のみ
- `health_digest_present`
- `semantic_contract_rows_count`
- `orderbook_summary_slots_count`
- `orderbook_contract_status_source`

---

## 8. current reading rules
### `short_horizon_bias`
- summary-first に決める
- active event rows は補助証拠として使う
- single event 名に直接支配させない

### `continuation_likelihood`
- continuity / trust / persistence / active event rows から読む
- orderbook persistence が not observable のときは過信しない

### `mean_reversion_likelihood`
- support / resistance / near wall / imbalance 系 summary を証拠として読む
- event family row を意味 owner として再評価しない

### `regime_transition_risk`
- interpretation bucket / continuity caution / active event richness の揺れを主証拠にする

### `liquidity_deterioration_risk`
- orderbook summary slot presence / persistence_observable / active event count を証拠にする

### `execution_feasibility_hint`
- 実行判断そのものではない
- shared hint に留める

### `health_digest` の扱い
- primary truth を作るためには使わない
- stale / caution / broken observer のような **補助 caution evidence** としてのみ使う
- `market_summary` の reading を反転させる owner にはしない

---

## 9. non-goals
- prediction 文言の最終表示
- tactic suggestion
- order plan
- target price
- stop / take-profit
- execution automation
- warroom wording
- AI prose generation
- prediction observer UI

---

## 10. anti-pattern
- prediction で L3 meaning を再定義する
- Health caution をそのまま prediction truth に格上げする
- active event rows を full contract completion と誤認する
- UI payload shape を shared prediction shape にする
- first slice に tactic / execution / target を混ぜる

---

## 11. done definition
Phase 3 first slice の near-term done は次。

1. `market_summary` anchor で `PredictionSummary` が 1 本切れている
2. evidence / confidence / horizon が wording-free に載っている
3. optional `health_digest` は caution input に限定されている
4. Health / UI / decision / execution と責務混線していない
5. prediction observer / tactic / execution を混ぜていない
6. additive-first で将来拡張できる

---

## 12. 一言
Phase 3 の最初の一手は、
**`market_summary` を土台にした shared prediction read model を 1 本切り、必要なら `health_digest` を caution 補助入力としてだけ足すこと**
である。

ここで欲張らず、observer / decision / tactic / execution を分離したまま始めるのが最も安全である。
