# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18AM_WARROOM_LATEST_PREDICTION_AUTO_REFRESH_UI_SMOKE_CHECK_2026-06-24.md
# desc: PS-Q18AM UI smoke/manual visual check packet for WarRoom latest prediction auto-refresh.
# PS-Q18AM WarRoom latest prediction auto-refresh UI smoke/manual visual check

Updated: 2026-06-24 JST

## Purpose

PS-Q18AM adds a smoke/manual visual check packet for the closed intermediate goal.

It does not change runtime behavior. It documents and guards what the operator should confirm in the WarRoom tab after PS-Q18AJ/PS-Q18AK:

```text
WarRoom tab automatically refreshes prediction display=true
bounded fragment refresh path=true
broad page reload=false
freshness/error fallback visible=true
execution/trading behavior=false
```

## Manual smoke checklist

1. Launch Operator UI normally.
2. Open the WarRoom tab.
3. Confirm the latest prediction auto-refresh panel is visible.
4. Confirm the freshness/fallback panel is visible.
5. Confirm the auto-refresh caption reports `auto_refresh=true`, `mode=poll_normal`, and `interval=5s`.
6. Confirm the freshness panel reports a `freshness_state` and safe fallback reason codes when the source is stale or missing.
7. Confirm there is no broad page reload flicker/whiteout.
8. Confirm there is no AutoTrade, broker, parameter, ledger, or runtime-write action shown or invoked by these panels.

## Structural close facts

```text
PS-Q18AJ auto_refresh_enabled=true
PS-Q18AJ fragment_slot_refresh_path_enabled=true
PS-Q18AJ partial_update_enabled=true
PS-Q18AJ broad_page_reload_disabled=true
PS-Q18AK freshness_monitor_enabled=true
PS-Q18AK error_fallback_visible=true
PS-Q18AK operator_safe_fallback_reason_codes_visible=true
PS-Q18AL intermediate_goal_reached=true
```

## Safety boundary

```text
real_prediction_widget_render_invoked=false
streamlit_real_widget_render_invoked=false
component_runtime_binding_allowed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
```

## Next

After a successful manual smoke check, the next separate gate can be either real-widget rendering review or a narrower UX polish slice. Keep AutoTrade, broker, parameter, ledger, and runtime writes disabled unless explicitly staged and approved.
