# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29V_WARROOM_V2_TIMEFRAME_WINDOW_2026-07-02.md
# desc: PS-Q29V WarRoom v2 timeframe-aware chart window binding.

# PS-Q29V WarRoom v2 timeframe-aware chart window

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29U_WARROOM_V2_CHART_READABILITY_DONE
Slice: PS-Q29V_WARROOM_V2_TIMEFRAME_WINDOW

## Decision

Q29V makes the Chart Review timeframe selector affect the bounded recent-row chart window.

```text
timeframe_window_binding=true
window_policy=bounded_recent_rows
1m_row_limit=60
5m_row_limit=240
15m_row_limit=720
1h_row_limit=1440
1d_row_limit=2880
chart_window_in_packet=true
read_only=true
display_only=true
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
would_send_to_broker=false
```

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_invoking_classifier=true
not_touching_autotrade_broker_ledger_mode_parameter=true
would_send_to_broker=false
```
