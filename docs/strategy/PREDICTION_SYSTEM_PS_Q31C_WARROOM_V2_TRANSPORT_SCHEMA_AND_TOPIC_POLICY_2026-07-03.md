# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31C_WARROOM_V2_TRANSPORT_SCHEMA_AND_TOPIC_POLICY_2026-07-03.md
# desc: PS-Q31C WarRoom v2 transport schema and topic policy split for whole-display seamless updates.

# PS-Q31C WarRoom v2 transport schema and topic policy

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31B_WARROOM_V2_DISABLED_TRANSPORT_SIMULATOR_CONTRACT_DONE
Slice: PS-Q31C_WARROOM_V2_TRANSPORT_SCHEMA_AND_TOPIC_POLICY

## Decision

PS-Q31C splits transport message schema and per-topic cadence/freshness policy into separate pure modules under `v2/transport/`. This keeps the true transport path reviewable before any WebSocket/SSE enablement.

```text
transport_schema_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/schema.py
topic_policy_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/topic_policy.py
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
classifier_invoked=false
transport_enabled_default=false
websocket_enabled=false
sse_enabled=false
push_connected=false
runtime_connected=false
would_send_to_broker=false
```

## Schema responsibility

`schema.py` owns only message-shape normalization and validation rules for WarRoom display update messages. It is compatible with the Q30G outbound payload contract and Q31B simulation frames.

```text
message_type=warroom_v2_widget_update
payload_kind=widget_update_event_envelope
patch_unit=widget_dom_region
broad_page_reload_required=false
read_only=true
display_only=true
prediction_generation_invoked=false
prediction_inference_invoked=false
would_send_to_broker=false
```

## Topic policy responsibility

`topic_policy.py` owns only display-topic classification, cadence hints, priority, freshness, and stale behavior. It covers the whole WarRoom display: top information, prediction-card display widgets, scenario display text, and bottom chart.

```text
policy_scope=whole_warroom_display
market_snapshot_update_class=fastest_safe
current_state_alerts_safety_update_class=high_priority_when_changed
prediction_card_display_update_class=evidence_change_or_moderate_frequency
scenario_text_display_update_class=evidence_change_or_moderate_frequency
chart_review_update_class=medium_or_operator_opt_in
prediction_generation_out_of_scope=true
```

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_opening_socket=true
not_sending_messages=true
not_starting_server=true
not_starting_client=true
not_touching_streamlit_ui=true
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
- schema.py exists and stays pure.
- topic_policy.py exists and stays pure.
- schema contract preserves Q30G message shape and disabled boundaries.
- topic policy covers every WARROOM_V2_WIDGET_TOPICS topic.
- prediction card topics are display-update targets, not prediction-generation targets.
- simulator remains focused on shadow-frame building.
- existing Q31B/Q31A/Q30G-Q30C guards remain green.
```
