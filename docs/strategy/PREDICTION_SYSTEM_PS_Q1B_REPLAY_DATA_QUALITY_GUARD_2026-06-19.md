# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q1B_REPLAY_DATA_QUALITY_GUARD_2026-06-19.md
# desc: Option B completion guard for read-only replay/evaluation data quality. Documentation and guard only.

# Prediction System PS-Q1B replay-data quality guard

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-Q1B completes the current-thread Option B request:

```text
Option B: read-only replay-data quality guard only.
```

This is not a production calibration behavior change. It adds a focused guard baseline over the existing offline/replay-only evaluation and advisory-only calibration review surface.

## Completion definition for this thread

Option B is considered complete in this thread when a committed guard verifies all of the following:

```text
PredictionEvaluationReport preserves not_evaluable evidence by family.
PredictionEvaluationReport preserves not_evaluable evidence by horizon.
PredictionEvaluationReport preserves not_evaluable evidence by confidence bucket.
PredictionEvaluationReport preserves not_evaluable evidence by caution bucket.
Missing outcome windows produce explicit data_quality_notes and warnings.
PredictionCalibrationReview turns not_evaluable skew into advisory data-quality risk.
PredictionCalibrationReview turns missing outcome skew into advisory data-quality risk.
Missing summary/schema drift is advisory-only and does not enable behavior changes.
Evaluation/calibration review inputs are not mutated by the guard path.
All read-only / non-executing / no broker / no mode / no AutoTrade append flags remain safe.
```

## What this does not mean

```text
It does not mean real replay datasets have been fully analyzed.
It does not mean production calibration is enabled.
It does not mean confidence/caution behavior is changed.
It does not mean family scores or labels are changed.
It does not mean TriggerEligibility is enabled.
It does not mean AutoTrade trigger integration is enabled.
```

Future richer replay-data checks can still be added, but this slice provides the committed read-only guard baseline requested before closing this thread.

## Guard fixture shape

The PS-Q1B guard uses an in-memory replay fixture:

```text
1 evaluated forecast record with an available outcome.
2 forecast records with missing outcome windows.
Different family / horizon / confidence / caution buckets are used so skew is visible in the summaries.
```

Expected evaluation evidence:

```text
evaluated_record_count = 1
not_evaluable_count = 2
data_quality_notes includes outcome_window_missing
warnings includes evaluation_records_with_missing_outcome_window
not_evaluable_count_by_family identifies the missing families
not_evaluable_count_by_horizon identifies the missing horizons
confidence_bucket_not_evaluable_count identifies missing confidence buckets
caution_bucket_not_evaluable_count identifies missing caution buckets
```

Expected calibration review evidence:

```text
data_quality_review.not_evaluable_ratio = 0.666667
data_quality_review.not_evaluable_skew = True
data_quality_review.missing_outcome_skew = True
risk_catalog_hits includes not_evaluable_skew
risk_catalog_hits includes missing_data_optimism
calibration_candidate_notes includes not_evaluable_skew
calibration_candidate_notes includes missing_outcome_skew
```

## Boundary preserved

```text
No production code changed.
No tests alter production behavior.
No live collection.
No Collector runtime import.
No AutoTrade import.
No broker/private API import.
No external API call.
No runtime artifact writes from Prediction System runner.
No AutoTrade decision append.
No command ledger append.
No mode/grant behavior.
No score changes.
No confidence behavior changes.
No caution behavior changes.
No family label changes.
No TriggerEligibility enablement.
```

## Relationship to PS-Q1 roadmap

PS-Q1 defined the full remaining roadmap and set the next implementation start as PS-Q2 source / artifact input coverage.

PS-Q1B is a current-thread closure addendum that completes the requested Option B read-only replay-data quality guard baseline before moving to the next thread.

Next thread remains:

```text
PS-Q2: source / artifact input coverage start
```

The replay-data quality baseline is now present and must not be treated as production calibration approval.

## PS-Q1B production behavior

```text
No production code changed.
No tests alter production behavior.
This slice is documentation and guard only.
```
