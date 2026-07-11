# path: ./docs/strategy/PREDICTION_SYSTEM_INFERENCE_ENGINE_V1_ALIGNMENT_AND_ROADMAP_2026-07-09.md
# desc: Operator/GPT aligned Prediction Inference Engine v1 design, responsibility separation, parameter-set governance, GPT review loop, WS/push UI contract, and checkpoint roadmap. Spec-only; no runtime behavior change.
# Prediction Inference Engine v1 Alignment and Roadmap

Updated: 2026-07-09 JST
Profile: BtcTradeSystem
Mode: alignment specification / roadmap lock / no runtime behavior change / no UI behavior change

<!-- PS_INFERENCE_ENGINE_V1_ALIGNMENT_ROADMAP_2026_07_09 -->

```text
ps_inference_engine_v1_alignment_roadmap=true
operator_gpt_alignment_agreed=true
inference_engine_is_core_system=true
not_a_toy_requirement=true
responsibility_separation_required=true
folder_structure_alignment_required=true
parameter_sets_per_prediction_family_required=true
parameter_set_comparison_required=true
parameter_set_rollback_required=true
human_gpt_review_loop_required=true
warroom_chart_analysis_request_required=true
ws_push_ui_display_only_required=true
market_regime_first_family=true
implementation_before_alignment_forbidden=true
broker_send_enabled=false
order_intent_submitted=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
ui_render_invokes_classifier=false
```

## 1. Purpose

This document records the aligned design direction before implementation resumes.

The target is not a cosmetic prediction-card feature. The target is a strong, extensible, replayable, calibratable Prediction Inference Engine that becomes a core weapon of BtcTradeSystem while remaining non-executing until a separate future gate.

The engine must produce predictions, preserve why each prediction was made, allow later outcome review, allow parameter-set comparison and rollback, and support additional prediction families without mixing responsibilities with Collector, WarRoom UI, or AutoTrade.

This document is spec-only. It does not change runtime behavior, enable broker/API calls, enable AutoTrade, mutate live parameters, or change UI rendering.

## 2. Non-negotiable principles

```text
1. Responsibility separation is mandatory.
2. Folder structure must reflect responsibility separation.
3. The inference engine must not be a plausible-looking toy.
4. Each prediction family owns versioned parameter sets.
5. Parameter sets must be comparable and rollback-capable.
6. Human/GPT review is an evidence source for improvement, not an automatic live parameter mutator.
7. UI displays read models and push packets only; UI does not infer.
8. Collector collects and normalizes market data only; Collector does not predict.
9. AutoTrade remains disconnected until a separate explicit return gate.
10. All prediction outputs must be traceable, replayable, and calibratable.
```

## 3. System responsibility model

```text
Collector
  Owns exchange/public data collection, canonical market artifacts, health, freshness, and source-quality artifacts.
  Must not classify market regime, render prediction cards, trade, or mutate prediction parameters.

Prediction Inference Engine
  Owns source snapshots, feature bundles, signal votes, prediction family execution, parameter-set selection, traces, read models, outcomes, and calibration.
  Must not render UI, send orders, call broker/private APIs, start/stop Collector, or mutate AutoTrade ledgers.

Prediction Family
  Owns family-specific labels, features, signals, outcome rules, read-model fields, parameter sets, and calibration interpretation.
  Must use parent engine contracts.

WarRoom UI
  Owns display only. It may show read models, push packets, trace paths, status, and review helpers.
  Must not run feature builders, classifiers, source interpretation, parameter mutation, broker calls, or AutoTrade triggers.

Push bridge / widget runtime
  Owns transport from latest read models or producer packets to widget state and UI refresh.
  Must remain receive/display oriented for this phase.

Human / GPT review
  Owns explanation, manual review, hypothesis proposal, miss analysis, and parameter-review suggestions.
  Must not become the canonical live prediction source or auto-apply parameters.

Outcome / Calibration
  Owns post-horizon scoring, hit/partial/miss/invalidated/unknown resolution, parameter-set comparison, source/family/horizon analysis, and rollback recommendation evidence.
  Must not auto-promote parameter sets without a human gate.
```

