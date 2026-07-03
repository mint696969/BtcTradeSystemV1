# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31I_WARROOM_V2_STREAMLIT_SHADOW_LOCAL_LOOP_OBSERVATION_NO_EXTERNAL_TRANSPORT_2026-07-03.md
# desc: PS-Q31I WarRoom v2 Streamlit hidden local-loop observation without external transport.

# PS-Q31I WarRoom v2 Streamlit hidden local-loop observation

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31H_WARROOM_V2_LOCAL_ONLY_TRUE_TRANSPORT_EXPERIMENT_DONE
Slice: PS-Q31I_WARROOM_V2_STREAMLIT_SHADOW_LOCAL_LOOP_OBSERVATION_NO_EXTERNAL_TRANSPORT

## Decision

PS-Q31I records the PS-Q31H local-only in-process transport experiment from the existing WarRoom Streamlit render path as hidden `session_state` observation only. It does not render UI, open sockets, send external messages, replace fragment refresh, or invoke prediction generation.

```text
observation_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/streamlit_observation.py
warroom_page_observation_state_key=warroom_v2_streamlit_local_loop_observation_q31i
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
local_loop_observed=true
message_emission_scope=in_process_return_value_only
external_message_send_enabled=false
websocket_enabled=false
sse_enabled=false
push_connected=false
runtime_connected=false
would_send_to_broker=false
visible_ui_decoration_added=false
fragment_refresh_replaced=false
```

## Observation responsibility

`streamlit_observation.py` owns only a hidden packet that combines the current fragment summary with a Q31H local-only experiment result. WarRoom page stores it in `st.session_state` without adding labels, metrics, captions, buttons, checkboxes, or components.

```text
messages_from_streamlit_path=[]
emitted_message_count_expected=0
local_loop_effective_observed=true
external_transport_scope=none
streamlit_visible_surface_changed=false
```

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_opening_socket=true
not_sending_external_messages=true
not_starting_server=true
not_starting_client=true
not_adding_visible_ui_decoration=true
not_replacing_streamlit_fragment_refresh=true
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
- streamlit_observation.py exists and stays pure.
- WarRoom page records hidden local-loop observation state only.
- Existing visible WarRoom layout remains unchanged.
- The hidden packet records Q31H local-only experiment result.
- The hidden packet emits zero messages by default from the Streamlit path.
- External transport flags remain false.
- Prediction-card display remains in target scope.
- Prediction generation/inference remains out of scope.
- existing Q31H-Q30C guards remain green.
```
