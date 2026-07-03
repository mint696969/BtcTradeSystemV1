# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31B_WARROOM_V2_DISABLED_TRANSPORT_SIMULATOR_CONTRACT_2026-07-03.md
# desc: PS-Q31B disabled in-process transport simulator contract for whole WarRoom v2 display updates.

# PS-Q31B WarRoom v2 disabled transport simulator contract

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31A_WARROOM_V2_TRUE_TRANSPORT_DESIGN_SPEC_DONE
Slice: PS-Q31B_WARROOM_V2_DISABLED_IN_PROCESS_TRANSPORT_SIMULATOR_CONTRACT

## Decision

PS-Q31B adds a disabled in-process transport simulator contract. It does not open sockets, send messages, start a server/client, touch Streamlit rendering, invoke prediction inference, or connect runtime/execution. It only frames existing Q30G outbound messages into a deterministic shadow frame for WarRoom v2 display widgets.

```text
disabled_in_process_transport_simulator=true
simulator_transport_enabled=false
simulator_sends_messages=false
simulator_opens_socket=false
websocket_enabled=false
sse_enabled=false
push_connected=false
runtime_connected=false
read_only=true
display_only=true
would_send_to_broker=false
classifier_invoked=false
prediction_generation_invoked=false
prediction_inference_invoked=false
```

## Target surfaces

The display-update goal includes the whole WarRoom tab: top information, prediction-card display widgets, scenario display text, and bottom chart. Prediction generation and inference remain out of scope.

```text
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
target_top_topics=warroom.current_state,warroom.alerts,warroom.safety,warroom.market.snapshot
target_prediction_display_topics=warroom.prediction.market_regime,warroom.prediction.trend_bias,warroom.prediction.reversal_zone,warroom.prediction.volatility_risk,warroom.prediction.liquidity_execution_quality,warroom.prediction.breakout_false_break,warroom.prediction.cross_venue_confirmation,warroom.prediction.human_technical_structure,warroom.prediction.scenario_ja
target_bottom_topics=warroom.chart.review
patch_unit=widget_dom_region
broad_page_reload_required=false
```

## Responsibility boundary

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/simulator.py
responsibility=disabled_in_process_shadow_frame_builder
schema_ownership=false
consumer_state_ownership=false
replay_ownership=false
ui_render_ownership=false
socket_lifecycle_ownership=false
prediction_generation_ownership=false
```

Future schema, topic policy, consumer state, replay, gates, and skeleton modules must remain separate under `v2/transport/`.

## Acceptance criteria

```text
- v2/transport/simulator.py exists and remains pure.
- simulator contract declares transport_enabled=false, websocket_enabled=false, sse_enabled=false.
- simulator accepts all WarRoom display topics, including prediction-card display topics.
- simulator does not invoke prediction generation, prediction inference, or classifier behavior.
- simulator preserves Q30G message payload shape and widget_dom_region patch unit.
- simulator produces deterministic in-process shadow frames only.
- existing Q30G-Q30C guard tests remain green.
```
