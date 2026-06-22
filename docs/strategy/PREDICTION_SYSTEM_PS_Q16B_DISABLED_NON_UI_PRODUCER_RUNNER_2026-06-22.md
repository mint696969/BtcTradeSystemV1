# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q16B_DISABLED_NON_UI_PRODUCER_RUNNER_2026-06-22.md
# desc: PS-Q16B disabled-by-default non-UI producer runner scaffold and status artifact writer for WarRoom realtime observation preparation.
# Prediction System PS-Q16B Disabled Non-UI Producer Runner

Updated: 2026-06-22 JST
Status: implementation + focused guard; not scheduled; not committed until GPT現物確認
Scope: disabled-by-default non-UI producer runner scaffold and explicit producer status artifact writer

## Purpose

PS-Q16B follows PS-Q16A and advances WarRoom realtime prediction observation without enabling continuous production yet.

This slice creates a runner scaffold that can make producer state visible to WarRoom through a status artifact:

```text
producer_status_artifact_relative_path=prediction/status/non_ui_scheduled_producer_status.json
```

It does not refresh or write the latest prediction artifact:

```text
latest_prediction_artifact_relative_path=prediction/latest_prediction_system_result.json
latest_prediction_artifact_write_enabled=false
```

## Safety state

```text
producer_enabled=false
scheduler_enabled=false
runtime_artifact_write_enabled=false
latest_prediction_artifact_write_enabled=false
ready_for_scheduler_enablement=false
ready_for_latest_prediction_artifact_write_automation=false
actual_export_runner_invoked=false
prediction_build_requested=false
warroom_ui_trigger_enabled=false
```

## Status write gate

The only IO allowed in PS-Q16B is the producer status artifact write.

It requires all of:

```text
operator_acknowledged=true
allow_status_artifact_write=true
execute_status_artifact_write=true
target_root_valid=true
```

Guard tests may use a temporary root with:

```text
allow_guard_test_root=true
```

The D-hot production root remains:

```text
D:\btc_ts_hot
```

## Status fields

The status payload must include the PS-Q16A required status fields:

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

## Explicitly deferred

```text
scheduler_registration=deferred
scheduled_loop=deferred
latest_prediction_artifact_refresh=deferred
actual_export_runner_invocation=deferred
WarRoom UI trigger=deferred
parameter apply=deferred
parameter staging write=deferred
AutoTrade trigger-candidate=deferred
broker/private API=forbidden
approval/decision/command ledger append=forbidden
```

## Next safe slice

```text
PS-Q16C: WarRoom read-only producer status loader/panel.
PS-Q16D: bounded manual refresh runner that invokes the existing actual export runner under explicit operator flags, still without scheduler registration.
PS-Q16E: scheduler enablement preflight guard and human decision checkpoint.
```
