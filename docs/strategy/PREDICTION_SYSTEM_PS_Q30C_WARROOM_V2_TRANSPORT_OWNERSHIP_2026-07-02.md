# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q30C_WARROOM_V2_TRANSPORT_OWNERSHIP_2026-07-02.md
# desc: PS-Q30C WarRoom v2 natural-update transport ownership contract.

# PS-Q30C WarRoom v2 transport ownership contract

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q30A_WARROOM_V2_CHART_REFRESH_OPT_IN_DONE
Slice: PS-Q30C_WARROOM_V2_TRANSPORT_OWNERSHIP

## Decision

Q30C defines the ownership contract required for the final natural widget update path without adding UI decoration or enabling live transport yet.

```text
transport_owner=external_read_model_event_bridge
ui_role=read_model_event_consumer_only
event_unit=widget_topic
patch_unit=widget_dom_region
natural_widget_update_goal=true
market_snapshot_topic=warroom.market.snapshot
chart_review_topic=warroom.chart.review
broad_page_reload_required=false
page_reload_enabled=false
browser_timer_reload_enabled=false
transport_implemented_now=false
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
read_only=true
display_only=true
would_send_to_broker=false
```

## Boundary

This slice prepares the contract for true WebSocket/SSE or another event bridge, but it does not start sockets, services, scheduler/producers, classifier calls, or execution behavior.

## Non-goals

```text
not_adding_ui_status_labels=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_invoking_classifier=true
not_touching_autotrade_broker_ledger_mode_parameter=true
would_send_to_broker=false
```
