# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q25G_WARROOM_PREDICTION_ARTIFACT_HORIZON_FRESHNESS_EXPIRY_VISIBILITY_2026-06-30.md
# desc: PS-Q25G WarRoom prediction artifact horizon freshness/expiry visibility. Display-only; no producer cadence or scheduler change.
# PS-Q25G WarRoom prediction artifact horizon freshness and expiry visibility

Updated: 2026-06-30 JST
Base: PS-Q25F WarRoom Live Nowcast horizon readiness and prediction-input handoff
Mode: WarRoom prediction artifact expiry display / display-only / no writes / no AutoTrade / no broker

```text
ps_q25g_warroom_prediction_artifact_horizon_freshness_expiry_visibility=true
base_reentry=PS_Q25F_WARROOM_LIVE_NOWCAST_HORIZON_READINESS_PREDICTION_INPUT_HANDOFF_DONE
prediction_horizon_expiry_visibility_added=true
operator_visible_horizon_expiry=true
horizon_expiry_rows_visible=true
overall_horizon_expiry_state_visible=true
short_horizon_expired_or_stale_visible=true
horizon_15s_supported=true
horizon_60s_supported=true
horizon_300s_supported=true
horizon_900s_supported=true
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

Q25G makes artifact age vs selected prediction horizon visible. Short-horizon predictions can expire even while the UI panel is refreshing normally. This slice prevents old 15s/60s/300s/900s prediction rows from being mistaken as live tactical guidance.

## Safety

This slice is display-only. It does not change prediction producer cadence, scheduler, artifacts, AutoTrade, broker, ledger, mode, or parameters.
