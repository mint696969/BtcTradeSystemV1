# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_FAMILY_ROADMAP_2026-07-11.md
# desc: Canonical MarketRegime family roadmap from current implementation through the completion gate immediately before the next prediction family begins.

# Prediction System MarketRegime Family Roadmap

Updated: 2026-07-14 JST
Checkpoint: MARKET_REGIME_FAMILY_ROADMAP_ACCEPTED
Contract status: current

<!-- PS_MARKET_REGIME_FAMILY_ROADMAP_2026_07_11 -->

```text
market_regime_is_first_reference_family=true
market_regime_is_not_parent_engine=true
current_state_and_future_forecast_separated=true
not_a_toy_requirement=true
baseline_comparison_required=true
confidence_calibration_required=true
transition_model_required=true
next_family_blocked_until_completion_gate=true
perfect_forever_block_forbidden=true
```

## 1. Purpose

MarketRegime is the first and most important prediction-family vertical slice because it provides market-state context for strategy selection, risk posture, and later prediction families.

Its goal is not to produce plausible-looking cards. Its goal is to provide an explainable, traceable, replayable, calibrated, transition-aware market-state estimate and future-regime forecast that later families can safely consume.

MarketRegime must not become the parent inference engine or a god object. Common contracts proven by this family are promoted to the parent layer; regime definitions, feature interpretation, transition semantics, scoring, and invalidation remain family-owned.

## 2. Completion philosophy

The project must avoid two opposite failures:

```text
under-building:
  cards look plausible but predictions are not independently justified

over-building:
  MarketRegime is pursued indefinitely and blocks every later family
```

Completion is therefore staged.

```text
Level 1:
  explainable, traceable, replayable, baseline-comparable

Level 2:
  transition-aware, empirically calibrated, shadow-compared

Level 3:
  stable context contract for later families
```

The MarketRegime family is considered complete for roadmap progression when Levels 1, 2, and the Level 3 context contract are accepted. Further research may continue later without blocking the next family.

## 3. Fixed model separation

### 3.1 Current state estimator

The current market state must be estimated independently from future forecast labels.

Required input families:

```text
recent price structure
realized volatility
spread and depth
order-flow imbalance
microprice and microprice bias
liquidity replenishment/disappearance
cross-venue agreement
data freshness and source quality
change-point evidence
```

Required output:

```text
current_regime_state
state_probability_or_calibrated_reliability
state_age
state_started_at
change_point_probability
transition_candidate
supporting_evidence
conflicting_evidence
UNKNOWN_or_abstain_reason
```

The existing shortest-future-label-for-current behavior may remain only as a bounded compatibility fallback during migration. It is not the target current-state model.

### 3.2 Future regime forecast

Future forecasts are independent horizon-specific predictions for:

```text
5m
15m
30m
60m
6h
12h
24h
```

Each forecast must preserve:

```text
origin_current_state
target_horizon
predicted_future_state
transition_path_candidate
raw_model_score_or_probability
calibrated_reliability
invalidation_conditions
feature_snapshot_ref
model_id
logic_version
parameter_set_id
target_definition_version
```

Short and long horizons may use different models or feature weighting. Short microstructure evidence must not be silently projected into 6h-24h forecasts.

## 4. Canonical roadmap

### MR-F0 — Canonical contract and delivery foundation

This is the current MR-VS6 work.

```text
MR-VS6.1 common family read-model contract and validators
MR-VS6.2 MarketRegime projection
MR-VS6.3 receive-only prediction topic and routing
MR-VS6.4 push-primary / artifact-fallback selection
MR-VS6.5 WarRoom display integration
MR-VS6.6 broad guards and closeout
```

Required identity chain:

```text
run_id
prediction_id
model_id
logic_version
parameter_set_id
feature_set_version
target_definition_version
training_window_ref
evaluation_window_ref
source_refs
```

Acceptance:

```text
canonical read model validated
canonical receive-only push validated
artifact fallback preserved
UI does not infer or recalculate confidence
operator UI and prediction full suites pass without exclusions
```

### MR-F1 — Forecast-label provenance and target audit

Every current upstream `primary_label` source must be traced.

Required provenance:

