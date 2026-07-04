# path: ./docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_WP5_TOPIC_ROUTING_SUBSCRIPTION_PLAN_2026-07-05.md
# desc: WP5 WarRoom manual trade support topic routing and subscription plan. Metadata-only intent before independent update pipeline.

# WP5 WarRoom topic routing and subscription plan

Date: 2026-07-05
Profile: BtcTradeSystem
Roadmap: PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_ROADMAP_WP1_WP13_2026-07-05.md
Base gate: PS_WP4_WARROOM_MANUAL_TRADE_SUPPORT_RECEIVE_ONLY_WEBSOCKET_PUSH_ROUTER_DONE
Slice: PS-WP5_WARROOM_MANUAL_TRADE_SUPPORT_TOPIC_ROUTING_AND_SUBSCRIPTION_PLAN

## Goal

WP5 fixes the topic namespace, topic-to-widget ownership, and receive-only subscription intent plan that WP6 can use for the independent widget update pipeline.

```text
wp5_completed=true
next_checkpoint=WP6_Independent_widget_update_pipeline
topic_namespace_ready=true
topic_route_plan_ready=true
subscription_plan_ready=true
receive_only_subscription_intent_ready=true
future_topic_addition_ready=true
route_count=7
channel_groups=market,receiver,warroom
architecture_only=true
manual_trade_support_read_only=true
warroom_page_modified=false
warroom_page_mount_added=false
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
