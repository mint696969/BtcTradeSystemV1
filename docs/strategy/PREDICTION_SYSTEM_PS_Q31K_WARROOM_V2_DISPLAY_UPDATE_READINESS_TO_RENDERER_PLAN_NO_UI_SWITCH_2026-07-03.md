# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31K_WARROOM_V2_DISPLAY_UPDATE_READINESS_TO_RENDERER_PLAN_NO_UI_SWITCH_2026-07-03.md
# desc: PS-Q31K WarRoom v2 renderer plan contract from display-update readiness, without UI switch.

# PS-Q31K WarRoom v2 display-update readiness to renderer plan

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31J_WARROOM_V2_LOCAL_LOOP_OBSERVATION_PACKET_TO_DISPLAY_UPDATE_READINESS_DONE
Slice: PS-Q31K_WARROOM_V2_DISPLAY_UPDATE_READINESS_TO_RENDERER_PLAN_NO_UI_SWITCH

## Decision

PS-Q31K adds a pure renderer plan contract under `v2/transport/renderer_plan.py`. It converts Q31J display-update readiness into a deterministic renderer plan for future widget DOM-region patching. It does not execute DOM patches, render Streamlit UI, switch the WarRoom page path, open sockets, send external messages, or invoke prediction generation.

```text
renderer_plan_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/renderer_plan.py
input_readiness_packet=warroom_v2_display_update_readiness_packet
output_plan=warroom_v2_renderer_plan_packet
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
renderer_patch_unit=widget_dom_region
renderer_executes_patch=false
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

## Renderer plan responsibility

`renderer_plan.py` owns only plan normalization. It classifies readiness into one of three plan statuses and prepares per-topic plan entries grouped by surface.

```text
shadow_ready_no_display_events -> renderer_plan_idle_shadow_ready
blocked_local_loop_not_ready -> renderer_plan_blocked
 display_events_ready_for_widget_dom_region -> renderer_plan_ready_no_ui_switch
plan_entry_action=prepare_widget_dom_region_patch
patch_execution_allowed=false
streamlit_render_allowed=false
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
- renderer_plan.py exists and stays pure.
- shadow_ready_no_display_events maps to renderer_plan_idle_shadow_ready.
- blocked_local_loop_not_ready maps to renderer_plan_blocked.
- display_events_ready_for_widget_dom_region maps to renderer_plan_ready_no_ui_switch.
- ready plan entries preserve surface/topic/patch_unit without executing patches.
- renderer output preserves external transport disabled flags.
- prediction-card display remains in target scope.
- prediction generation/inference remains out of scope.
- existing Q31J-Q30C guards remain green.
```
