# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q16D_BOUNDED_MANUAL_REFRESH_RUNNER_2026-06-22.md
# desc: PS-Q16D bounded manual refresh runner for latest prediction artifact and producer status visibility.
# Prediction System PS-Q16D Bounded Manual Refresh Runner

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: bounded manual refresh only; no scheduler and no WarRoom UI trigger

## Purpose

PS-Q16D adds a bounded manual refresh runner for the WarRoom realtime observation path.

It may invoke the existing PS-Q10H actual export runner once, then write producer status visibility, only when all explicit operator flags are true.

```text
actual_export_runner_invoked_only_after_all_explicit_flags=true
latest_prediction_artifact_relative_path=prediction/latest_prediction_system_result.json
producer_status_artifact_relative_path=prediction/status/non_ui_scheduled_producer_status.json
```

## Required manual gate

```text
operator_acknowledged=true
execute_manual_refresh=true
allow_actual_read=true
allow_prediction_build=true
allow_export_preflight=true
allow_latest_payload_export=true
allow_runtime_artifact_write=true
allow_status_artifact_write=true
execute_status_artifact_write=true
target_root_valid=true
```

## Safety state

```text
non_ui_runner_only=true
bounded_manual_run_only=true
producer_enabled=false
scheduler_enabled=false
scheduled_loop_enabled=false
warroom_ui_trigger_enabled=false
ui_triggered_runner_execution=false
ready_for_scheduler_enablement=false
ready_for_automation_enablement=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
```

## Status write behavior

The runner writes producer status after a manual attempt so WarRoom can observe success/failure.

Success status includes:

```text
last_success_at
last_success_generated_at
last_prediction_run_id
last_target_file_size_bytes
runtime_artifact_write_enabled=true
scheduler_enabled=false
producer_enabled=false
```

Blocked status includes blockers and keeps:

```text
scheduler_enabled=false
producer_enabled=false
disable_rollback_state=manual_refresh_only_disable_by_not_running; scheduler_not_registered
```

## Explicitly not in this slice

```text
scheduler_registration=false
scheduled_loop=false
WarRoom UI trigger=false
automation_enablement=false
parameter_apply=false
parameter_staging_write=false
approval_or_ledger_or_autotrade_or_broker=false
```

## Next safe slice

```text
PS-Q16E: operator-shell manual run wrapper/smoke using PS-Q16D against D-hot, with clean-tree precheck and WarRoom status visibility check.
PS-Q16F: scheduler enablement preflight guard and human decision checkpoint.
```
