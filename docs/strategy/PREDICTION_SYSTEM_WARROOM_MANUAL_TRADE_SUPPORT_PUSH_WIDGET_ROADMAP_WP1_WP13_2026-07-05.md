# path: ./docs/strategy/PREDICTION_SYSTEM_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_ROADMAP_WP1_WP13_2026-07-05.md
# desc: Fixed WarRoom manual trading support push-widget roadmap WP1-WP13. Locks checkpoint order, goals, completion criteria, and carry-forward rules across threads.

# WarRoom manual trading support push-widget roadmap WP1-WP13

Date: 2026-07-05
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync
Supersedes working focus after: CP2-CP13 receiver-only client roadmap close
Roadmap lock: PS_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_ROADMAP_WP1_WP13_LOCKED

## User priority lock

```text
primary_goal=WarRoom_manual_trade_support_completion
first_priority=independent_WebSocket_push_auto_updating_widgets
must_keep_extensible_for_future_widgets=true
thread_crossing_explanation_drift_allowed=false
roadmap_order_locked=true
```

WarRoom is to become a manual trading support cockpit. The first and highest-priority completion experience is:

```text
Each WarRoom widget independently receives WebSocket push market updates and refreshes seamlessly.
Each widget owns its own topic binding, state, freshness, stale/error status, and render packet.
One slow/stale/error widget must not stop other widgets.
Future widgets must be addable through a stable registry/manifest/contract without redesigning the page.
Broker/order/send/auto-trading remain separated until explicitly introduced by a later safe roadmap.
```

## Completion experience

```text
Open WarRoom
→ widgets appear as manual trading support surfaces
→ each widget has its own topic/stream binding
→ WebSocket push updates arrive and route to the right widget state
→ widgets refresh independently without manual reload
→ stale/error/heartbeat status is visible per widget
→ new widgets can be added by manifest/registry entry plus reducer/render packet
→ top information groups and bottom chart can be refined after widget push experience is stable
→ prediction cards connect last, after market push widgets and layout are reliable
```

## Fixed checkpoint roadmap

| Checkpoint | Goal | Completion target | Boundary |
|---|---|---|---|
| WP1 | WarRoom push widget architecture | Registry, manifest, topic binding, state snapshot, reducer, render packet, health status, push-router contracts fixed. | Architecture only; no real socket mount; no broker/order/send. |
| WP2 | Widget registry and manifest | Stable widget registry where each widget declares id, topic binding, reducer, render adapter, health requirements, and extension metadata. | No WarRoom page mount yet unless guarded; no operator controls. |
| WP3 | Per-widget state store | Independent bounded state store per widget with snapshot, update clock, stale/error fields, and isolation guarantees. | One widget failure cannot mutate or stop another widget. |
| WP4 | Receive-only WebSocket push router | Receive-only push router maps incoming topic messages to widget reducers. | Receive-only; no send/subscribe mutation/order/broker. |
| WP5 | Topic routing and subscription plan | Topic namespace and routing table for market streams, widget ownership, and future topic additions. | Subscription intent remains metadata until live gate is explicit. |
| WP6 | Independent widget update pipeline | Push message → topic router → reducer → state snapshot → render packet works independently per widget. | No global page rerender dependency that blocks all widgets. |
| WP7 | Per-widget freshness, stale, heartbeat, and error handling | Each widget exposes live/stale/error/slow state and last update metadata. | Runtime actions remain bounded; no reconnect/send side effects from widget layer. |
| WP8 | First real push widget set | Initial market widgets receive pushed data through the shared pipeline: book/depth, trades, spread/liquidity, lifecycle/health, summary/alerts metadata. | Read-only manual trading support; no order actions. |
| WP9 | WarRoom page mount for push widgets | WarRoom tab mounts the push widget grid through registry-driven render packets. | Mount only after no-send/no-broker/page guards pass. |
| WP10 | Widget extension contract | New widget addition process is documented and guarded: manifest + topic binding + reducer + render packet + tests. | No ad-hoc page wiring for new widgets. |
| WP11 | WarRoom top information layout | Top information groups are organized around market status, freshness, connection health, manual decision context, and risk cues. | After push widget experience is stable. |
| WP12 | WarRoom bottom chart layout | Bottom chart receives clean data adapters, refresh cadence, overlays, stale handling, and visual cleanup. | Chart rendering must respect rate limits and not block widgets. |
| WP13 | Prediction card connection and updates | Prediction cards connect and update after market push widgets/layout/chart are reliable. | Prediction remains separate from broker/order/send unless explicitly approved. |

## Non-negotiable order

```text
WP1_before_WP2=true
WP2_before_WP3=true
WP3_before_WP4=true
WP4_before_WP5=true
WP5_before_WP6=true
WP6_before_WP7=true
WP7_before_WP8=true
WP8_before_WP9=true
WP9_before_WP10=true
WP10_before_WP11=true
WP11_before_WP12=true
WP12_before_WP13=true
prediction_cards_last=true
top_layout_after_push_widget_experience=true
bottom_chart_after_top_layout_or_after_core_push_stability=true
```

## Architectural invariants

```text
widget_registry_required=true
widget_manifest_required=true
topic_binding_required=true
per_widget_state_required=true
per_widget_reducer_required=true
per_widget_render_packet_required=true
per_widget_health_status_required=true
push_router_required=true
state_isolation_required=true
bounded_buffers_required=true
freshness_status_required=true
stale_status_required=true
error_status_required=true
future_widget_extension_required=true
manual_trade_support_read_only_until_explicit_order_roadmap=true
```

## Safety invariants

```text
websocket_receive_only_until_explicit_send_roadmap=true
websocket_send_enabled=false
broker_send_enabled=false
order_intent_submitted=false
auto_trading_enabled=false
prediction_execution_before_wp13=false
widget_layer_must_not_submit_orders=true
widget_layer_must_not_append_ledger=true
widget_layer_must_not_call_broker=true
secrets_must_not_be_rendered=true
raw_payload_rendering_forbidden=true
endpoint_token_callable_rendering_forbidden=true
```

## Completion criteria for the roadmap

```text
wp1_completed=true
wp2_completed=true
wp3_completed=true
wp4_completed=true
wp5_completed=true
wp6_completed=true
wp7_completed=true
wp8_completed=true
wp9_completed=true
wp10_completed=true
wp11_completed=true
wp12_completed=true
wp13_completed=true
warroom_manual_trade_support_push_widgets_complete=true
warroom_widgets_independently_auto_update_from_websocket_push=true
future_widget_extension_contract_complete=true
warroom_top_information_layout_refined=true
warroom_bottom_chart_layout_refined=true
prediction_cards_connected_and_updating=true
```

## Carry-forward rule

Do not rename, reorder, skip, or reinterpret WP1-WP13 without an explicit decision note that names this roadmap lock and explains why the change is necessary.

When a new thread begins, load this document before planning WarRoom work. The correct next task is the first incomplete WP checkpoint in this table.

## Current next checkpoint

```text
current_gate=PS_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_ROADMAP_WP1_WP13_LOCKED
next_checkpoint=WP1_WarRoom_push_widget_architecture
next_task=PS-WP1_WARROOM_MANUAL_TRADE_SUPPORT_PUSH_WIDGET_ARCHITECTURE
required_previous_gate=PS_CP13_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_HIGH_VISIBILITY_REALTIME_DELIVERY_DANGER_ZONE_DONE
```
