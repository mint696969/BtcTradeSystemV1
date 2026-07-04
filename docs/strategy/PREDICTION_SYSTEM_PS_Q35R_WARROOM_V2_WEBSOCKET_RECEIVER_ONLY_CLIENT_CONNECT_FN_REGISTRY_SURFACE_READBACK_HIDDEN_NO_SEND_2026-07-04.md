# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35R_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_NO_SEND_2026-07-04.md
# desc: PS-Q35R WarRoom v2 WebSocket receiver-only client connect_fn registry surface hidden readback. Metadata-only; no default network client and no send.

# PS-Q35R WarRoom v2 WebSocket receiver-only client connect_fn registry surface hidden readback

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35Q_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_NO_SEND_DONE
Slice: PS-Q35R_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_NO_SEND

## Decision

PS-Q35R introduces a hidden metadata-only readback for Q35Q registry surface packets. It reads only status and boolean readiness fields. It does not return the raw Q35Q packet, registry keys, registry values, runtime config keys, runtime config values, registration key values, or callable values. It does not call connect_fn and does not send messages.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_readback.py
registry_surface_readback_version=prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback.ps_q35r.v1
requires_registry_surface_packet=true
requires_allow_registry_surface_readback_flag=true
read_only=true
metadata_only=true
hidden_readback_diagnostic=true
raw_registry_surface_packet_returned=false
registry_values_returned=false
registry_keys_returned=false
runtime_config_values_returned=false
runtime_config_keys_returned=false
callable_values_returned=false
registration_key_value_returned=false
connect_fn_called_at_readback=false
global_registry_mutated=false
no_hardcoded_endpoint=true
no_default_network_client=true
client_sends_messages=false
external_message_send_enabled=false
send_disabled=true
warroom_page_modified=false
warroom_page_visible_ui_modified=false
visible_information_added=false
visible_controls_added=false
streamlit_imported=false
streamlit_render_invoked=false
aggregator_exports_added=false
target_session_state_mutated=false
state_mutated=false
order_intent_submitted=false
would_send_to_broker=false
```

## Flow

```text
1. Q35R receives a Q35Q registry surface packet.
2. allow_registry_surface_readback must be true.
3. Q35R verifies the packet kind and reads only status/boolean metadata.
4. Q35R emits hidden readiness labels such as blocked, registry_ready_waiting_source_guard, ready_waiting_socket_guards, attempted_not_open_no_send, or opened_no_send.
5. Q35R never returns raw packet data, registry/runtime keys or values, registration key values, or callable values.
6. Q35R never calls connect_fn and never mutates registry/session state.
7. No message send is enabled at any layer.
```

## Non-goals

```text
not_importing_websocket_library=true
not_adding_default_network_client=true
not_hardcoding_endpoint=true
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
not_using_live_network_tests=true
```

## Acceptance criteria

```text
- Missing allow_registry_surface_readback blocks readback.
- Missing, invalid, or unrecognized registry surface packet blocks readback.
- Valid Q35Q packet produces hidden metadata-only readiness labels.
- Readback does not call connect_fn.
- Raw Q35Q packet, registry keys/values, runtime config keys/values, registration key values, and callable values are not returned.
- No default network client, send path, WarRoom page change, aggregator export, or broker/order/ledger path is added.
```

## Next boundary

Q35S may introduce a hidden session-state record for this readback packet, but it must remain default-off/no-send and avoid page/export changes in the same slice.