```text
producer module
input sources
used features
formula or model
model and logic version
parameter set
training window
validation window
target definition
label thresholds
prediction origin timestamp
evaluation timestamp
lookahead controls
```

Deliverables:

```text
primary-label provenance report
feature-to-label dependency graph
target-definition contract
lookahead audit
use / fix / replace decision table
```

No untraceable upstream label may be treated as canonical future-regime truth.

### MR-F2 — Current-state estimator

Build a dedicated current-state estimator from current and recent market evidence.

Initial model should be transparent and deterministic, with bounded parameter sets and explicit missing-data behavior.

Acceptance:

```text
current state does not require a future label
feature contributions are traceable
change-point evidence is exposed
UNKNOWN is allowed
state age and start time are preserved
current-state outcome rule is defined
```

### MR-F3 — Explainable feature scoring

Create family-owned candidate scores such as:

```text
trend_score
range_score
breakout_score
high_vol_chop_score
compression_score
reversal_score
panic_score
```

Each score must decompose into:

```text
price_structure contribution
volatility contribution
liquidity contribution
orderflow contribution
cross_venue contribution
source_quality adjustment
```

Rules:

```text
missing feature is not silently treated as zero evidence
freshness and quality are separate dimensions
blockers differ from weak contradictory evidence
weights and thresholds are parameter-set fields
all final label decisions are explainable
```

### MR-F4 — Transition and persistence model

Market states are temporally persistent and must not churn without evidence.

Required mechanisms:

```text
minimum dwell time
hysteresis
transition penalty
change-point evidence
invalid-transition guard
state persistence probability
```

Initial explicit transition examples:

```text
RANGE -> LOW_VOL_COMPRESSION
LOW_VOL_COMPRESSION -> BREAKOUT
BREAKOUT -> UP_TREND | DOWN_TREND
TREND -> REVERSAL_WATCH
REVERSAL_WATCH -> RANGE | opposite TREND
TREND -> HIGH_VOL_CHOP
```

An explicit transition matrix may be the first implementation. HMM, Markov-switching, or Bayesian change-point candidates remain shadow models until they beat the transparent baseline.

### MR-F5 — Horizon-specific future forecast

Build separate future-regime forecasting for each enabled horizon.

Feature emphasis policy:

```text
5m-60m:
  microstructure, orderflow, short price structure, short realized volatility

6h-24h:
  broader price structure, session context, cross-venue context,
  longer volatility state, macro/context inputs when available
```

Acceptance:

```text
one horizon never borrows another horizon label silently
future labels preserve origin current state
transition path is explicit
invalid or missing evidence yields UNKNOWN / abstain
future outcome rule is horizon-specific
```

### MR-F6 — Mandatory simple-baseline comparison

Every candidate model must be compared over identical windows against:

```text
always RANGE
last state persists
recent return sign
simple MA slope
simple volatility threshold
current forecast-label selection implementation
```

Comparison dimensions:

```text
same source snapshot
same prediction origin
same horizon
same target definition
same outcome resolver
same missing-data periods
same evaluation window
```

Minimum metrics:

```text
accuracy
balanced accuracy
macro F1
Brier score
log loss
expected calibration error
coverage rate
UNKNOWN rate
avoidable UNKNOWN rate
transition detection delay
state churn
regime duration consistency
```

A more complex candidate does not become canonical unless it provides material benefit over simple baselines or a clearly documented operational benefit such as safer abstention.

#### MR-F6 delivery sequence and closeout plan

MR-F6 baseline comparison logic is implemented through the final pure execution boundary. The remaining work is deliberately separated from prediction scoring so execution safety can mature without changing forecast behavior.

