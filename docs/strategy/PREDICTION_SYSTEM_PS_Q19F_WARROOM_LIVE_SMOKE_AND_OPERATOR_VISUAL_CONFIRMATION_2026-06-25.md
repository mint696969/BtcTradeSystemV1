# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19F_WARROOM_LIVE_SMOKE_AND_OPERATOR_VISUAL_CONFIRMATION_2026-06-25.md
# desc: PS-Q19F design/implementation note for WarRoom live smoke and operator visual confirmation.
# PS-Q19F WarRoom live smoke and operator visual confirmation

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: a8212052

## Purpose

PS-Q19F adds a read-only live smoke helper for the WarRoom prediction display path built in PS-Q19C through PS-Q19E.

It verifies:

```text
ps_q19f_warroom_live_smoke_and_operator_visual_confirmation=true
ps_q19e_dry_run_no_write_verified=true
ps_q19c_read_model_loaded=true
ps_q19d_display_packet_verified=true
operator_visual_confirmation_flags_supported=true
explicit_hot_latest_root_used_for_read_model=true
read_model_source_prefers_D_btc_ts_hot=true
runtime_artifact_write_performed_by_smoke=false
status_artifact_write_performed_by_smoke=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
ui_triggered_runner_execution=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Commands

Read-only smoke:

```powershell
python .\tools\check_phase4a_prediction_system_ps_q19f_warroom_live_smoke.py --root D:\btc_ts_hot
```

After the operator visually confirms the WarRoom tab, the same helper can record confirmation flags:

```powershell
python .\tools\check_phase4a_prediction_system_ps_q19f_warroom_live_smoke.py `
  --root D:\btc_ts_hot `
  --manual-visual-confirmation `
  --observed-panel-visible `
  --observed-prediction-rows `
  --observed-market-snapshot `
  --observed-safety-flags
```

Optional one-shot refresh remains PS-Q19E, not PS-Q19F:

```powershell
python .\tools\run_prediction_warroom_bounded_manual_refresh_ps_q19e.py `
  --root D:\btc_ts_hot `
  --execute-manual-refresh `
  --ack PS_Q19E_RUN_BOUNDED_NON_UI_MANUAL_REFRESH
```

## Safety boundary

```text
read_only_smoke_helper=true
runtime_artifact_write_performed_by_smoke=false
status_artifact_write_performed_by_smoke=false
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
PS-Q19G_WARROOM_OBSERVATION_CLOSE_AND_REFRESH_POLICY_DECISION
```

Use PS-Q19G to decide whether the current display + manual guarded refresh is enough for observation, or whether to add a real disabled-by-default scheduler/producer loop in a later slice.
