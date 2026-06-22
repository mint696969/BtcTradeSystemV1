# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q17N_PARAMETER_CANDIDATE_EVIDENCE_CONTRACT_2026-06-22.md
# desc: PS-Q17N parameter-candidate evidence contract after PS-Q17B inference-quality gap plan.
# Prediction System PS-Q17N Parameter-Candidate Evidence Contract

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: contract-only / diagnostic-only / plan-only / non-executing / no D-hot actual read / no parameter-candidate actual read / no WarRoom widget rendering / no parameter staging or apply

## Purpose

PS-Q17N turns the PS-Q17B P1 gap `parameter_candidate_evidence` into explicit source, baseline reference, candidate diff, rollback threshold, release gate, and WarRoom explanation contracts before parameter staging, parameter apply, confidence increase, or parameter-candidate widget reliability.

This slice does not read D-hot, read parameter candidates, tune/stage/apply parameters, refresh latest artifacts, render widgets, write runtime/status artifacts, append ledgers, trigger AutoTrade, or call broker/private APIs.

## Checker

```text
checker=check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.v1
source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1
source_gap_id=parameter_candidate_evidence
contract_only=true
diagnostic_only=true
plan_only=true
warroom_widget_design_premise=true
warroom_widget_implementation_allowed=false
parameter_candidate_actual_read_allowed=false
parameter_candidate_widget_rendering_allowed=false
parameter_candidate_reliability_claim_allowed=false
confidence_increase_allowed=false
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

## Parameter-candidate evidence contract rows

```text
P0 parameter_candidate_source_contract
P0 baseline_parameter_reference_contract
P0 candidate_parameter_diff_contract
P0 rollback_threshold_contract
P0 parameter_evidence_completeness_release_gate_contract
P1 warroom_parameter_candidate_explanation_contract
```

## Required parameter fields

```text
parameter_candidate.source_artifact_ref
parameter_candidate.generated_at
parameter_candidate.baseline.ref_id
parameter_candidate.baseline.parameter_set_id
parameter_candidate.candidate.candidate_id
parameter_candidate.candidate.changed_parameter_keys
parameter_candidate.candidate.expected_effect_summary
parameter_candidate.evidence.source_quality_ref_id
parameter_candidate.evidence.calibration_ref_id
parameter_candidate.evidence.replay_feedback_ref_id
parameter_candidate.rollback.rollback_threshold_ref_id
parameter_candidate.rollback.rollback_condition_summary
parameter_candidate_release_gate.evidence_complete
parameter_candidate_release_gate.parameter_staging_allowed
parameter_candidate_release_gate.parameter_apply_allowed
```

## Release rule

```text
baseline_candidate_rollback_evidence_required_before_staging=true
parameter_staging_write_allowed=false until baseline, candidate diff, rollback, source-quality, calibration, and replay evidence are complete.
parameter_apply_allowed=false until a later explicit approval/apply slice.
confidence_increase_allowed=false until parameter evidence and replay calibration are verified.
WarRoom parameter-candidate widget rendering remains deferred until release gate is true in a later slice.
```

## Not in this slice

```text
no_d_hot_actual_read
no_parameter_candidate_actual_read
no_live_parameter_candidate_evaluation
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
PS-Q17O: parameter-candidate evidence adapter or WarRoom prediction widget integration design checkpoint. Confidence increase, parameter staging/apply, and WarRoom widget rendering remain deferred.
```
