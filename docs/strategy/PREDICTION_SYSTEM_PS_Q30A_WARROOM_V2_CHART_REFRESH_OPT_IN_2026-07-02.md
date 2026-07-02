# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q30A_WARROOM_V2_CHART_REFRESH_OPT_IN_2026-07-02.md
# desc: PS-Q30A WarRoom v2 chart refresh opt-in.

# PS-Q30A WarRoom v2 chart refresh opt-in

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29Z_WARROOM_V2_METRICS_ONLY_FRAGMENT_REFRESH_DONE
Slice: PS-Q30A_WARROOM_V2_CHART_REFRESH_OPT_IN

## Decision

Q30A keeps metrics-only auto-refresh as the default and adds an operator opt-in for Chart Review fragment refresh.

```text
metrics_only_auto_refresh_default=true
chart_refresh_opt_in_available=true
chart_refresh_opt_in_enabled_default=false
active_fragment_targets_default=market_snapshot_strip
active_fragment_targets_when_opted_in=market_snapshot_strip,chart_review_panel
streamlit_fragment_refresh=true
page_reload_enabled=false
browser_timer_reload_enabled=false
read_only=true
display_only=true
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
would_send_to_broker=false
```

## Boundary

The opt-in only changes Streamlit fragment targets. It does not enable true WebSocket/SSE push or any execution behavior.

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_invoking_classifier=true
not_touching_autotrade_broker_ledger_mode_parameter=true
would_send_to_broker=false
```
