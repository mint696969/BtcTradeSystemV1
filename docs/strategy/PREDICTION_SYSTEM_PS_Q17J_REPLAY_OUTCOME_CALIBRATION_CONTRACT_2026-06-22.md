# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q17J_REPLAY_OUTCOME_CALIBRATION_CONTRACT_2026-06-22.md
# desc: PS-Q17J replay-outcome calibration contract after PS-Q17B inference-quality gap plan.
# Prediction System PS-Q17J Replay-Outcome Calibration Contract

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: contract-only / diagnostic-only / plan-only / non-executing / no D-hot actual read / no replay-history actual read / no WarRoom widget rendering

## Purpose

PS-Q17J turns the PS-Q17B P0 gap `replay_outcome_calibration` into explicit replay feedback, outcome window, forecast-to-outcome join key, release gate, and WarRoom explanation contracts before confidence, reliability, parameter tuning, or replay outcome widget claims.

This slice does not read D-hot, read replay history, compute outcomes, refresh latest artifacts, render widgets, write runtime/status artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.

## Checker

```text
checker=check_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract.v1
source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1
source_gap_id=replay_outcome_calibration
contract_only=true
diagnostic_only=true
plan_only=true
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

## Replay-outcome contract rows

```text
P0 replay_feedback_reference_contract
P0 outcome_window_contract
P0 forecast_to_outcome_join_key_contract
P0 replay_calibration_release_gate_contract
P1 outcome_metric_taxonomy_contract
P1 warroom_replay_outcome_explanation_contract
```

## Required replay fields

```text
replay_outcome_calibration.replay_feedback.run_id
replay_outcome_calibration.replay_feedback.generated_at
replay_outcome_calibration.replay_feedback.source_artifact_ref
replay_outcome_calibration.outcome_window.start_at
replay_outcome_calibration.outcome_window.end_at
replay_outcome_calibration.outcome_window.market_uid
replay_outcome_calibration.outcome_window.horizon_keys
replay_outcome_calibration.forecast_to_outcome_key.market_uid
replay_outcome_calibration.forecast_to_outcome_key.family
replay_outcome_calibration.forecast_to_outcome_key.horizon_key
replay_outcome_calibration.forecast_to_outcome_key.record_id
replay_outcome_calibration.outcome_metrics.predicted_direction_hit
replay_outcome_calibration.outcome_metrics.actual_return_bps
replay_outcome_calibration.outcome_metrics.magnitude_error_bps
replay_calibration_release_gate.replay_feedback_present
replay_calibration_release_gate.confidence_reliability_claim_allowed
```

## Release rule

```text
replay_feedback_present must be true before confidence or signal reliability claims.
confidence_reliability_claim_allowed remains false until replay feedback, outcome windows, join keys, and outcome metrics are verified.
parameter_tuning_allowed remains false until replay outcomes can tie prediction bands, baseline/candidate evidence, and rollback thresholds together.
WarRoom replay outcome widget rendering remains deferred until replay refs exist.
```

## Not in this slice

```text
no_d_hot_actual_read
no_replay_history_actual_read
no_outcome_computation
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
PS-Q17K: replay-outcome calibration adapter or scenario-trace semantic mapping contract. Confidence increase, parameter apply, and WarRoom widget rendering remain deferred.
```
