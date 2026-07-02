# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27Z_MARKET_REGIME_FORECAST_METRIC_EVIDENCE_QUALITY_CALIBRATION_2026-07-02.md
# desc: PS-Q27Z market-regime evidence-quality calibration from selected horizon forecast metrics. No UI/runtime writes.
# PS-Q27Z Market-regime forecast metric evidence-quality calibration

Updated: 2026-07-02 JST
Base: PS-Q27Y market-regime forecast metric confidence calibration
Mode: pure prediction core improvement / no UI change / no runtime artifact write / no scheduler or producer enablement / no trading guidance.

```text
ps_q27z_market_regime_forecast_metric_evidence_quality_calibration=true
base_reentry=PS_Q27Y_MARKET_REGIME_ENGINE_FORECAST_METRIC_CONFIDENCE_CALIBRATION_DONE
selected_lane=MARKET_REGIME_ENGINE_DHOT_PREVIEW_EVIDENCE_QUALITY_CALIBRATION
production_ui_code_changed=false
runtime_code_changed=false
market_regime_only=true
classifier_version=prediction.market_regime.regime_classifier.ps_q27z.v1
evidence_quality_calibrated_from_forecast_metric=true
legacy_evidence_quality_fallback_preserved=true
diagnostic_selected_evidence_quality_reason_added=true
confidence_calibration_preserved=true
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

## Purpose

PS-Q27Y made confidence horizon-aware. PS-Q27Z applies the same selected-horizon forecast metrics to evidence quality, which is used by the card border semantics.

If selected-horizon forecast metrics are absent, the classifier preserves the earlier source-score/count fallback.

## Non-goals

```text
not_changing_ui=true
not_changing_warroom_layout=true
not_writing_prediction_artifacts=true
not_writing_status_artifacts=true
not_enabling_scheduler_or_producer=true
not_adding_autotrade_or_broker_or_ledger_behavior=true
```
