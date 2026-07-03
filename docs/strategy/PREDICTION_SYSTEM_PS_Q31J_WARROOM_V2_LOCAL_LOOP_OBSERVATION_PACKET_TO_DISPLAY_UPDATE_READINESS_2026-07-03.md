# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31J_WARROOM_V2_LOCAL_LOOP_OBSERVATION_PACKET_TO_DISPLAY_UPDATE_READINESS_2026-07-03.md
# desc: PS-Q31J WarRoom v2 display-update readiness read-model from hidden local-loop observation packet.

# PS-Q31J WarRoom v2 local-loop observation to display-update readiness

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31I_WARROOM_V2_STREAMLIT_SHADOW_LOCAL_LOOP_OBSERVATION_NO_EXTERNAL_TRANSPORT_DONE
Slice: PS-Q31J_WARROOM_V2_LOCAL_LOOP_OBSERVATION_PACKET_TO_DISPLAY_UPDATE_READINESS

## Decision

PS-Q31J adds a pure display-update readiness read-model under `v2/transport/readiness.py`. It converts the hidden Q31I local-loop observation packet into a deterministic readiness packet for future widget DOM-region updates. It does not render UI, open sockets, send external messages, replace fragment refresh, or invoke prediction generation.

```text
readiness_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/readiness.py
input_packet=warroom_v2_streamlit_local_loop_observation_packet
output_read_model=warroom_v2_display_update_readiness_packet
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
readiness_patch_unit=widget_dom_region
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

## Readiness responsibility

`readiness.py` owns only read-model normalization. It classifies whether a hidden local-loop observation has no display events yet, has widget-region display events ready, or is blocked. It also summarizes observed topics by surface.

```text
empty_streamlit_path_status=shadow_ready_no_display_events
non_empty_valid_outbox_status=display_events_ready_for_widget_dom_region
blocked_status=blocked_local_loop_not_ready
surface_summary=top_information,prediction_display,bottom_chart
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
- readiness.py exists and stays pure.
- empty Q31I Streamlit observation maps to shadow_ready_no_display_events.
- non-empty local-loop outbox maps to display_events_ready_for_widget_dom_region.
- blocked local-loop observation maps to blocked_local_loop_not_ready.
- readiness output preserves external transport disabled flags.
- prediction-card display remains in target scope.
- prediction generation/inference remains out of scope.
- existing Q31I-Q30C guards remain green.
```
