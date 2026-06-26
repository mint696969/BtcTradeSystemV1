# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21D_WARROOM_PREDICTION_REFRESH_LIVE_BADGE_2026-06-26.md
# desc: PS-Q21D adds a visible live badge above the WarRoom prediction refresh status strip.
# PS-Q21D WarRoom prediction refresh live badge

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: 9fdaf6e4

## Purpose

PS-Q21C made the heartbeat searchable without scrolling to the footer. PS-Q21D makes the operator state even more obvious: a single visible live badge appears above the metric strip and says the prediction panel is refreshing, with heartbeat UTC, 5s interval, and broad reload disabled.

```text
ps_q21d_warroom_prediction_refresh_live_badge=true
operator_visible_refresh_live_badge=true
refresh_live_badge_version=prediction_warroom.warroom_prediction_refresh_live_badge.ps_q21d.v1
refresh_live_badge_state=prediction_refresh_live
refresh_live_badge_message_visible=true
refresh_live_badge_position=above_ps_q21c_status_strip
refresh_target=latest_prediction_warroom_read_model_display_panel
refresh_interval_sec=5
broad_page_reload_disabled=true
```

## UI behavior

```text
live_badge_success_when_auto_refresh_enabled=true
live_badge_mentions_heartbeat_utc=true
live_badge_mentions_interval_5s=true
live_badge_mentions_broad_reload_disabled=true
status_strip_preserved=true
footer_token_preserved=true
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

Manual UI smoke: confirm the live badge appears above the PS-Q21C status strip and the heartbeat UTC changes without page whiteout.
