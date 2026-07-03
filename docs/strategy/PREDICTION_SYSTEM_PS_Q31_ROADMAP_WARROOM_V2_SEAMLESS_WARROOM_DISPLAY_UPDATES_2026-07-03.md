# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31_ROADMAP_WARROOM_V2_SEAMLESS_WARROOM_DISPLAY_UPDATES_2026-07-03.md
# desc: Roadmap for WarRoom v2 seamless automatic display updates across the whole tab, while keeping prediction generation out of scope.

# PS-Q31 roadmap: seamless WarRoom v2 display updates

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31A_WARROOM_V2_TRUE_TRANSPORT_DESIGN_SPEC_DONE
Goal: seamless automatic display updates for the whole WarRoom tab

## Goal definition

The target state is a manual daytrade information board where WarRoom v2 updates all displayed surfaces with minimal perceived lag and without broad page reload.

This display-update goal includes prediction cards as display widgets. It does not include prediction generation, model inference, classifier invocation, scenario recalculation, AutoTrade, broker, order, ledger, mode, or parameter work.

```text
goal=seamless_warroom_display_updates
manual_daytrade_support=true
target_surfaces=top_information,prediction_cards,bottom_chart
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
primary_top_topics=warroom.current_state,warroom.alerts,warroom.safety,warroom.market.snapshot
primary_prediction_display_topics=warroom.prediction.market_regime,warroom.prediction.trend_bias,warroom.prediction.reversal_zone,warroom.prediction.volatility_risk,warroom.prediction.liquidity_execution_quality,warroom.prediction.breakout_false_break,warroom.prediction.cross_venue_confirmation,warroom.prediction.human_technical_structure,warroom.prediction.scenario_ja
primary_bottom_topics=warroom.chart.review
patch_unit=widget_dom_region
broad_page_reload_required=false
operator_decision_human_only=true
```

## Roadmap

```text
PS-Q31B: disabled in-process transport simulator contract
  Purpose: prove that Q30G outbound messages can be framed for all WarRoom display widgets without sockets.
  Enables: deterministic shadow frames for top information, prediction-card display payloads, scenario display text, and chart review.
  Still disabled: WebSocket, SSE, socket open, send, runtime, broker, classifier, prediction generation.

PS-Q31C: transport schema and topic policy modules
  Purpose: split schema and cadence/freshness policy under v2/transport/.
  Enables: per-topic update cadence for the whole WarRoom display.
  Does not do: prediction inference or prediction artifact generation.

PS-Q31D: consumer state, dedup, replay, and reconnect helpers
  Purpose: implement sequence/fingerprint state and replay cursor as pure helpers.
  Enables: idempotent widget-region update decisions across all display topics.

PS-Q31E: Streamlit shadow integration without UI decoration
  Purpose: compare current fragment refresh payloads with simulator frames in-process.
  Enables: confidence that displayed widgets can move independently.

PS-Q31F: local-only disabled producer/consumer skeleton behind flags
  Purpose: add lifecycle shape without opening sockets or sending events by default.
  Enables: operator-reviewed gate readiness.

PS-Q31G: operator-reviewed local transport enablement gate
  Purpose: decide SSE/WebSocket/local component path based on guards and observed latency.
  Enables: first local-only true transport experiment if explicitly approved.

PS-Q31H+: real transport implementation after explicit gate
  Purpose: replace or retire fragment refresh for WarRoom display widgets.
  Enables: seamless automatic display updates across the WarRoom tab.
```

## Non-negotiable constraints

```text
websocket_enabled=false until explicit accepted gate
sse_enabled=false until explicit accepted gate
transport_enabled_default=false
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
autotrade_allowed=false
broker_allowed=false
order_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
classifier_invoked=false
runtime_connected=false
would_send_to_broker=false
responsibility_separation_required=true
no_one_file_bloat=true
```
