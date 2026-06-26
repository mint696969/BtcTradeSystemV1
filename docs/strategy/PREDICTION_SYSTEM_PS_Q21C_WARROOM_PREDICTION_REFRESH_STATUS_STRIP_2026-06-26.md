# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21C_WARROOM_PREDICTION_REFRESH_STATUS_STRIP_2026-06-26.md
# desc: PS-Q21C promotes WarRoom prediction auto-refresh heartbeat from footer/search token into a visible status strip.
# PS-Q21C WarRoom prediction refresh status strip

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: 937c52fb

## Purpose

PS-Q21C makes the confirmed WarRoom prediction auto-refresh easier to see during normal operation. PS-Q21A/PS-Q21B proved the footer heartbeat works; PS-Q21C promotes the same display-only facts into a compact top-of-panel status strip.

```text
ps_q21c_warroom_prediction_refresh_status_strip=true
operator_visible_refresh_status_strip=true
refresh_status_strip_version=prediction_warroom.warroom_prediction_refresh_status_strip.ps_q21c.v1
refresh_target=latest_prediction_warroom_read_model_display_panel
refresh_interval_sec=5
heartbeat_visible_without_page_search=true
broad_page_reload_disabled=true
```

## UI behavior

```text
status_strip_position=top_of_ps_q19d_prediction_panel
status_strip_items=auto_refresh,heartbeat_utc,interval,target,broad_reload
status_strip_rendered_before_prediction_table=true
footer_token_preserved=true
manual_page_search_no_longer_required_for_heartbeat=true
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
no_loader_rewire
no_prediction_producer_enablement
no_scheduler_enablement
no_artifact_write
no_ps_q19r_scoring_change
no_autotrade_or_broker_path
no_order_or_parameter_behavior
```

## Next likely action

Run a short manual UI smoke to confirm the strip appears near the top of PS-Q19D and the heartbeat metric changes without page whiteout.