## 4. Target folder structure direction

The current repository has useful prediction foundation code, including `btcts.prediction.market_regime`. The target direction is to make responsibility boundaries explicit without risky large moves at the start.

Recommended long-term structure:

```text
btcts_next/src/btcts/prediction/
  engine/
    contracts.py
    family_registry.py
    source_registry.py
    horizon_policy.py
    run_context.py
    read_model_contracts.py
    push_packet_contracts.py

  parameter_sets/
    registry.py
    lifecycle.py
    comparison.py
    rollback.py

  trace/
    prediction_trace.py
    source_refs.py
    evidence_refs.py

  outcome/
    outcome_ledger.py
    resolver_contracts.py

  calibration/
    summary.py
    parameter_review.py
    replay_comparison.py

  review/
    warroom_chart_analysis_request.py
    human_review_note.py
    review_link.py
    gpt_analysis_note.py

  families/
    market_regime/
      source_snapshot.py
      features.py
      signal_registry.py
      signal_scoring.py
      classifier.py
      artifact_projection.py
      outcome_rule.py
      parameter_sets.py
      producer.py

    trend_bias/
    reversal_zone/
    breakout_false_break/
    volatility_risk/
    liquidity_execution_quality/
    macro_cross_context/
    trigger_candidate/
```

Migration policy:

```text
Do not perform a broad package reshuffle first.
First lock contracts and audit current market_regime.
Then move or wrap modules only when there is a focused guard and clear benefit.
```

## 5. Parent engine contracts

The parent engine must own reusable contracts used by all families:

```text
PredictionFamilyRegistry
SourceRegistry
HorizonPolicy
SourceRefContract
FeatureBundleContract
SignalRegistryContract
ParameterSetRegistry
ParameterSetLifecycle
InferenceRun
PredictionTrace
OutcomeLedger
CalibrationSummary
HumanReviewReference
ReadModelContract
PushPacketContract
```

Each family must declare:

```text
prediction_family_id
family_label_ja
family_role
supported_horizons
default_enabled_horizons
source_requirements
feature_requirements
signal_registry_version
outcome_rule_version
parameter_set_registry_version
read_model_contract_version
push_widget_contract_version
safety_profile
```

## 6. Initial prediction families

The initial family list is aligned as follows. Implementation must proceed one family at a time, not all at once.

| Order | Family ID | Japanese role | Purpose | Initial status |
|---:|---|---|---|---|
| 1 | `market_regime` | 地合い予測 | classify current and future market regime | first canonical family; current implementation exists but must be audited |
| 2 | `trend_bias` | トレンド予測 | long/short/range/no-edge directional bias by horizon | future family |
| 3 | `reversal_zone` | 反転予測 | reversal candidates, zones, invalidation | future family |
| 4 | `breakout_false_break` | ブレイク/騙し | breakout continuation versus false break/trap | future family |
| 5 | `volatility_risk` | ボラ警戒 | volatility expansion/compression/shock risk | future family |
| 6 | `liquidity_execution_quality` | 流動性/約定品質 | spread, book stability, slippage/execution quality | future family |
| 7 | `macro_cross_context` | 外部環境 | cross-venue, macro/session/context sources | future family/context family |
| 8 | `trigger_candidate` | 将来候補 | future AutoTrade candidate output after separate gate | non-executing and deferred |

Supporting/context families from older specs, such as `cross_venue_confirmation`, `human_technical_structure`, `algorithmic_participant_footprint`, and `opportunity_participation`, may feed the above families as source/signal/context families rather than necessarily becoming first-level UI rows.

## 7. Horizon policy

Use a shared parent horizon policy with per-family enabled subsets.

Initial parent horizon candidates:

```text
current
5m   / 300s
15m  / 900s
30m  / 1800s
60m  / 3600s
6h   / 21600s
12h  / 43200s
24h  / 86400s
```

Family examples:

```text
market_regime: current, 5m, 15m, 30m, 60m, 6h, 12h, 24h
trend_bias: 5m, 15m, 30m, 60m
reversal_zone: current, 5m, 15m, 30m, 60m
liquidity_execution_quality: current, 5m, 15m
macro_cross_context: 60m, 6h, 12h, 24h
```

