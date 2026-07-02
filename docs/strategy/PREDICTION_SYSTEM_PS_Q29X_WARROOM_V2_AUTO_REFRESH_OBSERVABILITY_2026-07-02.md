# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29X_WARROOM_V2_AUTO_REFRESH_OBSERVABILITY_2026-07-02.md
# desc: PS-Q29X WarRoom v2 auto refresh observability.

# PS-Q29X WarRoom v2 auto refresh observability

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29W_WARROOM_V2_SIDEBAR_AUTO_REFRESH_DONE
Slice: PS-Q29X_WARROOM_V2_AUTO_REFRESH_OBSERVABILITY

## Decision

Q29X makes WarRoom v2 browser-timer auto refresh observable in the main page without opening the expander.

```text
auto_refresh_observable_status_strip=true
last_rendered_at_visible=true
auto_refresh_source_visible=true
interval_visible=true
transport_visible=true
browser_timer_auto_refresh=true
read_only=true
display_only=true
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
would_send_to_broker=false
```

## Boundary

This is observability only. It does not enable WebSocket, SSE, server push, scheduler, producer, broker, or AutoTrade.

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_invoking_classifier=true
not_touching_autotrade_broker_ledger_mode_parameter=true
would_send_to_broker=false
```
