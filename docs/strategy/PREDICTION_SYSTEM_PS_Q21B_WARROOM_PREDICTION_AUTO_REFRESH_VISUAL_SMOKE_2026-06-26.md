# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21B_WARROOM_PREDICTION_AUTO_REFRESH_VISUAL_SMOKE_2026-06-26.md
# desc: PS-Q21B minimal smoke helper for WarRoom latest prediction auto-refresh visual confirmation.
# PS-Q21B WarRoom prediction auto-refresh visual smoke

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: 3063d391

## Purpose

PS-Q21B keeps the work focused on the requested WarRoom prediction auto-update behavior. It adds a minimal smoke helper that proves the display packet heartbeat changes without UI automation and gives the exact manual UI smoke path for the real WarRoom tab.

```text
ps_q21b_warroom_prediction_auto_refresh_visual_smoke=true
non_ui_packet_heartbeat_changed=true
manual_ui_smoke_required=true
manual_ui_smoke_command=.\tools\run_operator_ui_sr_fx_dhot.ps1 -Port 501
refresh_target=latest_prediction_warroom_read_model_display_panel
refresh_interval_sec=5
broad_page_reload_disabled=true
```

## Manual UI smoke path

```text
1. Start UI: .\tools\run_operator_ui_sr_fx_dhot.ps1 -Port 501
2. Open the shown Streamlit URL.
3. Select the WarRoom tab.
4. Expand PS-Q19D realtime prediction display.
5. Confirm footer contains auto_refresh=True.
6. Confirm refresh_heartbeat_utc changes roughly every 5 seconds without broad page reload.
```

## What the helper checks

```text
packet_auto_refresh_version=prediction_warroom.warroom_prediction_display_auto_refresh.ps_q21a.v1
packet_refresh_target=latest_prediction_warroom_read_model_display_panel
packet_refresh_interval_sec=5
packet_heartbeat_changes_between_two_packet_builds=true
source_footer_auto_refresh_marker_present=true
source_footer_refresh_heartbeat_marker_present=true
warroom_page_prediction_fragment_flag_present=true
operator_ui_launcher_present=true
```

## Safety boundary

```text
runtime_enablement_allowed=false
loader_binding_runtime_allowed=false
component_runtime_binding_allowed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
ps_q19r_scoring_policy_changed=false
collector_runtime_behavior_changed=false
market_state_writer_changed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Non-goals

```text
no_ui_automation
no_browser_control
no_artifact_write
no_loader_rewire
no_prediction_producer_enablement
no_scheduler_enablement
no_ps_q19r_scoring_change
no_autotrade_or_broker_path
```

## Next likely action

After manual UI smoke confirms the heartbeat changes on the real WarRoom tab, move to the next concrete UI/UX improvement rather than another review chain.
