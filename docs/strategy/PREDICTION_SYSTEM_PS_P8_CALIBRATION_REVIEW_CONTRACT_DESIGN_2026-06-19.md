# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P8_CALIBRATION_REVIEW_CONTRACT_DESIGN_2026-06-19.md
# desc: No-code contract design for offline Prediction System calibration review records using evaluation reports only.

# Prediction System PS-P8 calibration review contract design

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-P8 is a no-code contract design slice for a future `PredictionCalibrationReview` object.

It defines a read-only, non-executing review contract that consumes `PredictionEvaluationReport` outputs as evidence. It does not implement calibration logic and does not change production prediction behavior.

## Starting point

```text
PS-P6 defined the calibration/confidence roadmap and risk catalog.
PS-P7 added expected-result matrix and metamorphic guard coverage for evaluation outputs.
PredictionEvaluationReport exists as an in-memory offline/replay-only evaluation contract.
Evaluation outputs are evidence, not authority.
Validation cycles should remain focused and normally capped at about 3 cycles.
```

## Contract placement decision

```text
Future calibration review contracts should live in a separate prediction calibration/review module.
Do not add calibration review contracts to AutoTrade.
Do not place calibration review logic inside build_prediction_system_result.
Do not mutate PredictionSystemResult to store calibration outcomes.
Do not mutate PredictionEvaluationReport to store calibration outcomes.
PredictionEvaluationReport is an input snapshot to calibration review, not the owner of review state.
```

## Allowed inputs

```text
PredictionEvaluationReport object or dictionary.
PredictionEvaluationRecord objects or dictionaries already present in the evaluation report.
family_summary, horizon_summary, confidence_summary, caution_summary.
scenario_switch_summary and refresh_required_summary when present.
data_quality_notes, blockers, warnings, evaluated_record_count, not_evaluable_count.
source_ref, market_uid, evaluation_window_start, evaluation_window_end.
```

## Forbidden inputs and side effects

```text
No live collection.
No Collector runtime import.
No AutoTrade import.
No broker/private API import.
No external API call.
No command ledger append.
No AutoTrade decision append.
No approval append.
No mode/grant behavior.
No TriggerEligibility enablement.
No runtime artifact writes from Prediction System runner.
No score formula changes.
No confidence behavior changes.
No caution behavior changes.
No rule_based_v0 label changes.
No direct feed into trading or execution.
```

## PredictionCalibrationReview intended shape

```text
PredictionCalibrationReview:
  review_id: str
  review_version: str
  generated_at: str
  source_evaluation_report_id: str | None
  source_evaluation_version: str | None
  market_uid: str
  source_ref: str | None
  evaluation_window_start: str | None
  evaluation_window_end: str | None
  evaluated_record_count: int
  not_evaluable_count: int
  skipped_record_count: int
  confidence_bucket_review: dict[str, object]
  caution_bucket_review: dict[str, object]
  family_review: dict[str, object]
  horizon_review: dict[str, object]
  data_quality_review: dict[str, object]
  scenario_switch_review: dict[str, object]
  refresh_required_review: dict[str, object]
  risk_catalog_hits: tuple[str, ...]
  calibration_candidate_notes: tuple[str, ...]
  blockers: tuple[str, ...]
  warnings: tuple[str, ...]
  read_only: bool = True
  non_executing: bool = True
  would_change_score_formula: bool = False
  would_change_confidence_behavior: bool = False
  would_change_caution_behavior: bool = False
  would_change_family_labels: bool = False
  would_enable_trigger_eligibility: bool = False
  would_collect_public_source: bool = False
  would_write_runtime_artifact: bool = False
  would_send_to_broker: bool = False
  broker_execution_requested: bool = False
  mode_apply_requested: bool = False
  command_ledger_append_requested: bool = False
  autotrade_decision_append_requested: bool = False
```

## Review sub-shapes

