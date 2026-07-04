# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35T_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_READBACK_NO_SEND_2026-07-04.md
# desc: PS-Q35T WarRoom v2 WebSocket receiver-only client connect_fn registry surface hidden-record readback. Metadata-only; no page, no socket, no send.

# PS-Q35T WarRoom v2 WebSocket receiver-only client connect_fn registry surface hidden-record readback

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35S_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_NO_SEND_DONE
Slice: PS-Q35T_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_READBACK_HIDDEN_RECORD_READBACK_NO_SEND

## Decision

PS-Q35T introduces a metadata-only hidden readback for the Q35S session-state record. It reads only the known Q35S state key and returns status/boolean metadata. It does not return the raw hidden record value, session_state keys, raw Q35R/Q35Q packets, registry/runtime keys or values, registration key values, callable values, endpoint values, or token values.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback.py
hidden_record_readback_version=prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_readback.ps_q35t.v1
source_hidden_record_key=warroom_v2_ws_receiver_only_client_connect_fn_registry_surface_readback_hidden_record_q35s
requires_session_state_mapping=true
requires_allow_hidden_record_readback_flag=true
read_only=true
metadata_only=true
hidden_readback_diagnostic=true
raw_hidden_record_value_returned=false
raw_readback_packet_recorded=false
raw_registry_surface_packet_returned=false
session_state_keys_returned=false
registry_values_returned=false
registry_keys_returned=false
runtime_config_values_returned=false
runtime_config_keys_returned=false
callable_values_returned=false
registration_key_value_returned=false
connect_fn_called_at_hidden_record_readback=false
target_session_state_mutated=false
state_mutated=false
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
1. Q35T receives a session_state mapping.
2. allow_hidden_record_readback must be true.
3. Q35T reads only the configured Q35S hidden record key.
4. Missing, non-mapping, or unrecognized hidden record values block readback.
5. Recognized Q35S hidden records produce only status/boolean metadata and a hidden readiness label.
6. Q35T never returns the raw hidden record value or session_state keys.
7. Q35T never calls connect_fn and never mutates session_state or global registry state.
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
- Missing allow_hidden_record_readback blocks readback.
- Missing, invalid, or unrecognized Q35S hidden record blocks readback.
- Valid Q35S hidden record produces metadata-only hidden readiness labels.
- Raw hidden record values and session_state keys are not returned.
- Readback does not call connect_fn or mutate session_state.
- No default network client, send path, WarRoom page change, aggregator export, or broker/order/ledger path is added.
```

## Next boundary

Q35U may introduce a compact hidden health summary that composes Q35T, but it must remain metadata-only/no-send and avoid page/export changes in the same slice.
