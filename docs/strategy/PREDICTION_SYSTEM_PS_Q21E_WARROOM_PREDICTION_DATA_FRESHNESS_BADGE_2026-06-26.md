# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21E_WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_2026-06-26.md
# desc: PS-Q21E adds a visible data freshness badge to separate panel refresh liveness from prediction data freshness.
# PS-Q21E WarRoom prediction data freshness badge

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: fdc0b498

## Purpose

PS-Q21D shows that the prediction panel is refreshing. PS-Q21E adds a separate prediction-data freshness badge so operators do not confuse a live-refreshing panel with fresh prediction data.

```text
ps_q21e_warroom_prediction_data_freshness_badge=true
operator_visible_data_freshness_badge=true
data_freshness_badge_version=prediction_warroom.warroom_prediction_data_freshness_badge.ps_q21e.v1
data_freshness_badge_position=below_ps_q21c_refresh_status_strip
panel_liveness_and_data_freshness_separated=true
freshness_state_visible=true
prediction_age_visible=true
prediction_row_count_visible=true
prediction_generated_at_visible=true
```

## UI behavior

```text
data_freshness_badge_success_when_fresh=true
data_freshness_badge_warning_when_delayed_or_stale=true
live_badge_preserved=true
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

Manual UI smoke: confirm the data freshness badge appears below the refresh status area and clearly distinguishes panel liveness from prediction data freshness.
