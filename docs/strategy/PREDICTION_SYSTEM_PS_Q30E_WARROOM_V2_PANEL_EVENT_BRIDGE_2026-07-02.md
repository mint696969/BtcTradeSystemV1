# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q30E_WARROOM_V2_PANEL_EVENT_BRIDGE_2026-07-02.md
# desc: PS-Q30E WarRoom v2 panel packet to read-model event bridge adapter.

# PS-Q30E WarRoom v2 panel event bridge adapter

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q30D_WARROOM_V2_READ_MODEL_EVENT_BRIDGE_DONE
Slice: PS-Q30E_WARROOM_V2_PANEL_EVENT_BRIDGE

## Decision

Q30E connects existing read-only panel packets to the Q30D read-model event bridge contract.

```text
panel_packet_event_bridge=true
input_kind=existing_panel_packets
output_kind=read_model_event_bridge_packet
market_snapshot_packet_source=build_warroom_v2_market_snapshot_strip_packet
chart_review_packet_source=build_warroom_v2_chart_review_panel_packet
market_snapshot_topic=warroom.market.snapshot
chart_review_topic=warroom.chart.review
patch_unit=widget_dom_region
broad_page_reload_required=false
transport_implemented_now=false
bridge_starts_transport=false
bridge_reads_dhot=false
bridge_invokes_classifier=false
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
read_only=true
display_only=true
would_send_to_broker=false
```

## Boundary

This adapter consumes already-built panel packets. It does not add UI labels, read D-hot directly, start sockets, write runtime artifacts, call classifiers, or execute trade behavior.

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
