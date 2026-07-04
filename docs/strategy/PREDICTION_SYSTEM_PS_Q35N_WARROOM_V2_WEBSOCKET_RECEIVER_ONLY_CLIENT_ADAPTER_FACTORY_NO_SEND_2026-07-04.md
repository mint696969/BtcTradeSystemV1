# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35N_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_ADAPTER_FACTORY_NO_SEND_2026-07-04.md
# desc: PS-Q35N WarRoom v2 WebSocket receiver-only client adapter factory. Explicit runtime config and injected factory only; no default network client and no send.

# PS-Q35N WarRoom v2 WebSocket receiver-only client adapter factory no-send

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35M_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_RUNTIME_WIRING_NO_SEND_DONE
Slice: PS-Q35N_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_ADAPTER_FACTORY_NO_SEND

## Decision

PS-Q35N introduces an adapter factory boundary for receiver-only client runtime wiring. It still does not import a websocket library, does not create a default network client, and does not hardcode an endpoint. It accepts explicit runtime config and an injected adapter factory, then builds an injected opener only after Q35K preflight readiness, endpoint presence, and allow_adapter_factory are all true.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_adapter_factory.py
adapter_factory_version=prediction_warroom.v2.transport.ws_receiver_only_client_adapter_factory.ps_q35n.v1
composes_q35k_preflight=true
composes_q35m_runtime_wiring=true
requires_runtime_config=true
runtime_config_values_returned=false
runtime_config_keys_returned=true
requires_endpoint_url_from_runtime_config=true
requires_allow_adapter_factory_flag=true
requires_injected_adapter_factory=true
adapter_factory_called_only_after_preflight_ready=true
adapter_factory_called_only_after_endpoint_present=true
adapter_factory_called_only_after_allow_flag=true
injected_adapter_factory_only=true
injected_opener_only=true
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
1. Build Q35K preflight from compact_status_badge_packet and operator_scope_ack.
2. If preflight is not ready, do not call adapter_factory.
3. If endpoint_url is missing from runtime_config, do not call adapter_factory.
4. If allow_adapter_factory is false, do not call adapter_factory.
5. If adapter_factory is missing, do not continue.
6. Call injected adapter_factory once to obtain an opener callable.
7. Pass the opener into Q35M runtime wiring.
8. Q35M/Q35L apply socket request/ack/allow guards and may call opener once.
9. No message send is enabled at any layer.
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
```

## Acceptance criteria

```text
- Preflight not-ready prevents adapter_factory calls.
- Missing endpoint config prevents adapter_factory calls.
- Missing allow_adapter_factory prevents adapter_factory calls.
- With all Q35K/Q35M/Q35L guards true, injected factory is called once and produced opener is called once.
- Packet returns runtime config presence/keys only; raw runtime_config values are not returned.
- Factory exceptions and non-callable factory results are reported as packet data.
- No default network client, send path, WarRoom page change, aggregator export, or broker/order/ledger path is added.
```

## Next boundary

Q35O may introduce an actual adapter implementation behind this factory. Keep it no-send and avoid WarRoom page/export changes in the same slice.
