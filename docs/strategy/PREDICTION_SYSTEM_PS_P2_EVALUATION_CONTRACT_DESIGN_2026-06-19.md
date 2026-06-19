# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P2_EVALUATION_CONTRACT_DESIGN_2026-06-19.md
# desc: No-code contract design for offline/replay-only Prediction System evaluation records and reports.

# Prediction System PS-P2 evaluation contract design

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-P2 is a no-code design slice for future offline/replay-only evaluation contracts.

It defines `PredictionEvaluationRecord` and `PredictionEvaluationReport` as intended contract shapes before any production code is added. This is documentation and guard only.

## Starting point

```text
PS-P1 selected offline/replay-only evaluation as the next quality line.
Prediction System remains standalone, read-only, non-executing, and AutoTrade/Collector separated.
ForecastLedgerRecord / ForecastLedgerBatch are in-memory contract objects only.
TriggerEligibility remains blocked.
```

## Contract placement decision

```text
Future evaluation contracts should live in a separate prediction evaluation/replay module.
Do not add these contracts to AutoTrade.
Do not place evaluation logic inside build_prediction_system_result.
Do not mutate PredictionSystemResult to store evaluation outcomes.
PredictionSystemResult is an input snapshot to evaluation, not the owner of evaluation state.
```

## PredictionEvaluationRecord intended shape

```text
PredictionEvaluationRecord:
  evaluation_record_id: str
  evaluation_version: str
  generated_at: str
  prediction_run_id: str
  prediction_generated_at: str
  market_uid: str
  source_prediction_ref: str | None
  source_forecast_record_ref: str | None
  family: str
  horizon_sec: int
  horizon_label: str
  horizon_key: str
  predicted_label: str
  predicted_score: float | None
  predicted_confidence: str
  predicted_caution_level: str | None
  predicted_trigger_eligibility_state: str
  scenario_switch_hint: str | None
  refresh_required: bool | None
  evaluation_window_start: str
  evaluation_window_end: str
  outcome_source_ref: str | None
  outcome_available: bool
  observed_start_price: float | None
  observed_end_price: float | None
  observed_return_bps: float | None
  observed_direction: str
  adverse_excursion_bps: float | None
  favorable_excursion_bps: float | None
  hit_label: str
  timing_label: str
  confidence_bucket: str
  caution_bucket: str
  not_evaluable_reason: str | None
  blockers: tuple[str, ...]
  warnings: tuple[str, ...]
  read_only: bool = True
  non_executing: bool = True
  would_collect_public_source: bool = False
  would_write_runtime_artifact: bool = False
  would_send_to_broker: bool = False
  broker_execution_requested: bool = False
  mode_apply_requested: bool = False
  command_ledger_append_requested: bool = False
  autotrade_decision_append_requested: bool = False
```

## PredictionEvaluationRecord label vocabularies

```text
observed_direction:
  up
  down
  flat
  unknown

hit_label:
  correct_direction
  wrong_direction
  neutral_or_flat
  not_evaluable

timing_label:
  early
  timely
  late
  not_evaluable

confidence_bucket:
  unknown
  low
  medium
  high

caution_bucket:
  unknown
  low
  medium
  high
  blocked
```

## PredictionEvaluationRecord required invariants

```text
If outcome_available is false, hit_label must be not_evaluable.
If observed_start_price or observed_end_price is missing, observed_return_bps must be None.
If predicted_trigger_eligibility_state is not blocked, the record must add a warning because current Prediction System expectation is blocked.
Record generation must not collect live data.
Record generation must not write files by default.
Record generation must not append AutoTrade decisions or command ledger entries.
Record generation must not send broker orders.
```

## PredictionEvaluationReport intended shape

