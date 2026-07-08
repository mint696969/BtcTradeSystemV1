# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_OUTCOME_RULE_V1_2026-07-08.md
# desc: Market-regime outcome rule v1. Spec-only; defines hit/partial/miss/invalidated/unknown evaluation, calibration fields, and GPT/operator hypothesis validation lane.
# Market Regime Outcome Rule v1

Updated: 2026-07-08 JST
Base: Market Regime Signal Registry v1 / Horizon Weight v1 / Trace and Calibration Spec
Mode: outcome rule specification lock / no runtime behavior change

<!-- PS_MARKET_REGIME_OUTCOME_RULE_V1_LOCK_2026_07_08 -->

```text
ps_market_regime_outcome_rule_v1_lock=true
market_regime_only=true
outcome_rule_version=market_regime_outcome_rule.2026_07_08.v1
outcome_labels=hit,partial,miss,invalidated,unknown
prediction_percent_is_not_win_rate=true
invalidated_is_recorded_separately=true
gpt_hypothesis_lane_allowed=true
gpt_hypothesis_requires_replay_validation=true
parameter_set_promotion_requires_human_gate=true
runtime_code_changed=false
ui_classifier_invocation_allowed=false
broker_send_enabled=false
order_intent_submitted=false
autotrade_trigger_allowed=false
```

## 1. Purpose

This document fixes the initial outcome evaluation rules for market-regime prediction.

The outcome system must answer:

```text
At prediction time, what did the engine believe?
What horizon was predicted?
What happened by horizon expiry?
Did the primary regime hold or materialize?
Did a declared counter-scenario or invalidation occur?
Was the prediction truly wrong, partially useful, invalidated, or unjudgeable due to data quality?
```

Outcome evaluation is for replay, calibration, parameter-set comparison, and future improvement. It is not broker execution and not AutoTrade permission.

## 2. Outcome labels

Use these labels:

```text
hit
partial
miss
invalidated
unknown
```

Meanings:

```text
hit        = primary market-regime reading held or materialized for the horizon according to the family rule.
partial    = primary reading was not fully correct, but declared counter-scenario, conflict, or useful warning captured the actual behavior.
miss       = primary reading and declared alternatives failed, and data quality was sufficient to judge.
invalidated= declared invalidation condition triggered before or during the horizon; record separately from miss.
unknown    = outcome cannot be judged due to missing/stale/invalid data or ambiguous artifact coverage.
```

`invalidated` should not be hidden. It is important because a good prediction should say what would prove it wrong.

## 3. Evaluation window

For each prediction:

```text
evaluation_start_utc = generated_at_utc
evaluation_end_utc   = generated_at_utc + horizon_sec
```

Outcome resolver should read market records, candle store refs, orderflow summaries, orderbook/liquidity summaries, and source-quality summaries for the evaluation window.

Recommended fields:

```text
prediction_id
run_id
prediction_family_id
primary_regime
confidence_percent
horizon_key
horizon_sec
generated_at_utc
evaluation_start_utc
evaluation_end_utc
resolved_at_utc
outcome_label
actual_regime_summary
invalidation_triggered
invalidation_trigger_ts
counter_scenario_observed
source_quality_at_resolution
judgeable=true|false
```

## 4. General scoring fields

Outcome rows should preserve enough compact metrics for calibration:

```text
regime_hold_ratio
primary_regime_evidence_ratio
counter_regime_evidence_ratio
range_break_count
confirmed_break_hold_count
false_break_count
max_favorable_move
max_adverse_move
max_drawdown_from_prediction
realized_volatility
spread_max
spread_median
thin_book_ratio
liquidity_absorption_events
orderflow_directional_persistence
volume_confirmation_state
source_gap_count
stale_source_count
```

These are compact summaries, not raw data duplication.

## 5. RANGE outcome rule

A RANGE prediction is a hit when price behavior remains bounded and mean-reverting for the horizon.

Hit examples:

```text
price stays inside declared or inferred range
brief boundary tests fail and return inside range
VWAP/center reversion remains visible
no confirmed break-and-hold with volume/orderflow confirmation
volatility remains compatible with range behavior
```

Partial examples:

```text
range held for most of the horizon but broke late
range held, but volatility/chop warning was more important than primary RANGE
counter-scenario BREAKOUT_WATCH was declared and boundary pressure occurred
```

Miss examples:

```text
confirmed break-and-hold occurs early and persists
clear UP_TREND or DOWN_TREND emerges without declared counter-scenario
HIGH_VOL_CHOP dominates and RANGE was high-confidence without warning
```

Invalidated examples:

