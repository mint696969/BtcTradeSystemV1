# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19E_NON_UI_MANUAL_OR_SCHEDULED_REFRESH_GUARDED_2026-06-25.md
# desc: PS-Q19E design/implementation note for guarded non-UI manual/scheduled refresh entrypoint.
# PS-Q19E Non-UI manual or scheduled refresh guarded

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: c7385d24

## Purpose

PS-Q19E adds the guarded non-UI refresh entrypoint needed after the WarRoom display-only panel was mounted in PS-Q19D.

This slice does not enable a scheduler or producer loop by default. It adds an operator-run tool that is dry-run/no-write by default and can invoke the existing Q16D bounded manual refresh runner only when the explicit ACK is supplied.

```text
ps_q19e_non_ui_manual_or_scheduled_refresh_guarded=true
q16d_bounded_manual_refresh_runner_reused=true
operator_tool_added=true
default_dry_run_no_write=true
explicit_ack_required=true
manual_refresh_ack=PS_Q19E_RUN_BOUNDED_NON_UI_MANUAL_REFRESH
scheduled_refresh_declared=true
scheduled_loop_enabled=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
runtime_behavior_changed_by_patch=false
collector_data_collection_changed=false
ui_code_changed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Operator command shape

Dry-run / no write:

```powershell
python .\tools\run_prediction_warroom_bounded_manual_refresh_ps_q19e.py
```

One bounded non-UI manual refresh, when intentionally approved by the operator:

```powershell
python .\tools\run_prediction_warroom_bounded_manual_refresh_ps_q19e.py `
  --root D:\btc_ts_hot `
  --execute-manual-refresh `
  --ack PS_Q19E_RUN_BOUNDED_NON_UI_MANUAL_REFRESH
```

Scheduled request is represented but disabled:

```powershell
python .\tools\run_prediction_warroom_bounded_manual_refresh_ps_q19e.py --request-scheduled-refresh
```

## Safety boundary

```text
non_ui_runner_only=true
bounded_manual_run_only=true_when_ack_and_execute
manual_runtime_artifact_write_gate_declared=true
runtime_artifact_write_performed_by_patch=false
status_artifact_write_performed_by_patch=false
scheduled_loop_enabled=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
ui_triggered_runner_execution=false
approval_or_authorization_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```

## Next recommended slice

```text
PS-Q19F_WARROOM_LIVE_SMOKE_AND_OPERATOR_VISUAL_CONFIRMATION
```

After PS-Q19E is committed, the operator may run one bounded manual refresh if desired, then visually confirm the WarRoom display-only panel updates. AutoTrade trigger work remains deferred.
