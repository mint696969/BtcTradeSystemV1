# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29S_WARROOM_V2_DHOT_CHART_SERIES_BINDING_2026-07-02.md
# desc: PS-Q29S WarRoom v2 D-hot read-only chart series binding.

# PS-Q29S WarRoom v2 D-hot read-only chart series binding

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29R_WARROOM_V2_DHOT_MARKET_SNAPSHOT_BINDING_DONE
Slice: PS-Q29S_WARROOM_V2_DHOT_CHART_SERIES_BINDING

## Decision

Q29S binds the bottom WarRoom v2 Chart Review panel to a bounded, read-only recent D-hot market overview series.

```text
dhot_chart_series_read_only_binding=true
actual_chart_series_bound=true
chart_packet_range_summary_bound=true
source_kind=dhot_market_state_chart_series_read_only
read_only=true
display_only=true
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
would_send_to_broker=false
```

## Chart series fields

```text
ts
mid_price
best_bid
best_ask
spread
spread_bps
trust_state
continuity_state
interpretation_bucket
```

## Still staged for later slices

```text
clicked_at_selection_binding=false
range_start_range_end_selection_binding=false
prediction_marker_annotation_binding=false
push_auto_refresh_transport=false
```

## Non-goals

```text
not_invoking_classifier=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_touching_autotrade_broker_ledger_mode_parameter=true
would_send_to_broker=false
```
