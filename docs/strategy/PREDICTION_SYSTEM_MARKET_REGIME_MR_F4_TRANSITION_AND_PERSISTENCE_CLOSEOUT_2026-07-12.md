# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F4_TRANSITION_AND_PERSISTENCE_CLOSEOUT_2026-07-12.md
# desc: Closeout for MarketRegime temporal persistence, guarded transitions, and canonical current-state application.

# Prediction System MarketRegime MR-F4 Transition and Persistence Closeout

Updated: 2026-07-12 JST
Checkpoint: MR_F4_TRANSITION_AND_PERSISTENCE_BEHAVIOR_ACCEPTED
Status: accepted
Next gate: MR_F5_HORIZON_SPECIFIC_FUTURE_FORECAST_IMPLEMENTATION
Accepted head: e4f0d913

## Scope accepted

MR-F4 adds explicit temporal persistence and guarded transition behavior to the canonical MarketRegime current-state estimator.

```text
minimum_dwell_time=true
hysteresis=true
transition_penalty=true
change_point_evidence=true
invalid_transition_guard=true
state_persistence_probability=true
explicit_transition_matrix=true
canonical_transition_application=true
state_churn_guarded=true
impossible_transition_accepted=false
broker_private_api_used=false
autotrade_triggered=false
order_submission_allowed=false
```

## Accepted implementation

```text
transition policy:
  btcts_next/src/btcts/prediction/market_regime/transition_policy.py

parameter contract:
  btcts_next/src/btcts/prediction/market_regime/parameter_set.py

current-state selection and persistence proposal:
  btcts_next/src/btcts/prediction/market_regime/current_state_estimator.py
  btcts_next/src/btcts/prediction/market_regime/current_state_persistence.py

classifier diagnostics:
  btcts_next/src/btcts/prediction/market_regime/inference/regime_classifier.py

focused guards:
  btcts_next/src/btcts/prediction/tests/test_market_regime_transition_policy.py
  btcts_next/src/btcts/prediction/tests/test_market_regime_transition_persistence_sequence.py
  btcts_next/src/btcts/prediction/tests/test_market_regime_current_state_persistence.py
  btcts_next/src/btcts/prediction/tests/test_market_regime_current_state_estimator.py
  btcts_next/src/btcts/prediction/tests/test_market_regime_regime_classifier_v1.py
  btcts_next/src/btcts/prediction/tests/test_market_regime_write_latest_mvp.py
```

## Transition policy contract

The policy evaluates previous state, candidate state, state age, candidate margin, change-point evidence, and family parameters.

```text
logic_version=prediction.market_regime.transition_policy.mr_f4.v1
minimum_dwell_sec=300
hysteresis_margin=0.10
change_point_override_threshold=0.80
transition_penalty=0.12
persistence_probability_calibrated=false
would_send_to_broker=false
```

Accepted decisions:

```text
unknown
started
continued
held
transitioned
```

Accepted blockers include:

```text
candidate_regime_unknown
invalid_transition
minimum_dwell_not_satisfied
hysteresis_margin_not_satisfied
```

An invalid transition remains blocked even when change-point evidence exceeds the override threshold.

## Persistence and churn behavior

Repeated nearby observations do not reset an unchanged state.

```text
same_regime_preserves_state_started_at=true
same_regime_increments_state_age=true
insufficient_dwell_holds_previous=true
insufficient_margin_holds_previous=true
valid_transition_after_dwell_and_margin=true
invalid_transition_holds_previous=true
```

The persisted-sequence guard validates:

```text
first state starts at observation time
continued state preserves original start time
held candidate preserves previous regime
accepted transition starts the new regime
invalid transition remains held under high change-point evidence
```

## Canonical label ownership

MR-F4 activates transition-policy ownership for the canonical current-state label.

```text
canonical_application_enabled=true
transition_policy_observation_only=false
score_alone_can_switch_label=false
transition_policy_required_for_switch=true
```

Selection behavior:

```text
current evidence unusable:
  UNKNOWN

recommendation ready and transition accepted:
  use accepted regime

recommendation not ready or transition held:
  preserve previous persisted regime

no previous persisted regime:
  use bounded MR-F2 current-L4 fallback
```

This preserves a fail-closed migration path while preventing score-only label churn.

## Diagnostic consistency

Current-evidence diagnostics recognize both the legacy estimator reason and MR-F4 transition-policy reason.

