# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29T_WARROOM_V2_AUTO_REFRESH_STAGING_2026-07-02.md
# desc: PS-Q29T WarRoom v2 browser-timer auto refresh staging.

# PS-Q29T WarRoom v2 browser-timer auto refresh staging

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29S_WARROOM_V2_DHOT_CHART_SERIES_BINDING_DONE
Slice: PS-Q29T_WARROOM_V2_AUTO_REFRESH_STAGING

## Decision

Q29T adds an operator-controlled browser-timer auto refresh control below the WarRoom v2 top bar.

```text
browser_timer_auto_refresh=true
transport_kind=browser_timer_polling
auto_refresh_available=true
auto_refresh_enabled_default=false
refresh_targets=market_snapshot_strip,prediction_cards,chart_review_panel
min_interval_ms=1000
default_interval_ms=2000
max_interval_ms=60000
read_only=true
display_only=true
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
would_send_to_broker=false
```

## Boundary

This is not a WebSocket/SSE push transport. It is a Streamlit/browser timer refresh helper that reloads the page when explicitly enabled by the operator.

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_invoking_classifier=true
not_touching_autotrade_broker_ledger_mode_parameter=true
would_send_to_broker=false
```
