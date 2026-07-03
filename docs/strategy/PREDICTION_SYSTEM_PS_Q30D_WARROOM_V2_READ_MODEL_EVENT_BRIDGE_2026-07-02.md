# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q30D_WARROOM_V2_READ_MODEL_EVENT_BRIDGE_2026-07-02.md
# desc: PS-Q30D WarRoom v2 read-model event bridge prototype.

# PS-Q30D WarRoom v2 read-model event bridge prototype

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q30C_WARROOM_V2_TRANSPORT_OWNERSHIP_DONE
Slice: PS-Q30D_WARROOM_V2_READ_MODEL_EVENT_BRIDGE

## Decision

Q30D adds a local read-model event bridge prototype for future natural widget updates.

```text
read_model_event_bridge_prototype=true
input_kind=prebuilt_read_model_payload
output_kind=widget_update_event_envelope
fingerprint_algorithm=sha256_json_sort_keys_24
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

The bridge accepts already-built read-model payloads, computes stable fingerprints, creates `WidgetUpdateEvent`, and wraps it in the transport envelope contract. It does not read D-hot directly, start sockets, write runtime artifacts, call classifiers, or execute trade behavior.

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
