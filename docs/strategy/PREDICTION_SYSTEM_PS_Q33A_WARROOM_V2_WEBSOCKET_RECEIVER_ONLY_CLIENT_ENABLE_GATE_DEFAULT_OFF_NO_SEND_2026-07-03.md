# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q33A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_ENABLE_GATE_DEFAULT_OFF_NO_SEND_2026-07-03.md
# desc: PS-Q33A WarRoom v2 WebSocket receiver-only client enable gate. Default-off, no send, and no socket open.

# PS-Q33A WarRoom v2 WebSocket receiver-only client enable gate default-off no-send

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32Z_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_VISIBLE_MOUNT_POINT_OPERATOR_ACK_OBSERVATION_AND_MANUAL_SMOKE_GUIDE_DONE
Slice: PS-Q33A_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_ENABLE_GATE_DEFAULT_OFF_NO_SEND

## Decision

PS-Q33A starts the receiver path after the Q32 display/mount preparation line. It adds a pure receiver-only client enable gate. The gate is default-off, operator-ack-gated, and no-send. Even when the gate becomes ready, this slice does not open a socket, does not start a client, and does not subscribe live. It only marks the next receiver-only slice as eligible.

```text
gate_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_enable_gate.py
gate_kind=warroom_v2_ws_receiver_only_client_enable_gate_default_off_no_send
input_pipeline=q32z_visible_mount_point_operator_ack_observation,q32b_hidden_ws_display_client_observation,q32a_ws_display_client_contract
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
agreed_refresh_policy=push_first_fragment_render_lightweight_state_pluggable_widget_custom_component_island_ready_later
receiver_enable_requested_default=false
operator_receiver_enable_ack_default=false
receiver_enable_gate_status_default=receiver_enable_gate_hidden_default
receiver_enable_gate_status_ready=receiver_enable_gate_ready_for_next_slice_no_socket
q32_display_mount_preparation_required=true
q32_display_mount_preparation_default=false
manual_smoke_ready_required=true
receiver_only=true
send_disabled=true
receive_only_boundary=true
receiver_client_enable_allowed_for_next_slice_default=false
receiver_client_enable_allowed_effective=false
receiver_enabled_effective=false
socket_opened=false
client_started=false
client_sends_messages=false
external_message_send_enabled=false
websocket_enabled=false
runtime_connected=false
push_connected=false
```

## Refresh policy agreement carried forward

```text
primary_refresh_path=websocket_push_receiver_future
ui_refresh_model=streamlit_fragment_first
state_model=lightweight_receiver_state_in_session_state
render_scope=top_minimal_status_line_first_selected_live_widgets_second
broad_page_reload=avoided_by_default
browser_timer_reload=legacy_fallback_only
component_island_strategy=available_later_for_high_frequency_surfaces
receiver_boundary=receive_only_no_external_send
extensibility_boundary=topic_policy_message_schema_read_model_adapter_widget_fragment_adapter
```

## Non-goals

```text
not_modifying_warroom_page=true
not_adding_visible_controls=true
not_opening_socket=true
not_starting_client=true
not_subscribing_live=true
not_sending_external_messages=true
not_using_polling_fallback=true
not_using_browser_timer_reload=true
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
- ws_receiver_only_client_enable_gate.py exists and stays pure.
- Default receiver enable gate is hidden/default-off.
- Ready requires receiver_enable_requested=true, operator_receiver_enable_ack=true, and Q32Z manual smoke ready=true.
- Ready status only marks receiver_client_enable_allowed_for_next_slice=true.
- The slice never starts a client, opens a socket, sends messages, subscribes live, or enables runtime connection.
- WarRoom page is not modified.
- No visible controls are added.
- Existing Q32Z-Q30C guards remain green.
```
