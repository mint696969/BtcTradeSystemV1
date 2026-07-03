# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32F_WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_2026-07-03.md
# desc: PS-Q32F WarRoom v2 hidden session_state compact WS status line gate observation. No UI mount and no socket open.

# PS-Q32F WarRoom v2 compact WS status line gate observation to hidden session state

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32E_WARROOM_V2_COMPACT_WS_STATUS_LINE_RENDER_GATE_DEFAULT_OFF_DONE
Slice: PS-Q32F_WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT

## Decision

PS-Q32F records the Q32E default-off compact WS status line gate in the WarRoom Streamlit render path as hidden `session_state` only. It keeps the future top minimal operator status line observable while still not mounting it and not opening a socket.

```text
observation_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_gate_observation.py
state_key=warroom_v2_compact_ws_status_line_gate_observation_q32f
input_pipeline=q32d_ws_display_connection_status_observation,q32e_compact_ws_status_line_gate
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
render_requested_default=false
operator_read_only_ack_default=false
default_gate_status=compact_ws_status_line_hidden_default
status_line_ready_for_future_mount_default=false
status_line_visible_now=false
status_line_mounted_now=false
warroom_page_hidden_state_only=true
warroom_visible_surface=top_minimal_operator_status_line_later
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
- compact_ws_status_line_gate_observation.py exists and stays pure.
- WarRoom page records hidden compact WS status line gate observation state only.
- Existing visible WarRoom layout remains unchanged.
- Default gate is compact_ws_status_line_hidden_default.
- render_requested=false and operator_read_only_ack=false by default.
- status_line_visible_now=false and status_line_mounted_now=false.
- no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32E-Q30C guards remain green.
```
