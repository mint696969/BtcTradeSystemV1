# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F2_CURRENT_STATE_ESTIMATOR_CLOSEOUT_2026-07-12.md
# desc: Closeout for the dedicated MarketRegime current-state estimator, persistence, and current-state outcome semantics.

# Prediction System MarketRegime MR-F2 Current-State Estimator Closeout

Updated: 2026-07-12 JST
Checkpoint: MR_F2_CURRENT_STATE_ESTIMATOR_ACCEPTED
Status: accepted
Next gate: MR_F3_EXPLAINABLE_FEATURE_SCORING_IMPLEMENTATION

## Scope accepted

MR-F2 separates the current MarketRegime state from future forecast labels.

```text
current_horizon_uses_future_forecast_label=false
current_state_estimator_dedicated=true
unknown_allowed=true
feature_evidence_traceable=true
state_persistence_enabled=true
current_state_outcome_rule_defined=true
broker_private_api_used=false
autotrade_triggered=false
order_submission_allowed=false
```

## Accepted implementation

```text
current estimator:
  btcts_next/src/btcts/prediction/market_regime/current_state_estimator.py

state persistence:
  btcts_next/src/btcts/prediction/market_regime/current_state_persistence.py
  prediction/market_regime/current_state.json

classifier integration:
  btcts_next/src/btcts/prediction/market_regime/inference/regime_classifier.py

writer integration:
  btcts_next/src/btcts/prediction/market_regime/tools/write_latest.py

current outcome rule:
  btcts_next/src/btcts/prediction/market_regime/outcome_resolver.py
  market_regime_current_state_outcome_rule.mr_f2.v1
```

## Behavioral result

The current horizon now uses current and recent L4 candle evidence. It no longer selects the shortest future forecast label.

```text
fresh usable current evidence:
  emits current state

missing or stale current evidence:
  emits UNKNOWN

same persisted regime:
  preserves state_started_at
  increments state_age_sec

changed persisted regime:
  resets state_started_at
  emits transition_detected=true

UNKNOWN prediction outcome:
  remains unknown
  is not counted as miss
```

Future horizons preserve their exact-horizon forecast behavior.

## Explainability and semantic limits

The estimator exposes source cutoff, threshold set, price-window evidence, realized-volatility evidence, persistence status, and transition diagnostics.

`change_point_evidence_score` is a transparent deterministic heuristic. It is not a calibrated probability.

```text
change_point_probability=None
change_point_probability_calibrated=false
```

MR-F3 must implement decomposed family-owned candidate scores. MR-F4 must implement the full temporal transition model, including minimum dwell, hysteresis, transition penalties, invalid-transition guards, and persistence probability.

## Outcome semantics

Current-state outcome resolution is separate from future-horizon forecast expiry resolution.

```text
current rule:
  market_regime_current_state_outcome_rule.mr_f2.v1

future rule:
  market_regime_outcome_rule.2026_07_08.v1

UNKNOWN prediction:
  outcome_label=unknown
  never converted to miss
```

This closes the MR-F1 `UNKNOWN-as-miss` blocker for the implemented outcome path.

## Compatibility updates

Prediction artifact and Operator UI preview tests were updated so fixtures without current L4 evidence render the current card as `UNKNOWN`, while future forecast cards preserve their existing labels.

No UI inference or confidence recalculation was introduced.

## Verification evidence

```text
prediction_full_suite=288_passed
operator_ui_full_suite=1184_passed
focused_estimator_tests=2_passed
focused_classifier_tests=16_passed
focused_writer_tests=7_passed
persistence_and_outcome_tests=11_passed
all_patch_runners_idempotent=true
git_diff_check=passed
ast_production_files=5_passed
same_regime_persistence_guard=passed
transition_reset_guard=passed
current_future_outcome_separation_guard=passed
unknown_not_miss_guard=passed
collection_errors=0
test_exclusions=0
```

## Safety

```text
read_only_market_sources=true
would_send_to_broker=false
broker_private_api=false
autotrade=false
order_submission=false
live_parameter_apply=false
parameter_auto_promotion=false
```

## Acceptance decision

```text
mr_f2_current_state_estimator_accepted=true
current_future_label_separation_accepted=true
state_age_and_start_preservation_accepted=true
current_outcome_rule_accepted=true
unknown_fail_closed_accepted=true
next_gate=MR_F3_EXPLAINABLE_FEATURE_SCORING_IMPLEMENTATION
```
