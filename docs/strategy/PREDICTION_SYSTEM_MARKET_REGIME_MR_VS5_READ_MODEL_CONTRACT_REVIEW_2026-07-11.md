# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_VS5_READ_MODEL_CONTRACT_REVIEW_2026-07-11.md
# desc: Defines the MR-VS5 read-only MarketRegime explanation contract before implementation.
# Prediction System MarketRegime MR-VS5 Read-Model Contract Review

Updated: 2026-07-11 JST
Mode: contract review / no runtime behavior change / no D-hot write / no UI render change
Checkpoint: MR_VS5_READ_MODEL_CONTRACT_REVIEW

<!-- PS_MARKET_REGIME_MR_VS5_READ_MODEL_CONTRACT_REVIEW_2026_07_11 -->

```text
mr_vs5_read_model_contract_review=true
market_regime_only=true
ui_reads_read_models_only=true
ui_prediction_invoked=false
ui_classifier_invoked=false
ui_raw_market_read=false
ui_confidence_recalculation=false
ui_parameter_mutation=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_intent_submitted=false
parameter_auto_promotion_allowed=false
live_parameter_apply_allowed=false
no_code_change=true
no_D_hot_write=true
no_producer_restart=true
no_UI_render_change=true
```

## 1. Purpose

This document fixes the MR-VS5 contract before implementing the WarRoom confidence/evidence explanation panel.

The purpose is not to change MarketRegime inference, confidence values, parameter sets, producer behavior, or D-hot artifacts. The purpose is to define which existing artifact owns each display value, how the UI must interpret it, which fields are still missing, and how the implementation will remain read-only and non-executing.

## 2. Current verified boundary