The horizon contract must preserve UTC timestamps, generated_at, expiry_at, timeframe_sec, and evaluation windows.

## 8. Parameter-set governance

Each prediction family must own versioned parameter sets. Parameter sets are not hidden constants.

Required parameter-set capabilities:

```text
family-specific registry
active parameter_set_id
candidate parameter_set_id
status: draft / shadow / paper / active / retired / rollback_candidate
created_at / created_by / reason
weights
thresholds
source reliability settings
horizon-specific weights
confidence caps
invalidation thresholds
supported horizons
calibration summary reference
human/GPT review references
```

The operator goal is explicitly supported:

```text
GPT and human analysis can propose parameter changes.
The operator can save multiple parameter sets.
The system can compare parameter sets by family/horizon/regime/outcome.
If a change worsens results, the operator can roll back to a previous set.
```

Hard safety rule:

```text
No GPT analysis, calibration job, or UI interaction may auto-promote or auto-apply live parameters without a separate human approval gate.
```

### 8.1 Regime/time applicability and performance memory

<!-- PS_PARAMETER_SET_REGIME_TIME_APPLICABILITY_ADDENDUM_2026_07_09 -->

A parameter set is not simply `good` or `bad`. It must preserve where and when it worked.

Each parameter set should be able to carry applicability and performance metadata such as:

```text
intended_market_regimes
  e.g. RANGE, UP_TREND, DOWN_TREND, HIGH_VOL_CHOP, LOW_VOL_COMPRESSION

intended_session_or_time_windows
  e.g. Tokyo morning, Europe open, US session, weekend, high-liquidity window, low-liquidity window

validated_market_regimes
  regimes where outcome/calibration evidence shows the set performed acceptably

validated_time_windows
  date ranges, session windows, and volatility/liquidity conditions where the set performed acceptably

known_bad_conditions
  regimes, sessions, source-quality states, volatility states, or liquidity states where the set degraded

sample_size_by_condition
  enough evidence count by family / horizon / regime / session / source-quality bucket

performance_by_condition
  hit / partial / miss / invalidated / unknown, calibration score, overconfidence, underconfidence

recommended_usage_policy
  active_candidate | shadow_only | avoid_in_condition | rollback_candidate | retired

operator_notes / gpt_review_refs
  human/GPT analysis references explaining why the set was created, adjusted, kept, or rolled back
```

This enables regime-aware and session-aware strategy selection later:

```text
A range-tuned parameter set may be preferred during stable RANGE conditions.
A breakout-sensitive set may be shadow-tested during BREAKOUT_WATCH or range-edge pressure.
A liquidity-defensive set may be preferred during thin book / wide spread conditions.
A parameter set that performed well in one period must not be assumed to work in all future regimes.
```

The engine must support comparing multiple parameter sets over the same historical windows and over condition-filtered windows.

Minimum comparison dimensions:

```text
prediction_family
horizon
predicted_regime
observed_regime
market_session
date_range
volatility_state
liquidity_state
source_quality_state
parameter_set_id
confidence_bucket
review_note_refs
```

The UI may later show this as parameter-set evidence, but selection/apply remains a separate human-gated operation.

## 9. Parameter-set improvement loop

The intended improvement loop is:

```text
1. Engine emits prediction with parameter_set_id and trace.
2. WarRoom shows prediction read model.
3. Operator selects chart point/range and asks GPT for analysis.
4. GPT/human analysis is stored as review evidence.
5. Outcome resolver scores expired predictions.
6. Calibration aggregates hit/partial/miss/invalidated/unknown by family, horizon, regime, and parameter_set.
7. A parameter-review proposal is created.
8. Operator saves a candidate parameter set.
9. Candidate runs in shadow/paper comparison.
10. Operator promotes, keeps testing, or rolls back.
```

Parameter-set comparison must support at least:

