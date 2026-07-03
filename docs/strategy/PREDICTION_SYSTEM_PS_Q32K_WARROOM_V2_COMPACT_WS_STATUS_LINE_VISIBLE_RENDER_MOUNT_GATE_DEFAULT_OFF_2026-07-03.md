# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32K_WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_MOUNT_GATE_DEFAULT_OFF_2026-07-03.md
# desc: PS-Q32K WarRoom v2 compact WS status line visible render mount gate. Default-off; no UI mount and no socket open.

# PS-Q32K WarRoom v2 compact WS status line visible render mount gate default-off

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32J_WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_ADAPTER_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_DONE
Slice: PS-Q32K_WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_MOUNT_GATE_DEFAULT_OFF

## Decision

PS-Q32K defines the final default-off gate for mounting the compact WS status line into the future top minimal operator status line. It consumes the Q32J hidden render adapter observation and may mark the Japanese payload as ready for future Streamlit mount, but it still does not render or mount anything.

```text
gate_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_visible_render_mount_gate.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
gate_kind=warroom_v2_compact_ws_status_line_visible_render_mount_gate_default_off
input_pipeline=q32j_compact_ws_status_line_visible_render_adapter_observation
visible_render_mount_requested_default=false
operator_visible_render_mount_ack_default=false
visible_render_adapter_requested_default=false
operator_visible_render_ack_default=false
visible_mount_requested_default=false
operator_visible_mount_ack_default=false
status_gate_render_requested_default=false
status_gate_read_only_ack_default=false
default_gate_status=compact_ws_status_line_visible_render_mount_hidden_default
ready_gate_status=compact_ws_status_line_visible_render_mount_ready_not_mounted
warroom_mount_surface=top_minimal_operator_status_line
warroom_mount_position=after_header_before_focus_nav_later
warroom_page_modified=false
status_line_visible_now=false
status_line_mounted_now=false
streamlit_render_invoked=false
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
- compact_ws_status_line_visible_render_mount_gate.py exists and stays pure.
- Default gate is hidden/off.
- Ready state requires visible_render_mount_requested=true, operator_visible_render_mount_ack=true, and upstream Q32J render payload ready.
- Ready state still reports visible_now=false, mounted_now=false, and streamlit_render_invoked=false in this slice.
- The future mount payload preserves the exact six Japanese display items and compact_line_ja.
- WarRoom page is not modified in this slice.
- no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32J-Q30C guards remain green.
```
