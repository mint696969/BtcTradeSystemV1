# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q25T_SINGLE_PRODUCER_60S_DISABLED_IMPLEMENTATION_PREFLIGHT_2026-06-30.md
# desc: PS-Q25T single producer 60s disabled implementation preflight. Structural preflight only; no production code or runtime enablement.
# PS-Q25T single producer 60s disabled implementation preflight

Updated: 2026-06-30 JST
Base: PS-Q25S single producer 60s implementation planning
Mode: disabled-implementation-preflight-only / structural candidate mapping / no production code change / no scheduler / no writes

```text
ps_q25t_single_producer_60s_disabled_implementation_preflight=true
base_reentry=PS_Q25S_WARROOM_PREDICTION_SINGLE_PRODUCER_60S_IMPLEMENTATION_PLANNING_DONE
selected_option_id=single_producer_60s_candidate
selected_target_cadence_sec=60
disabled_implementation_preflight_added=true
preflight_only=true
structural_candidate_mapping_added=true
implementation_allowed_by_this_packet=false
production_code_changed=false
producer_cadence_changed=false
scheduler_action_changed=false
scheduler_enabled=false
producer_enabled=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
latest_manifest_written=false
run_sidecars_written=false
manual_one_shot_run_allowed=false
scheduler_enablement_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
```

## Structural candidate mapping

Q25T maps existing disabled-by-default components to the future 60s single producer path. It does not edit these files in this slice.

```text
future_disabled_runner_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_runner.py
future_bounded_manual_refresh_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_bounded_manual_refresh_runner.py
future_disabled_scheduler_wrapper_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py
future_disabled_once_run_checker_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_once_run_checker.py
future_guarded_once_run_plan_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py
future_status_panel_observer_candidate=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_status_panel.py
```

## Required future implementation shape

```text
default_enabled=false
scheduler_enabled_initially=false
producer_enabled_initially=false
runtime_artifact_write_initially=false
status_artifact_write_initially=false
latest_prediction_artifact_write_initially=false
warroom_ui_trigger=false
no_overlap_runs=true
single_run_lock_required=true
on_existing_lock=skip_and_report_status
status_visibility_required_before_enablement=true
rollback_disable_path_required=true
manual_one_shot_requires_separate_gate=true
scheduler_enablement_requires_separate_gate=true
```

## Future Q25U boundary

Q25U may add a disabled implementation preflight contract or narrow code skeleton only if it preserves:

```text
no scheduler registration
no scheduled loop
no automatic runtime writes
no latest_manifest write
no sidecar write
no WarRoom UI trigger
no AutoTrade trigger
no broker/private API
no ledger append
no mode apply
no parameter apply
```

Q25T itself is a stop point before code change.