```text
same time window comparison
family + horizon comparison
regime-specific comparison
time-period / session-specific comparison
volatility/liquidity condition comparison
source-quality condition comparison
confidence bucket comparison
overconfidence / underconfidence analysis
miss reason analysis
known-good / known-bad condition extraction
rollback recommendation evidence
```

The system should be able to answer practical operator questions:

```text
Which parameter set worked best in RANGE during the last 7 days?
Which parameter set degraded during HIGH_VOL_CHOP?
Which parameter set works during Tokyo session but fails during US session?
Which set is best for 5m trend_bias but weak for 30m?
Which set should be retired, kept as shadow, promoted, or rolled back?
```

## 10. WarRoom chart analysis request / Human-GPT review loop

The existing WarRoom chart copy JSON, currently shaped as `warroom_chart_analysis_request.2026_07_06.v2_interactive_selection`, is part of the engine-growth design.

It must be treated as a lightweight human/GPT review input packet, not merely a UI convenience.

Required semantics:

```text
selection_origin = warroom_v2_interactive_candlestick_chart
selection_type = single_candle | range
selected_range.start_ts_utc / end_ts_utc are canonical UTC lookup anchors
candle_ts_semantics = bucket_start_utc
lookup_key = time_utc
source hot root = D:/btc_ts_hot
cold root = E:/btc_ts only when explicitly requested
preferred source = D-hot derived L4 candle store first
safety = read_only / manual_review_only / no prediction invocation / no classifier invocation / no broker
```

The request must preserve source relpaths such as:

```text
data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/closed.jsonl
data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/forming.json
data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/meta.json
data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/update_state.json
```

## 11. Review artifacts

Recommended artifact family:

```text
prediction/review_requests/date=YYYY-MM-DD/*.json
prediction/review_notes/date=YYYY-MM-DD/*.json
prediction/review_links/date=YYYY-MM-DD/part-00001.jsonl
```

`review_request` stores the copied chart-selection request.

`review_note` stores structured GPT/human analysis, for example:

```text
review_note_id
review_request_id
analyzed_at_utc
selected_range
observed_pattern
market_regime_interpretation
trend_interpretation
reversal_clues
breakout_false_break_clues
volatility_comment
liquidity_comment
disagreement_with_engine
suggested_parameter_review
confidence_in_review
safety
```

`review_link` connects review evidence to predictions and outcomes:

```text
review_request_id
review_note_id
related_run_ids
related_prediction_ids
related_families
relation_type
selected_range_start_utc
selected_range_end_utc
```

Allowed `relation_type` examples:

```text
evidence_before_prediction
prediction_context
post_prediction_outcome_review
manual_correction
miss_reason_analysis
parameter_tuning_hint
```

## 12. WS / push / UI display contract

The target display flow is:

```text
Prediction producer
  -> latest artifacts / read models
  -> prediction push packet
  -> WarRoom widget store/session state
  -> UI card renderer
```

UI must display only. UI may have a fallback artifact read path for operator visibility, but the primary target is push-packet driven display.

Family card layout direction:

```text
Market Regime row
  current / 5m / 15m / 30m / 60m / 6h / 12h / 24h cards

Trend Bias row
  enabled horizon cards

Reversal Zone row
  enabled horizon cards

Breakout / False Break row
  enabled horizon cards

Volatility Risk row
  enabled horizon cards

Liquidity / Execution Quality row
  enabled horizon cards
```

Each card surface should remain compact:

```text
family label
horizon label
primary label
confidence/reference strength percent
short tag
freshness badge
evidence quality border/background
```

Details can include:

```text
reason lines
conflict lines
invalidation lines
source contributions
parameter_set_id
trace path
outcome/calibration status
review links
```


## 12.1 Family scenario parts and parent scenario guidance
<!-- PS_FAMILY_SCENARIO_PART_CONTRACT_V1_ROADMAP_2026_07_10 -->

WarRoom section `3. Inference scenario guidance` must ultimately show a parent-composed scenario guidance read model, not a single-family caption and not UI-generated logic.

Each prediction family must produce a scenario part:

```text
market_regime scenario part
trend_bias scenario part
reversal_zone scenario part
breakout_false_break scenario part
volatility_risk scenario part
liquidity_execution_quality scenario part
macro_cross_context scenario part
trigger_candidate scenario part, deferred and non-executing
```