Current WarRoom reader:

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
```

Current direct inputs:

```text
prediction/market_regime/latest_cards.json
prediction/market_regime/calibration/latest_read_model.json
prediction/market_regime/parameter_set_comparison/latest_read_model.json
prediction/scenario_guidance/latest_read_model.json
```

Planned additional read-only inputs for MR-VS5 explanation:

```text
prediction/market_regime/latest_read_model.json
prediction/market_regime/source_scorecard/latest_current_primary.json
```

The UI must not read raw market artifacts to reconstruct prediction meaning. It must not call a classifier, feature builder, confidence estimator, calibration calculator, source reliability calculator, or parameter comparison engine during render.

## 3. Existing UI and artifact observations

The currently displayed short-horizon cards show legacy display confidence while shadow diagnostics exist in the artifact.

```text
display_confidence_replaced=false
shadow_confidence_only=true
```

Therefore:

```text
current display confidence remains canonical for card surface
shadow confidence remains diagnostic only
shadow confidence must not replace display confidence in MR-VS5
future confidence replacement requires a separate reviewed slice
```

The current artifact/UI can also show an apparently live card while one or more forecast records are stale. These are different freshness domains and must not be represented by one ambiguous badge.

## 4. Contract decisions locked before implementation

### 4.1 Display confidence and shadow confidence

The following values are separate concepts:

```text
display_confidence_percent
legacy_confidence_percent
shadow_display_confidence_percent
confidence_cap_percent
calibration_score
source_reliability_percent
estimated_signal_strength_percent
```

Rules:

```text
display_confidence_percent is the current card-surface value
shadow_display_confidence_percent is diagnostic only
calibration_score is not win rate and not prediction accuracy
source_reliability_percent is historical source evidence, not current-card confidence
estimated_signal_strength_percent is not automatically interchangeable with regime confidence
no value may be substituted for another in the UI adapter
```

### 4.2 UNKNOWN semantics

`UNKNOWN` is a valid safety classification.

The current `UNKNOWN / 15%` display remains unchanged in this slice. MR-VS5 only documents and displays the reason chain.

The adapter must distinguish:

```text
classification=UNKNOWN
classification_confidence_percent
prediction_unavailable_or_blocked
estimated_signal_strength_percent
blocker_reason_codes
warning_reason_codes
```

A future change from `UNKNOWN / 15%` to another numeric policy requires a separate inference-contract and UI-contract review.

### 4.3 Freshness domains

The following freshness domains must remain separate:

```text
artifact_freshness
prediction_generated_freshness
source_snapshot_freshness
forecast_record_freshness
market_snapshot_freshness
```

`LIVE` must never imply that every source is fresh.

The explanation packet must expose the specific stale or missing domain and the associated age/reason when available.

### 4.4 Source semantics

The following fields must never be collapsed into one generic contribution percentage:

```text
configured_weight
current_signal_contribution
current_signal_direction
current_signal_strength
current_quality
current_freshness
historical_reliability
trusted_sample_count
ready
```

Source direction values:

```text
supporting
contradicting
neutral
unavailable
not_ready
```

### 4.5 Calibration semantics

Calibration display must include explicit wording equivalent to:

```text
calibration score is an early evaluation statistic, not win rate
sample count is required context
hit / partial / miss counts are shown separately
parameter-set count is shown
current and legacy cohorts remain separated
```

The current-primary state is not sufficient to claim a mature or stable accuracy estimate.

### 4.6 Parameter-set comparison

When only one trusted parameter set exists:

```text
comparison_ready=false
comparison_state=insufficient_parameter_sets
best_parameter_set_claim_allowed=false
promotion_recommendation_allowed=false
auto_promotion_allowed=false
```

The UI may show the active parameter-set ID and comparison blockers. It must not declare the active set superior.

### 4.7 Not-ready sources

Not-ready sources must remain visible.

Current required representation:

```text
source_id=market_regime.price_structure
ready=false
trusted_sample_count=0
minimum_trusted_sample_count=20
remaining_trusted_samples=20
```

The source must not be hidden, inferred from another source, or treated as calibrated.

## 5. Artifact ownership map

| Display concern | Canonical source | Notes |
|---|---|---|
| Card label | `latest_cards.json` | Current card surface value |
| Card display confidence | `latest_cards.json` | Do not replace with shadow value |
| Card short tag / surface warnings | `latest_cards.json` | Compact surface only |
| Detailed confidence decomposition | `latest_read_model.json` | Read-only explanation |
| Current supporting/conflicting evidence | `latest_read_model.json` and card detail fields | Preserve reason codes and trace refs |
| Source current quality/freshness | `latest_read_model.json` | Current-run evidence state |
| Source historical reliability/readiness | `source_scorecard/latest_current_primary.json` | Outcome-based evidence |
| Outcome/calibration summary | `calibration/latest_read_model.json` | Never label as win rate |
| Parameter-set comparison state | `parameter_set_comparison/latest_read_model.json` | Fail closed when insufficient |
| Parent scenario guidance | `scenario_guidance/latest_read_model.json` | Parent-owned; UI does not merge family meaning |
| Trace link | card/read-model trace refs | No raw market duplication |
| Safety state | artifact safety blocks and UI hard guard | All execution flags remain false |

## 6. Proposed WarRoom explanation packet

The adapter should normalize source artifacts into one immutable display packet.

```text
MarketRegimeExplanationPacket
  schema_version
  generated_at
  horizon_key
  card
    label
    label_ja
    display_confidence_percent
    short_tag
    freshness_badge
  confidence
    display_confidence_percent
    shadow_confidence_percent
    shadow_only
    display_replaced
    cap_percent
    cap_reasons
    estimated_signal_strength_percent
    explanation_lines
  evidence
    evidence_quality
    dominant_evidence_tier
    supporting
    contradicting
    neutral
  sources[]
    source_id
    direction
    configured_weight
    current_signal_strength
    quality
    freshness
    historical_reliability_percent
    trusted_sample_count
    minimum_trusted_sample_count
    ready
    not_ready_reason
  blockers[]
  warnings[]
  fallbacks[]
  outcome
    cohort
    sample_count
    hit
    partial
    miss
    invalidated
    unknown
  calibration
    score
    sample_count
    interpretation=not_win_rate
  parameter_set
    active_parameter_set_id
    trusted_parameter_set_count
    comparison_ready
    comparison_blockers
    auto_promotion_allowed=false
  trace
    run_id
    prediction_id
    trace_refs
  safety
    read_only=true
    prediction_invoked=false
    classifier_invoked=false
    raw_market_read=false
    broker_private_api_allowed=false
    autotrade_trigger_allowed=false
    order_intent_submitted=false
