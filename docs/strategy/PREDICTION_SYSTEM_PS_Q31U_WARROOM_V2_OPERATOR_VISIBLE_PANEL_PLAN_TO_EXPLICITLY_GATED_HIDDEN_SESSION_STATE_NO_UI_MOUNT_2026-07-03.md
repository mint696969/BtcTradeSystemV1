# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31U_WARROOM_V2_OPERATOR_VISIBLE_PANEL_PLAN_TO_EXPLICITLY_GATED_HIDDEN_SESSION_STATE_NO_UI_MOUNT_2026-07-03.md
# desc: PS-Q31U WarRoom v2 hidden session_state operator visible panel plan observation. No UI mount and no socket.

# PS-Q31U WarRoom v2 operator visible panel plan to hidden session state

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31T_WARROOM_V2_HIDDEN_DIAGNOSTIC_OBSERVATION_TO_OPERATOR_VISIBLE_PANEL_PLAN_DEFAULT_OFF_DONE
Slice: PS-Q31U_WARROOM_V2_OPERATOR_VISIBLE_PANEL_PLAN_TO_EXPLICITLY_GATED_HIDDEN_SESSION_STATE_NO_UI_MOUNT

## Decision

PS-Q31U records the Q31T operator-visible panel plan in the WarRoom Streamlit render path as hidden `session_state` only. It preserves the WebSocket-first future transport premise and keeps the explicit request defaults off. This slice does not mount the panel, render visible UI, enable WebSocket, introduce polling/browser-reload alternatives, submit OrderIntent, append ledgers, apply mode/parameters, or send broker orders.

```text
observation_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_visible_panel_observation.py
state_key=warroom_v2_operator_visible_panel_observation_q31u
input_pipeline=q31r_operator_diagnostic_observation,q31s_bidirectional_order_boundary,q31t_operator_visible_panel_plan
websocket_first_future_transport=true
bidirectional_websocket_premise=true
no_polling_fallback_introduced=true
no_browser_timer_reload_introduced=true
streamlit_path_messages=[]
operator_visible_panel_requested_default=false
operator_read_only_ack_default=false
operator_visible_panel_allowed_default=false
operator_visible_panel_plan_status_default=operator_visible_panel_plan_hidden_default
plan_row_count_default=0
plan_packet_only=true
plan_mounts_into_warroom=false
plan_renders_ui=false
plan_visible_now=false
warroom_page_ui_switch=false
websocket_enabled=false
socket_opened=false
external_message_send_enabled=false
order_intent_submitted=false
broker_send_enabled=false
would_send_to_broker=false
```

## Observation responsibility

`operator_visible_panel_observation.py` owns only hidden packet assembly. The WarRoom page stores it in `st.session_state` without labels, metrics, captions, buttons, checkboxes, components, or diagnostic panel content.

## Non-goals

```text
not_mounting_panel_into_warroom=true
not_rendering_streamlit=true
not_rendering_visible_diagnostic=true
not_adding_visible_ui_decoration=true
not_using_polling_fallback=true
not_using_browser_timer_reload=true
not_enabling_websocket=true
not_opening_socket=true
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
- operator_visible_panel_observation.py exists and stays pure.
- WarRoom page records hidden operator visible panel observation state only.
- Existing visible WarRoom layout remains unchanged.
- Default Streamlit path uses messages=[] and explicit request defaults false.
- Plan status defaults to operator_visible_panel_plan_hidden_default.
- Plan preserves WebSocket-first premise and no polling/browser-reload alternatives.
- UI mount/render, socket, OrderIntent, broker, ledger, mode, and parameter effects remain false.
- existing Q31T-Q30C guards remain green.
```
