# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21A_WARROOM_PREDICTION_DISPLAY_AUTO_REFRESH_2026-06-26.md
# desc: PS-Q21A enables explicit auto-refresh visibility for the WarRoom latest prediction display panel.
# PS-Q21A WarRoom prediction display auto refresh

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: c6ce7cdc

## Purpose

PS-Q21A moves from review-only work back to the requested WarRoom prediction display priority. It makes the actual latest prediction WarRoom display panel an explicit bounded fragment auto-refresh target and adds an operator-visible heartbeat in the prediction panel footer.

```text
ps_q21a_warroom_prediction_display_auto_refresh=true
warroom_prediction_display_auto_refresh_enabled=true
operator_visible_refresh_heartbeat=true
refresh_target=latest_prediction_warroom_read_model_display_panel
refresh_interval_sec=5
broad_page_reload_disabled=true
```

## UI behavior

```text
warroom_page_prediction_fragment_default=true
warroom_prediction_auto_refresh_enabled_session_key=warroom_prediction_auto_refresh_enabled
prediction_panel_uses_streamlit_fragment_run_every=true
prediction_panel_refresh_interval_sec=5
prediction_panel_footer_shows_refresh_heartbeat_utc=true
prediction_panel_footer_shows_auto_refresh=true
```

The WarRoom page now resolves a prediction-specific fragment flag. This keeps the prediction panel refreshing by default even if future page-level refresh tuning changes elsewhere. The change is display-only and does not enable broad page reload.

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

## Next likely slice

```text
PS-Q21B_WARROOM_PREDICTION_AUTO_REFRESH_VISUAL_SMOKE_OR_MANUAL_UI_CHECK
```

Next should be a minimal UI smoke/manual check for the actual WarRoom tab, not another long review chain.
