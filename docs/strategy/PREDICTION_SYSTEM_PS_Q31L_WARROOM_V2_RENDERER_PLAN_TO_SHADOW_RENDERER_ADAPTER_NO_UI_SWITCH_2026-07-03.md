# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31L_WARROOM_V2_RENDERER_PLAN_TO_SHADOW_RENDERER_ADAPTER_NO_UI_SWITCH_2026-07-03.md
# desc: PS-Q31L WarRoom v2 shadow renderer adapter contract from renderer plan, without UI switch.

# PS-Q31L WarRoom v2 renderer plan to shadow renderer adapter

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31K_WARROOM_V2_DISPLAY_UPDATE_READINESS_TO_RENDERER_PLAN_NO_UI_SWITCH_DONE
Slice: PS-Q31L_WARROOM_V2_RENDERER_PLAN_TO_SHADOW_RENDERER_ADAPTER_NO_UI_SWITCH

## Decision

PS-Q31L adds a pure shadow renderer adapter under `v2/transport/shadow_renderer.py`. It converts Q31K renderer plan entries into shadow-only patch candidates for inspection. It does not execute patches, render Streamlit UI, switch the WarRoom page path, open sockets, send external messages, or invoke prediction generation.

```text
shadow_renderer_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/shadow_renderer.py
input_plan=warroom_v2_renderer_plan_packet
output_adapter_packet=warroom_v2_shadow_renderer_adapter_packet
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
shadow_candidate_patch_unit=widget_dom_region
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

## Adapter responsibility

`shadow_renderer.py` owns only shadow packet normalization. A ready renderer plan becomes `shadow_renderer_ready_no_ui_switch` with candidate rows. Idle and blocked plans stay non-rendering.

```text
renderer_plan_ready_no_ui_switch -> shadow_renderer_ready_no_ui_switch
renderer_plan_idle_shadow_ready -> shadow_renderer_idle
renderer_plan_blocked -> shadow_renderer_blocked
candidate_action=shadow_prepare_widget_dom_region_patch
candidate_executes_patch=false
candidate_streamlit_render_allowed=false
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
- shadow_renderer.py exists and stays pure.
- ready renderer plan maps to shadow_renderer_ready_no_ui_switch.
- idle renderer plan maps to shadow_renderer_idle.
- blocked renderer plan maps to shadow_renderer_blocked.
- candidate rows preserve surface/topic/patch_unit without executing patches.
- adapter output preserves external transport disabled flags.
- prediction-card display remains in target scope.
- prediction generation/inference remains out of scope.
- existing Q31K-Q30C guards remain green.
```
