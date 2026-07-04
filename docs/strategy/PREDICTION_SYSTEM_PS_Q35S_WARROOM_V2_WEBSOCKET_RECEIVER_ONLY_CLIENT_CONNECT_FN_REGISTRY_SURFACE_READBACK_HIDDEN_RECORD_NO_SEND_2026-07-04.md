# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35S_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_NO_SEND_2026-07-04.md
# desc: PS-Q35S WarRoom v2 WebSocket receiver-only client connect_fn registry surface readback hidden session-state record. Default-off metadata-only; no page, no socket, no send.

# PS-Q35S WarRoom v2 WebSocket receiver-only client connect_fn registry surface readback hidden record

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35R_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_NO_SEND_DONE
Slice: PS-Q35S_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_NO_SEND

## Decision

PS-Q35S introduces a default-off hidden session-state record for the Q35R metadata-only readback packet. It requires an explicit request, operator ack, a ready Q35R readback packet, and a provided mutable session_state mapping. It records only sanitized metadata and does not modify WarRoom page code, exports, registry state, socket state, or send paths.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record.py
registry_surface_readback_hidden_record_version=prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record.ps_q35s.v1
hidden_record_key=warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_q35s
requires_registry_surface_readback_packet=true
requires_hidden_record_request=true
requires_operator_hidden_record_ack=true
requires_mutable_session_state_mapping=true
hidden_record_requested_default=false
operator_hidden_record_ack_default=false
hidden_session_state_recorded=true
hidden_record_effective_mutation_scope=provided_session_state_key_only
record_metadata_only=true
raw_readback_packet_recorded=false
raw_registry_surface_packet_returned=false
registry_values_returned=false
registry_keys_returned=false
runtime_config_values_returned=false
runtime_config_keys_returned=false
callable_values_returned=false
registration_key_value_returned=false
connect_fn_called_at_hidden_record=false
global_registry_mutated=false
warroom_page_modified=false
warroom_page_visible_ui_modified=false
visible_information_added=false
visible_controls_added=false
streamlit_imported=false
streamlit_render_invoked=false
aggregator_exports_added=false
client_sends_messages=false
external_message_send_enabled=false
send_disabled=true
order_intent_submitted=false
would_send_to_broker=false
```

## Flow

```text
1. Q35S receives a Q35R registry surface readback packet.
2. hidden_record_requested and operator_hidden_record_ack must both be true.
3. The Q35R readback packet must be recognized and ready.
4. A mutable session_state mapping must be provided explicitly.
5. Q35S records only metadata fields under the Q35S hidden record key.
6. Q35S does not record raw Q35R/Q35Q packets, registry/runtime keys or values, registration key values, callable values, or sensitive endpoint/token values.
7. Q35S never calls connect_fn and never mutates global registry state.
8. No message send is enabled at any layer.
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
- Default call does not mutate session_state.
- Missing operator ack, missing ready readback, and missing session_state block hidden record.
- Ready readback with request and ack writes exactly one metadata-only hidden record under the Q35S key.
- Raw Q35R/Q35Q packets, registry keys/values, runtime config keys/values, registration key values, callable values, endpoint values, and token values are not recorded or returned.
- Hidden record does not call connect_fn.
- No default network client, send path, WarRoom page change, aggregator export, or broker/order/ledger path is added.
```

## Next boundary

Q35T may introduce a hidden readback of the Q35S session-state record, but it must remain metadata-only/no-send and avoid page/export changes in the same slice.
