# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32D_WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_2026-07-03.md
# desc: PS-Q32D WarRoom v2 hidden session_state WS display connection status observation. No UI mount and no socket open.

# PS-Q32D WarRoom v2 WS display connection status observation to hidden session state

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32C_WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_CONTRACT_NO_SOCKET_OPEN_DONE
Slice: PS-Q32D_WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT

## Decision

PS-Q32D records the Q32C compact WS display connection-status packet in the WarRoom Streamlit render path as hidden `session_state` only. This prepares the future minimal operator status line, but does not mount it visibly and does not open a socket.

```text
observation_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_connection_status_observation.py
state_key=warroom_v2_ws_display_connection_status_observation_q32d
input_pipeline=q32b_ws_display_client_observation,q32c_ws_display_connection_status_contract
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
streamlit_path_messages=[]
default_status_code=ws_not_started_no_socket_open
default_transport_state_ja=WS未接続（準備中）
default_data_freshness_ja=未接続のため未取得
default_last_update_age_ja=未接続
warroom_status_line_allowed_later=true
warroom_status_line_visible_now=false
warroom_status_line_mounted_now=false
compact_status_only=true
detailed_diagnostics_default_surface=audit_or_diagnostics_tab
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
not_mounting_status_line_into_warroom=true
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
- ws_display_connection_status_observation.py exists and stays pure.
- WarRoom page records hidden WS display connection-status observation state only.
- Existing visible WarRoom layout remains unchanged.
- Default status is ws_not_started_no_socket_open / WS未接続（準備中）.
- Future-visible status line remains allowed_later only and visible_now=false.
- no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32C-Q30C guards remain green.
```