```

## 7. Warning taxonomy

MR-VS5 uses the following display taxonomy without changing producer reason codes:

```text
info
  informational state; no quality degradation implied

degraded
  data exists but quality/freshness is reduced

blocked
  prediction or label selection is prevented

fallback
  alternate source/path/label was used

not_ready
  contract exists but trusted evidence threshold is not met
```

Examples that must be classified rather than flattened:

```text
latest_prediction
forecast_records_stale
forecast_records_age_sec
orderbook_spread_unavailable
bitflyer_spot_reference_missing
insufficient_candles_for_long_ma
insufficient_exact_horizon_candles
market_regime_unknown
```

The adapter preserves original reason codes and adds only a display category and human-readable label.

## 8. Parent scenario guidance boundary

WarRoom scenario guidance is parent-owned.

```text
family_decides_overall_scenario=false
warroom_section_3_reads_parent_guidance_only=true
same_run_recursive_dependency_allowed=false
```

MR-VS5 must not merge MarketRegime evidence into parent guidance inside the UI. It may display a link or shared run reference when available.

## 9. Prediction-family boundary

MarketRegime remains the first canonical family. MR-VS5 must not begin implementation of another family.

Canonical family IDs are registry keys, not UI labels. Before the next family vertical slice, parent registry naming differences in older documents must be reconciled explicitly.

## 10. Missing or not-yet-canonical fields

The review identifies the following likely gaps or ambiguities that the adapter must handle fail-closed:

```text
single canonical dominant_evidence_tier field may be absent
current contribution and configured weight may require separate extraction
freshness domains may not share one normalized structure
human-readable warning taxonomy is not canonical yet
review_request/review_note/review_link persistence is incomplete
parameter-set comparison has only one trusted set
source scorecard has not been connected to WarRoom
price_structure remains not ready
same-run linkage across cards, calibration, scorecard, and parent guidance may be absent or partial
```

Missing fields must produce an explicit unavailable state. The UI must not synthesize evidence.

## 11. Implementation slices after this review

### Slice A: explanation adapter

```text
read existing artifacts only
normalize into MarketRegimeExplanationPacket
bounded file-size checks
schema/type guards
explicit missing/error states
no Streamlit rendering change
```

### Slice B: adapter tests

Required cases:

```text
all artifacts present
latest_read_model missing
source scorecard missing
calibration missing
parameter comparison missing
malformed JSON
artifact too large
UNKNOWN horizon
stale forecast
shadow confidence present but not promoted
price_structure 0/20 not ready
one trusted parameter set
safety flag violation rejected or surfaced
```

### Slice C: explanation renderer

```text
compact card surface remains unchanged
new detail panel reads adapter packet only
supporting and contradicting evidence separated
source quality/freshness/reliability separated
calibration explicitly marked not win rate
not-ready source visible
trace and artifact paths available in detail
```

### Slice D: connected acceptance

```text
D-hot read-only verification
log inspection before UI inspection
UI visual inspection after tests
no producer restart
no D-hot mutation
no classifier invocation
no raw market read
repository clean
```

## 12. MR-VS5 acceptance criteria

```text
artifact ownership is unambiguous
card confidence and shadow confidence are not mixed
LIVE and source freshness are not conflated
source weight/current contribution/reliability are separate
UNKNOWN remains fail-closed
calibration is not presented as win rate
one-parameter-set state is presented as comparison unavailable
not-ready price_structure remains visible
UI reads one normalized explanation packet
UI performs no inference or recalculation
all execution and auto-promotion flags remain false
targeted tests pass
WarRoom visual inspection passes
repository working tree is expected and clean after commit
```

## 13. Deferred work

The following are not part of the first MR-VS5 implementation slice:

```text
changing 65% card confidence
promoting shadow confidence to display confidence
changing UNKNOWN 15% policy
producer restart or scheduling change
warning scorecard persistence
price_structure signal generation changes
multiple parameter-set generation
review ledger persistence
new prediction family implementation
AutoTrade or broker connection
```

## 14. Decision summary

```text
proceed_to_adapter_implementation_after_review=true
operator_blocking_decision_required=false
safety_defaults_locked=true
large_slice_allowed_with_guarded_substeps=true
log_then_artifact_then_UI_inspection_required=true
```