The parent inference engine owns the composition step:

```text
family scenario parts -> parent scenario guidance read model -> WarRoom display
```

Rules:

```text
A family may describe its own scenario contribution.
A family must not decide the whole scenario alone.
The parent engine resolves dominant/supporting/conflicting parts.
The UI displays the parent read model only.
The UI must not run family classifiers or combine evidence itself.
No scenario part grants trade permission.
```

This is required for every prediction family and for every future extension of the inference engine.

## 13. Current MarketRegime status and audit stance

Current MarketRegime artifacts exist in D-hot and are visible in WarRoom. However, they must not be treated as complete without audit.

Known current observations:

```text
D:/btc_ts_hot/prediction/market_regime/latest_cards.json exists.
It currently emits 8 horizon cards.
Recent visible output is mostly RANGE / 70% or 78%.
It references forecast_records from prediction/runs/2026-07-02/132020_generated_at_2026-07-02T13_20_20Z/forecast_records.jsonl.
The loop appears to run with Collector, but source freshness and logic quality require review.
```

Audit questions:

```text
Why are outputs mostly RANGE / 70%?
Which signals actually drive each card?
Are signal scores dominated by source_quality only?
Is old forecast_records dependency acceptable, temporary, or a defect?
Does latest D-hot L4 candle/market-state data drive current reasoning?
Are traces sufficient for GPT/human review?
Are outcome/calibration scores self-referential or genuinely future-horizon based?
Can the family be converted to the parent contract without broad UI changes?
```

## 13.1 Canonical MarketRegime family roadmap

The current authoritative MarketRegime family roadmap is:

`docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_FAMILY_ROADMAP_2026-07-11.md`

It defines the separation of current-state estimation and future-regime forecasting, forecast-label provenance audit, explainable feature scoring, transition modeling, simple-baseline comparison, confidence calibration, shadow comparison, and the completion gate immediately before `trend_bias` begins.

The detailed MarketRegime phases in this document remain historical alignment context where they differ. The dedicated family roadmap is authoritative for current MarketRegime execution order and completion criteria.

## 14. Roadmap and checkpoints

### Phase 0: Alignment spec and roadmap lock

Done when:

```text
This document exists.
Operator and GPT agree on responsibility separation, family list, parameter-set governance, GPT review loop, push/UI boundary, and no-toy requirement.
No runtime behavior changes are made.
```

### Phase 1: Current MarketRegime audit

Deliverables:

```text
MarketRegime file/source/artifact inventory
source dependency report
RANGE/70% cause report
trace/outcome/calibration trust report
use/fix/discard table
```

Checkpoint:

```text
Do not modify prediction logic until the audit identifies exactly what is reusable.
```

### Phase 2: Parent engine contract skeleton

Deliverables:

```text
family registry contract
horizon policy contract
parameter-set lifecycle contract
read model contract
push packet contract
review request/link/note contract
```

Checkpoint:

```text
Contracts compile and have fixture validation.
No live producer change yet.
```

### Phase 3: MarketRegime v1 correction

Deliverables:

```text
source snapshot corrected or explicitly bounded
feature bundle verified against latest D-hot sources
signal scoring explainable
parameter_set_id attached everywhere
trace row complete
latest_cards/read_model/status valid
```

Checkpoint:

```text
MarketRegime output is not fixed-looking RANGE/70% without evidence.
UNKNOWN is allowed when evidence is insufficient.
```

### Phase 4: Push packet connection

Deliverables:

```text
MarketRegime read model to prediction push packet
WP13/context-card replacement or wrapper with true prediction packet
UI renderer displays packet only, with artifact fallback clearly labeled
```

Checkpoint:

```text
UI does not run inference and does not reinterpret sources.
```

### Phase 5: Review loop artifacts

Deliverables:

```text
WarRoom chart analysis request can be stored as review_request
GPT/human analysis can be stored as review_note
review_link can connect notes to prediction ids and outcomes
```

Checkpoint:

