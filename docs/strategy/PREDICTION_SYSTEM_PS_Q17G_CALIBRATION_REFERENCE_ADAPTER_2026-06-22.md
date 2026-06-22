# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q17G_CALIBRATION_REFERENCE_ADAPTER_2026-06-22.md
# desc: PS-Q17G standalone calibration reference adapter after PS-Q17F contract.
# Prediction System PS-Q17G Calibration Reference Adapter

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: adapter-only / contract-only / diagnostic-only / non-executing / no D-hot actual read / no confidence increase / no signal reliability claim / no parameter tuning / no WarRoom widget rendering

## Purpose

PS-Q17G proves a standalone adapter can normalize supplied calibration refs into the PS-Q17F calibration reference contract shape.

This slice does not read D-hot, generate predictions, refresh latest artifacts, render widgets, write runtime/status artifacts, increase confidence, make signal reliability claims, tune/stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.

## Checker

```text
checker=check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.v1
adapter_version=calibration_reference_adapter.v1
source_checker=check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.v1
adapter_only=true
contract_only=true
diagnostic_only=true
warroom_widget_design_premise=true
warroom_widget_implementation_allowed=false
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
calibration_ref_id
market_uid
sample_window.start_at
sample_window.end_at
sample_window.market_uid
sample_window.horizon_keys
calibration_refs.signal_strength.model_version
calibration_refs.signal_strength.sample_count
calibration_refs.signal_strength.bucket_metrics
calibration_refs.reference_hit_rate.model_version
calibration_refs.reference_hit_rate.sample_count
calibration_refs.reference_hit_rate.bucket_metrics
calibration_release_gate.calibration_refs_present
calibration_release_gate.confidence_band_claim_allowed=false
calibration_release_gate.signal_reliability_claim_allowed=false
calibration_release_gate.parameter_tuning_allowed=false
warroom_calibration_explanation_packet.render_allowed=false
```

## Adapter invariants

```text
calibration refs may be normalized for review only
confidence_band_claim_allowed=false
signal_reliability_claim_allowed=false
parameter_tuning_allowed=false
warroom widget rendering remains deferred
D-hot read is not allowed
runtime/status writes are not allowed
```

## Not in this slice

```text
no_d_hot_actual_read
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
PS-Q17H: prediction-delta history contract or calibration adapter integration design. Confidence increase, parameter apply, and WarRoom widget rendering remain deferred.
```
