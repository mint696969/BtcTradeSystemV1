# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31S_WARROOM_V2_BIDIRECTIONAL_WEBSOCKET_AND_ORDER_INTENT_BOUNDARY_DESIGN_2026-07-03.md
# desc: PS-Q31S WarRoom v2 bidirectional WebSocket and OrderIntent boundary design. Contract only; no socket and no order send.

# PS-Q31S WarRoom v2 bidirectional WebSocket and OrderIntent boundary design

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31R_WARROOM_V2_OPERATOR_DIAGNOSTIC_PANEL_TO_HIDDEN_SESSION_STATE_NO_VISIBLE_UI_DONE
Slice: PS-Q31S_WARROOM_V2_BIDIRECTIONAL_WEBSOCKET_AND_ORDER_INTENT_BOUNDARY_DESIGN

## Decision

For a WarRoom where the operator can switch between human judgement and automatic trading, WebSocket push is the right long-term transport direction. The transport must be split into two responsibility planes:

```text
read_model_push_plane=server_to_warroom_ui
command_intent_plane=warroom_ui_or_autotrade_to_order_intent_gateway
```

The WarRoom display should receive low-latency state, market, chart, safety, and prediction-card updates through server push. Human trading and AutoTrade should not bypass the order logic. They should both submit a normalized intent into the same OrderIntent gateway path, then pass risk, mode, runtime, private-readiness, preview, ledger, and broker-send gates.

## Repository anchors

```text
autotrade_order_intent=btcts_next/src/btcts/autotrade/execution/intents.py::OrderIntent
manual_order_preview=btcts_next/src/btcts/autotrade/execution/order_preview.py::build_bitflyer_fx_manual_order_preview
autotrade_pipeline=btcts_next/src/btcts/autotrade/pipeline.py::run_shadow_paper_dry_run_vertical_slice
paper_ledger=btcts_next/src/btcts/autotrade/execution/paper_ledger.py
warroom_display_transport=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/
```

## Contract boundary

```text
websocket_direction_preferred=bidirectional
server_to_ui_display_push=true
ui_to_server_order_intent_future=true
autotrade_to_order_intent_future=true
human_and_autotrade_share_order_intent_gateway=true
warroom_page_places_orders_directly=false
warroom_widget_places_orders_directly=false
order_logic_responsibility=autotrade.execution.OrderIntent_gateway
manual_decision_source=human_operator
automatic_decision_source=autotrade_logic
mode_switch_required=true
mode_switch_mutual_exclusion_required=true
idempotency_key_required=true
risk_gate_required=true
private_readiness_required=true
ledger_required_before_broker_send=true
broker_send_disabled_in_this_slice=true
websocket_enabled=false
socket_opened=false
order_intent_submitted=false
would_send_to_broker=false
```

## Intended future flow

```text
WarRoom read-model event -> WebSocket display push -> widget update
Human operator decision -> command intent envelope -> OrderIntent gateway -> risk/readiness/preview/ledger -> broker gate
AutoTrade decision -> OrderIntent gateway -> risk/readiness/preview/ledger -> broker gate
```

The difference between human and automatic trading is the decision source, not the order path. Both sources must converge before execution.

## Non-goals

```text
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
not_mounting_new_ui=true
not_rendering_streamlit=true
```

## Acceptance criteria

```text
- bidirectional_order_boundary.py exists and stays pure.
- contract prefers bidirectional WebSocket as future transport.
- display push plane and order intent plane are separated.
- human and AutoTrade decision sources converge at one OrderIntent gateway.
- WarRoom page/widgets do not own order placement.
- mode switch, mutual exclusion, idempotency, risk gate, private readiness, and ledger gates are explicit.
- this slice enables no socket and sends no order.
- existing Q31R-Q30C guards remain green.
```