```text
confidence_bucket_review:
  bucket_hit_rate
  bucket_average_return_bps
  bucket_not_evaluable_count
  ordering_notes
  confidence_ordering_suspect

caution_bucket_review:
  bucket_adverse_excursion
  bucket_wrong_direction_rate
  bucket_not_evaluable_count
  discrimination_notes
  caution_bucket_not_discriminative

family_review:
  directional_hit_rate_by_family
  average_return_bps_by_family
  adverse_excursion_bps_by_family
  not_evaluable_count_by_family
  family_underperformance_candidates

horizon_review:
  directional_hit_rate_by_horizon
  average_return_bps_by_horizon
  adverse_excursion_bps_by_horizon
  not_evaluable_count_by_horizon
  horizon_underperformance_candidates

scenario_switch_review:
  scenario_switch_watch_follow_through_rate
  scenario_switch_watch_wrong_direction_rate
  scenario_switch_review_not_ready

refresh_required_review:
  refresh_required_follow_through_rate
  refresh_required_not_evaluable_count
  refresh_required_review_not_ready

data_quality_review:
  not_evaluable_count
  not_evaluable_ratio
  data_quality_notes
  not_evaluable_skew
  missing_outcome_skew
```

## Advisory candidate notes vocabulary

```text
confidence_ordering_suspect
caution_bucket_not_discriminative
family_underperformance_candidate
horizon_underperformance_candidate
not_evaluable_skew
missing_outcome_skew
schema_drift_suspect
silent_fallback_suspect
lookahead_bias_review_required
overconfidence_review_required
aggregation_hiding_review_required
scenario_switch_review_not_ready
refresh_required_review_not_ready
evaluation_report_missing
evaluation_records_missing
calibration_review_in_memory_only
```

## Required invariants

```text
Review generation must be read_only and non_executing.
Review generation must not change score formulas.
Review generation must not change confidence behavior.
Review generation must not change caution behavior.
Review generation must not change family labels.
Review generation must not enable TriggerEligibility.
Review generation must not collect live data.
Review generation must not write files by default.
Review generation must not append AutoTrade decisions or command ledger entries.
Review generation must not send broker orders.
Advisory notes must not directly mutate PredictionSystemResult, PredictionEvaluationReport, or AutoTrade state.
```

## Missing / invalid input behavior

```text
Missing evaluation report -> blockers include evaluation_report_missing.
Missing evaluation records with an otherwise present report -> warnings include evaluation_records_missing or blockers if review cannot proceed.
Missing confidence_summary -> warnings include confidence_summary_missing.
Missing caution_summary -> warnings include caution_summary_missing.
Missing family_summary -> warnings include family_summary_missing.
Missing horizon_summary -> warnings include horizon_summary_missing.
Scenario switch placeholders are allowed but must mark scenario_switch_review_not_ready.
Refresh-required placeholders are allowed but must mark refresh_required_review_not_ready.
```

## Calibration review is advisory only

```text
A calibration review may identify candidate risks.
A calibration review must not change predictions.
A calibration review must not change scores.
A calibration review must not change confidence labels.
A calibration review must not change caution labels.
A calibration review must not change trading behavior.
Any future behavior change requires a separate approved design, implementation, guard, and human review.
```

## Future implementation sequence

```text
PS-P9: in-memory PredictionCalibrationReview builder from PredictionEvaluationReport only.
PS-P10: confidence/caution candidate guard with no production score changes.
PS-P11: whole-surface evaluation/calibration CC pass.
PS-P12: stop/review checkpoint before any production calibration behavior change.
```

## Data-root role policy

```text
Use D:\btc_ts_hot only for latest/runtime/current state checks when explicitly needed.
Use E:\btc_ts only for cold/archive/copy validation or long-term retained replay datasets.
PS-P8 itself does not read either root.
Future calibration review implementation must keep data-root access explicit, read-only, and guard-covered.
```

## Validation cycle policy

```text
Focused verification should normally complete within about 3 validation cycles.
More than about 3 cycles requires an explicit safety, trading-boundary, data-loss, or hard-to-localize failure reason.
PS-P8 itself is documentation and guard only, so broad repeated validation is not required.
```

## PS-P8 production behavior

```text
No production code changed.
No tests alter production behavior.
This design is documentation and guard only.
```
