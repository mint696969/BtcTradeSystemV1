# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27Y_MARKET_REGIME_FORECAST_METRIC_CONFIDENCE_CALIBRATION_2026-07-02.md
# desc: PS-Q27Y market-regime confidence calibration from horizon-specific forecast metrics. No UI/runtime writes.
# PS-Q27Y Market-regime forecast metric confidence calibration

Updated: 2026-07-02 JST
Base: PS-Q27X D-hot horizon-specific preview verification
Mode: pure prediction core improvement / no UI change / no runtime artifact write / no scheduler or producer enablement / no trading guidance.

```text
ps_q27y_market_regime_forecast_metric_confidence_calibration=true
base_reentry=PS_Q27X_MARKET_REGIME_ENGINE_DHOT_HORIZON_SPECIFIC_PREVIEW_VERIFY_DONE
selected_lane=MARKET_REGIME_ENGINE_DHOT_PREVIEW_EVIDENCE_QUALITY_OR_CONFIDENCE_CALIBRATION
production_ui_code_changed=false
runtime_code_changed=false
market_regime_only=true
forecast_score_by_horizon_signal_added=true
forecast_signal_strength_by_horizon_signal_added=true
forecast_reference_hit_rate_by_horizon_signal_added=true
classifier_version=prediction.market_regime.regime_classifier.ps_q27y.v1
confidence_calibrated_from_forecast_metric=true
legacy_confidence_fallback_preserved=true
diagnostic_selected_forecast_metric_added=true
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

PS-Q27W made the market-regime label horizon-specific. PS-Q27Y makes confidence horizon-aware too when forecast metrics exist.

The feature bundle now exposes:

```text
market_regime_scores_by_horizon_sec
market_regime_signal_strength_percent_by_horizon_sec
market_regime_reference_hit_rate_percent_by_horizon_sec
```

The classifier uses these selected-horizon metrics only for confidence calibration. If they are absent, it preserves the earlier confidence fallback so older fixtures and missing-metric paths continue to behave safely.

## Non-goals

```text
not_changing_ui=true
not_changing_warroom_layout=true
not_writing_prediction_artifacts=true
not_writing_status_artifacts=true
not_enabling_scheduler_or_producer=true
not_adding_autotrade_or_broker_or_ledger_behavior=true
```
