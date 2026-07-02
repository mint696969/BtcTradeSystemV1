# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29U_WARROOM_V2_CHART_READABILITY_2026-07-02.md
# desc: PS-Q29U WarRoom v2 chart readability view polish.

# PS-Q29U WarRoom v2 chart readability

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29T_WARROOM_V2_AUTO_REFRESH_STAGING_DONE
Slice: PS-Q29U_WARROOM_V2_CHART_READABILITY

## Decision

Q29U improves Chart Review readability while staying read-only and display-only.

```text
chart_readability_mode=price_and_bps
price_view=mid_price,best_bid,best_ask
mid_change_bps_view=true
spread_bps_view=true
range_summary_metrics=true
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
