# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32B_WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_SOCKET_OPEN_2026-07-03.md
# desc: PS-Q32B WarRoom v2 hidden session_state WS display client observation. No socket open and no UI mount.

# PS-Q32B WarRoom v2 WS display client observation to hidden session state

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32A_WARROOM_V2_WS_DISPLAY_CLIENT_CONTRACT_NO_SOCKET_OPEN_DONE
Slice: PS-Q32B_WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_SOCKET_OPEN

## Decision

PS-Q32B records the Q32A no-socket WS display client contract and receive buffer in the WarRoom Streamlit render path as hidden `session_state` only. It keeps the UI-side receiver path observable while still opening no socket, mounting no UI, and sending no messages.

```text
observation_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_client_observation.py
state_key=warroom_v2_ws_display_client_observation_q32b
input_pipeline=q31z_ws_display_adapter_observation,q32a_ws_display_client_contract
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
streamlit_path_messages=[]
default_streamlit_message_count=0
received_message_count_default=0
dropped_count_default=0
websocket_display_push_required=true
websocket_display_push_main_path=true
ui_receiver_side=true
server_to_warroom_ui=true
bounded_receive_buffer=true
socket_open_requested=false
socket_opened=false
client_started=false
client_sends_messages=false
external_message_send_enabled=false
websocket_enabled=false
runtime_connected=false
push_connected=false
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
- ws_display_client_observation.py exists and stays pure.
- WarRoom page records hidden WS display client observation state only.
- Existing visible WarRoom layout remains unchanged.
- Default Streamlit path uses messages=[].
- received_message_count defaults to 0 and dropped_count defaults to 0.
- WS display push remains the main path but socket_opened=false and client_started=false.
- Browser timer polling remains legacy compatibility only; no new polling or browser reload fallback is introduced.
- no UI mount, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32A-Q30C guards remain green.
```