```text
PredictionEvaluationReport:
  evaluation_report_id: str
  evaluation_version: str
  generated_at: str
  market_uid: str
  source_ref: str | None
  evaluation_window_start: str | None
  evaluation_window_end: str | None
  input_prediction_count: int
  input_forecast_record_count: int
  evaluated_record_count: int
  skipped_record_count: int
  not_evaluable_count: int
  family_summary: dict[str, object]
  horizon_summary: dict[str, object]
  confidence_summary: dict[str, object]
  caution_summary: dict[str, object]
  scenario_switch_summary: dict[str, object]
  refresh_required_summary: dict[str, object]
  data_quality_notes: tuple[str, ...]
  calibration_candidate_notes: tuple[str, ...]
  blockers: tuple[str, ...]
  warnings: tuple[str, ...]
  read_only: bool = True
  non_executing: bool = True
  would_collect_public_source: bool = False
  would_write_runtime_artifact: bool = False
  would_send_to_broker: bool = False
  broker_execution_requested: bool = False
  mode_apply_requested: bool = False
  command_ledger_append_requested: bool = False
  autotrade_decision_append_requested: bool = False
```

## PredictionEvaluationReport required summaries

```text
family_summary:
  directional_hit_rate_by_family
  average_return_bps_by_family
  adverse_excursion_bps_by_family
  not_evaluable_count_by_family

horizon_summary:
  directional_hit_rate_by_horizon
  average_return_bps_by_horizon
  adverse_excursion_bps_by_horizon
  not_evaluable_count_by_horizon

confidence_summary:
  confidence_bucket_hit_rate
  confidence_bucket_average_return_bps
  confidence_bucket_not_evaluable_count

caution_summary:
  caution_bucket_adverse_excursion
  caution_bucket_wrong_direction_rate
  caution_bucket_not_evaluable_count

scenario_switch_summary:
  scenario_switch_watch_follow_through_rate
  scenario_switch_watch_wrong_direction_rate

refresh_required_summary:
  refresh_required_follow_through_rate
  refresh_required_not_evaluable_count
```

## Skip / not-evaluable behavior

```text
Missing outcome window -> not_evaluable with not_evaluable_reason=outcome_window_missing.
Invalid outcome prices -> not_evaluable with not_evaluable_reason=outcome_price_invalid.
Missing prediction label -> not_evaluable with not_evaluable_reason=prediction_label_missing.
Unsupported family/horizon -> skipped with warning, not a hard failure.
Blocked prediction output -> evaluable only if outcome exists; keep blockers in record.
```

## Input normalization expectations

```text
A later builder may accept PredictionSystemResult dictionaries, ForecastLedgerBatch dictionaries, or ForecastLedgerRecord dictionaries.
The builder should normalize to record-like rows internally.
The builder should never require AutoTrade objects.
The builder should never require Collector runtime objects.
The builder should treat source refs as metadata only.
```

## Data-root role policy

```text
Use D:\btc_ts_hot only for latest/runtime/current state checks when explicitly needed.
Use E:\btc_ts only for cold/archive/copy validation or long-term retained replay datasets.
PS-P2 itself does not read either root.
Later implementation must keep data-root access explicit, read-only, and guard-covered.
```

## Future implementation sequence

```text
PS-P3: add in-memory evaluation contracts/builders in a separate prediction evaluation module.
PS-P4: add missing outcome / not_evaluable guard coverage.
PS-P5: add in-memory aggregate evaluation report builder.
PS-P6: no-code calibration/confidence roadmap using evaluation outputs only.
```

## Hard boundaries

```text
No production code changed in PS-P2.
No evaluation implementation added in PS-P2.
No score formula changes.
No rule_based_v0 label changes.
No scenario_review_summary behavior changes.
No TriggerEligibility enablement.
No live collection.
No Collector runtime import.
No AutoTrade import.
No broker/private API import.
No external API call.
No artifact/runtime writes from Prediction System runner.
No AutoTrade decision append.
No command ledger append.
No mode/grant behavior.
```

## Default next recommendation

```text
Choose PS-P3: in-memory evaluation contract/builder skeleton.
```

Only proceed to PS-P3 after confirming PS-P2 guard passes and the working tree is clean.

## PS-P2 production behavior

```text
No production code changed.
No tests alter production behavior.
This design is documentation and guard only.
```
