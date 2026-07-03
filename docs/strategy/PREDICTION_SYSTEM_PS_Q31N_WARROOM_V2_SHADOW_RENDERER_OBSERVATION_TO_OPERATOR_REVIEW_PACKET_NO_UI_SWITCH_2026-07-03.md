# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31N_WARROOM_V2_SHADOW_RENDERER_OBSERVATION_TO_OPERATOR_REVIEW_PACKET_NO_UI_SWITCH_2026-07-03.md
# desc: PS-Q31N WarRoom v2 operator-review packet from hidden shadow renderer observation without UI switch.

# PS-Q31N WarRoom v2 shadow renderer observation to operator-review packet

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31M_WARROOM_V2_SHADOW_RENDERER_ADAPTER_TO_SESSION_OBSERVATION_NO_UI_SWITCH_DONE
Slice: PS-Q31N_WARROOM_V2_SHADOW_RENDERER_OBSERVATION_TO_OPERATOR_REVIEW_PACKET_NO_UI_SWITCH

## Decision

PS-Q31N adds a pure operator-review packet builder under `v2/transport/operator_review.py`. It converts the Q31M hidden shadow renderer observation into a compact operator-review packet for future inspection. It does not render UI, execute patches, switch the WarRoom page path, open sockets, send external messages, or invoke prediction generation.

```text
operator_review_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_review.py
input_observation=warroom_v2_shadow_renderer_observation_packet
output_review_packet=warroom_v2_operator_shadow_renderer_review_packet
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
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

## Review responsibility

`operator_review.py` owns only read-model summarization. It classifies hidden observation into idle, ready, or blocked review states and emits bounded rows for operator inspection in a future UI slice.

```text
shadow_renderer_idle -> operator_review_idle_shadow_no_candidates
shadow_renderer_ready_no_ui_switch -> operator_review_ready_shadow_candidates
shadow_renderer_blocked -> operator_review_blocked_shadow_renderer
review_row_action=inspect_shadow_candidate
review_row_executes_patch=false
review_row_renders_ui=false
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
- operator_review.py exists and stays pure.
- idle shadow observation maps to operator_review_idle_shadow_no_candidates.
- ready shadow observation maps to operator_review_ready_shadow_candidates.
- blocked shadow observation maps to operator_review_blocked_shadow_renderer.
- review rows preserve candidate topic/surface/patch_unit without executing patches.
- operator-review output preserves external transport disabled flags.
- prediction-card display remains in target scope.
- prediction generation/inference remains out of scope.
- existing Q31M-Q30C guards remain green.
```
