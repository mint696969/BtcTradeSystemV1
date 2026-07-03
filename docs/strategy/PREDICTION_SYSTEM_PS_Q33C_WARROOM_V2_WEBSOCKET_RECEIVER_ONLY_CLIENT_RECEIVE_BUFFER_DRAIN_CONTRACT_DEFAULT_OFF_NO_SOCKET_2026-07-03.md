# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q33C_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_RECEIVE_BUFFER_DRAIN_CONTRACT_DEFAULT_OFF_NO_SOCKET_2026-07-03.md
# desc: PS-Q33C WarRoom v2 WebSocket receiver-only client receive-buffer drain contract. Default-off, no socket open, and no send.

# PS-Q33C WarRoom v2 WebSocket receiver-only client receive-buffer drain contract default-off no-socket

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q33B_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_HIDDEN_STATE_DEFAULT_OFF_NO_SOCKET_DONE
Slice: PS-Q33C_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_RECEIVE_BUFFER_DRAIN_CONTRACT_DEFAULT_OFF_NO_SOCKET

## Decision

PS-Q33C adds a pure receive-buffer drain contract for the receiver-only client path. It composes Q33B receiver hidden state and the existing Q32A receive buffer packet. The slice defines how accepted display messages may be previewed for a future lightweight receiver state drain, but it does not perform the drain, mutate session state, open sockets, start a client, subscribe live, or send messages.

```text
drain_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_receive_buffer_drain_contract.py
drain_kind=warroom_v2_ws_receiver_only_client_receive_buffer_drain_contract_default_off_no_socket
input_pipeline=q33b_receiver_only_client_hidden_state,q32a_ws_display_client_receive_buffer
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
agreed_refresh_policy=push_first_fragment_render_lightweight_state_pluggable_widget_custom_component_island_ready_later
drain_requested_default=false
operator_drain_ack_default=false
drain_contract_status_default=receive_buffer_drain_hidden_default
drain_contract_status_ready=receive_buffer_drain_ready_for_next_slice_no_socket
receive_buffer_drain_allowed_for_next_slice_default=false
receive_buffer_drain_allowed_effective=false
messages_drained_now=0
state_mutated=false
session_state_write_allowed=false
warroom_page_modified=false
visible_controls_added=false
receiver_only=true
send_disabled=true
socket_opened=false
client_started=false
client_sends_messages=false
external_message_send_enabled=false
websocket_enabled=false
runtime_connected=false
push_connected=false
```

## Drain semantics

```text
drain_contract_is_preview_only=true
drain_contract_is_not_socket_owner=true
drain_contract_is_not_client_runtime=true
drain_contract_is_not_subscription_runtime=true
drain_contract_is_not_send_path=true
drain_source=existing_q32a_receive_buffer_packet_messages
drain_target=future_lightweight_receiver_state_next_slice
drain_preview_max_default=16
drain_effective_mutation=false
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
not_rendering_drain_state=true
not_mutating_session_state=true
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
- ws_receiver_only_client_receive_buffer_drain_contract.py exists and stays pure.
- Default packet status is receive_buffer_drain_hidden_default.
- Ready requires drain_requested=true, operator_drain_ack=true, and Q33B receiver hidden state next-slice eligibility=true.
- Ready packet may include drain preview messages from the Q32A receive buffer.
- Ready packet still has receive_buffer_drain_allowed_effective=false and messages_drained_now=0.
- WarRoom page is not modified.
- socket_opened=false, client_started=false, client_sends_messages=false, websocket_enabled=false.
- Existing Q33B-Q30C guards remain green.
```
