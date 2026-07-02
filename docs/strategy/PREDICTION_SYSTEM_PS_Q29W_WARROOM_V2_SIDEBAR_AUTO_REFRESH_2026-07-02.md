# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29W_WARROOM_V2_SIDEBAR_AUTO_REFRESH_2026-07-02.md
# desc: PS-Q29W WarRoom v2 sidebar-driven browser-timer auto refresh.

# PS-Q29W WarRoom v2 sidebar auto refresh bridge

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29V_WARROOM_V2_TIMEFRAME_WINDOW_DONE
Slice: PS-Q29W_WARROOM_V2_SIDEBAR_AUTO_REFRESH

## Decision

Q29W makes WarRoom v2 auto refresh consume the existing Operator UI sidebar controls.

```text
sidebar_auto_refresh_consumed=true
auto_refresh_source=operator_sidebar
browser_timer_auto_refresh=true
ui_auto_refresh=true_enables_timer
ui_refresh_interval_seconds_converted_to_ms=true
read_only=true
display_only=true
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
would_send_to_broker=false
```

## Boundary

This remains browser timer polling. It is not WebSocket, SSE, or server push transport.

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_invoking_classifier=true
not_touching_autotrade_broker_ledger_mode_parameter=true
would_send_to_broker=false
```
