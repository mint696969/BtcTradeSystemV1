# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18AP_WARROOM_LATEST_PREDICTION_UI_VISIBILITY_POLISH_2026-06-24.md
# desc: PS-Q18AP UI visibility polish for WarRoom latest prediction auto-refresh display.
# PS-Q18AP WarRoom latest prediction UI visibility polish

Updated: 2026-06-24 JST

## Purpose

PS-Q18AP fixes the UX gaps recorded in PS-Q18AO.

It adds browser-searchable plain text tokens and a visible refresh heartbeat to the existing Q18AJ/Q18AK WarRoom panels.

## Added visible/searchable tokens

```text
PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT
auto_refresh_enabled=true
refresh_mode=poll_normal
refresh_interval_sec=5
refresh_heartbeat_utc=<utc timestamp>
PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS
freshness_state=stale
safe_fallback_reason_codes=source_generated_at_stale
observed_now_utc=<utc timestamp>
source_age_sec=<seconds>
```

## Scope

This is display polish only. It keeps DataFrame rows but no longer relies on DataFrame-only text for operator searchability.

## Safety boundary retained

```text
real_prediction_widget_rendering_allowed=false
real_prediction_widget_render_invoked=false
streamlit_real_widget_render_invoked=false
component_runtime_binding_allowed=false
component_props_bound_to_runtime=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
```

## Next

After this patch, repeat manual UI smoke. Expected result: browser find can locate `freshness_state`, `safe_fallback_reason_codes`, and `refresh_heartbeat_utc`; operator can see the heartbeat changing without broad page reload.