```text
MR-F6.18 accepted:
  immutable request schema v4
  complete request-hash binding
  external expected-hash confirmation
  writer-scope confirmation
  pure final execution boundary
  no writer invocation or D-hot write

MR-F6.19:
  deterministic dry-run execution plan
  bind request, writer, destination, acknowledgements, and execution-time identity
  no writer invocation

MR-F6.20:
  dry-run writer invocation adapter
  exercise the exact public writer contract without modifying D-hot
  preserve disabled-by-default and one-shot boundaries

MR-F6.21:
  idempotency and duplicate-safe receipt contract
  distinguish absent, already-satisfied, and conflicting destination states

MR-F6.22:
  failure recovery and resume contract
  define partial-failure, retry, and fail-closed behavior

MR-F6.23:
  immutable audit and replay evidence
  preserve request, boundary, plan, result, and receipt identity

MR-F6.24 Integration & Hardening:
  responsibility and dependency audit
  unreachable and duplicate-contract audit
  request/hash/writer/destination identity audit
  public-interface freeze
  full-suite guards
  roadmap, architecture, philosophy, and gpt_room synchronization

MR-F6 closeout:
  publish accepted contracts, known gaps, rollback point, and handoff pack
```

MR-F6.24 is a mandatory quality gate, not optional cleanup. It adds no prediction shortcut, automatic promotion, broker path, scheduler, or live parameter mutation.

#### MR-F7 parallel-start condition

MR-F7 confidence-calibration work may begin after MR-F6.20 is accepted because calibration quality and execution-safety hardening have separate owners. Parallel work must obey these conditions:

```text
mr_f6_20_accepted=true
mr_f7_may_start_in_parallel=true
mr_f6_21_through_mr_f6_24_remain_mandatory=true
mr_f6_closeout_may_not_be_skipped=true
market_regime_ready_for_next_family=false
trend_bias_family_still_blocked=true
shared_contract_changes_require_cross-track_review=true
```

MR-F7 parallel start does not satisfy `MARKET_REGIME_READY_FOR_NEXT_FAMILY`. The next prediction family remains blocked until MR-F6 through MR-F10 and the family completion gate are accepted.

#### Thread-handoff readiness

A new development thread becomes preferred only after MR-F6 closeout and its architecture freeze are complete. Before handoff, the repository must contain enough canonical material that a new GPT can recover the same responsibility boundaries and safety posture without relying on conversation history.

Required handoff pack:

```text
MarketRegime architecture overview
prediction philosophy and non-toy requirements
MR-F6 execution-contract map
hardening checklist and accepted public interfaces
MR-F7 start guide and parallel-work boundaries
current roadmap and gpt_room state
known gaps, rollback point, and full-suite evidence
```

### MR-F7 — Confidence calibration

Displayed confidence must evolve from a heuristic support score toward empirical reliability.

Calibration dimensions:

```text
horizon
predicted regime
model_id
parameter_set_id
market session
volatility bucket
liquidity bucket
source-quality bucket
```

Target flow:

```text
raw model probability or score
  -> out-of-sample calibration
  -> sample-size shrinkage
  -> source/freshness cap
  -> displayed confidence
```

Required checks:

```text
reliability by confidence bucket
high-confidence miss concentration
overconfidence and underconfidence
sample sufficiency
long-horizon confidence caps
abstention quality
```

Displayed confidence must never be described as a calibrated probability until the relevant calibration guard passes.

### MR-F8 — Shadow model and parameter-set comparison

At minimum compare:

```text
A. explainable weighted-score model
B. transition/statistical model
```

Future candidates may include ML or ensemble models.

Governance:

```text
auto promotion forbidden
live parameter apply forbidden
human approval required
rollback required
same-window comparison required
condition-specific performance preserved
```

### MR-F9 — Review, outcome, and calibration evidence loop

Complete the operational improvement loop:

```text
prediction trace
  -> horizon expiry
  -> outcome resolution
  -> calibration summary
  -> WarRoom chart selection
  -> review_request
  -> human/GPT review_note
  -> review_link
  -> parameter/model review proposal
```

Review evidence may recommend changes but may not mutate canonical live parameters automatically.

### MR-F10 — Stable context contract for later families

MarketRegime must publish a family-neutral context that later families can consume without importing MarketRegime implementation details.

Required context fields:

```text
current_regime
current_state_reliability
state_age
state_stability
change_point_probability
future_regime_distribution_by_horizon
transition_risk
volatility_context
liquidity_context
source_quality_context
invalidation_hints
trace_refs
```

Example later-family use:

```text
trend_bias:
  suppress directional confidence in stable RANGE

breakout_false_break:
  increase attention during compression-to-breakout transition

reversal_zone:
  increase attention during mature trend plus change-point rise

liquidity_execution_quality:
  tighten caution during HIGH_VOL_CHOP or PANIC_SPIKE
```

