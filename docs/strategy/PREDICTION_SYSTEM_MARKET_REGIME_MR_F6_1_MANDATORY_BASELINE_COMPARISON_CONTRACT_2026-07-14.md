# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_1_MANDATORY_BASELINE_COMPARISON_CONTRACT_2026-07-14.md
# desc: Defines the MR-F6.1 fail-closed same-window mandatory baseline comparison contract.

# Prediction System MarketRegime MR-F6.1 Mandatory Baseline Comparison Contract

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

<!-- PS_MARKET_REGIME_MR_F6_1_MANDATORY_BASELINE_COMPARISON_CONTRACT_2026_07_14 -->

## Purpose

Establish a fail-closed, read-only comparison contract before baseline generation is connected to D-hot evidence.

The comparison requires the accepted MR-F5 candidate and all mandatory simple baselines:

```text
always_range
last_state_persists
recent_return_sign
simple_ma_slope
simple_volatility_threshold
current_forecast_label_selection
```

## Same-window identity

Every candidate must provide exactly the same set of comparison slots. A slot is identified by:

```text
prediction_origin
evaluation_window_ref
source_snapshot_ref
target_horizon_sec
target_definition_version
outcome_resolver_version
```

Missing baselines, extra candidates, duplicate slots, or different slot sets block comparison.

## Minimum metrics

The pure evaluator reports:

```text
accuracy
balanced_accuracy
macro_f1
brier_score
log_loss
expected_calibration_error
coverage_rate
unknown_rate
avoidable_unknown_rate
transition_detection_delay_sec
state_churn_rate
regime_duration_consistency
```

Metrics are descriptive only. They do not promote a model or apply parameters.

## Safety boundary

```text
read_only_inputs=true
writes_dhot=false
shadow_only=true
canonical_replacement=false
parameter_auto_promotion_allowed=false
live_parameter_apply_allowed=false
human_gate_required=true
```

## Follow-up slices

MR-F6.2 will implement deterministic generators for the mandatory baselines from a shared no-lookahead evidence record.

MR-F6.3 will project accepted MR-F5 operational rows and generated baseline rows into this contract and run same-window evaluation.

MR-F6.4 will add report/read-model projection and closeout evidence. UI must not recalculate metrics.
