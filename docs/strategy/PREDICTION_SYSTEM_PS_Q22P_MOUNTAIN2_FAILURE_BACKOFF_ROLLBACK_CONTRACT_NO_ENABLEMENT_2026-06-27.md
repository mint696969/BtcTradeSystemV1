# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q22P_MOUNTAIN2_FAILURE_BACKOFF_ROLLBACK_CONTRACT_NO_ENABLEMENT_2026-06-27.md
# desc: PS-Q22P defines future Mountain2 tick failure/backoff/status visibility/rollback contract. No scheduler enablement, no trigger addition, no recurring execution, no runtime writes.
# PS-Q22P Mountain2 failure / backoff / rollback contract no enablement

Updated: 2026-06-27 JST
Base head: 2d879d79

```text
ps_q22p_mountain2_failure_backoff_rollback_contract_no_enablement=true
read_only_contract_only=true
no_scheduler_enablement=true
no_trigger_addition=true
no_recurring_or_periodic_execution=true
no_latest_prediction_artifact_write=true
no_status_artifact_write=true
no_lock_acquire=true
no_broker_autotrade=true
```

## Purpose

PS-Q22O introduced a no-enable future scheduled tick skeleton. PS-Q22P defines how that future tick must behave on success, skip, failure, stale lock, and rollback before Mountain2 can be approved.

This slice does not execute Mountain2 and does not write runtime artifacts.

## Future failure/backoff contract

```text
future_tick_must_write_status_on_success=true
future_tick_must_write_status_on_failure=true
future_tick_must_write_status_on_skip=true
future_tick_must_preserve_last_success_on_failure=true
future_tick_must_not_delete_latest_on_failure=true
future_tick_must_increment_consecutive_failure_count=true
future_tick_soft_backoff_after_failures=2
future_tick_hard_disable_after_failures=3
future_tick_must_fail_closed_on_blockers=true
future_tick_must_release_lock_on_success_failure_or_skip=true
future_tick_must_not_retry_inside_same_tick=true
future_tick_must_require_operator_for_rollback_or_enablement=true
```

## Future rollback contract

```text
rollback_must_disable_scheduler_first=true
rollback_must_remove_added_periodic_trigger=true
rollback_must_restore_disabled_dry_run_action_if_action_replaced=true
rollback_must_not_delete_latest_prediction=true
rollback_must_not_mutate_parameters=true
rollback_must_not_append_ledger=true
rollback_must_preserve_status_visibility=true
```

## Current slice boundary

```text
scheduler_enabled=false
trigger_added=false
trigger_addition_allowed_now=false
recurring_enablement_allowed_now=false
periodic_execution_enabled=false
producer_loop_enabled=false
producer_runner_invoked=false
latest_prediction_artifact_written=false
status_artifact_written=false
lock_file_created=false
lock_acquire_attempted=false
lock_release_attempted=false
rollback_executed=false
warroom_ui_trigger_allowed=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
would_send_to_broker=false
would_write_collector_state=false
```

## Next after PS-Q22P

Implement a no-enable pre-live checklist or stop at the actual Mountain2 danger boundary. Before replacing task action, adding trigger, enabling scheduler, or allowing recurring/periodic execution, the assistant must stop and request explicit operator approval.