```text
fresh_current_evidence_remains_live=true
current_state_estimator_used=true
selected_label_source=current_state_estimator
selected_forecast_label_empty_for_current_state=true
selected_l4_candle_regime_hint_preserved=true
canonical_selection_reason_exposed=true
transition_application_exposed=true
```

`shadow_transition_observation_only` is packet-specific:

```text
transition applied to selected label:
  false

transition not applied to selected label:
  true
```

## Explicit transition matrix

The initial family-owned matrix accepts only explicit neighboring transitions. Representative paths include:

```text
RANGE -> LOW_VOL_COMPRESSION | BREAKOUT | HIGH_VOL_CHOP
LOW_VOL_COMPRESSION -> RANGE | BREAKOUT
BREAKOUT -> UP_TREND | DOWN_TREND | HIGH_VOL_CHOP | RANGE
TREND -> REVERSAL_WATCH | HIGH_VOL_CHOP | RANGE
REVERSAL_WATCH -> RANGE | UP_TREND | DOWN_TREND | HIGH_VOL_CHOP
HIGH_VOL_CHOP -> RANGE | UP_TREND | DOWN_TREND | PANIC_SPIKE
PANIC_SPIKE -> HIGH_VOL_CHOP | RANGE
```

Self-transitions are allowed. Unlisted transitions are rejected.

## Persistence probability maturity

The policy exposes a bounded persistence probability for diagnostics, but it is not yet empirically calibrated.

```text
persistence_probability_exposed=true
persistence_probability_calibrated=false
used_as_activation_gate=false
displayed_as_calibrated_probability=false
```

Calibration remains MR-F7 work and does not block acceptance of the transparent MR-F4 transition baseline.

## D-hot evidence

A read-only probe used current artifacts under `D:/btc_ts_hot` and did not call a writer.

Representative final observation:

```text
selected_current_label=DOWN_TREND
persisted_current_state_present=false
shadow_recommendation_ready=false
shadow_recommended_regime_code=UNKNOWN
shadow_transition_decision=unknown
shadow_transition_blocker=candidate_regime_unknown
shadow_transition_applied_to_selected_label=false
shadow_transition_observation_only=true
write_function_called=false
would_send_to_broker=false
```

The absence of `prediction/market_regime/current_state.json` means the live one-shot writer had not persisted this artifact at probe time. Persistence semantics were therefore verified with isolated tmp fixtures rather than by mutating D-hot.

```text
d_hot_modified=false
fixture_persistence_sequence_verified=true
live_writer_execution_required_for_first_persisted_state=true
```

## Verification evidence

```text
transition_policy_shadow_head=8db023ec
persisted_sequence_guard_head=ee92abb9
canonical_application_head=e4f0d913
prediction_full_suite=320_passed
operator_ui_full_suite=1184_passed
focused_mr_f4_boundary=59_passed
canonical_selection_boundary=38_passed
persisted_sequence_tests=5_passed
git_diff_check=passed
working_tree_after_commit=clean
test_exclusions=0
```

## Safety

```text
read_only_market_sources=true
d_hot_probe_write=false
raw_market_payload_in_read_model=false
ui_inference=false
ui_confidence_recalculation=false
broker_private_api=false
autotrade=false
order_submission=false
parameter_auto_promotion=false
```

## Known non-blocking gaps

```text
persistence_probability_not_calibrated=true
live_d_hot_persisted_state_not_yet_observed=true
statistical_transition_models_remain_shadow_only=true
future_horizon_forecast_not_part_of_mr_f4=true
```

These gaps belong to later roadmap stages or operational observation and do not invalidate the transparent transition baseline.

## Acceptance decision

```text
mr_f4_transition_and_persistence_behavior_accepted=true
minimum_dwell_behavior_accepted=true
hysteresis_behavior_accepted=true
transition_penalty_accepted=true
change_point_override_accepted=true
invalid_transition_guard_accepted=true
state_persistence_probability_contract_accepted=true
canonical_transition_application_accepted=true
state_churn_guard_accepted=true
impossible_transition_acceptance_forbidden=true
current_gate=MR_F4_TRANSITION_AND_PERSISTENCE_BEHAVIOR_ACCEPTED
next_gate=MR_F5_HORIZON_SPECIFIC_FUTURE_FORECAST_IMPLEMENTATION
```
