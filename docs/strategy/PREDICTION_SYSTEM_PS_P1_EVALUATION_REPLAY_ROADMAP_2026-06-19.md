# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P1_EVALUATION_REPLAY_ROADMAP_2026-06-19.md
# desc: No-code roadmap for offline/replay-only evaluation of standalone Prediction System outputs.

# Prediction System PS-P1 evaluation / replay-feedback roadmap

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-P1 is a no-code roadmap slice for offline/replay-only evaluation of emitted Prediction System outputs against later outcomes.

It intentionally does not implement evaluation logic yet. It defines the allowed inputs, intended outputs, metrics, and safety boundaries before any evaluation/replay code is added.

## Starting point

```text
PS-O3 closed the whole-surface Code Check line.
Prediction System is standalone, read-only, non-executing, and AutoTrade/Collector separated.
All 11 rule_based_v0 families emit structured outputs.
scenario_review_summary is available as a top-level review-only digest.
forecast_batch contains in-memory ForecastLedgerRecord contract objects only.
TriggerEligibility remains blocked.
```

## Evaluation goal

```text
Measure how emitted predictions behave against later market outcomes in offline/replay context.
Use the result to inform future calibration/confidence roadmap work.
Do not use evaluation results to trade, grant execution, or modify live behavior directly.
```

## Allowed input classes

```text
Previously emitted PredictionSystemResult dictionaries or serialized snapshots.
ForecastLedgerRecord / ForecastLedgerBatch contract-shaped records.
Later observed market outcome windows from offline/replay datasets.
Replay metadata such as evaluation_window_start, evaluation_window_end, horizon_sec, market_uid, and source_ref.
Existing source quality / provider reliability summaries when already present in the prediction snapshot.
```

## Data-root role policy

```text
Use D:\btc_ts_hot only for latest/runtime/current state checks when explicitly needed.
Use E:\btc_ts only for cold/archive/copy validation or long-term retained replay datasets.
PS-P1 itself does not read either root; this roadmap only records the intended role separation.
Later evaluation implementation must keep data-root access explicit, read-only, and guard-covered.
```

## Forbidden inputs and side effects

```text
No live collection.
No Collector runtime import.
No AutoTrade import.
No broker/private API import.
No external API call.
No live orderbook/tradeflow polling.
No AutoTrade decision append.
No command ledger append.
No approval ledger append.
No mode/grant behavior.
No runtime artifact writes from the Prediction System runner.
No TriggerEligibility enablement.
No score formula changes in the roadmap slice.
No rule_based_v0 label changes in the roadmap slice.
```

## Candidate evaluation record shape

A later implementation may introduce a separate evaluation/replay contract, not a modification of PredictionSystemResult.

```text
PredictionEvaluationRecord:
  evaluation_version
  prediction_run_id
  prediction_generated_at
  market_uid
  family
  horizon_sec
  horizon_label
  predicted_label
  predicted_score
  predicted_confidence
  predicted_caution_level
  evaluation_window_start
  evaluation_window_end
  observed_return_bps
  observed_direction
  adverse_excursion_bps
  favorable_excursion_bps
  hit_label
  timing_label
  confidence_bucket
  blockers
  warnings
  source_refs
  read_only = True
  non_executing = True
  would_send_to_broker = False
  would_append_autotrade_decision = False
  would_append_command_ledger = False
```

## Candidate aggregate report shape

```text
PredictionEvaluationReport:
  evaluation_version
  generated_at
  market_uid
  input_prediction_count
  evaluated_record_count
  skipped_record_count
  horizon_summary
  family_summary
  confidence_summary
  caution_summary
  scenario_review_summary_quality_notes
  data_quality_notes
  blockers
  warnings
  read_only = True
  non_executing = True
```

## Candidate metrics

```text
directional_hit_rate_by_horizon
directional_hit_rate_by_family
average_return_bps_by_label
median_return_bps_by_label
adverse_excursion_bps_by_label
favorable_excursion_bps_by_label
confidence_bucket_hit_rate
caution_bucket_adverse_excursion
scenario_switch_watch_follow_through_rate
refresh_required_follow_through_rate
skipped_due_to_missing_outcome_count
```

## Evaluation labels

```text
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
```

## Guarding expectations for implementation slices

```text
Evaluation implementation must be in a separate replay/evaluation module, not inside AutoTrade.
Prediction System runner must remain non-writing.
Any output artifact writer must be explicit and outside build_prediction_system_result.
Default implementation should return in-memory records first.
File writes, if ever added, require a separate approved slice and guard.
Static boundary scan must reject Collector runtime imports, AutoTrade imports, broker/private API imports, external API calls, append_decision_jsonl, command ledger append, and mode/grant behavior.
```

## Recommended next implementation path

```text
PS-P2: no-code evaluation contract design.
PS-P3: in-memory evaluation record builder skeleton from supplied prediction snapshots and supplied outcome windows.
PS-P4: focused guard for missing outcomes and skipped/not_evaluable records.
PS-P5: aggregate evaluation report builder in memory.
PS-P6: calibration/confidence roadmap using evaluation outputs only.
```

## Default next recommendation

```text
Choose PS-P2: no-code evaluation contract design.
```

## PS-P1 production behavior

```text
No production code changed.
No tests alter production behavior.
This roadmap is documentation and guard only.
```
