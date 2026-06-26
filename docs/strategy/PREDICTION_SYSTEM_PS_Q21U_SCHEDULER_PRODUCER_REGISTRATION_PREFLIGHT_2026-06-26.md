# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21U_SCHEDULER_PRODUCER_REGISTRATION_PREFLIGHT_2026-06-26.md
# desc: PS-Q21U adds a read-only scheduler/producer registration preflight contract. No scheduler registration, producer loop, lock creation/acquire/release, runner invocation, or writes.
# PS-Q21U scheduler / producer registration preflight

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: f56bf48c

## Purpose

PS-Q21T proved a single D-hot lock creation smoke and rollback, then refreshed visibility back to non-stale/no-lock. PS-Q21U defines the next approval boundary for a future disabled non-UI scheduler registration. It does not register a scheduler and does not enable a producer loop.

```text
ps_q21u_scheduler_producer_registration_preflight=true
read_only_registration_preflight_only=true
preflight_state=observed_result
separate_operator_approval_required=true
required_operator_confirmation=REGISTER_DISABLED_NON_UI_SCHEDULER_ONCE_WITH_ROLLBACK_PLAN
producer_loop_separate_operator_approval_required=true
scheduler_registration_allowed_now=false
producer_loop_allowed_now=false
recurring_enablement_allowed_now=false
```

## Registration preflight contract

```text
clean_worktree_required=true
ps_q21q_visibility_non_stale_disabled_no_lock_required=true
d_hot_lock_absent_required_before_registration=true
scheduler_registration_default_disabled=true
register_disabled_scheduler_only=true
producer_loop_must_remain_disabled=true
runner_invocation_must_remain_disabled=true
status_artifact_write_must_remain_disabled=true
post_registration_visibility_recheck_required=true
rollback_plan_required=true
rollback_unregister_scheduler_only=true
producer_loop_enablement_still_separate_approval=true
broker_and_autotrade_never_allowed=true
```

## Rollback plan boundary

```text
rollback_scope=unregister_only_the_disabled_non_ui_scheduler_registered_by_the_approved_slice
rollback_must_not_delete_prediction_or_status_artifacts=true
rollback_must_not_delete_d_hot_lock_artifacts_except_explicit_smoke_lock_rollback=true
rollback_must_not_enable_producer_loop=true
rollback_must_not_touch_broker_or_autotrade=true
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

## Explicit non-execution result

```text
scheduler_registered=false
scheduler_started=false
scheduled_loop_enabled=false
producer_loop_enabled=false
producer_runner_invoked=false
bounded_manual_refresh_invoked=false
actual_export_runner_invoked=false
latest_prediction_artifact_written=false
status_artifact_written=false
warroom_ui_trigger_invoked=false
```

## Interpretation

PS-Q21U is not scheduler registration. It only verifies whether a future disabled scheduler registration slice could be separately approved. Producer loop enablement remains a later, separate approval even after disabled scheduler registration.
