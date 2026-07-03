# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32A_WARROOM_V2_WS_DISPLAY_CLIENT_CONTRACT_NO_SOCKET_OPEN_2026-07-03.md
# desc: PS-Q32A WarRoom v2 UI-side WS display client contract. Contract only; no socket open and no UI mount.

# PS-Q32A WarRoom v2 WS display client contract no socket open

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31Z_WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_SOCKET_DONE
Slice: PS-Q32A_WARROOM_V2_WS_DISPLAY_CLIENT_CONTRACT_NO_SOCKET_OPEN

## Decision

PS-Q32A defines the UI-side WebSocket display client contract for WarRoom v2 without opening a socket. The client is the receiver side of the display push plane. It accepts only normalized WarRoom display messages from the Q31Y/Q31Z adapter path, keeps a bounded receive buffer, and describes reconnect/subscribe responsibilities without performing network, UI, or order effects.

```text
client_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_client.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
client_kind=ws_display_client_contract_no_socket_open
websocket_display_push_required=true
websocket_display_push_main_path=true
ui_receiver_side=true
server_to_warroom_ui=true
command_intent_plane=warroom_ui_or_autotrade_to_order_intent_gateway
subscriptions_source=q31x_realtime_japanese_read_surface_targets
inbound_source=q31z_ws_display_adapter_observation_outbox
bounded_receive_buffer=true
receive_buffer_default_limit=128
socket_open_requested_default=false
socket_opened=false
client_started=false
client_sends_messages=false
external_message_send_enabled=false
websocket_enabled=false
runtime_connected=false
push_connected=false
```

## Client responsibility

```text
- subscribe to WarRoom display target topics later
- receive server-to-UI display messages later
- validate message schema
- keep only display target messages
- keep latest bounded receive buffer
- expose Japanese read surface metadata
- never submit commands or orders
```

## Non-goals

```text
not_mounting_panel_into_warroom=true
not_rendering_streamlit=true
not_enabling_websocket=true
not_opening_socket=true
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
- ws_display_client.py exists and stays pure.
- client contract is UI receiver side but opens no socket.
- subscriptions come from the realtime Japanese read surface target topics.
- receive buffer accepts only WarRoom display target messages.
- invalid/non-display messages are dropped with reasons.
- no polling/browser reload fallback is introduced.
- no UI mount, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q31Z-Q30C guards remain green.
```
