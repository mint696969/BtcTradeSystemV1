# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19G_WARROOM_OBSERVATION_CLOSE_AND_REFRESH_POLICY_DECISION_2026-06-25.md
# desc: PS-Q19G observation close and refresh policy decision for WarRoom latest prediction path.
# PS-Q19G WarRoom observation close and refresh policy decision

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 7f74d649

## Purpose

PS-Q19G closes the wiring/observation portion of the WarRoom realtime prediction path and declares the next safe refresh policy.

PS-Q19F proved that the WarRoom prediction display path now reads D hot:

```text
observed_source_artifact_path=D:/btc_ts_hot/prediction/latest_prediction_system_result.json
observed_prediction_row_count=24
observed_freshness_state=stale
```

The path is wired correctly, but the latest prediction artifact is stale. Therefore PS-Q19G chooses **manual refresh first, scheduler deferred**.

```text
ps_q19g_warroom_observation_close_and_refresh_policy_decision=true
observation_path_ready=true
read_model_source_is_hot_latest_root=true
manual_refresh_recommended_now=true
refresh_policy_decision=manual_refresh_first_scheduler_deferred
scheduler_policy_decision=do_not_enable_scheduler_until_after_manual_refresh_visual_confirmation
scheduled_loop_enabled=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
runtime_artifact_write_performed_by_policy_helper=false
status_artifact_write_performed_by_policy_helper=false
manual_refresh_executed_by_policy_helper=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Next operator action

PS-Q19G does not execute the refresh. It only prints the safe command shape.

One bounded non-UI manual refresh:

```powershell
python .\tools\run_prediction_warroom_bounded_manual_refresh_ps_q19e.py `
  --root D:\btc_ts_hot `
  --execute-manual-refresh `
  --ack PS_Q19E_RUN_BOUNDED_NON_UI_MANUAL_REFRESH
```

Then resmoke / visual confirmation:

```powershell
python .\tools\check_phase4a_prediction_system_ps_q19f_warroom_live_smoke.py `
  --root D:\btc_ts_hot `
  --manual-visual-confirmation `
  --observed-panel-visible `
  --observed-prediction-rows `
  --observed-market-snapshot `
  --observed-safety-flags
```

## Safety boundary

```text
read_only_policy_helper=true
runtime_artifact_write_performed_by_policy_helper=false
status_artifact_write_performed_by_policy_helper=false
manual_refresh_executed_by_policy_helper=false
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

## Next recommended step

```text
PS-Q19H_OPERATOR_ACK_BOUNDED_MANUAL_REFRESH_AND_WARROOM_VISUAL_RESMOKE
```

This next step is operational and ACK-gated. It may not need repository code changes unless the refresh or WarRoom smoke exposes another issue.
