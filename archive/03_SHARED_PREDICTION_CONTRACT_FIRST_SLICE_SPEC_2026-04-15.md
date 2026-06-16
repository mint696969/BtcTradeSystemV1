# path: ./tmp/03_SHARED_PREDICTION_CONTRACT_FIRST_SLICE_SPEC_2026-04-15.md
# desc: Phase 3 shared prediction contract first-slice spec anchored on market_summary current truth.

更新日: 2026-04-15
位置づけ: `./tmp/` 正式仕様書候補 / Phase 3 entry first slice
対象: `market_summary` anchor を用いた shared-first prediction contract

---

## 1. この仕様書の目的
本仕様書は、Phase 3 の最初の 1 本目として切る
**shared prediction contract first slice**
の shape と boundary を固定するための文書である。

ここで大事なのは、prediction を

- L3 meaning owner の再実装
- Health v2 の延長
- decision / tactic / execution の先食い

として始めないこと。

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

### UI / observer がまだ owner でないもの
- prediction wording
- prediction observer page
- tactic / execution 表示都合

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

---

## 5. first slice shape
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
  evidence_version
  confidence
  caution_level
  continuation_likelihood
  mean_reversion_likelihood
  regime_transition_risk
  liquidity_deterioration_risk
  execution_feasibility_hint
  short_horizon_bias
  evidence
  diagnostics
```

---

## 6. field draft
### identity / provenance
- `prediction_type`
  - 例: `shared_prediction_summary`
- `prediction_version`
  - 例: `phase3.v1alpha1`
- `source_kind`
  - 例: `market_summary_anchor`
- `market_uid`
- `event_ts`
- `freshness`
- `is_stale`

### horizon
- `horizon`
  - 例: `micro`, `short`

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
- `evidence.summary_source`
- `evidence.semantic_runtime_wiring_status`
- `evidence.orderbook_wiring_status`
- `evidence.interpretation_bucket`
- `evidence.trust_state`
- `evidence.continuity_state`
- `evidence.semantic_active_event_count`
- `evidence.orderbook_active_event_count`
- `evidence.orderbook_summary_slots_present`
- `evidence.orderbook_persistence_observable`
- `evidence.notable_events`
- `evidence.alert_candidates`

### diagnostics
- wording-free な debug-safe field のみ

---

## 7. first-slice reading rules
### `short_horizon_bias`
- summary-first に決める
- active event rows は補助証拠として使う
- single event 名に直接支配させない

### `continuation_likelihood`
- continuity / trust / active event rows / persistence から読む
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
- caution / favorable / unfavorable の shared hint に留める

---

## 8. non-goals
- prediction 文言の最終表示
- tactic suggestion
- order plan
- target price
- stop / take-profit
- execution automation
- warroom wording
- AI prose generation

---

## 9. anti-pattern
- prediction で L3 meaning を再定義する
- Health caution をそのまま prediction に格上げする
- active event rows を full contract completion と誤認する
- UI payload shape を shared prediction shape にする
- first slice に tactic / execution / target を混ぜる

---

## 10. first implementation guidance
### まず作るもの
- `PredictionSummary`
- `PredictionSummaryBuildInput`
- `build_prediction_summary(...)`

### 想定配置
- `btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_summary.py`

### optional next
- thin adapter は consumer need が見えてから
- observer UI は Phase 3.5 以後でよい

---

## 11. done definition
Phase 3 first slice の near-term done は次。

1. `market_summary` anchor で `PredictionSummary` が 1 本切れている
2. evidence / confidence / horizon が wording-free に載っている
3. Health / UI / decision / execution と責務混線していない
4. prediction observer / tactic / execution を混ぜていない
5. additive-first で将来拡張できる

---

## 12. 一言
Phase 3 の最初の一手は、
**`market_summary` を土台にした shared prediction read model を 1 本切ること**
である。

ここで欲張らず、observer / decision / tactic / execution を分離したまま始めるのが最も安全である。
