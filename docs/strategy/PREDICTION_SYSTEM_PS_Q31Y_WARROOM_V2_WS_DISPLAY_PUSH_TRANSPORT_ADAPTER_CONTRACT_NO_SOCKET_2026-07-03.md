# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31Y_WARROOM_V2_WS_DISPLAY_PUSH_TRANSPORT_ADAPTER_CONTRACT_NO_SOCKET_2026-07-03.md
# desc: PS-Q31Y WarRoom v2 WS display push transport adapter contract. Contract only; no socket and no UI mount.

# PS-Q31Y WarRoom v2 WS display push transport adapter contract

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31X_WARROOM_V2_REALTIME_JAPANESE_READ_SURFACE_WS_DISPLAY_TARGET_CONTRACT_DONE
Slice: PS-Q31Y_WARROOM_V2_WS_DISPLAY_PUSH_TRANSPORT_ADAPTER_CONTRACT_NO_SOCKET

## Decision

PS-Q31Y creates the no-socket contract for the future WarRoom v2 WebSocket display push adapter. It is the main path that will replace Streamlit/browser timer refresh for the WarRoom display plane. This slice still opens no socket and sends no messages; it only normalizes the future display-push outbox and keeps all command/order behavior disconnected.

```text
adapter_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_adapter.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
adapter_kind=ws_display_push_transport_adapter_contract_no_socket
websocket_display_push_required=true
websocket_display_push_main_path=true
bidirectional_websocket_premise=true
read_model_push_plane=server_to_warroom_ui
command_intent_plane=warroom_ui_or_autotrade_to_order_intent_gateway
browser_timer_polling_is_legacy_compat_only=true
browser_timer_refresh_replacement_target=true
no_new_polling_fallback=true
no_browser_timer_reload_introduced=true
socket_opened=false
adapter_sends_messages=false
external_message_send_enabled=false
websocket_enabled=false
runtime_connected=false
push_connected=false
order_intent_submitted=false
broker_send_enabled=false
would_send_to_broker=false
```

## Diagnostic placement policy

WarRoom must stay readable. Detailed diagnostics should not be dumped into the main WarRoom tab by default.

```text
warroom_diagnostic_policy=minimal_status_only
diagnostic_minimal_summary_allowed_in_warroom=true
detailed_diagnostics_default_surface=audit_or_diagnostics_tab
warroom_visible_diagnostic_panel_default=false
visible_panel_render_plan_deprioritized=true
allowed_warroom_diagnostic_summary_fields=safety_state,data_freshness,transport_state,last_update_age
```

This means WarRoom can show operator-useful minimal state such as safety, freshness, and transport connection state. Deep diagnostics, review packets, gate internals, and verbose traces belong in a future Audit/Diagnostics tab unless explicitly promoted as a compact operator warning.

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
- ws_display_adapter.py exists and stays pure.
- adapter contract is the WS display push main path, but no socket is opened.
- outbox normalizes only known WarRoom display target messages.
- browser timer refresh remains legacy compatibility only and no new polling fallback is introduced.
- WarRoom diagnostic policy is minimal status only; detailed diagnostics route to Audit/Diagnostics surface.
- no UI mount, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q31X-Q30C guards remain green.
```
