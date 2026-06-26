# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21W_REGISTER_DISABLED_SCHEDULER_ONCE_2026-06-26.md
# desc: PS-Q21W adds a gated one-time disabled Windows Scheduled Task registration tool. Default is dry-run/no registration; producer loop remains separate.
# PS-Q21W register disabled scheduler once

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: ea4bc3e1

## Purpose

PS-Q21W introduces the gated tool for one real disabled scheduler registration. The default command does not register anything. With the exact confirmation token, the tool may register one Windows Scheduled Task that is disabled, has no trigger, and points only to the PS-Q21V dry-run tool.

```text
ps_q21w_register_disabled_scheduler_once=true
default_execution_is_dry_run_no_registration=true
execute_registration_requires_confirmation=REGISTER_DISABLED_NON_UI_SCHEDULER_ONCE_WITH_ROLLBACK_PLAN
registered_task_state_required=Disabled
registered_task_trigger_count_required=0
producer_loop_still_separate_approval=true
scheduler_registered_by_default=false
```

## Task contract

```text
task_name=BTC_TS_PredictionWarRoom_NonUI_DisabledScheduler
task_path=\BtcTradeSystem\
action_target=tools/run_phase4a_prediction_system_ps_q21v_disabled_scheduler_registration_smoke.py
action_mode=PS-Q21V dry-run only
triggers=0
state=Disabled
run_level=Limited
rollback=Unregister only this task if action matches PS-Q21V dry-run
```

## Preconditions for actual registration

```text
repo_clean_required=true
PS-Q21U_preflight_ready_required=true
D_hot_lock_absent_required=true
exact_operator_confirmation_required=true
post_registration_query_required=true
rollback_guard_required=true
```

## Safety boundary

```text
producer_loop_enabled=false
producer_runner_invoked=false
latest_prediction_artifact_written=false
status_artifact_written=false
warroom_ui_trigger_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
would_write_collector_state=false
```

## Not in this slice

```text
no_producer_loop_enablement
no_runner_invocation
no_prediction_artifact_write
no_status_artifact_write
no_D_hot_lock_creation
no_lock_acquire_or_release
no_WarRoom_UI_trigger
no_parameter_apply
no_ledger_append
no_AutoTrade
no_broker_private_api
```

## Next gate

```text
ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN
```

Producer loop enablement remains a later, separate approval even after disabled scheduler registration succeeds.
