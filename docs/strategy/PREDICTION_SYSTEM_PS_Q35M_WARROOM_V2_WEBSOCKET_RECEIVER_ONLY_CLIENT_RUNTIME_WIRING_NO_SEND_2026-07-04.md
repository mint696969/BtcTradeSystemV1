# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35M_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_RUNTIME_WIRING_NO_SEND_2026-07-04.md
# desc: PS-Q35M WarRoom v2 WebSocket receiver-only client runtime wiring. Composes Q35K preflight and Q35L guarded open; injected opener only and no send.

# PS-Q35M WarRoom v2 WebSocket receiver-only client runtime wiring no-send

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35L_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_GUARDED_SOCKET_OPEN_NO_SEND_DONE
Slice: PS-Q35M_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_RUNTIME_WIRING_NO_SEND

## Decision

PS-Q35M wires the existing Q35K preflight and Q35L guarded socket-open boundary into one receiver-only runtime packet. It does not add a default network client, does not hardcode an endpoint, does not modify WarRoom page, and does not send messages. Any socket-open attempt still occurs only through the injected opener used by Q35L.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_runtime_wiring.py
runtime_wiring_version=prediction_warroom.v2.transport.ws_receiver_only_client_runtime_wiring.ps_q35m.v1
composes_q35k_preflight=true
composes_q35l_guarded_socket_open=true
requires_compact_status_badge_packet=true
requires_operator_scope_ack_for_preflight=true
requires_socket_open_requested=true
requires_operator_socket_open_ack=true
requires_endpoint_url=true
requires_allow_socket_open_flag=true
requires_injected_socket_open_callable=true
injected_opener_only=true
no_hardcoded_endpoint=true
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

## Flow

```text
1. Build Q35K preflight from compact_status_badge_packet and operator_scope_ack.
2. Pass Q35K preflight into Q35L guarded socket open.
3. Q35L applies request/ack/endpoint/allow/opener guards.
4. If all guards pass, Q35L calls injected opener once.
5. Q35M returns preflight packet, guarded-open packet, and top-level summary flags.
6. No message send is enabled at any layer.
```

## Non-goals

```text
not_hardcoding_endpoint=true
not_importing_websocket_library=true
not_adding_default_network_client=true
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
- Badge/preflight not-ready blocks runtime wiring before opener call.
- Missing operator_scope_ack blocks runtime wiring before opener call.
- With all Q35K/Q35L guards true, injected opener is called exactly once.
- Opener success and failure are preserved as packet data.
- No send path, WarRoom page change, aggregator export, or default network client is added.
```

## Next boundary

Q35N may introduce a real adapter factory or runtime source for the injected opener. Keep it narrow, no-send, and avoid broker/order/ledger/mode/parameter/prediction paths.
