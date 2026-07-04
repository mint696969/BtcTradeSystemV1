# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35L_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_GUARDED_SOCKET_OPEN_NO_SEND_2026-07-04.md
# desc: PS-Q35L WarRoom v2 WebSocket receiver-only client guarded socket-open boundary. Injected opener only, no hardcoded endpoint, and no send.

# PS-Q35L WarRoom v2 WebSocket receiver-only client guarded socket open no-send

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35K_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_START_PREFLIGHT_NO_SOCKET_NO_SEND_DONE
Slice: PS-Q35L_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_GUARDED_SOCKET_OPEN_NO_SEND

## Decision

PS-Q35L is the first guarded receiver-only socket-open boundary. It does not import a network client, does not hardcode an endpoint, does not modify WarRoom page, and does not send messages. It can call only an injected opener function after Q35K preflight readiness, socket_open_requested, operator_socket_open_ack, endpoint presence, and allow_socket_open are all true.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_guarded_socket_open.py
guarded_socket_open_version=prediction_warroom.v2.transport.ws_receiver_only_client_guarded_socket_open.ps_q35l.v1
requires_q35k_preflight_ready=true
requires_socket_open_requested=true
requires_operator_socket_open_ack=true
requires_endpoint_url=true
requires_allow_socket_open_flag=true
requires_injected_socket_open_callable=true
injected_opener_only=true
no_hardcoded_endpoint=true
socket_opened=true_only_when_injected_opener_reports_open
client_started=true_only_when_injected_opener_reports_open
websocket_enabled=true_only_when_injected_opener_reports_open
runtime_connected=true_only_when_injected_opener_reports_open
push_connected=true_only_when_injected_opener_reports_open
client_sends_messages=false
external_message_send_enabled=false
send_disabled=true
warroom_page_modified=false
warroom_page_visible_ui_modified=false
visible_information_added=false
visible_controls_added=false
renders_badge_now=false
renders_card_now=false
renders_balloon_now=false
renders_warning_now=false
renders_help_text_now=false
streamlit_imported=false
streamlit_render_allowed=false
streamlit_render_invoked=false
aggregator_exports_added=false
target_session_state_mutated=false
state_mutated=false
order_intent_submitted=false
would_send_to_broker=false
```

## Guard order

```text
1. Q35K preflight readiness required.
2. socket_open_requested required.
3. operator_socket_open_ack required.
4. endpoint_url required.
5. allow_socket_open flag required.
6. injected socket_open_fn required.
7. call injected opener once.
8. report open/failure as packet data.
9. never send messages.
```

## Non-goals

```text
not_hardcoding_endpoint=true
not_importing_websocket_library=true
not_modifying_warroom_page=true
not_adding_aggregator_exports=true
not_adding_visible_controls=true
not_sending_external_messages=true
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
- Without Q35K preflight readiness, injected opener is not called.
- Without request, operator ack, endpoint, allow flag, or opener, injected opener is not called.
- With all guards true, injected opener is called exactly once.
- Open success is reported only from opener result.
- Opener failure is reported as packet data and does not send messages.
- WarRoom page and aggregator exports are not modified.
```

## Next boundary

Q35M may integrate this boundary with a real receiver client adapter or runtime wiring, but it must keep no-send guarantees and avoid broker/order/ledger paths.
