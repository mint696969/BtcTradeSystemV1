# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31O_WARROOM_V2_OPERATOR_REVIEW_PACKET_TO_HIDDEN_SESSION_STATE_NO_VISIBLE_UI_2026-07-03.md
# desc: PS-Q31O WarRoom v2 hidden session_state operator-review observation without visible UI.

# PS-Q31O WarRoom v2 operator-review packet to hidden session state

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31N_WARROOM_V2_SHADOW_RENDERER_OBSERVATION_TO_OPERATOR_REVIEW_PACKET_NO_UI_SWITCH_DONE
Slice: PS-Q31O_WARROOM_V2_OPERATOR_REVIEW_PACKET_TO_HIDDEN_SESSION_STATE_NO_VISIBLE_UI

## Decision

PS-Q31O stores the Q31N operator-review packet in the existing WarRoom Streamlit render path as hidden `session_state` observation only. It composes the Q31M hidden shadow renderer observation and Q31N operator-review packet in a pure helper, then records the resulting packet. It does not render visible UI, execute patches, switch the WarRoom page path, open sockets, send external messages, or invoke prediction generation.

```text
observation_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_review_observation.py
warroom_page_observation_state_key=warroom_v2_operator_review_observation_q31o
input_pipeline=q31m_shadow_renderer_observation,q31n_operator_review_packet
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
streamlit_path_messages=[]
streamlit_path_review_row_count=0
operator_review_status_default=operator_review_idle_shadow_no_candidates
review_packet_only=true
review_renders_ui=false
shadow_renderer_only=true
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

`operator_review_observation.py` owns only hidden packet assembly. The WarRoom page stores it in `st.session_state` without adding labels, metrics, captions, buttons, checkboxes, or components.

```text
messages_from_streamlit_path=[]
operator_review_status_expected=operator_review_idle_shadow_no_candidates
review_row_count_expected=0
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
- operator_review_observation.py exists and stays pure.
- WarRoom page records hidden operator-review observation state only.
- Existing visible WarRoom layout remains unchanged.
- The default Streamlit path uses messages=[] and review_row_count=0.
- Review packet remains review-only and review_renders_ui=false.
- External transport flags remain false.
- Prediction-card display remains in target scope.
- Prediction generation/inference remains out of scope.
- existing Q31N-Q30C guards remain green.
```
