# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q25D_WARROOM_LIVE_NOWCAST_SOURCE_IMPORTANCE_SIGNAL_LAYERING_2026-06-30.md
# desc: PS-Q25D WarRoom Live Nowcast source importance and signal layering. Display-only current-state source weighting before prediction interpretation.
# PS-Q25D WarRoom Live Nowcast source importance and signal layering

Updated: 2026-06-30 JST
Base: PS-Q25C WarRoom Live Nowcast operator summary and attention classification
Mode: WarRoom current-state source layering / display-only / no writes / no AutoTrade / no broker

```text
ps_q25d_warroom_live_nowcast_source_importance_signal_layering=true
base_reentry=PS_Q25C_WARROOM_LIVE_NOWCAST_OPERATOR_SUMMARY_ATTENTION_CLASSIFICATION_DONE
warroom_live_nowcast_source_layering_added=true
source_importance_rows_visible=true
source_layer_summary_rows_visible=true
prediction_input_gate_visible=true
operator_read_order_visible=true
current_state_not_prediction=true
foundation_integrity_layer_supported=true
microstructure_now_layer_supported=true
trade_flow_now_layer_supported=true
operational_pressure_layer_supported=true
prediction_input_gate_layer_supported=true
current_nowcast_profile_supported=true
tactical_5m_profile_supported=true
tactical_15m_profile_supported=true
scenario_30m_1h_profile_supported=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_action_changed=false
scheduler_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
```

## Purpose

Q25D adds an explicit source-importance and signal-layering view on top of Q25B/Q25C nowcast. The operator can read which current-state sources matter first before any tactical or scenario prediction is interpreted.

Read order:

```text
foundation_integrity → microstructure_now → trade_flow_now → operational_pressure → prediction_input_gate
```

## Safety

This slice is display-only. It does not write artifacts, mutate scheduler settings, enable AutoTrade, call broker/private APIs, append ledgers, apply modes, or apply parameters.
