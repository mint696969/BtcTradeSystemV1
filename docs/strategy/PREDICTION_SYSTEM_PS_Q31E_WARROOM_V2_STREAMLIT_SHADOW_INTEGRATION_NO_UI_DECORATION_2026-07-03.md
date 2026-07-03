# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31E_WARROOM_V2_STREAMLIT_SHADOW_INTEGRATION_NO_UI_DECORATION_2026-07-03.md
# desc: PS-Q31E WarRoom v2 Streamlit shadow integration without visible UI decoration or live transport enablement.

# PS-Q31E WarRoom v2 Streamlit shadow integration without UI decoration

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31D_WARROOM_V2_CONSUMER_STATE_DEDUP_REPLAY_HELPERS_DONE
Slice: PS-Q31E_WARROOM_V2_STREAMLIT_SHADOW_INTEGRATION_NO_UI_DECORATION

## Decision

PS-Q31E records an in-process shadow integration packet from the existing WarRoom Streamlit render path. It compares the current fragment-refresh posture with disabled transport frame, topic policy, and replay cursor contracts. It does not add visible UI decoration, open sockets, send messages, or replace Streamlit fragment refresh.

```text
shadow_integration_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/shadow_integration.py
warroom_page_shadow_state_key=warroom_v2_transport_shadow_integration_q31e
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
visible_ui_decoration_added=false
fragment_refresh_replaced=false
transport_enabled_default=false
websocket_enabled=false
sse_enabled=false
push_connected=false
runtime_connected=false
would_send_to_broker=false
```

## Shadow integration responsibility

`shadow_integration.py` owns only a hidden comparison packet. It is allowed to summarize current Streamlit fragment settings and disabled transport preparation state. It is not allowed to render UI, write artifacts, open sockets, or invoke prediction generation.

```text
input=current_warroom_fragment_summary,optional_q30g_messages,optional_consumer_state
output=hidden_shadow_integration_packet
stored_in=st.session_state[warroom_v2_transport_shadow_integration_q31e]
visible_rendering=false
streamlit_component_added=false
button_added=false
checkbox_added=false
metric_added=false
caption_added=false
```

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_opening_socket=true
not_sending_messages=true
not_starting_server=true
not_starting_client=true
not_replacing_streamlit_fragment_refresh=true
not_adding_visible_ui_decoration=true
not_invoking_prediction_generation=true
not_invoking_prediction_inference=true
not_invoking_classifier=true
not_connecting_runtime=true
not_connecting_broker=true
not_creating_order=true
not_appending_ledger=true
not_applying_mode=true
not_applying_parameter=true
```

## Acceptance criteria

```text
- shadow_integration.py exists and stays pure.
- WarRoom page records hidden shadow state only in session_state.
- Existing visible WarRoom layout remains unchanged.
- Shadow packet includes fragment summary, disabled frame, topic policy contract, and reconnect request shape.
- Prediction-card display updates remain in target scope.
- Prediction generation/inference remains out of scope.
- existing Q31D/Q31C/Q31B/Q31A/Q30G-Q30C guards remain green.
```