```text
two closed candles hold outside range boundary
volume-confirmed break beyond boundary
orderflow and liquidity both confirm break direction
```

## 6. UP_TREND outcome rule

An UP_TREND prediction is a hit when upward structure and pullback support hold through the horizon.

Hit examples:

```text
higher high / higher low behavior continues
price remains above VWAP or key moving structure for meaningful share of horizon
pullbacks hold and buying resumes
upward moves are volume/orderflow supported
```

Partial examples:

```text
upward move occurs but becomes HIGH_VOL_CHOP
uptrend holds only part of horizon and declared reversal/weakness warning appears
primary direction is right but confidence was capped correctly due to conflict
```

Miss examples:

```text
price fails to advance and returns to RANGE without declared range counter-scenario
DOWN_TREND emerges instead
reversal occurs early without declared invalidation or caution
```

Invalidated examples:

```text
key higher low breaks
price accepts below VWAP/support after the prediction
sell orderflow plus liquidity break confirms downside
```

## 7. DOWN_TREND outcome rule

A DOWN_TREND prediction is a hit when downward structure and rebound selling hold through the horizon.

Hit examples:

```text
lower high / lower low behavior continues
price remains below VWAP or key moving structure for meaningful share of horizon
rebounds fail and selling resumes
downward moves are volume/orderflow supported
```

Partial examples:

```text
downward move occurs but becomes HIGH_VOL_CHOP
trend holds only part of horizon and declared reversal/absorption warning appears
primary direction is right but confidence was capped correctly due to conflict
```

Miss examples:

```text
price fails to decline and returns to RANGE without declared range counter-scenario
UP_TREND emerges instead
reversal occurs early without declared invalidation or caution
```

Invalidated examples:

```text
key lower high breaks
price accepts above VWAP/resistance after the prediction
buy orderflow plus liquidity break confirms upside
```

## 8. LOW_VOL_COMPRESSION outcome rule

A LOW_VOL_COMPRESSION prediction is a hit when volatility/range/body size remains compressed and directional commitment does not appear.

Hit examples:

```text
ATR/realized volatility stays low relative to recent baseline
candle bodies and range remain compressed
orderflow is not persistently directional
spread and depth remain stable enough for compression state
```

Partial examples:

```text
compression holds for most of horizon then begins expansion
BREAKOUT_WATCH counter-scenario was declared and boundary pressure appears
```

Miss examples:

```text
strong volatility expansion occurs early
clear UP_TREND/DOWN_TREND/BREAKOUT_WATCH appears without declared counter-scenario
HIGH_VOL_CHOP appears quickly
```

Invalidated examples:

```text
ATR expansion threshold triggered
two or more expanded-body candles close beyond compression range
volume/orderflow confirms expansion
```

## 9. BREAKOUT_WATCH outcome rule

BREAKOUT_WATCH is a watch regime, not a guaranteed breakout prediction.

A BREAKOUT_WATCH prediction is a hit when breakout-relevant pressure, attempt, false-break, or confirmed break condition materializes within the horizon.

Hit examples:

```text
price repeatedly pressures range boundary
break attempt occurs
false break occurs and was relevant to operator attention
confirmed break-and-hold occurs
liquidity thins or disappears near boundary
orderflow accelerates toward boundary
```

Partial examples:

```text
boundary pressure increases but no actual attempt occurs
compression continues but watch condition remains valid
breakout attempt occurs after most of the horizon elapsed
```

Miss examples:

```text
price moves back to calm range center with no boundary pressure
LOW_VOL_COMPRESSION persists with no watch relevance
opposite regime emerges without declared counter-scenario
```

Invalidated examples:

```text
boundary pressure disappears and source signals normalize
range center reversion invalidates watch thesis
opposite-side absorption clearly rejects breakout setup
```

## 10. REVERSAL_WATCH outcome rule

REVERSAL_WATCH is also a watch regime, not a guaranteed reversal prediction.

A REVERSAL_WATCH prediction is a hit when trend continuation weakens, absorption appears, price rejects a level, or reversal attempt materializes.

Hit examples:

```text
wick rejection near level appears
flow absorption appears against prior direction
CVD/price divergence appears
trend stalls and fails to make clean continuation
actual reversal attempt occurs
```

Partial examples:

```text
stall/absorption appears but no reversal follows
reversal occurs late in horizon
HIGH_VOL_CHOP appears after warning
```

Miss examples:

```text
clean trend continuation occurs without stall or absorption
no relevant rejection/divergence occurs
opposite watch condition dominates without declared conflict
```

Invalidated examples:

