# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32M_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_DEFAULT_OFF_2026-07-03.md
# desc: PS-Q32M WarRoom v2 compact WS status line minimal renderer spec. Default-off; no WarRoom page mount and no socket open.

# PS-Q32M WarRoom v2 compact WS status line Streamlit minimal renderer default-off

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32L_WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_MOUNT_GATE_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_DONE
Slice: PS-Q32M_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_MINIMAL_RENDERER_DEFAULT_OFF

## Decision

PS-Q32M defines a default-off minimal renderer specification for the compact WS status line. It consumes Q32L hidden visible render mount gate observation and returns a future one-line Japanese status-row model, but it does not import Streamlit, call Streamlit, or mount anything into WarRoom page.

```text
renderer_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_streamlit_minimal_renderer.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
renderer_kind=warroom_v2_compact_ws_status_line_streamlit_minimal_renderer_default_off
input_pipeline=q32l_compact_ws_status_line_visible_render_mount_gate_observation
renderer_requested_default=false
operator_renderer_ack_default=false
visible_render_mount_requested_default=false
operator_visible_render_mount_ack_default=false
visible_render_adapter_requested_default=false
operator_visible_render_ack_default=false
default_renderer_status=compact_ws_status_line_streamlit_minimal_renderer_hidden_default
ready_renderer_status=compact_ws_status_line_streamlit_minimal_renderer_model_ready_not_rendered
warroom_mount_surface=top_minimal_operator_status_line
warroom_mount_position=after_header_before_focus_nav_later
warroom_page_modified=false
renderer_model_created=true
render_instruction_kind=future_single_line_status_text
status_line_visible_now=false
status_line_mounted_now=false
streamlit_imported=false
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
- compact_ws_status_line_streamlit_minimal_renderer.py exists and stays pure.
- Default renderer is hidden/off.
- Ready state requires renderer_requested=true, operator_renderer_ack=true, and upstream Q32L render mount ready.
- Ready state returns renderer_model but still reports visible_now=false, mounted_now=false, and streamlit_render_invoked=false.
- The renderer model preserves the exact six Japanese display items and compact_line_ja.
- WarRoom page is not modified in this slice.
- no Streamlit import, no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32L-Q30C guards remain green.
```
