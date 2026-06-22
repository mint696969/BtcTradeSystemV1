# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q17D_TIER0_SOURCE_QUALITY_GATE_COVERAGE_CONTRACT_2026-06-22.md
# desc: PS-Q17D tier0 source-quality gate coverage contract after PS-Q17C diagnostic.
# Prediction System PS-Q17D Tier0 Source-Quality Gate Coverage Contract

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: contract-only / diagnostic-only / plan-only / non-executing / no D-hot actual read / no confidence increase / no WarRoom widget rendering

## Purpose

PS-Q17D turns the PS-Q17C P0 diagnostic `tier0_source_quality_gate_coverage` into an explicit field contract before confidence increase or WarRoom widget reliability claims.

This slice does not read D-hot, generate predictions, refresh latest artifacts, render widgets, write runtime/status artifacts, increase confidence, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.

## Checker

```text
checker=check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.v1
source_checker=check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.v1
source_diagnostic_id=tier0_source_quality_gate_coverage
contract_only=true
diagnostic_only=true
plan_only=true
warroom_widget_design_premise=true
warroom_widget_implementation_allowed=false
confidence_increase_allowed=false
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

## Tier0 gate contract rows

```text
P0 tier0_gate_state_reason_contract
P0 required_usable_source_count_contract
P0 record_cap_provenance_contract
P0 confidence_release_gate_contract
P1 family_horizon_coverage_contract
P1 operator_action_reason_contract
```

## Required tier0 fields

```text
tier0_source_quality_gate.state
tier0_source_quality_gate.reason_codes
tier0_source_quality_gate.reason_severity_by_code
source_artifact_coverage.required_source_count
source_artifact_coverage.usable_source_count
source_artifact_coverage.missing_source_count
source_artifact_coverage.by_family
source_artifact_coverage.by_horizon
signal_strength_cap_reason.by_record
estimated_signal_strength_percent.pre_cap
estimated_signal_strength_percent.post_cap
confidence_release_gate.source_quality_gate_passed
```

## Gate and severity enums

```text
gate_state_enum=pass,warn,fail,unknown
reason_severity_enum=blocking,warning,context_only
```

## Release rule

```text
confidence_release_gate.source_quality_gate_passed must be true before any confidence increase.
confidence_release_gate.confidence_increase_allowed remains false unless no blocking reason codes remain.
WarRoom widget reliability claims remain deferred until tier0 gate state/reason/count/cap provenance contracts exist.
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
no_parameter_staging_write
no_parameter_apply
no_confidence_increase
no_approval
no_ledger_append
no_autotrade_trigger
no_broker_private_api
no_freshness_bypass
```

## Recommended next safe slice

```text
PS-Q17E: tier0 gate contract implementation adapter or calibration reference contract. Confidence increase and WarRoom widget rendering remain deferred.
```
