# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31R_WARROOM_V2_OPERATOR_DIAGNOSTIC_PANEL_TO_HIDDEN_SESSION_STATE_NO_VISIBLE_UI_2026-07-03.md
# desc: PS-Q31R WarRoom v2 hidden session_state operator diagnostic panel adapter observation without visible UI.

# PS-Q31R WarRoom v2 operator diagnostic panel adapter to hidden session state

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31Q_WARROOM_V2_OPERATOR_DIAGNOSTIC_GATE_TO_VISIBLE_READ_ONLY_PANEL_EXPLICITLY_DISABLED_BY_DEFAULT_DONE
Slice: PS-Q31R_WARROOM_V2_OPERATOR_DIAGNOSTIC_PANEL_TO_HIDDEN_SESSION_STATE_NO_VISIBLE_UI

## Decision

PS-Q31R stores the Q31Q operator diagnostic panel adapter packet in the existing WarRoom Streamlit render path as hidden `session_state` observation only. It composes the Q31O operator-review observation, Q31P diagnostic gate, and Q31Q diagnostic panel adapter in a pure helper, then records the resulting packet. It does not render visible UI, mount the diagnostic panel, execute patches, switch the WarRoom page path, open sockets, send external messages, or invoke prediction generation.

```text
observation_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_diagnostic_observation.py
warroom_page_observation_state_key=warroom_v2_operator_diagnostic_observation_q31r
input_pipeline=q31o_operator_review_observation,q31p_diagnostic_gate,q31q_diagnostic_panel_adapter
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
streamlit_path_messages=[]
streamlit_path_panel_row_count=0
visible_diagnostic_requested_default=false
operator_read_only_ack_default=false
diagnostic_panel_status_default=diagnostic_panel_disabled_hidden_default
panel_adapter_only=true
panel_mounts_into_warroom=false
panel_renders_ui=false
panel_visible_now=false
renderer_executes_patch=false
patch_execution_allowed=false
streamlit_render_allowed=false
warroom_page_ui_switch=false
broad_page_reload_required=false
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

`operator_diagnostic_observation.py` owns only hidden packet assembly. The WarRoom page stores it in `st.session_state` without adding labels, metrics, captions, buttons, checkboxes, components, or visible diagnostic content.

```text
messages_from_streamlit_path=[]
diagnostic_gate_status_expected=diagnostic_gate_hidden_default
diagnostic_panel_status_expected=diagnostic_panel_disabled_hidden_default
panel_row_count_expected=0
external_transport_scope=none
streamlit_visible_surface_changed=false
```

## Non-goals

```text
not_rendering_visible_diagnostic=true
not_mounting_panel_into_warroom=true
not_adding_visible_ui_decoration=true
not_enabling_websocket=true
not_enabling_sse=true
not_opening_socket=true
not_sending_external_messages=true
not_starting_server=true
not_starting_client=true
not_replacing_streamlit_fragment_refresh=true
not_switching_warroom_ui_path=true
not_executing_dom_patch=true
not_rendering_streamlit=true
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
- operator_diagnostic_observation.py exists and stays pure.
- WarRoom page records hidden operator diagnostic observation state only.
- Existing visible WarRoom layout remains unchanged.
- The default Streamlit path uses messages=[] and panel_row_count=0.
- Panel packet remains adapter-only and panel_renders_ui=false.
- External transport flags remain false.
- Prediction-card display remains in target scope.
- Prediction generation/inference remains out of scope.
- existing Q31Q-Q30C guards remain green.
```
