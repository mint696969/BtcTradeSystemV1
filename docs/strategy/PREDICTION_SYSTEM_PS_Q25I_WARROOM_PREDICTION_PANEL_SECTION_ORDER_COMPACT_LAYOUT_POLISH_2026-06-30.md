# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q25I_WARROOM_PREDICTION_PANEL_SECTION_ORDER_COMPACT_LAYOUT_POLISH_2026-06-30.md
# desc: PS-Q25I WarRoom prediction panel section order and compact layout polish. Display-only layout-only change.
# PS-Q25I WarRoom prediction panel section order and compact layout polish

Updated: 2026-06-30 JST
Base: PS-Q25H WarRoom prediction data age severity and operator action guidance
Mode: WarRoom prediction panel layout polish / display-only / no writes / no AutoTrade / no broker

```text
ps_q25i_warroom_prediction_panel_section_order_compact_layout_polish=true
base_reentry=PS_Q25H_WARROOM_PREDICTION_DATA_AGE_SEVERITY_OPERATOR_ACTION_GUIDANCE_DONE
prediction_compact_layout_added=true
operator_visible_compact_layout=true
compact_layout_rendered=true
compact_layout_top_priority=operator_action_guidance_first
compact_layout_rows_visible=true
compact_layout_detail_tables_still_visible=true
layout_only_change=true
producer_cadence_changed=false
scheduler_action_changed=false
scheduler_enabled=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
```

## Purpose

Q25I adds a compact top summary to the WarRoom prediction panel so the operator sees the most important stale/expired prediction guidance before detailed tables: operator action, prediction data age, horizon expiry, generated_at, and UI heartbeat.

## Safety

This is layout-only and display-only. It does not change prediction producer cadence, scheduler, artifacts, AutoTrade, broker, ledger, mode, or parameters.