```text
A selected chart range can be tied to prediction trace and later outcome/calibration.
```

### Phase 6: Outcome and calibration loop

Deliverables:

```text
expired prediction outcome resolver
family/horizon/regime/parameter_set calibration summary
overconfidence/underconfidence report
rollback comparison support
```

Checkpoint:

```text
Operator can compare parameter sets and identify rollback candidates.
```

### Phase 7: Next family one-by-one

Initial order:

```text
trend_bias
reversal_zone
breakout_false_break
volatility_risk
liquidity_execution_quality
macro_cross_context
trigger_candidate last and non-executing
```

Checkpoint:

```text
No new family is added until the previous family satisfies trace/outcome/calibration/read-model requirements.
```


## 14.1 Roadmap refinement: MarketRegime vertical-slice development policy

<!-- PS_MARKET_REGIME_VERTICAL_SLICE_ROADMAP_REFINEMENT_2026_07_10 -->

Updated: 2026-07-10 JST
Mode: roadmap refinement / doc-only / no runtime behavior change / no UI behavior change

This section refines how Phase 2 through Phase 7 should be executed after the evidence-source confidence contract and parent scenario guidance work.

The project must **not** try to complete a giant all-family prediction design matrix before implementation. That would be over-designed and detached from real D-hot evidence, real cards, real outcomes, and real calibration behavior.

Instead, treat MarketRegime as the first/reference vertical slice:

```text
market_regime = reference family / first vertical slice
```

Build the real MarketRegime evidence profile, display confidence, source reliability, outcome, calibration, and WarRoom explanation path first. While doing this, classify every discovered component into one of four layers:

```text
1. Parent inference / all-family common
   - display confidence estimator
   - confidence calibration
   - source reliability
   - source scorecards
   - horizon confidence caps
   - source agreement
   - outcome/calibration scoring contracts
   - WarRoom confidence semantics

2. Many-family common
   - evidence source weight profiles
   - source priority policy
   - blocker/veto semantics
   - freshness gates
   - quality gates
   - read-only review packets

3. Some-family common
   - trend/reversal/breakout shared structure logic
   - volatility/liquidity shared risk caps
   - macro/session/context helpers

4. Family-specific
   - MarketRegime state definitions
   - MarketRegime source interpretation
   - MarketRegime-specific blockers
   - MarketRegime-specific card labels and traces
```

MarketRegime is central because it influences all other prediction families, but it must not become the parent inference engine or a god object.

During every MarketRegime implementation slice, ask:

```text
Is this truly MarketRegime-specific,
or should it move to parent/common prediction logic?
```

### 14.1.1 Current completed parent/common foundation

As of 2026-07-10, the following parent/common confidence foundation exists:

```text
commit=fc64d1d8 prediction: add evidence source confidence contract
module=btcts_next/src/btcts/prediction/evidence_sources.py
contract=prediction.evidence_source_weight_profile.2026_07_10.v1
confidence_model_owner=parent_common_prediction_layer
```

The contract includes:

```text
evidence source descriptors
family/horizon/parameter_set scoped weight profiles
source reliability percent
signal strength percent
freshness/quality percent
source agreement
display confidence estimator
horizon confidence caps
card interval calibration policy
no raw payload duplication guard
no broker/AutoTrade/order/parameter auto-apply safety flags
```

Displayed confidence is common/parent-owned, not family-specific.

Family-specific logic owns:

```text
source selection
source direction
signal strength
family-specific blockers
family scenario state
```

Parent/common prediction logic owns:

```text
source weight contract
source reliability percent
source agreement
freshness/quality adjustment
horizon confidence cap
display confidence percent
calibration to the next same-family same-horizon card
```

Reason:

```text
MarketRegime 80%, TrendBias 80%, Reversal 80%, etc. must have the same meaning in WarRoom.
Family results differ, but displayed confidence scale must be comparable across families.
```

### 14.1.2 Confidence semantics

Displayed confidence is not prophecy.

For a family/horizon card, confidence means:

```text
How much the current evidence supports this card result
until the next same-family same-horizon card is produced.
```

Calibration target:

```text
current card -> next same-family same-horizon card interval
```

