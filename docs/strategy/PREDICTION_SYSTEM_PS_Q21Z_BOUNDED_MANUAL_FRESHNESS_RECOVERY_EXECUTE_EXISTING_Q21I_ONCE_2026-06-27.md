# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21Z_BOUNDED_MANUAL_FRESHNESS_RECOVERY_EXECUTE_EXISTING_Q21I_ONCE_2026-06-27.md
# desc: PS-Q21Z adds a gated one-shot wrapper for executing the existing PS-Q21I bounded manual freshness recovery once. Default is no execution; exact token required.
# PS-Q21Z bounded manual freshness recovery execute existing Q21I once

Updated: 2026-06-27 JST
Branch: docs/phase2-handoff-sync
Base clean head: 3255e569

## Purpose

PS-Q21Y confirmed that freshness recovery is ready for an operator-tokened one-shot PS-Q21I bounded manual refresh. PS-Q21Z adds a small gated wrapper around the existing PS-Q21I tool so the execution boundary is explicit, testable, and separate from producer-loop shadow once.

```text
ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once=true
default_execution_is_dry_run_no_write=true
execute_existing_q21i_once_requires_confirmation=WRITE_D_HOT_LATEST_PREDICTION_ONCE
requires_operator_acknowledged_flag=true
requires_execute_existing_q21i_once_flag=true
requires_q21y_ready_for_operator_token=true
producer_loop_shadow_once_still_separate=true
producer_loop_shadow_once_requires_confirmation=ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN
recurring_enablement_allowed_now=false
```

## Write scope when explicitly executed later

```text
uses_existing_tool=tools/run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write.py
writes_latest_prediction_artifact=D:\btc_ts_hot\prediction\latest_prediction_system_result.json
writes_status_artifact=D:\btc_ts_hot\prediction\status\non_ui_scheduled_producer_status.json
writes_only_when_all_cli_gates_present=true
writes_only_when_q21y_ready=true
single_run_only=true
```

## Safety boundary

```text
producer_loop_enabled=false
producer_runner_invoked=false
scheduled_loop_enabled=false
scheduler_enabled=false
scheduler_enablement_allowed_now=false
trigger_added=false
trigger_addition_allowed_now=false
recurring_enablement_allowed_now=false
warroom_ui_trigger_allowed=false
approval_or_ledger_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
would_write_collector_state=false
```

## Not in this slice

```text
no_producer_runner_invocation
no_producer_loop_shadow_once
no_scheduler_enablement
no_trigger_addition
no_recurring_enablement
no_warroom_ui_trigger
no_parameter_apply
no_parameter_staging_write
no_ledger_append
no_AutoTrade
no_broker_private_api
```

## Operator command after commit and explicit approval

```powershell
python .\tools\run_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once.py `
  --operator-acknowledged `
  --execute-existing-q21i-once `
  --confirmation WRITE_D_HOT_LATEST_PREDICTION_ONCE
```

This command performs only a bounded manual freshness recovery through PS-Q21I. It does not authorize producer-loop shadow once, scheduler enablement, trigger addition, or recurring enablement.
