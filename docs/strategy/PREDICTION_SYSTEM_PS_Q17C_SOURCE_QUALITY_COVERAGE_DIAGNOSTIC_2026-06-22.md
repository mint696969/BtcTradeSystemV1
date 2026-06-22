# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q17C_SOURCE_QUALITY_COVERAGE_DIAGNOSTIC_2026-06-22.md
# desc: PS-Q17C source-quality coverage diagnostic after PS-Q17B inference-quality gap plan.
# Prediction System PS-Q17C Source-Quality Coverage Diagnostic

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: diagnostic-only / plan-only / non-executing / no D-hot actual read / no WarRoom widget rendering

## Purpose

PS-Q17C decomposes the PS-Q17B P0 gap `source_quality_cap_and_coverage` into concrete diagnostic contracts before increasing confidence or implementing WarRoom realtime widgets.

This slice does not read D-hot, generate predictions, refresh latest artifacts, render widgets, write runtime/status artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.

## Checker

```text
checker=check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.v1
source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1
source_quality_gap_id=source_quality_cap_and_coverage
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

## Source-quality diagnostics

```text
P0 tier0_source_quality_gate_coverage
P0 source_quality_warning_taxonomy
P0 source_artifact_coverage_mapping
P0 signal_strength_cap_reason_accounting
P1 basis_and_cross_venue_reference_requirements
P1 context_profile_minimum_source_requirements
```

## Observed warning taxonomy to make actionable

```text
tier0_source_quality_gate_not_passed
tier0_source_quality_missing_or_degraded
tier0_source_quality_signal_strength_capped
basis_blocker:bitflyer_spot_reference_missing
low_usable_venue_count_liquidity_caution
context_profile_family_minimum_sources_missing
technical_warning:insufficient_candles_for_long_ma
```

## Required source-quality fields before confidence increase

```text
tier0_source_quality_gate.state
tier0_source_quality_gate.reason_codes
source_artifact_coverage.by_family
source_artifact_coverage.required_source_count
source_artifact_coverage.usable_source_count
source_contribution_ledger.by_record
signal_strength_cap_reason.by_record
basis_reference_status.bitflyer_spot
cross_venue_reference_status.usable_venue_count
context_profile_source_caps.by_family
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
PS-Q17D: tier0 source-quality gate coverage contract or calibration reference contract. WarRoom widget rendering remains deferred.
```
