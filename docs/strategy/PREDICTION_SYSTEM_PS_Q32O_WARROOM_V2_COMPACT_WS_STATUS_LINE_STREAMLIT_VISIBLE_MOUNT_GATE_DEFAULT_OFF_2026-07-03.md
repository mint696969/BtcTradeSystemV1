# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32O_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_VISIBLE_MOUNT_GATE_DEFAULT_OFF_2026-07-03.md
# desc: PS-Q32O WarRoom v2 compact WS status line Streamlit visible mount gate. Default-off; no WarRoom page mount and no socket open.

# PS-Q32O WarRoom v2 compact WS status line Streamlit visible mount gate default-off

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32N_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_DONE
Slice: PS-Q32O_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_VISIBLE_MOUNT_GATE_DEFAULT_OFF

## Decision

PS-Q32O defines a default-off visible mount gate for the compact WS status line Streamlit renderer model. It consumes Q32N hidden minimal renderer observation and decides whether a future WarRoom top minimal status line may be mounted, but it does not import Streamlit, call Streamlit, or modify WarRoom page.

```text
gate_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_streamlit_visible_mount_gate.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
gate_kind=warroom_v2_compact_ws_status_line_streamlit_visible_mount_gate_default_off
input_pipeline=q32n_compact_ws_status_line_streamlit_minimal_renderer_observation
visible_streamlit_mount_requested_default=false
operator_visible_streamlit_mount_ack_default=false
renderer_requested_default=false
operator_renderer_ack_default=false
default_gate_status=compact_ws_status_line_streamlit_visible_mount_hidden_default
ready_gate_status=compact_ws_status_line_streamlit_visible_mount_ready_not_mounted
ready_requires=visible_streamlit_mount_requested_true_and_operator_visible_streamlit_mount_ack_true_and_upstream_renderer_model_ready_true
warroom_mount_surface=top_minimal_operator_status_line
warroom_mount_position=after_header_before_focus_nav_later
warroom_page_modified=false
mount_allowed_for_future_warroom_page_default=false
status_line_visible_now=false
status_line_mounted_now=false
streamlit_imported=false
streamlit_render_invoked=false
renderer_model_preserved=true
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
not_modifying_warroom_page=true
not_importing_streamlit=true
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
- compact_ws_status_line_streamlit_visible_mount_gate.py exists and stays pure.
- Default visible mount gate is hidden/off.
- Ready state requires visible_streamlit_mount_requested=true, operator_visible_streamlit_mount_ack=true, and upstream Q32N renderer model ready.
- Ready state may set mount_allowed_for_future_warroom_page=true but still reports visible_now=false, mounted_now=false, and streamlit_render_invoked=false.
- The gate packet preserves renderer_model, display_items, compact_line_ja, and the six Japanese item labels.
- WarRoom page is not modified in this slice.
- no Streamlit import, no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32N-Q30C guards remain green.
```
