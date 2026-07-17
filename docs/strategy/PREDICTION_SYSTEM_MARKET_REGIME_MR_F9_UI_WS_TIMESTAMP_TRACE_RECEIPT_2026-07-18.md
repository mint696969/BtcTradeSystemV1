# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_UI_WS_TIMESTAMP_TRACE_RECEIPT_2026-07-18.md
# desc: Read-only MR-F9 producer/artifact/selection/transport/render timestamp trace receipt.

# MarketRegime MR-F9 UI/WS Timestamp Trace Receipt

Updated: 2026-07-18 JST
Status: accepted_with_limitation
Decision: PROCEED_TO_MR_F10_OFFLINE_DESIGN

<!-- MR_F9_UI_WS_TIMESTAMP_TRACE_RECEIPT_2026_07_18 -->

## Scope

This trace was performed read-only while the MR-F9 24-hour collection remained running. No producer, lease, D-hot artifact, UI inference, classifier, broker, AutoTrade, order, scheduler, or live parameter behavior was changed.

## Observed lanes

### Lane A — MR-F9 24-hour collection evidence

```text
source=prediction/market_regime/runtime_horizon_collections/collection_id=mr-f9-24h-fad90fe3ed0cf9805322
run_shape=prediction/market_regime/runtime_horizons/date=*/runs/run-*/
purpose=bounded multi-origin evidence and later outcome maturity
current_ui_card_direct_read=false
```

### Lane B — MarketRegime push selected read model

```text
topic=prediction.family.market_regime
selector=select_market_regime_read_model_source
selection_order=valid_push_then_valid_artifact_then_unavailable
prediction_timestamp=read_model.generated_at -> prediction_generated_at
transport_timestamp=message.received_at_ms -> transport_received_at_ms
source_merge=false
confidence_recalculation=false
prediction_invoked=false
classifier_invoked=false
```

Current page wiring calls the selector with push state only. It does not pass an artifact read model. The current D-hot WarRoom adapter emits market-state topics and does not emit `prediction.family.market_regime`.

### Lane C — actual WarRoom MarketRegime card rendering

```text
artifact=prediction/market_regime/latest_cards.json
observed_generated_at=2026-07-17T18:24:40Z
observed_run_id=market_regime_20260717T182440Z_once
observed_prediction_id=market_regime_20260717T182440Z_once:latest
renderer=render_rt_prediction_cards
artifact_read_only=true
ui_prediction_invoked=false
ui_classifier_invoked=false
```

The renderer first attempts the selected read-model bridge. When that bridge is unusable, it reads `latest_cards.json` directly and renders those cards. The observed card artifact is a separate once-style producer output, not an MR-F9 runtime-horizon collection run.

## Timestamp preservation findings

```text
push prediction generated_at is copied without regeneration
push transport received_at_ms is preserved through widget snapshot and selected source packet
latest_cards generated_at is read from artifact metadata
UI render may create a fallback current timestamp only when a packet lacks generated_at/source_generated_at/forecast_generated_at
no cross-source confidence merge occurs in the selected source adapter
no UI-side prediction or classifier execution occurs
```

## Limitation

A single end-to-end chain

```text
MR-F9 24h collection artifact
  -> selected common read model
  -> prediction.family.market_regime push packet
  -> WarRoom card
```

is not currently wired in the observed runtime. Therefore this receipt does not claim that the 24-hour collection artifact is visible in WarRoom cards.

## Decision

```text
decision=ACCEPTED_WITH_LIMITATION
MR_F10_OFFLINE_STABLE_CONTEXT_CONTRACT_DESIGN_ALLOWED=true
MR_F9_COLLECTION_MONITORING_REMAINS_ACTIVE=true
MR_F9_12_HOUR_CHECKPOINT_REMAINS_REQUIRED=true
MR_F9_UI_COLLECTION_INTEGRATION_FOLLOW_UP_REQUIRED=true
later_phase_start_does_not_close_earlier_open_items=true
```

The limitation is not a reason to stop the current collection. It is an integration follow-up to preserve explicitly through MR-F9 closeout.
