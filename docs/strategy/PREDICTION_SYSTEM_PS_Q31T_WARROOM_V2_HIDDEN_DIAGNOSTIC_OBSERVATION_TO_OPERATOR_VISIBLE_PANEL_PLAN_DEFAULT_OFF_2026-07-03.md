# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31T_WARROOM_V2_HIDDEN_DIAGNOSTIC_OBSERVATION_TO_OPERATOR_VISIBLE_PANEL_PLAN_DEFAULT_OFF_2026-07-03.md
# desc: PS-Q31T WarRoom v2 default-off operator-visible panel plan with WebSocket-first premise. Contract only; no UI mount and no socket.

# PS-Q31T WarRoom v2 hidden diagnostic observation to operator-visible panel plan

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31S_WARROOM_V2_BIDIRECTIONAL_WEBSOCKET_AND_ORDER_INTENT_BOUNDARY_DESIGN_DONE
Slice: PS-Q31T_WARROOM_V2_HIDDEN_DIAGNOSTIC_OBSERVATION_TO_OPERATOR_VISIBLE_PANEL_PLAN_DEFAULT_OFF

## Decision

PS-Q31T creates a pure operator-visible panel plan from the Q31R hidden diagnostic observation while preserving the Q31S WebSocket-first future transport premise. This is a plan-only slice: it does not mount the panel into WarRoom, render Streamlit UI, open sockets, fall back to polling/browser-reload workarounds, submit OrderIntent, append ledgers, apply mode/parameters, or send broker orders.

```text
plan_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_visible_panel_plan.py
input_observation=warroom_v2_operator_diagnostic_observation_packet
input_boundary=warroom_v2_bidirectional_websocket_order_intent_boundary
output_plan=warroom_v2_operator_visible_panel_plan_packet
websocket_first_future_transport=true
bidirectional_websocket_premise=true
read_model_push_plane=server_to_warroom_ui
command_intent_plane=warroom_ui_or_autotrade_to_order_intent_gateway
no_polling_fallback_introduced=true
no_browser_timer_reload_introduced=true
operator_visible_panel_default_enabled=false
operator_visible_panel_requested_default=false
operator_read_only_ack_default=false
operator_visible_panel_allowed_default=false
plan_packet_only=true
plan_mounts_into_warroom=false
plan_renders_ui=false
plan_visible_now=false
panel_read_only=true
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
order_intent_submitted=false
broker_send_enabled=false
would_send_to_broker=false
websocket_enabled=false
socket_opened=false
external_message_send_enabled=false
```

## Plan responsibility

`operator_visible_panel_plan.py` owns only read-only plan normalization. It reads Q31R diagnostic observation status and Q31S boundary constraints, then emits a bounded plan. The allowed plan still does not render; it only says that a future explicitly gated panel could be mounted on the WebSocket-first display plane.

```text
requested=false -> operator_visible_panel_plan_hidden_default
requested=true,ack=false -> operator_visible_panel_plan_blocked_read_only_ack_required
requested=true,ack=true,diagnostic_ready=false -> operator_visible_panel_plan_blocked_diagnostic_not_ready
requested=true,ack=true,diagnostic_ready=true -> operator_visible_panel_plan_ready_default_off_no_mount
```

## Non-goals

```text
not_mounting_panel_into_warroom=true
not_rendering_streamlit=true
not_rendering_visible_diagnostic=true
not_adding_visible_ui_decoration=true
not_using_polling_fallback=true
not_using_browser_timer_reload=true
not_enabling_websocket=true
not_opening_socket=true
not_sending_external_messages=true
not_submitting_order_intent=true
not_sending_order_to_broker=true
not_appending_live_order_ledger=true
not_applying_mode=true
not_applying_parameter=true
not_invoking_prediction_generation=true
not_invoking_prediction_inference=true
not_invoking_classifier=true
```

## Acceptance criteria

```text
- operator_visible_panel_plan.py exists and stays pure.
- plan preserves WebSocket-first future transport premise.
- plan explicitly avoids polling/browser reload alternatives.
- default request=false maps to operator_visible_panel_plan_hidden_default.
- request=true without read-only acknowledgement is blocked.
- request=true with acknowledgement but non-ready diagnostic is blocked.
- request=true with acknowledgement and ready diagnostic creates ready plan, but still does not mount or render UI.
- OrderIntent submission and broker send remain false.
- existing Q31S-Q30C guards remain green.
```
