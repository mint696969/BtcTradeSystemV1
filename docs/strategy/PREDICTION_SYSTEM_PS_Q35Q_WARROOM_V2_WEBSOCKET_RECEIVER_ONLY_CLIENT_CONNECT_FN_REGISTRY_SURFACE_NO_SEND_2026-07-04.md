# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35Q_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_NO_SEND_2026-07-04.md
# desc: PS-Q35Q WarRoom v2 WebSocket receiver-only client connect_fn registry surface. Explicit in-memory mapping only; no default network client and no send.

# PS-Q35Q WarRoom v2 WebSocket receiver-only client connect_fn registry surface no-send

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35P_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_SOURCE_GUARDED_NO_SEND_DONE
Slice: PS-Q35Q_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_REGISTRY_SURFACE_NO_SEND

## Decision

PS-Q35Q introduces a non-network registration surface for Q35P. The surface accepts an explicit in-memory mapping of registration key to callable and a runtime_config key that selects one callable. It does not mutate a global registry, does not store callable values globally, does not import a network library, and does not send messages.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_registry_surface.py
connect_fn_registry_surface_version=prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_registry_surface.ps_q35q.v1
composes_q35p_connect_fn_source=true
requires_registry_mapping=true
requires_registration_key_from_runtime_config=true
requires_allow_registration_surface_flag=true
requires_allow_connect_fn_source_flag=true
registry_values_returned=false
callable_values_returned=false
callable_values_stored_globally=false
direct_connect_fn_from_runtime_config_ignored=true
global_registry_mutated=false
connect_fn_called_at_registration_surface=false
q35p_source_build_still_does_not_call_connect_fn=true
runtime_config_values_returned=false
runtime_config_keys_returned=true
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
1. Q35Q receives an explicit in-memory connect_fn_registry mapping.
2. Q35Q reads runtime_config connect_fn_registration_key/connect_fn_name/receiver_connect_fn_key.
3. If allow_registration_surface is false, do not resolve a callable.
4. Any direct low_level_connect_fn/connect_fn already present in runtime_config is stripped at the Q35Q boundary.
5. If the key is missing, not registered, or registered value is non-callable, Q35P receives no callable.
6. If Q35Q guards pass, inject low_level_connect_fn into a derived adapter runtime_config for Q35P.
7. Q35P still requires allow_connect_fn_source and does not call connect_fn during source build.
8. Q35N still waits for preflight, endpoint, allow_adapter_factory, socket request, operator ack, and allow_socket_open.
9. Q35O still waits for embedded allow_adapter_open before calling connect_fn.
10. No message send is enabled at any layer.
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
- Missing allow_registration_surface blocks registry resolution.
- Missing key, missing registration, and non-callable registration block before connect_fn.
- Registry surface does not call connect_fn.
- Direct low_level_connect_fn/connect_fn in runtime_config is ignored unless supplied by registry resolution.
- Q35P allow_connect_fn_source still blocks before adapter factory creation.
- Q35N socket guards block before adapter_factory and connect_fn.
- Q35O allow_adapter_open still blocks before connect_fn.
- With all Q35Q/Q35P/Q35N/Q35M/Q35L/Q35O guards true, registered connect_fn is called exactly once.
- Runtime config values, registry values, and callable values are not returned.
- No default network client, send path, WarRoom page change, aggregator export, or broker/order/ledger path is added.
```

## Next boundary

Q35R may introduce a runtime packet/readiness readback for the registry surface, but it must remain hidden/no-send and avoid page/export changes in the same slice.
