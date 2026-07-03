# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32Q_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_RENDERER_DEFAULT_OFF_2026-07-03.md
# desc: PS-Q32Q WarRoom v2 compact WS status line top minimal renderer contract. Default-off; no WarRoom page mount and no socket open.

# PS-Q32Q WarRoom v2 compact WS status line Streamlit top minimal status-line renderer default-off

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32P_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_VISIBLE_MOUNT_GATE_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_DONE
Slice: PS-Q32Q_WARROOM_V2_COMPACT_WS_STATUS_LINE_STREAMLIT_TOP_MINIMAL_STATUS_LINE_RENDERER_DEFAULT_OFF

## Decision

PS-Q32Q defines a default-off top minimal status-line renderer contract for the compact WS status line. It consumes Q32P hidden visible mount gate observation and prepares a future Streamlit call model, but it does not import Streamlit, call Streamlit, or modify WarRoom page.

```text
renderer_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_streamlit_top_minimal_status_line_renderer.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
renderer_kind=warroom_v2_compact_ws_status_line_streamlit_top_minimal_status_line_renderer_default_off
input_pipeline=q32p_compact_ws_status_line_streamlit_visible_mount_gate_observation
top_minimal_status_line_render_requested_default=false
operator_top_minimal_status_line_render_ack_default=false
visible_streamlit_mount_requested_default=false
operator_visible_streamlit_mount_ack_default=false
default_renderer_status=compact_ws_status_line_streamlit_top_minimal_status_line_renderer_hidden_default
ready_renderer_status=compact_ws_status_line_streamlit_top_minimal_status_line_renderer_ready_not_rendered
ready_requires=top_minimal_status_line_render_requested_true_and_operator_ack_true_and_upstream_mount_allowed_true
warroom_mount_surface=top_minimal_operator_status_line
warroom_mount_position=after_header_before_focus_nav_later
warroom_page_modified=false
future_streamlit_call_prepared=true
future_streamlit_call_kind=single_markdown_status_line_later
streamlit_imported=false
streamlit_render_invoked=false
status_line_visible_now=false
status_line_mounted_now=false
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
- compact_ws_status_line_streamlit_top_minimal_status_line_renderer.py exists and stays pure.
- Default top minimal renderer is hidden/off.
- Ready state requires top_minimal_status_line_render_requested=true, operator_top_minimal_status_line_render_ack=true, and upstream Q32P mount allowed.
- Ready state may prepare a future call model but still reports visible_now=false, mounted_now=false, and streamlit_render_invoked=false.
- The renderer packet preserves renderer_model, display_items, compact_line_ja, and the six Japanese item labels.
- WarRoom page is not modified in this slice.
- no Streamlit import, no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32P-Q30C guards remain green.
```