MarketRegime context may condition another prediction. It must not directly grant trade permission.

## 5. Completion gate before the next family

The next prediction family must not begin until this gate is accepted:

```text
MARKET_REGIME_READY_FOR_NEXT_FAMILY
```

Required conditions:

```text
MR-F0 canonical read model and push path accepted
MR-F1 provenance and target audit accepted
MR-F2 current-state estimator accepted
MR-F3 explainable feature scoring accepted
MR-F4 transition and persistence behavior accepted
MR-F5 horizon-specific future forecasts accepted
MR-F6 simple-baseline comparison completed
MR-F7 confidence calibration accepted at defined maturity threshold
MR-F8 at least two models or parameter sets shadow-compared
MR-F9 outcome/review/calibration loop operational
MR-F10 stable context contract accepted
operator UI full suite clean
prediction full suite clean
no broker/AutoTrade/order connection
```

Completion does not require permanent research perfection. Remaining improvements must be classified as:

```text
non-blocking model research
additional feature enrichment
more sample accumulation
future calibration refinement
future ensemble candidate
```

These may continue after the next family starts, provided the stable context contract and accepted baseline remain backward compatible or are changed under the contract-change policy.

## 6. Next-family transition

The first family after MarketRegime remains:

```text
trend_bias
```

The transition checkpoint is:

```text
current_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
next_gate=TREND_BIAS_FAMILY_IMPLEMENTATION_READINESS
```

Before transition, a closeout must record:

```text
accepted model and parameter_set_id
accepted target definitions
accepted calibration maturity
baseline comparison summary
known bad conditions
known non-blocking gaps
stable context contract version
rollback point
full-suite evidence
```

## 7. Safety and non-goals

Throughout this roadmap:

```text
UI inference forbidden
UI confidence recalculation forbidden
broker/private API forbidden
AutoTrade trigger forbidden
order submission forbidden
parameter auto-promotion forbidden
live parameter apply forbidden
raw market payload in family read model forbidden
```

MarketRegime provides prediction context, not execution authorization.

## 8. Current start point

```text
reference_head=cf868d55
current_gate=MR_F6_FINAL_EXECUTION_BOUNDARY_ACCEPTED
next_gate=MR_F6_19_DRY_RUN_EXECUTION_PLAN
current_phase=MR-F6
mr_f5_complete=true
mr_f6_18_complete=true
mr_f6_writer_invoked=false
mr_f6_d_hot_modified=false
mr_f7_parallel_start_allowed=false
mr_f7_parallel_start_condition=MR_F6_20_ACCEPTED
mr_f6_24_hardening_required=true
market_regime_family_ready_for_next_prediction_family=false
implementation_started=true
```

MR-F6 accepted checkpoint:

```text
commit=cf868d55
request_schema=prediction.market_regime.origin_evidence_execution_request.mr_f6_17.v4
execution_boundary=prediction.market_regime.origin_evidence_execution_boundary.mr_f6_18.v1
market_regime_suite=314_passed
writer_invoked=false
d_hot_modified=false
scheduler_enabled=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
```

MR-F5 closeout:

```text
status=accepted
closeout=docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_OPERATIONAL_EVIDENCE_AND_CANONICAL_MIGRATION_REVIEW_CLOSEOUT_2026-07-14.md
canonical_promotion=deferred
reason=long_horizon_performance_and_candidate_non_separation
prediction_full_suite=461_passed
operator_ui_full_suite=1230_passed
```

## 9. Acceptance decision

```text
market_regime_family_roadmap_current=true
current_and_future_models_separated=true
forecast_provenance_required=true
feature_scoring_required=true
transition_model_required=true
simple_baseline_comparison_required=true
confidence_calibration_required=true
shadow_comparison_required=true
stable_context_contract_required=true
next_family_completion_gate_defined=true
market_regime_family_roadmap_accepted=true
```

## MR-VS6.1 closeout

```text
status=accepted
closeout=docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_VS6_1_CLOSEOUT_2026-07-11.md
prediction_full_suite=277_passed
next_gate=MR_VS6_2_MARKET_REGIME_PROJECTION_IMPLEMENTATION
```
