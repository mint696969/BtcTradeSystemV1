# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q32C_WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_CONTRACT_NO_SOCKET_OPEN_2026-07-03.md
# desc: PS-Q32C WarRoom v2 compact WS display connection status contract. Contract only; no socket open and no UI mount.

# PS-Q32C WarRoom v2 WS display connection status contract no socket open

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q32B_WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_SOCKET_OPEN_DONE
Slice: PS-Q32C_WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_CONTRACT_NO_SOCKET_OPEN

## Decision

PS-Q32C defines a compact Japanese connection-status contract for the future WarRoom minimal operator status line. It is derived from the Q32B hidden WS display client observation and is allowed to describe only compact WarRoom-safe information: transport state, data freshness, last update age, received count, dropped count, and operator guidance. This slice does not render it, does not mount UI, and does not open a socket.

```text
status_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_connection_status.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
status_kind=warroom_v2_ws_display_connection_status_contract_no_socket_open
warroom_status_line_allowed_later=true
warroom_status_line_mounted_now=false
allowed_warroom_status_fields=transport_state_ja,data_freshness_ja,last_update_age_ja,received_message_count,dropped_count,operator_guidance_ja
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

## Status semantics

```text
status=ws_not_started_no_socket_open
label_ja=WS未接続（準備中）
operator_guidance_ja=画面更新はまだWS接続ではありません。表示契約のみ確認中です。
```

Future connected states may be added only after the socket gate is explicit and guarded.

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
- ws_display_connection_status.py exists and stays pure.
- status packet is derived from Q32B client observation.
- default status is ws_not_started_no_socket_open.
- Japanese labels and operator guidance are compact and WarRoom-safe.
- detailed diagnostics remain routed to Audit/Diagnostics by default.
- no UI mount, no socket open, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q32B-Q30C guards remain green.
```
