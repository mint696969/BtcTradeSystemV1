# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q17H_PREDICTION_DELTA_HISTORY_CONTRACT_2026-06-22.md
# desc: PS-Q17H prediction-delta history contract after PS-Q17B inference-quality gap plan.
# Prediction System PS-Q17H Prediction-Delta History Contract

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: contract-only / diagnostic-only / plan-only / non-executing / no D-hot actual read / no history actual read / no WarRoom widget rendering

## Purpose

PS-Q17H turns the PS-Q17B P0 gap `prediction_delta_history` into explicit previous/latest lineage and delta contracts before realtime delta widgets or WarRoom widget reliability claims.

This slice does not read D-hot, read prediction history, generate predictions, refresh latest artifacts, render widgets, write runtime/status artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.

## Checker

```text
checker=check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.v1
source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1
source_gap_id=prediction_delta_history
contract_only=true
diagnostic_only=true
plan_only=true
warroom_widget_design_premise=true
warroom_widget_implementation_allowed=false
delta_widget_rendering_allowed=false
history_actual_read_allowed=false
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

## Prediction-delta contract rows

```text
P0 previous_latest_snapshot_reference_contract
P0 latest_snapshot_lineage_contract
P0 delta_computation_key_contract
P0 warroom_delta_widget_release_contract
P1 delta_reason_taxonomy_contract
P1 history_retention_and_freshness_contract
```

## Required delta fields

```text
prediction_delta_history.previous_snapshot.run_id
prediction_delta_history.previous_snapshot.generated_at
prediction_delta_history.previous_snapshot.source_artifact_ref
prediction_delta_history.latest_snapshot.run_id
prediction_delta_history.latest_snapshot.generated_at
prediction_delta_history.latest_snapshot.source_artifact_ref
prediction_delta_history.delta_key.market_uid
prediction_delta_history.delta_key.family
prediction_delta_history.delta_key.horizon_key
prediction_delta_history.changed_fields
prediction_delta_history.delta_reason_codes
prediction_delta_release_gate.history_available
prediction_delta_release_gate.widget_reliability_claim_allowed
```

## Release rule

```text
history_available must be true before realtime delta widget reliability claims.
widget_reliability_claim_allowed remains false until previous/latest lineage and delta keys are verified.
WarRoom delta widget rendering remains deferred until history source, retention, freshness, and delta reason taxonomy exist.
```

## Not in this slice

```text
no_d_hot_actual_read
no_history_actual_read
no_ui_cleanup
no_widget_rendering_patch
no_warroom_page_mutation
no_warroom_ui_triggered_prediction_generation
no_manual_refresh_invocation
no_scheduler_enablement
no_status_write
no_runtime_write
no_parameter_staging_write
no_parameter_apply
no_approval
no_ledger_append
no_autotrade_trigger
no_broker_private_api
no_freshness_bypass
```

## Recommended next safe slice

```text
PS-Q17I: prediction-delta history adapter or replay-outcome calibration contract. Confidence increase, parameter apply, and WarRoom widget rendering remain deferred.
```
