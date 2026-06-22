# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q17K_REPLAY_OUTCOME_CALIBRATION_ADAPTER_2026-06-22.md
# desc: PS-Q17K standalone replay-outcome calibration adapter after PS-Q17J contract.
# Prediction System PS-Q17K Replay-Outcome Calibration Adapter

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: adapter-only / contract-only / diagnostic-only / non-executing / no D-hot actual read / no replay-history actual read / no WarRoom widget rendering

## Purpose

PS-Q17K proves a standalone adapter can normalize supplied replay feedback/outcome rows into the PS-Q17J replay-outcome calibration contract shape.

This slice does not read D-hot, read replay history, compute live outcomes, refresh latest artifacts, render widgets, write runtime/status artifacts, increase confidence, claim signal reliability, tune/stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.

## Checker

```text
checker=check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.v1
adapter_version=replay_outcome_calibration_adapter.v1
source_checker=check_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract.v1
adapter_only=true
contract_only=true
diagnostic_only=true
warroom_widget_design_premise=true
warroom_widget_implementation_allowed=false
replay_history_actual_read_allowed=false
replay_outcome_widget_rendering_allowed=false
confidence_increase_allowed=false
signal_reliability_claim_allowed=false
parameter_tuning_allowed=false
d_hot_actual_read_allowed=false
read_only=true
non_executing=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
approval_or_authorization_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
warroom_ui_trigger_enabled=false
refresh_invocation_allowed=false
scheduler_enabled=false
```

## Adapter output shape

```text
replay_outcome_calibration.replay_feedback.run_id
replay_outcome_calibration.replay_feedback.generated_at
replay_outcome_calibration.replay_feedback.source_artifact_ref
replay_outcome_calibration.outcome_window.start_at
replay_outcome_calibration.outcome_window.end_at
replay_outcome_calibration.outcome_window.market_uid
replay_outcome_calibration.outcome_window.horizon_keys
replay_outcome_calibration.outcome_rows[].forecast_to_outcome_key.market_uid
replay_outcome_calibration.outcome_rows[].forecast_to_outcome_key.family
replay_outcome_calibration.outcome_rows[].forecast_to_outcome_key.horizon_key
replay_outcome_calibration.outcome_rows[].forecast_to_outcome_key.record_id
replay_outcome_calibration.outcome_rows[].outcome_metrics.predicted_direction_hit
replay_outcome_calibration.outcome_rows[].outcome_metrics.actual_return_bps
replay_outcome_calibration.outcome_rows[].outcome_metrics.magnitude_error_bps
replay_calibration_release_gate.replay_feedback_present
replay_calibration_release_gate.confidence_reliability_claim_allowed=false
replay_calibration_release_gate.signal_reliability_claim_allowed=false
replay_calibration_release_gate.parameter_tuning_allowed=false
warroom_replay_outcome_widget.render_allowed=false
```

## Adapter invariants

```text
replay feedback may be normalized for review only
confidence_reliability_claim_allowed=false
signal_reliability_claim_allowed=false
parameter_tuning_allowed=false
WarRoom replay outcome widget rendering remains deferred
D-hot read is not allowed
replay-history actual read is not allowed
runtime/status writes are not allowed
```

## Not in this slice

```text
no_d_hot_actual_read
no_replay_history_actual_read
no_live_outcome_computation
no_ui_cleanup
no_widget_rendering_patch
no_warroom_page_mutation
no_warroom_ui_triggered_prediction_generation
no_manual_refresh_invocation
no_scheduler_enablement
no_status_write
no_runtime_write
no_parameter_tuning
no_parameter_staging_write
no_parameter_apply
no_confidence_increase
no_signal_reliability_claim
no_approval
no_ledger_append
no_autotrade_trigger
no_broker_private_api
no_freshness_bypass
```

## Recommended next safe slice

```text
PS-Q17L: scenario-trace semantic mapping contract or parameter-candidate evidence contract. Confidence increase, parameter apply, and WarRoom widget rendering remain deferred.
```
