# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21O_SINGLE_RUN_LOCK_CONTRACT_NO_FILE_CREATION_2026-06-26.md
# desc: PS-Q21O adds a read-only single non-overlapping run-lock contract. No lock file creation, scheduler registration, producer loop, or writes.
# PS-Q21O single non-overlapping run-lock contract

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: e4ea9a48

## Purpose

PS-Q21N produced a disabled non-UI scheduler/producer dry-run design. PS-Q21O adds the next required boundary: a single non-overlapping run-lock contract. This slice describes the future lock path, owner fields, acquire/release policy, and stale-lock recovery policy without creating a lock file or invoking any runner.

```text
ps_q21o_single_run_lock_contract=true
read_only_lock_contract_only=true
lock_contract_ready=observed_result
lock_file_creation_allowed=false
lock_file_write_allowed=false
lock_acquire_allowed_now=false
scheduler_registration_allowed=false
producer_loop_allowed=false
recurring_enablement_allowed_now=false
```

## Lock contract design

```text
lock_relative_path_design=prediction/runtime/non_ui_scheduler_producer.lock.json
single_non_overlapping_runner_lock_required=true
lock_owner_fields=run_id,pid,host,started_at_utc,expires_at_utc,reason
lock_stale_after_sec=900
acquire_policy=future_runner_must_acquire_lock_before_actual_read_or_export
release_policy=future_runner_must_release_lock_after_success_or_failure
stale_lock_recovery_policy=future_runner_may_recover_only_after_stale_age_and_status_visibility
overlap_policy=skip_or_fail_closed_if_lock_active_never_overlap_runs
enablement_allowed_without_lock=false
```

## Explicit non-execution result

```text
lock_file_created=false
lock_file_written=false
lock_acquire_attempted=false
lock_acquired=false
lock_release_attempted=false
lock_released=false
stale_lock_deleted=false
scheduler_registered=false
scheduler_started=false
producer_loop_enabled=false
producer_runner_invoked=false
bounded_manual_refresh_invoked=false
actual_export_runner_invoked=false
latest_prediction_artifact_written=false
status_artifact_written=false
warroom_ui_trigger_invoked=false
```

## Safety boundary

```text
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
warroom_ui_trigger_allowed=false
approval_or_ledger_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
would_write_collector_state=false
```

## Interpretation

PS-Q21O is a lock contract only. It does not create a lock file and does not acquire or release any lock. A later disabled lock smoke may use a temp/mock path, but scheduler registration, producer loop enablement, and artifact writes remain separate approvals.
