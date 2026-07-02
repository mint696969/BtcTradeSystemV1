# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27W_MARKET_REGIME_HORIZON_SPECIFIC_CLASSIFIER_2026-07-02.md
# desc: PS-Q27W market-regime horizon-specific classifier. Uses forecast_records horizon labels instead of one latest label for all horizons. No UI/runtime writes.
# PS-Q27W Market-regime horizon-specific classifier

Updated: 2026-07-02 JST
Base: PS-Q27U WarRoom market-regime detail density reduction
Mode: pure prediction core improvement / no UI change / no runtime artifact write / no scheduler or producer enablement / no trading guidance.

```text
ps_q27w_market_regime_horizon_specific_classifier=true
base_reentry=PS_Q27U_MARKET_REGIME_ENGINE_WARROOM_DETAIL_DENSITY_REDUCTION_DONE
selected_lane=MARKET_REGIME_ENGINE_HORIZON_SPECIFIC_CLASSIFIER
production_ui_code_changed=false
runtime_code_changed=false
market_regime_only=true
horizon_specific_labels_enabled=true
current_horizon_uses_shortest_forecast_label=true
exact_horizon_label_preferred=true
latest_label_fallback_preserved=true
diagnostic_selected_forecast_label_added=true
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

Before this slice, the classifier selected one latest market-regime label and reused it across all horizons. That made the WarRoom row visually useful but not yet horizon-specific.

This slice keeps the same data sources and safety boundaries, but preserves horizon labels from `forecast_records`:

```text
forecast_records[horizon_sec=300].primary_label -> 5分後
forecast_records[horizon_sec=900].primary_label -> 15分後
forecast_records[horizon_sec=21600].primary_label -> 6時間後
horizon_sec=0 -> shortest available forecast label
missing exact horizon -> latest label fallback
```

## Non-goals

```text
not_changing_ui=true
not_changing_warroom_layout=true
not_writing_prediction_artifacts=true
not_enabling_scheduler_or_producer=true
not_adding_autotrade_or_broker_or_ledger_behavior=true
```