Predictions may change before a larger horizon resolves. Source invalidation, stale evidence, spread/quality deterioration, regime shift, or fresh contradictory evidence may reduce confidence or change the card before the broader horizon completes.

Default confidence caps should be higher near now and lower farther out:

```text
nowcast:       99
short_horizon: 92
mid_horizon:   82
long_horizon:  68
context:       60
```

Do not use raw hit rate directly as confidence. Source reliability must eventually consider:

```text
sample count / shrinkage
recency
regime-specific performance
horizon-specific performance
Brier score
log loss
calibration error
payoff/risk impact where applicable
unknown/abstain behavior
```

### 14.1.3 Revised interpretation of phases

Phase 2 is no longer just abstract contract skeleton work. It now includes already-started parent/common confidence contracts:

```text
completed:
  evidence source confidence contract
  parent-owned display confidence semantics
  card interval calibration policy
  source reliability/weight profile foundation
```

Phase 3 should be executed as a MarketRegime vertical slice, not merely a one-off correction:

```text
MarketRegime default evidence profile
MarketRegime currentness/staleness gates
MarketRegime card confidence via parent/common estimator
MarketRegime source scorecard/read model
MarketRegime outcome/calibration loop
WarRoom read-only confidence decomposition
```

Phase 7 must remain blocked until MarketRegime has exercised the core pattern:

```text
evidence source profile
display confidence estimator
source reliability / scorecard
outcome and calibration loop
WarRoom confidence explanation
```

Do not implement TrendBias/Reversal/Breakout/etc. before the MarketRegime vertical slice proves the common confidence/calibration pattern.

### 14.1.4 Immediate roadmap insertion

The next roadmap steps should be:

```text
MR-VS1: MarketRegime default evidence profile
  - pure/read-only module
  - uses btcts.prediction.evidence_sources
  - no D-hot write
  - no producer restart
  - no WarRoom change initially
  - no classifier/prediction invocation
  - no broker/AutoTrade/order/parameter mutation

MR-VS2: MarketRegime currentness and stale-source gates
  - prevent stale forecast_records from being treated as live truth
  - expose stale-source confidence caps/blockers
  - allow UNKNOWN/risk-off instead of plausible but unsupported cards

MR-VS3: MarketRegime card confidence integration
  - use parent/common display confidence estimator
  - keep family logic responsible for direction/signal/blockers only
  - attach confidence decomposition to read model/trace

MR-VS4: MarketRegime source scorecard and calibration read model
  - score source reliability by family/horizon/parameter_set/source
  - include sample count, recency, calibration quality, and regime-specific performance
  - no auto-promotion or live parameter apply

MR-VS5: WarRoom read-only confidence explanation
  - show display confidence and decomposition
  - show applied caps, blockers, freshness, source agreement
  - UI remains display-only
```

This refinement supersedes any interpretation that Phase 2 requires completing all parent contracts before MarketRegime implementation continues. The correct approach is planned vertical-slice development: implement MarketRegime first, extract common parts only when the slice proves they are useful, and preserve safety/read-only boundaries throughout.


### 14.1.5 Decision guardrails before continuing MarketRegime implementation

<!-- PS_MARKET_REGIME_VERTICAL_SLICE_DECISION_GUARDRAILS_2026_07_10 -->

The project should not decide every family-specific prediction method before implementation. However, the following guardrails must be fixed before continuing the MarketRegime vertical slice so future GPT/developer work does not drift.

#### Outcome semantics

Outcome scoring must distinguish:

```text
correct
incorrect
partial
unknown / abstain
risk_off / blocked
stale / invalidated
```

`unknown`, `risk_off`, or blocked states must not be automatically treated as failures. Avoiding low-quality predictions is part of prediction quality. The exact scoring formula can evolve, but the outcome read model must preserve enough labels to analyze abstain/unknown behavior separately from wrong directional calls.


#### Unknown / abstain discipline

<!-- PS_MARKET_REGIME_VERTICAL_SLICE_UNKNOWN_ABSTAIN_DISCIPLINE_2026_07_10 -->

