# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29Q_WARROOM_V2_CHART_REVIEW_MARKET_SNAPSHOT_CONTRACT_2026-07-02.md
# desc: PS-Q29Q WarRoom v2 chart review and market snapshot contract.

# PS-Q29Q WarRoom v2 chart review and market snapshot contract

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29P_WARROOM_V2_ROW_LEVEL_DETAIL_OVERLAY_DONE
Slice: PS-Q29Q_WARROOM_V2_CHART_REVIEW_AND_MARKET_SNAPSHOT_CONTRACT

## Decision

Q29Q adds the next WarRoom v2 visual/contract layer for manual-trade review and later chart review.

```text
market_snapshot_strip_above_prediction_cards=true
chart_review_panel_bottom=true
copy_for_gpt_ready=true
schema_version=warroom_chart_review.v1
timeframe_placeholders=1m,5m,15m,1h,1d
selection_placeholders=clicked_at,range_start,range_end
annotation_layers=predictions,orderbook,orders,manual
push_ready=true
auto_refresh_ready=true
data_connected=false
runtime_connected=false
push_connected=false
```

## Market snapshot baseline fields

```text
market
ltp
best_bid
best_ask
spread
data_age_sec
data_state
change_1m_pct
change_5m_pct
change_15m_pct
change_1h_pct
invalidation_watch
```

## Secondary fields reserved for Q29R and later

```text
range_5m_pct
range_15m_pct
short_term_volatility
recent_volume
trade_density
board_imbalance
top_bid_size
top_ask_size
depth_0_1_pct
fx_spot_basis
alert_flags
```

## Non-goals

```text
not_connecting_dhot=true
not_invoking_classifier=true
not_binding_actual_chart_data=true
not_calling_bitflyer_api=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_touching_autotrade_broker_ledger_mode_parameter=true
not_changing_legacy_warroom=true
```
