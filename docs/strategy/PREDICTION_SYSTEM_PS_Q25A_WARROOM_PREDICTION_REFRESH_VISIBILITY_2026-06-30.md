# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q25A_WARROOM_PREDICTION_REFRESH_VISIBILITY_2026-06-30.md
# desc: PS-Q25A WarRoom prediction refresh visibility. Display-only UI clarity for prediction data generated_at vs panel heartbeat.
# PS-Q25A WarRoom prediction refresh visibility

Updated: 2026-06-30 JST
Mode: WarRoom prediction display-only UI clarity / no runtime writes / no scheduler / no AutoTrade / no broker

```text
ps_q25a_warroom_prediction_refresh_visibility=true
base_reentry=PS_Q24N_AUTOTRADE_READ_ONLY_STATUS_PAGE_ACTUAL_PAGE_WIRING_GATE_AWAITING_HUMAN_DECISION_DONE
autotrade_page_py_modified=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_action_changed=false
scheduler_enabled=false
ledger_append=false
mode_apply=false
parameter_apply=false
warroom_prediction_panel_update_visibility_added=true
prediction_data_generated_at_visible=true
prediction_data_generated_at_jst_visible=true
panel_refresh_heartbeat_jst_visible=true
prediction_data_generation_and_panel_refresh_separated=true
fragment_flag_status_uses_actual_render_argument=true
```

## Purpose

Operator observation: WarRoom prediction appears not to update automatically.

D-hot evidence showed the prediction artifact itself is advancing on the producer cadence, while the UI heartbeat and prediction data generated_at were not clearly separated in the panel. This made the panel look stale even when either the panel heartbeat or the producer output was changing.

PS-Q25A adds a display-only visibility strip to separate:

```text
prediction_data_generated_at = prediction result changed only when producer writes a new artifact
panel_refresh_heartbeat = UI panel rerender heartbeat
```

## Safety

This slice does not enable or change any scheduler, runtime write, prediction artifact write, AutoTrade trigger, broker call, ledger append, mode apply, command surface, or parameter apply.
