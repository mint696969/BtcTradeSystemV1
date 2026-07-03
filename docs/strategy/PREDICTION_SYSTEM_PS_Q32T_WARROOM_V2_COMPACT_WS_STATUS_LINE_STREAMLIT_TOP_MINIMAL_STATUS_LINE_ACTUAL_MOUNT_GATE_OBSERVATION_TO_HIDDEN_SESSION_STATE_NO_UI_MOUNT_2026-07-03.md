# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32T_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_ACTUAL_MOUNT_GATE_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_2026-07-03.md
# desc: PS-Q32T WarRoom v2 hidden compact WS status line top minimal actual mount gate observation. No UI mount and no socket open.

# PS-Q32T WarRoom v2 compact WS status line Streamlit top minimal actual mount gate observation to hidden session state

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32S_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_ACTUAL_MOUNT_GATE_DEFAULT_OFF_DONE
Slice: PS-Q32T_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_ACTUAL_MOUNT_GATE_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT

## Decision

PS-Q32T records the Q32S default-off actual mount gate packet in the WarRoom Streamlit render path as hidden `session_state` only. It preserves the future Streamlit call model, actual mount decision, renderer model, display items, and compact Japanese status text while still not mounting or rendering the line.

```text
observation_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_streamlit_top_minimal_status_line_actual_mount_gate_observation.py
state_key=warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_actual_mount_gate_observation_q32t
input_pipeline=q32r_compact_ws_status_line_streamlit_top_minimal_status_line_renderer_observation,q32s_compact_ws_status_line_streamlit_top_minimal_status_line_actual_mount_gate
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
actual_mount_requested_default=false
operator_actual_mount_ack_default=false
top_minimal_status_line_render_requested_default=false
operator_top_minimal_status_line_render_ack_default=false
default_gate_status=compact_ws_status_line_streamlit_top_minimal_status_line_actual_mount_hidden_default
actual_mount_allowed_for_future_warroom_page_default=false
status_line_visible_now=false
status_line_mounted_now=false
streamlit_imported=false
streamlit_render_invoked=false
warroom_page_hidden_state_only=true
warroom_mount_surface=top_minimal_operator_status_line
warroom_mount_position=after_header_before_focus_nav_later
future_streamlit_call_model_preserved=true
future_streamlit_call_name=markdown
renderer_model_preserved=true
display_item_count=6
display_item_labels_ja=WS状態,データ鮮度,最終更新,受信数,破棄数,案内
compact_line_ja_preserved=true
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
not_rendering_streamlit=true
not_importing_streamlit=true
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
- compact_ws_status_line_streamlit_top_minimal_status_line_actual_mount_gate_observation.py exists and stays pure.
- WarRoom page records hidden compact WS status line top minimal actual mount gate observation state only.
- Existing visible WarRoom layout remains unchanged.
- Default gate is compact_ws_status_line_streamlit_top_minimal_status_line_actual_mount_hidden_default.
- actual_mount_requested=false and operator_actual_mount_ack=false by default.
- actual_mount_allowed_for_future_warroom_page=false by default.
- status_line_visible_now=false, status_line_mounted_now=false, streamlit_imported=false, and streamlit_render_invoked=false.
- Q32S guard allows later hidden observation while still forbidding direct actual mount gate packet/version, actual_mount_allowed_for_future_warroom_page, visible labels, and Streamlit rendering in WarRoom page.
- no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32S-Q30C guards remain green.
```
