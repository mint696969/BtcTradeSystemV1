# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q17F_CALIBRATION_REFERENCE_CONTRACT_2026-06-22.md
# desc: PS-Q17F calibration reference contract after PS-Q17B inference-quality gap plan.
# Prediction System PS-Q17F Calibration Reference Contract

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: contract-only / diagnostic-only / plan-only / non-executing / no D-hot actual read / no confidence increase / no parameter tuning / no WarRoom widget rendering

## Purpose

PS-Q17F turns the PS-Q17B P0 gap `calibration_refs_and_signal_strength_validation` into explicit calibration reference contracts before confidence increase, signal reliability claims, parameter tuning, or WarRoom widget reliability claims.

This slice does not read D-hot, generate predictions, refresh latest artifacts, render widgets, write runtime/status artifacts, increase confidence, tune/stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.

## Checker

```text
checker=check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.v1
source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1
source_gap_id=calibration_refs_and_signal_strength_validation
contract_only=true
diagnostic_only=true
plan_only=true
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

## Calibration contract rows

```text
P0 signal_strength_calibration_reference_contract
P0 reference_hit_rate_calibration_reference_contract
P0 calibration_sample_window_contract
P0 confidence_band_release_contract
P1 parameter_candidate_calibration_dependency_contract
P1 warroom_calibration_explanation_contract
```

## Required calibration fields

```text
calibration_refs.signal_strength.model_version
calibration_refs.signal_strength.sample_window.start_at
calibration_refs.signal_strength.sample_window.end_at
calibration_refs.signal_strength.sample_count
calibration_refs.signal_strength.bucket_metrics
calibration_refs.reference_hit_rate.model_version
calibration_refs.reference_hit_rate.sample_window.start_at
calibration_refs.reference_hit_rate.sample_count
calibration_refs.reference_hit_rate.bucket_metrics
calibration_release_gate.calibration_refs_present
calibration_release_gate.confidence_band_claim_allowed
calibration_release_gate.parameter_tuning_allowed
```

## Release rule

```text
calibration_refs_present must be true before confidence band claims.
confidence_band_claim_allowed remains false while calibration refs are missing or stale.
parameter_tuning_allowed remains false until signal-strength and reference-hit-rate refs can tie baseline/candidate/rollback evidence together.
WarRoom signal calibration widget rendering remains deferred until refs exist.
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
PS-Q17G: calibration reference adapter or prediction-delta history contract. Confidence increase, parameter apply, and WarRoom widget rendering remain deferred.
```
