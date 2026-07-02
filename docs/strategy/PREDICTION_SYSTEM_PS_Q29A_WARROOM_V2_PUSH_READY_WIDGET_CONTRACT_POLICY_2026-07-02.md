# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29A_WARROOM_V2_PUSH_READY_WIDGET_CONTRACT_POLICY_2026-07-02.md
# desc: PS-Q29A WarRoom v2 push-ready widget read-model contract policy.

# PS-Q29A WarRoom v2 push-ready widget read-model policy

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q28D_MARKET_REGIME_ENGINE_DISPLAY_COMPLETION_SIGNOFF_DONE
Slice: PS-Q29A_WARROOM_V2_PUSH_READY_WIDGET_READ_MODEL_CONTRACT

## Decision

Keep the current `warroom_page.py` as **WarRoom Legacy** for reference, diagnostics, and regression evidence.
Do not try to shrink it by deleting historical sections first.
Create WarRoom v2 as a new, operator-first, push-ready dashboard shape.

WarRoom v2 is a read-model consumer. It must not own artifact scanning, classifier invocation, cache invalidation, WebSocket/SSE source handling, broker behavior, ledger behavior, AutoTrade behavior, scheduler behavior, producer behavior, mode apply, or parameter apply.

## Target shape

```text
D-hot / prediction / collector artifacts
  -> artifact fingerprint or watcher
  -> WidgetUpdateEvent
  -> WidgetReadModel
  -> WebSocket/SSE or polling adapter
  -> WarRoom v2 widget
```

Only the event source should change later:

```text
current: poll/fingerprint check -> WidgetUpdateEvent
future: watcher/WebSocket/SSE -> WidgetUpdateEvent
```

## Folder responsibility

```text
prediction_warroom/v2/safety.py
  shared read-only/display-only/non-executing flags

prediction_warroom/v2/topics.py
  widget topic catalog and topic-level update unit

prediction_warroom/v2/contracts.py
  WidgetReadModel and WidgetUpdateEvent contracts

prediction_warroom/v2/layout_policy.py
  operator-first widget order and zones

prediction_warroom/market_regime/
  market-regime-specific adapters and probes remain separate

prediction_warroom/panels/
  Streamlit renderers only

views/warroom_page.py
  legacy page; keep as reference and avoid adding new ownership
```

## UI goal

WarRoom v2 should be visually simple:

```text
top mini bars:
  current state / safety / alerts

prediction card grid:
  market_regime
  trend_bias
  reversal_zone
  volatility_risk
  liquidity_execution_quality
  breakout_false_break
  cross_venue_confirmation
  human_technical_structure

card detail:
  balloon / overlay with sources, reasons, warnings, invalidation, freshness, model version

below cards:
  Japanese prediction scenario area

debug:
  raw and diagnostics collapsed by default
```

## Persistent operating rule

All later WarRoom work must preserve these rules:

```text
responsibility_separation_required=true
one_file_bloat_prevention_required=true
prefer_new_small_modules_over_warroom_page_growth=true
warroom_page_layout_shell_only=true
widget_read_model_consumer_only=true
widget_topic_update_unit=true
future_websocket_sse_compatible=true
legacy_warroom_retained_as_reference=true
```

## Non-goals

```text
not_rewriting_current_warroom_now=true
not_removing_legacy_sections_now=true
not_enabling_websocket_now=true
not_enabling_sse_now=true
not_reading_dhot_in_page=true
not_invoking_classifier_in_page=true
not_adding_broker_or_ledger_or_autotrade=true
not_enabling_scheduler_or_producer=true
not_writing_runtime_or_prediction_or_status_artifacts=true
```

## Safety flags

```text
read_only=true
display_only=true
non_executing=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
would_send_to_broker=false
```

## Acceptance criteria

```text
- v2 topic catalog exists and uses topic as widget update unit
- WidgetReadModel and WidgetUpdateEvent are Streamlit-independent
- layout policy places prediction scenario below prediction cards
- legacy WarRoom remains untouched
- no D-hot path read, classifier invocation, WebSocket/SSE runtime, broker, ledger, scheduler, producer, mode, or parameter behavior is added
- v2 files stay small and responsibility-separated
```
