# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q16A_NON_UI_SCHEDULED_PRODUCER_CONTRACT_2026-06-22.md
# desc: PS-Q16A contract-only design for WarRoom realtime prediction observation via a future disabled-by-default non-UI scheduled producer.
# Prediction System PS-Q16A Non-UI Scheduled Producer Contract

Updated: 2026-06-22 JST
Status: contract / guard / visibility design only
Scope: WarRoom realtime prediction observation and accuracy-review visibility; AutoTrade trigger-candidate work is deferred.

## Purpose

PS-Q16A starts Option B from the PS-Q15F handoff.

The current priority is:

```text
WarRoom tab can observe Prediction System output as a continually refreshed read-only source,
and the operator can review accuracy / calibration adjustment candidates safely.
```

This slice does **not** enable a scheduler, producer loop, runtime artifact write automation, WarRoom UI trigger, parameter apply/staging, AutoTrade, broker/private API, approval, or ledger behavior.

## Source of truth from PS-Q15F

```text
Option A proved PS-Q12D -> PS-Q10H -> PS-Q9Y can refresh D:\btc_ts_hot\prediction\latest_prediction_system_result.json.
WarRoom latest prediction source can reach latest_prediction_source_ready after a fresh artifact exists.
The remaining gap is ongoing production/freshness of the latest prediction artifact.
```

## Contract identity

```text
contract_version=prediction_warroom_non_ui_scheduled_producer_contract.ps_q16a.v1
latest_prediction_artifact_relative_path=prediction/latest_prediction_system_result.json
producer_status_artifact_relative_path=prediction/status/non_ui_scheduled_producer_status.json
freshness_max_age_sec=3600
freshness_warning_age_sec=900
recommended_cadence_sec=300
minimum_cadence_sec=60
maximum_cadence_sec=900
```

## First-slice safety state

```text
contract_only=true
guard_only=true
visibility_design_required=true
non_ui_only=true
producer_enabled=false
scheduler_enabled=false
runtime_artifact_write_enabled=false
warroom_ui_trigger_enabled=false
ready_for_scheduler_enablement=false
ready_for_runtime_artifact_write_automation_enablement=false
```

## Required producer status visibility

Future disabled runner and WarRoom status display must preserve these fields:

```text
producer_version
producer_state
producer_enabled
scheduler_enabled
runtime_artifact_write_enabled
latest_prediction_artifact_relative_path
status_artifact_relative_path
freshness_max_age_sec
recommended_cadence_sec
last_run_started_at
last_run_finished_at
last_success_at
last_failure_at
last_success_generated_at
last_prediction_run_id
last_target_file_size_bytes
last_warning_count
last_blocker_count
consecutive_failure_count
safe_flags
warnings
blockers
disable_rollback_state
```

WarRoom should show missing producer status as:

```text
producer_status=not_configured_or_not_running
latest_prediction_source=existing read-only adapter result
operator_note=continuous producer not enabled yet; do not force-ready
```

## Accuracy / calibration review boundary

The WarRoom target is not only live display. It must also let the operator review accuracy-improvement candidates while avoiding silent mutation.

Allowed in this slice:

```text
source_quality_cap_review
signal_strength_band_calibration_review
warning_to_blocker_threshold_review
horizon_family_weight_review
replay_outcome_calibration_review
```

Forbidden in this slice:

```text
parameter_apply_request=blocked
parameter_staging_write_request=blocked
silent_live_parameter_mutation_request=blocked
parameter_version_append_request=blocked
AutoTrade trigger threshold activation=true
```

Any future adjustment requires human review and replay/shadow evidence before apply or staging write.

## Disable / rollback path

Before scheduler enablement, a disable/rollback path must be visible:

```text
default_enabled=false
rollback_action=disable scheduler or runner; WarRoom continues read-only observation of last artifact/status
rollback_does_not_delete_latest_prediction_artifact=true
rollback_does_not_force_ready=yes
rollback_does_not_mutate_parameters=true
rollback_requires_operator_visibility=true
```

## Forbidden behavior in PS-Q16A

```text
request_scheduler_enable=true
request_runtime_artifact_write_enable=true
request_producer_enable=true
request_warroom_ui_trigger=true
request_parameter_apply_request=blocked
request_parameter_staging_write_request=blocked
request_approval_or_ledger_or_autotrade_or_broker=true
broker_private_api_request=blocked
ledger_append_request=blocked
freshness_bypass_request=blocked
force_ready_request=blocked
```

## Next safe slices

```text
PS-Q16B: disabled-by-default non-UI producer runner scaffold and status artifact writer, still not scheduled.
PS-Q16C: WarRoom read-only producer status visibility panel.
PS-Q16D: bounded manual run / smoke proving latest artifact refresh + status visibility.
PS-Q16E: scheduler enablement preflight guard and human decision checkpoint.
```

AutoTrade trigger-candidate contract remains deferred until WarRoom realtime observation and accuracy-review visibility are stable.
