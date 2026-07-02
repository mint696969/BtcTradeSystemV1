# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29Z_WARROOM_V2_METRICS_ONLY_FRAGMENT_REFRESH_2026-07-02.md
# desc: PS-Q29Z WarRoom v2 metrics-only default fragment refresh.

# PS-Q29Z WarRoom v2 metrics-only fragment refresh default

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29Y_WARROOM_V2_FRAGMENT_REFRESH_DONE
Slice: PS-Q29Z_WARROOM_V2_METRICS_ONLY_FRAGMENT_REFRESH

## Decision

Q29Z reduces refresh visual noise by making the default fragment auto-refresh target metrics-only.

```text
metrics_only_auto_refresh_default=true
available_fragment_targets=market_snapshot_strip,chart_review_panel
active_fragment_targets=market_snapshot_strip
chart_review_auto_refresh_enabled=false
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

Chart Review remains available and can be opted into later, but it is not auto-refreshed by default to avoid chart redraw noise.

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_invoking_classifier=true
not_touching_autotrade_broker_ledger_mode_parameter=true
would_send_to_broker=false
```
