# path: ./docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP12_BOTTOM_CHART_LAYOUT_2026-07-05.md
# desc: WP12 WarRoom manual trade support bottom chart layout.

# WP12 WarRoom bottom chart layout

Date: 2026-07-05
Profile: BtcTradeSystem
Roadmap: PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_ROADMAP_WP1_WP13_2026-07-05.md
Base gate: PS_WP11_WARROOM_MANUAL_TRADE_SUPPORT_TOP_LAYOUT_PUSH_WIDGET_POLISH_DONE
Slice: PS-WP12_WARROOM_MANUAL_TRADE_SUPPORT_BOTTOM_CHART_LAYOUT

## Goal

WP12 adds a bottom chart layout adapter fed by push-widget render packets, with overlays, refresh cadence, stale handling, and visual cleanup while preserving the read-only no-action boundary.

```text
wp12_completed=true
next_checkpoint=WP13_Prediction_card_connection_and_updates
bottom_chart_layout_ready=true
bottom_chart_data_adapter_ready=true
bottom_chart_overlay_ready=true
bottom_chart_refresh_cadence_ready=true
bottom_chart_stale_handling_ready=true
bottom_chart_visual_cleanup_ready=true
bottom_chart_read_only_ready=true
chart_row_count=7
overlay_count=4
stale_row_count=0
refresh_cadence_ms=1000
rate_limit_respected=true
manual_trade_support_read_only=true
warroom_page_modified=true
warroom_page_mount_added=true
websocket_opened=false
websocket_receive_loop_started=false
websocket_send_enabled=false
websocket_subscribe_invoked=false
external_network_used=false
raw_payload_rendered=false
endpoint_value_rendered=false
token_value_rendered=false
callable_value_rendered=false
secret_exposure=false
broker_send_enabled=false
would_send_to_broker=false
order_intent_submitted=false
ledger_append_allowed=false
auto_trading_enabled=false
prediction_invoked=false
classifier_invoked=false
```
