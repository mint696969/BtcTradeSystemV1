# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31P_WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_TO_VISIBLE_READ_ONLY_DIAGNOSTIC_GATE_2026-07-03.md
# desc: PS-Q31P WarRoom v2 visible read-only diagnostic gate from operator-review observation, without rendering UI.

# PS-Q31P WarRoom v2 operator-review observation to visible read-only diagnostic gate

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31O_WARROOM_V2_OPERATOR_REVIEW_PACKET_TO_HIDDEN_SESSION_STATE_NO_VISIBLE_UI_DONE
Slice: PS-Q31P_WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_TO_VISIBLE_READ_ONLY_DIAGNOSTIC_GATE

## Decision

PS-Q31P adds a pure diagnostic gate builder under `v2/transport/operator_diagnostic_gate.py`. It converts the Q31O hidden operator-review observation into a default-off, read-only diagnostic gate packet. This slice does not render the diagnostic panel; it only decides whether a future visible read-only diagnostic would be allowed after explicit operator request and read-only acknowledgement.

```text
diagnostic_gate_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_diagnostic_gate.py
input_observation=warroom_v2_operator_review_observation_packet
output_gate_packet=warroom_v2_operator_review_diagnostic_gate_packet
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
visible_diagnostic_default_enabled=false
visible_diagnostic_requested_default=false
operator_read_only_ack_default=false
visible_diagnostic_allowed_default=false
future_visible_diagnostic_read_only=true
gate_packet_only=true
gate_renders_ui=false
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

## Gate responsibility

`operator_diagnostic_gate.py` owns only pure permission/readiness normalization. It emits bounded review metadata and keeps actual rendering disabled in this slice.

```text
requested=false -> diagnostic_gate_hidden_default
requested=true,ack=false -> diagnostic_gate_blocked_read_only_ack_required
requested=true,ack=true -> diagnostic_gate_ready_visible_read_only_no_render_here
gate_row_action=diagnostic_inspect_read_only
row_executes_patch=false
row_renders_ui=false
```

## Non-goals

```text
not_rendering_visible_diagnostic=true
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
- operator_diagnostic_gate.py exists and stays pure.
- default request=false maps to diagnostic_gate_hidden_default.
- request=true without ack maps to diagnostic_gate_blocked_read_only_ack_required.
- request=true with ack maps to diagnostic_gate_ready_visible_read_only_no_render_here.
- gate rows preserve operator-review status and review row counts without rendering UI.
- gate output preserves external transport disabled flags.
- prediction-card display remains in target scope.
- prediction generation/inference remains out of scope.
- existing Q31O-Q30C guards remain green.
```
