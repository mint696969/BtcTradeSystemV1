# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P6_CALIBRATION_CONFIDENCE_ROADMAP_2026-06-19.md
# desc: No-code roadmap for calibration/confidence review using offline Prediction System evaluation outputs only.

# Prediction System PS-P6 calibration / confidence roadmap

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-P6 is a no-code roadmap slice for future calibration and confidence review using offline/replay-only Prediction System evaluation outputs.

It does not change score formulas, confidence labels, caution labels, rule family labels, trigger eligibility, or live behavior. It records how evaluation outputs should be used to find quality risks before any calibration implementation is added.

## Starting point

```text
PS-P1 selected offline/replay-only evaluation.
PS-P2 defined evaluation record/report contracts.
PS-P3 added in-memory PredictionEvaluationRecord and PredictionEvaluationReport builders.
PS-P4 added not_evaluable / missing outcome guard coverage.
PS-P5 aligned confidence_summary and caution_summary keys with the PS-P2 contract.
Prediction System remains standalone, read-only, non-executing, and AutoTrade/Collector separated.
```

## Calibration principle

```text
Evaluation outputs are evidence, not authority.
Calibration candidates must be reviewed before changing production score, confidence, caution, family labels, or trigger behavior.
Do not directly feed evaluation results into AutoTrade.
Do not use evaluation results to grant execution.
Do not enable TriggerEligibility from calibration output.
```

## Allowed inputs for future calibration review

```text
PredictionEvaluationReport dictionaries.
PredictionEvaluationRecord dictionaries.
family_summary, horizon_summary, confidence_summary, caution_summary.
data_quality_notes and not_evaluable_count.
scenario_switch_summary and refresh_required_summary when implemented beyond placeholder values.
Offline replay metadata and source refs already present in evaluation outputs.
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
No score formula changes in PS-P6.
No confidence behavior changes in PS-P6.
No caution behavior changes in PS-P6.
No rule_based_v0 label changes in PS-P6.
```

## Candidate calibration review questions

```text
Does high confidence have a higher directional_hit_rate than medium and low confidence?
Does high confidence have lower not_evaluable_count than unknown confidence?
Does caution high show higher adverse excursion or wrong-direction rate than caution low?
Does any family have persistently weak directional_hit_rate_by_family?
Does any horizon have persistently weak directional_hit_rate_by_horizon?
Are missing outcomes concentrated in one family, horizon, source, or replay window?
Do scenario_switch_watch cases later follow through, reverse, or remain not_evaluable?
Do refresh_required cases show degraded follow-through versus normal cases?
Do blocked/cautious outputs correctly preserve non-executing flags?
```

## Expected-result matrix for future guards

```text
case: long_bias + price up
expect: correct_direction, observed_direction=up, evaluated_record_count increments

case: long_bias + price down
expect: wrong_direction, observed_direction=down, caution/family/horizon summaries count the miss

case: short_bias + price down
expect: correct_direction, observed_direction=down, evaluated_record_count increments

case: short_bias + price up
expect: wrong_direction, observed_direction=up, caution/family/horizon summaries count the miss

case: flat outcome within threshold
expect: neutral_or_flat, not a forced correct_direction

case: missing outcome
expect: not_evaluable, not_evaluable_reason=outcome_window_missing, no execution flags enabled

case: invalid price
expect: not_evaluable, not_evaluable_reason=outcome_price_invalid, observed_return_bps=None

case: missing prediction label
expect: not_evaluable, not_evaluable_reason=prediction_label_missing

case: trigger_eligibility_state not blocked
expect: warning only, no execution flags enabled

case: high confidence underperforms low confidence in repeated replay
expect: calibration_candidate_notes may flag confidence_ordering_suspect in future, but no immediate score/confidence change
```

## Metamorphic checks to add before calibration implementation

```text
Price scale invariance: multiplying all prices by the same positive factor must not change observed_return_bps, observed_direction, or hit_label.
Outcome removal: removing a matching outcome window must convert the record to not_evaluable.
Window identity: changing only source_ref must not change hit_label or observed_return_bps.
Execution invariance: any calibration/evaluation review must keep would_send_to_broker=False and command_ledger_append_requested=False.
Order invariance: reordering input records should not change aggregate counts, only record ordering if preserved by builder.
Bucket monotonic review: high confidence should not be assumed better; it must be measured against lower buckets.
```

## Risk catalog for Prediction System evaluation and calibration

```text
schema_drift: design keys and implementation keys diverge.
silent_fallback: unknown/default values hide missing or invalid data.
lookahead_bias: outcome or future information leaks into prediction-time fields.
overconfidence: confidence label is stronger than observed hit rate supports.
missing_data_optimism: missing outcomes or missing inputs make the system look better than it is.
boundary_leak: evaluation or calibration imports AutoTrade, Collector runtime, broker, or append paths.
metric_mismatch: aggregate metric improves while the operational review objective does not.
label_ambiguity: predicted labels such as no_edge, risk, range, or neutral are scored inconsistently.
aggregation_hiding: weak family or horizon is hidden by overall average.
not_evaluable_skew: too many not_evaluable records distort confidence or caution review.
causality_drift: source quality or provider reliability context is treated as a causal calibration signal without review.
```

## Candidate future calibration output shape

A later implementation may add a separate review object, not production scoring behavior.

```text
PredictionCalibrationReview:
  review_id
  generated_at
  source_evaluation_report_id
  evaluated_record_count
  not_evaluable_count
  family_risk_notes
  horizon_risk_notes
  confidence_risk_notes
  caution_risk_notes
  data_quality_notes
  calibration_candidate_notes
  blockers
  warnings
  read_only = True
  non_executing = True
  would_change_score_formula = False
  would_change_confidence_behavior = False
  would_change_caution_behavior = False
  would_enable_trigger_eligibility = False
  would_send_to_broker = False
  would_append_autotrade_decision = False
  would_append_command_ledger = False
```

## Review thresholds are advisory only

```text
A future review may flag confidence_ordering_suspect when high confidence hit rate is below medium or low confidence.
A future review may flag family_underperformance_candidate when a family is below a reviewed threshold.
A future review may flag horizon_underperformance_candidate when a horizon is below a reviewed threshold.
A future review may flag caution_bucket_not_discriminative when caution buckets do not separate adverse excursion or wrong-direction rate.
A future review may flag not_evaluable_skew when not_evaluable_count dominates any family/horizon/bucket.
These flags must not directly change production prediction behavior.
```

## Future implementation sequence

```text
PS-P7: expected-result matrix / metamorphic guard extension for evaluation outputs.
PS-P8: no-code calibration review contract design.
PS-P9: in-memory PredictionCalibrationReview builder from PredictionEvaluationReport only.
PS-P10: confidence/caution candidate guard with no production score changes.
PS-P11: whole-surface evaluation/calibration CC pass.
```

## Data-root role policy

```text
Use D:\btc_ts_hot only for latest/runtime/current state checks when explicitly needed.
Use E:\btc_ts only for cold/archive/copy validation or long-term retained replay datasets.
PS-P6 itself does not read either root.
Future replay/calibration slices must keep data-root access explicit, read-only, and guard-covered.
```

## PS-P6 production behavior

```text
No production code changed.
No tests alter production behavior.
This roadmap is documentation and guard only.
```
