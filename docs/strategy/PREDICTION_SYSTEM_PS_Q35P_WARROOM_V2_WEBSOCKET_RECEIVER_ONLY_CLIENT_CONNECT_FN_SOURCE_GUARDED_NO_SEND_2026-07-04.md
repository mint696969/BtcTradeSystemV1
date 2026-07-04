# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35P_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_SOURCE_GUARDED_NO_SEND_2026-07-04.md
# desc: PS-Q35P WarRoom v2 WebSocket receiver-only client connect_fn source. Runtime-config callable source only; no default network client and no send.

# PS-Q35P WarRoom v2 WebSocket receiver-only client connect_fn source guarded no-send

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35O_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_NO_SEND_ADAPTER_IMPLEMENTATION_DONE
Slice: PS-Q35P_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_CONNECT_FN_SOURCE_GUARDED_NO_SEND

## Decision

PS-Q35P introduces a concrete source boundary for the Q35O low-level connect function. The source is still explicit runtime configuration: a callable stored under low_level_connect_fn or connect_fn. Q35P does not import a network library, does not create a default client, does not hardcode an endpoint, and does not send messages.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_connect_fn_source.py
connect_fn_source_version=prediction_warroom.v2.transport.ws_receiver_only_client_connect_fn_source.ps_q35p.v1
composes_q35n_adapter_factory=true
composes_q35o_no_send_adapter=true
requires_runtime_config=true
requires_low_level_connect_fn_from_runtime_config=true
requires_allow_connect_fn_source_flag=true
requires_q35n_q35m_q35l_guards=true
connect_fn_called_at_source_build=false
adapter_factory_created_only_after_source_allow_and_callable=true
runtime_config_values_returned=false
runtime_config_keys_returned=true
connect_fn_value_returned=false
callable_values_forwarded_to_adapter_runtime_config=false
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
1. Q35P reads runtime_config keys only and looks for low_level_connect_fn or connect_fn.
2. If allow_connect_fn_source is false, do not create an adapter factory.
3. If the connect function is missing or non-callable, do not create an adapter factory.
4. If source guards pass, build a Q35O adapter factory without calling connect_fn.
5. Strip callable values before forwarding runtime_config to Q35N/Q35O adapter runtime config.
6. Q35N still waits for preflight, endpoint, allow_adapter_factory, socket request, operator ack, and allow_socket_open.
7. Q35O still waits for embedded allow_adapter_open before calling connect_fn.
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
- Missing allow_connect_fn_source blocks adapter factory creation.
- Missing or non-callable connect_fn blocks adapter factory creation.
- Source build does not call connect_fn.
- Q35N socket guards block before adapter_factory and connect_fn.
- Q35O allow_adapter_open still blocks before connect_fn.
- With all Q35N/Q35M/Q35L and Q35O guards true, connect_fn is called exactly once.
- Runtime config values and callable values are not returned or forwarded to adapter runtime config.
- No default network client, send path, WarRoom page change, aggregator export, or broker/order/ledger path is added.
```

## Next boundary

Q35Q may introduce a non-network runtime registration surface for this source, but it must keep explicit operator/source/socket guards and avoid page/export changes in the same slice.
