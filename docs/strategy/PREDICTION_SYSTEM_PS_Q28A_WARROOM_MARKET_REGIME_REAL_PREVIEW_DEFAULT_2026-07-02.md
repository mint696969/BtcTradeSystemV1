# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q28A_WARROOM_MARKET_REGIME_REAL_PREVIEW_DEFAULT_2026-07-02.md
# desc: PS-Q28A WarRoom market-regime real D-hot preview default. UI copy stable; read-only display only.
# PS-Q28A WarRoom market-regime real preview default

Updated: 2026-07-02 JST
Base: PS-Q27Z market-regime forecast metric evidence-quality calibration
Mode: production UI display policy change only; no copy addition; no runtime artifact write; no scheduler or producer enablement; no trading guidance.

```text
ps_q28a_warroom_market_regime_real_preview_default=true
base_reentry=PS_Q27Z_MARKET_REGIME_ENGINE_FORECAST_METRIC_EVIDENCE_QUALITY_CALIBRATION_DONE
selected_lane=MARKET_REGIME_ENGINE_UI_STABLE_REAL_PREVIEW_COMPLETION_AND_DEFAULT_POLICY
production_ui_code_changed=true
ui_copy_added=false
warroom_market_regime_real_preview_default_on=true
operator_can_disable_to_sample=true
classifier_version=prediction.market_regime.regime_classifier.ps_q27z.v1
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

Make the already-implemented market-regime logic visible by default in WarRoom. The existing short checkbox remains as an operator override to fall back to sample cards. No explanatory UI copy is added.

## Non-goals

```text
not_changing_card_layout=true
not_adding_ui_explanations=true
not_writing_prediction_artifacts=true
not_writing_status_artifacts=true
not_enabling_scheduler_or_producer=true
not_adding_autotrade_or_broker_or_ledger_behavior=true
```