`unknown`, `no_edge`, `risk_off`, and blocked states are allowed because avoiding low-quality predictions is part of prediction quality. However, they must not become a way to hide weak logic or inflate apparent accuracy.

Core rule:

```text
unknown is not a safe-looking trash bucket.
unknown must be earned by explicit evidence failure, contradiction, invalidation, or quality/risk gate.
```

Every non-directional or blocked card must carry enough metadata for later audit:

```text
state
reason_code
blocking_source_ids
missing_required_source_ids
stale_source_ids
conflicting_source_ids
quality_failure_ids
confidence_before_block
applied_confidence_cap
recovery_condition
```

Allowed reasons include:

```text
required_source_missing
required_source_stale
source_quality_failed
source_freshness_invalid
high_weight_source_conflict
confidence_below_minimum_after_calibration
risk_off_gate_active
blocker_or_veto_source_active
insufficient_sample_for_reliability
```

Disallowed reasons:

```text
unknown_without_reason
unknown_to_avoid_accountability
unknown_because_model_has_no_logic_yet
unknown_when_required_sources_are_fresh_and_aligned
```

Outcome/scorecard must track both prediction quality and coverage:

```text
coverage_rate
unknown_rate
blocked_rate
avoidable_unknown_count
valid_unknown_count
missed_opportunity_after_unknown
```

A valid unknown should not be punished like a wrong directional call. But excessive or avoidable unknowns are a quality failure. If a family/horizon produces too many unknown cards, the system must treat it as an implementation/calibration problem, not as success.

When reviewing reliability, separate:

```text
directional correctness
calibration quality
coverage quality
abstain/unknown quality
```

This preserves the intended behavior: only truly judgment-impossible states become unknown, while the system is still pressured to make useful, well-calibrated predictions when evidence is good enough.

#### Scorecard granularity

Source reliability must be tracked at least by:

```text
prediction_family_id
horizon_key
horizon_group
parameter_set_id
source_id
```

Do not collapse reliability into a single global score. A source can be strong for one family/horizon/regime and weak for another.

#### Confidence semantics

Displayed confidence remains parent/common-owned and means:

```text
confidence in the current card result until the next same-family same-horizon card
```

It is not prophecy and not a claim that the broader market will move in a straight line for the whole horizon.

#### Parameter-set mutation policy

Even if outcome/calibration analysis suggests better source weights or reliability defaults:

```text
no auto-promotion
no live parameter apply
no producer-side mutation without explicit human gate
```

Preferred flow:

```text
analysis -> shadow parameter_set -> comparison/read model -> human review -> explicit commit/apply slice
```

#### Confidence is not action permission

Display confidence must not be used as direct order permission, position size, or AutoTrade trigger.

```text
99% confidence != enter trade
```

Action, if ever added in the future, must be separately gated by expected value, liquidity, risk, drawdown, execution quality, and explicit human-approved trading policy.

#### MarketRegime must not become a god object

MarketRegime is the reference family and first vertical slice. It is allowed to reveal new common requirements. But whenever MarketRegime implementation adds a new mechanism, classify it as:

```text
parent/all-family common
many-family common
some-family common
market_regime-specific
```

Promote common confidence, scorecard, calibration, source reliability, and display semantics to parent/common modules rather than leaving them hidden under `prediction/market_regime`.

## 15. Explicit non-goals

```text
Do not make UI prediction logic.
Do not make GPT analysis canonical live prediction.
Do not auto-apply GPT-suggested parameters.
Do not auto-promote calibration candidates.
Do not connect AutoTrade.
Do not call broker/private APIs.
Do not append order/decision ledgers.
Do not optimize for pretty cards before trace/outcome/calibration.
Do not hide UNKNOWN/no-edge results.
Do not call a family complete because it renders plausible cards.
```

## 16. Immediate next task

The next implementation task after this spec is not UI work.

```text
PS-INFERENCE_ENGINE_MARKET_REGIME_AUDIT
```

Scope:

```text
Read current MarketRegime code and D-hot artifacts.
Produce a use/fix/discard audit and a correction plan.
No logic rewrite until the audit is accepted.
```
