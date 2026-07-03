# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31Q_WARROOM_V2_OPERATOR_DIAGNOSTIC_GATE_TO_VISIBLE_READ_ONLY_PANEL_EXPLICITLY_DISABLED_BY_DEFAULT_2026-07-03.md
# desc: PS-Q31Q WarRoom v2 visible read-only diagnostic panel adapter, explicitly disabled by default and without rendering UI.

# PS-Q31Q WarRoom v2 operator diagnostic gate to visible read-only panel adapter

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31P_WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_TO_VISIBLE_READ_ONLY_DIAGNOSTIC_GATE_DONE
Slice: PS-Q31Q_WARROOM_V2_OPERATOR_DIAGNOSTIC_GATE_TO_VISIBLE_READ_ONLY_PANEL_EXPLICITLY_DISABLED_BY_DEFAULT

## Decision

PS-Q31Q adds a pure diagnostic panel adapter under `v2/transport/operator_diagnostic_panel.py`. It converts the Q31P diagnostic gate packet into a bounded read-only panel adapter packet. The panel is explicitly disabled by default and this slice still does not render Streamlit UI, mount the panel into WarRoom, execute DOM patches, open sockets, send external messages, or invoke prediction generation.

```text
panel_adapter_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_diagnostic_panel.py
input_gate_packet=warroom_v2_operator_review_diagnostic_gate_packet
output_panel_packet=warroom_v2_operator_review_diagnostic_panel_adapter_packet
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
visible_panel_default_enabled=false
panel_requested_default=false
panel_allowed_default=false
panel_adapter_only=true
panel_mounts_into_warroom=false
panel_renders_ui=false
panel_visible_now=false
panel_read_only=true
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

## Adapter responsibility

`operator_diagnostic_panel.py` owns only panel packet normalization. It creates read-only panel sections and rows only when the upstream gate is ready, while preserving `panel_renders_ui=false` and `panel_mounts_into_warroom=false`.

```text
diagnostic_gate_hidden_default -> diagnostic_panel_disabled_hidden_default
diagnostic_gate_blocked_read_only_ack_required -> diagnostic_panel_blocked_read_only_ack_required
diagnostic_gate_ready_visible_read_only_no_render_here -> diagnostic_panel_ready_read_only_disabled_by_default
panel_row_action=present_read_only_diagnostic_row
panel_row_renders_ui=false
panel_row_executes_patch=false
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
- operator_diagnostic_panel.py exists and stays pure.
- hidden default gate maps to diagnostic_panel_disabled_hidden_default.
- blocked gate maps to diagnostic_panel_blocked_read_only_ack_required.
- ready gate maps to diagnostic_panel_ready_read_only_disabled_by_default.
- panel packet remains adapter-only and panel_renders_ui=false.
- WarRoom page is not changed in this slice.
- panel output preserves external transport disabled flags.
- prediction-card display remains in target scope.
- prediction generation/inference remains out of scope.
- existing Q31P-Q30C guards remain green.
```
