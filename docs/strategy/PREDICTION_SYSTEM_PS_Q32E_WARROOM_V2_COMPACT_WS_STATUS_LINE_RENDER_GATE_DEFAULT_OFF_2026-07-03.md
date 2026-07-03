# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32E_WARROOM_V2_COMPACT_WS_STATUS_LINE_RENDER_GATE_DEFAULT_OFF_2026-07-03.md
# desc: PS-Q32E WarRoom v2 compact WS status line render gate. Default-off; no UI mount and no socket open.

# PS-Q32E WarRoom v2 compact WS status line render gate default-off

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32D_WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_DONE
Slice: PS-Q32E_WARROOM_V2_COMPACT_WS_STATUS_LINE_RENDER_GATE_DEFAULT_OFF

## Decision

PS-Q32E defines a default-off render gate for the compact WS status line that may later appear in the main WarRoom tab. The gate consumes Q32D hidden connection-status observation and exposes only WarRoom-safe Japanese fields. It does not mount UI, does not render Streamlit, and does not open a socket.

```text
gate_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_gate.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
gate_kind=warroom_v2_compact_ws_status_line_render_gate_default_off
input_pipeline=q32d_ws_display_connection_status_observation
render_requested_default=false
operator_read_only_ack_default=false
status_line_visible_now_default=false
status_line_mounted_now_default=false
default_gate_status=compact_ws_status_line_hidden_default
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

## Allowed future status row

```text
transport_state_ja=WS未接続（準備中）
data_freshness_ja=未接続のため未取得
last_update_age_ja=未接続
received_message_count=0
dropped_count=0
operator_guidance_ja=画面更新はまだWS接続ではありません。表示契約のみ確認中です。
```

The row is contract output only in this slice. It must not be mounted into WarRoom until a later explicit observation/mount gate passes.

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
- compact_ws_status_line_gate.py exists and stays pure.
- default gate is hidden/off.
- ready state requires render_requested=true and operator_read_only_ack=true.
- ready state exposes exactly the compact Q32C/Q32D status fields.
- WarRoom page is not modified in this slice.
- no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32D-Q30C guards remain green.
```
