# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q25H_WARROOM_PREDICTION_DATA_AGE_SEVERITY_OPERATOR_ACTION_GUIDANCE_2026-06-30.md
# desc: PS-Q25H WarRoom prediction data age severity and operator action guidance. Display-only; no producer cadence or scheduler change.
# PS-Q25H WarRoom prediction data age severity and operator action guidance

Updated: 2026-06-30 JST
Base: PS-Q25G WarRoom prediction artifact horizon freshness/expiry visibility
Mode: WarRoom prediction-age operator guidance / display-only / no writes / no AutoTrade / no broker

```text
ps_q25h_warroom_prediction_data_age_severity_operator_action_guidance=true
base_reentry=PS_Q25G_WARROOM_PREDICTION_ARTIFACT_HORIZON_FRESHNESS_EXPIRY_VISIBILITY_DONE
prediction_operator_action_guidance_added=true
operator_visible_action_guidance=true
operator_action_severity_visible=true
prediction_tactical_readiness_visible=true
ignore_live_tactical_horizons_visible=true
context_only_horizons_visible=true
wait_for_new_prediction_artifact_visible=true
do_not_confuse_ui_heartbeat_with_prediction_update_visible=true
producer_cadence_changed=false
scheduler_action_changed=false
scheduler_enabled=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
```

## Purpose

Q25H translates Q25G horizon expiry into operator action guidance: which horizons to ignore as live tactical guidance, which horizons are context-only, when to wait for a new prediction artifact, and why UI heartbeat must not be confused with prediction data generation.

## Safety

This slice is display-only. It does not change prediction producer cadence, scheduler, artifacts, AutoTrade, broker, ledger, mode, or parameters.