```text
prior trend continues with volume and structure confirmation
reversal level breaks cleanly without rejection
absorption signal disappears and continuation accepts price
```

## 11. HIGH_VOL_CHOP outcome rule

A HIGH_VOL_CHOP prediction is a hit when volatility is elevated and directional quality is poor.

Hit examples:

```text
large ranges or ATR expansion persist
many wicks / failed breaks / rapid reversals appear
spread widens or book thins
high volume occurs without stable directional acceptance
operator should treat new entries as risky
```

Partial examples:

```text
chop appears briefly then resolves into declared trend/breakout counter-scenario
volatility remains high but direction becomes cleaner late in horizon
```

Miss examples:

```text
clean trend emerges early and remains stable
calm range/low-vol compression appears instead
```

Invalidated examples:

```text
spread normalizes, volatility compresses, and clean structure emerges
confirmed trend acceptance replaces chop
```

## 12. UNKNOWN outcome rule

UNKNOWN is a valid safety classification.

A prediction of UNKNOWN is a hit-like valid safety result when the horizon remains unjudgeable, conflicted, stale, missing, or too noisy according to source-quality rules.

Recommended outcome labels:

```text
hit      = UNKNOWN/no-call remained justified
partial  = UNKNOWN was justified early but clear regime emerged late
miss     = data was good and a clean regime was already present, but engine incorrectly withheld
unknown  = outcome itself cannot be evaluated
```

UNKNOWN should be calibrated carefully. The goal is not to hide poor inference by returning UNKNOWN too often.

## 13. GPT / operator hypothesis validation lane

The engine should allow GPT/operator-suggested patterns, but they are hypotheses, not truth.

Examples of hypothesis sources:

```text
operator_manual_review
GPT chart analysis
replay pattern discovery
professional/AI participant behavior hypothesis
liquidity hunting hypothesis
stop-run / false-break hypothesis
session behavior hypothesis
macro/cross-market lead-lag hypothesis
```

A hypothesis should be recorded with:

```text
hypothesis_id
origin=gpt|operator|replay|manual_rule
created_at_utc
description
expected_signal_effect
expected_horizon
expected_regime_context
source_refs
parameter_set_candidate_ref
promotion_state=candidate|shadow|active|rejected|archived
validation_metrics_ref
```

Hard rules:

```text
gpt_hypothesis_is_not_active_truth_by_default=true
hypothesis_must_be_replay_validated=true
promotion_to_active_requires_parameter_set_version=true
promotion_to_active_requires_human_gate=true
old_traces_must_remain_readable=true
```

This preserves the value of GPT pattern suggestions while preventing unvalidated hidden logic.

## 14. Calibration outputs

Outcome/calibration should produce compact summaries by:

```text
regime
horizon
parameter_set_id
signal_registry_version
horizon_weight_version
source_family
confidence_bucket
hypothesis_id_if_any
```

Calibration should detect:

```text
overconfidence
underconfidence
source_family_overweight
source_family_underweight
invalidations_that_worked
invalidations_that_failed
UNKNOWN_overuse
watch_regime_usefulness
hypothesis_candidate_performance
```

## 15. Outcome row shape

Minimum JSONL row shape:

```json
{
  "schema_version": "market_regime_outcome.2026_07_08.v1",
  "outcome_id": "outcome_...",
  "prediction_id": "prediction_...",
  "run_id": "market_regime_...",
  "prediction_family_id": "market_regime",
  "primary_regime": "RANGE",
  "horizon_key": "15m",
  "horizon_sec": 900,
  "generated_at_utc": "2026-07-08T07:00:00Z",
  "evaluation_start_utc": "2026-07-08T07:00:00Z",
  "evaluation_end_utc": "2026-07-08T07:15:00Z",
  "resolved_at_utc": "2026-07-08T07:16:00Z",
  "outcome_label": "hit",
  "judgeable": true,
  "invalidation_triggered": false,
  "counter_scenario_observed": false,
  "summary_metrics": {},
  "source_refs": {},
  "versions": {
    "outcome_rule": "market_regime_outcome_rule.2026_07_08.v1",
    "signal_registry": "market_regime_signal_registry.2026_07_08.v1",
    "horizon_weight": "market_regime_horizon_weight.2026_07_08.v1"
  }
}
```

## 16. Non-goals

```text
not_a_trading_result_ledger=true
not_a_broker_ledger=true
not_autotrade_permission=true
not_a_simple_win_rate_only_metric=true
not_allowed_to_rewrite_past_prediction_trace=true
```

Outcome rules exist to improve inference quality, not to create fake certainty.
