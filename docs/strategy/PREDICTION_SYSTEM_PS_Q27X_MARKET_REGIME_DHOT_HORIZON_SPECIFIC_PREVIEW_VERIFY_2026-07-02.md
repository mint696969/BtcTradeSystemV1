# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27X_MARKET_REGIME_DHOT_HORIZON_SPECIFIC_PREVIEW_VERIFY_2026-07-02.md
# desc: PS-Q27X D-hot horizon-specific preview verification. Documentation/test/tmp-runner only; no production UI code change.
# PS-Q27X Market-regime D-hot horizon-specific preview verify

Updated: 2026-07-02 JST
Base: PS-Q27W market-regime horizon-specific classifier
Mode: documentation / test / tmp read-only probe runner only; no production UI code change; no runtime artifact write; no scheduler or producer enablement; no trading guidance.

```text
ps_q27x_market_regime_dhot_horizon_specific_preview_verify=true
base_reentry=PS_Q27W_MARKET_REGIME_ENGINE_HORIZON_SPECIFIC_CLASSIFIER_DONE
selected_lane=MARKET_REGIME_ENGINE_DHOT_HORIZON_SPECIFIC_REAL_PREVIEW_VERIFY
production_code_changed=false
production_ui_code_changed=false
runtime_code_changed=false
real_dhot_probe_runner_added=true
dhot_like_test_fixture_added=true
horizon_specific_dhot_preview_guard_added=true
classifier_version=prediction.market_regime.regime_classifier.ps_q27y.v1
market_regime_only=true
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

Verify that the current horizon-specific classifier works through the D-hot preview path before any further UI or artifact-writing work.

The test uses a D-hot-like fixture. The tmp runner can read real `D:\btc_ts_hot` explicitly and prints a compact JSON summary only.

## Expected verification

```text
latest_manifest_read=true
forecast_records_market_regime_labels_by_horizon_sec_built=true
classifier_stage_version=prediction.market_regime.regime_classifier.ps_q27y.v1
current_horizon_uses_shortest_forecast_label=true
exact_horizon_label_preferred=true
latest_label_fallback_preserved=true
warroom_preview_binding_stage_version_ps_q27y=true
would_send_to_broker=false
```

## Non-goals

```text
not_changing_ui=true
not_changing_warroom_layout=true
not_writing_prediction_artifacts=true
not_writing_status_artifacts=true
not_enabling_scheduler_or_producer=true
not_adding_autotrade_or_broker_or_ledger_behavior=true
```
