# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29R_WARROOM_V2_DHOT_MARKET_SNAPSHOT_BINDING_2026-07-02.md
# desc: PS-Q29R WarRoom v2 D-hot read-only market snapshot binding.

# PS-Q29R WarRoom v2 D-hot read-only market snapshot binding

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29Q_WARROOM_V2_CHART_REVIEW_MARKET_SNAPSHOT_CONTRACT_DONE
Slice: PS-Q29R_WARROOM_V2_DHOT_MARKET_SNAPSHOT_BINDING

## Decision

Q29R binds the WarRoom v2 Market Snapshot Strip and Chart Review packet to the current D-hot market overview through the existing Operator UI market_state read service.

```text
dhot_market_snapshot_read_only_binding=true
market_snapshot_values_bound=true
chart_packet_market_snapshot_bound=true
source_kind=dhot_market_state_read_only
read_only=true
display_only=true
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
would_send_to_broker=false
```

## Bound fields

```text
market
ltp_or_mid_price
best_bid
best_ask
spread
spread_bps
data_age_sec
data_state
invalidation_watch=PREVIEW_ONLY_when_connected
board_imbalance_reserved
near_liquidity_reserved
```

## Still staged for later slices

```text
actual_chart_series_binding=false
change_1m_5m_15m_1h_binding=false
push_auto_refresh_transport=false
annotation_layers_runtime_binding=false
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
