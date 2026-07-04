# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35O_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_NO_SEND_ADAPTER_IMPLEMENTATION_2026-07-04.md
# desc: PS-Q35O WarRoom v2 WebSocket receiver-only client no-send adapter implementation. Explicit low-level connect function injection only; no default network client and no send.

# PS-Q35O WarRoom v2 WebSocket receiver-only client no-send adapter implementation

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35N_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_ADAPTER_FACTORY_NO_SEND_DONE
Slice: PS-Q35O_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_NO_SEND_ADAPTER_IMPLEMENTATION

## Decision

PS-Q35O introduces an actual receiver-only no-send adapter wrapper behind the Q35N adapter factory boundary. It still does not import a websocket library, does not create a default network client, and does not hardcode an endpoint. It wraps an explicitly injected low-level connect function and exposes an opener callable compatible with Q35N/Q35M/Q35L.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_no_send_adapter.py
no_send_adapter_version=prediction_warroom.v2.transport.ws_receiver_only_client_no_send_adapter.ps_q35o.v1
requires_low_level_connect_fn=true
requires_endpoint_url=true
requires_allow_adapter_open_flag=true
low_level_connect_fn_injected_only=true
connect_called_only_on_adapter_open=true
adapter_open_allowed_only_after_allow_flag=true
factory_embeds_allow_adapter_open_from_runtime_config=true
factory_creation_connects=false
injected_adapter_factory_compatible=true
injected_opener_compatible=true
runtime_config_values_returned=false
runtime_config_keys_returned=true
connect_result_sanitized=true
endpoint_url_values_returned=false
no_hardcoded_endpoint=true
no_default_network_client=true
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
1. Q35O receives an injected low_level_connect_fn.
2. Q35O can build an adapter factory compatible with Q35N.
3. Factory creation does not connect.
4. Q35N calls factory only after preflight/endpoint/allow_adapter_factory/socket request/operator socket-open ack/allow_socket_open/factory guards pass.
5. Q35M/Q35L call the produced opener only after socket request/ack/allow guards pass.
6. Q35O adapter calls low_level_connect_fn(endpoint, config) once.
7. Connect result is sanitized before packet exposure.
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
- Missing connect_fn blocks adapter open.
- Missing allow_adapter_open blocks direct adapter open and Q35N factory-produced opener.
- Adapter factory creation does not connect.
- With Q35N/Q35M/Q35L guards true, injected low-level connect is called exactly once.
- Q35N preflight blocks before factory/connect calls.
- Runtime config raw values and sensitive connect result fields are not exposed.
- No default network client, send path, WarRoom page change, aggregator export, or broker/order/ledger path is added.
```

## Next boundary

Q35P may wire a concrete low-level connect function from runtime configuration, but it must keep no-send guarantees, avoid live-network tests, and avoid WarRoom page/export changes in the same slice.
