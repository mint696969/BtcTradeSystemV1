# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32G_WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_MOUNT_GATE_DEFAULT_OFF_2026-07-03.md
# desc: PS-Q32G WarRoom v2 compact WS status line visible mount gate. Default-off; no UI mount and no socket open.

# PS-Q32G WarRoom v2 compact WS status line visible mount gate default-off

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32F_WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_DONE
Slice: PS-Q32G_WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_MOUNT_GATE_DEFAULT_OFF

## Decision

PS-Q32G defines the default-off visible mount gate for the compact WS status line. It fixes the future WarRoom surface as a top minimal operator status line, consumes the Q32F hidden gate observation, and requires explicit mount request plus read-only acknowledgement plus ready Q32E/Q32F status-line gate. This slice does not mount the line and does not touch WarRoom page.

```text
gate_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_visible_mount_gate.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
gate_kind=warroom_v2_compact_ws_status_line_visible_mount_gate_default_off
input_pipeline=q32f_compact_ws_status_line_gate_observation
visible_mount_requested_default=false
operator_visible_mount_ack_default=false
status_gate_render_requested_default=false
status_gate_read_only_ack_default=false
default_gate_status=compact_ws_status_line_visible_mount_hidden_default
ready_gate_status=compact_ws_status_line_visible_mount_ready_not_mounted
warroom_mount_surface=top_minimal_operator_status_line
warroom_mount_position=after_header_before_focus_nav_later
warroom_page_modified=false
status_line_visible_now=false
status_line_mounted_now=false
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
- compact_ws_status_line_visible_mount_gate.py exists and stays pure.
- Default gate is hidden/off.
- Ready state requires visible_mount_requested=true, operator_visible_mount_ack=true, status_gate_render_requested=true, and status_gate_read_only_ack=true.
- Ready state still reports visible_now=false and mounted_now=false in this slice.
- WarRoom page is not modified in this slice.
- no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32F-Q30C guards remain green.
```
