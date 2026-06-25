# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q20I_EXPLICIT_READ_ONLY_LOADER_BINDING_HELPER_DISABLED_BY_DEFAULT_2026-06-26.md
# desc: PS-Q20I explicit read-only loader binding helper disabled by default.
# PS-Q20I explicit read-only loader binding helper disabled by default

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: 3f702377

## Purpose

PS-Q20I adds an explicit read-only helper that can attach the PS-Q20G optional observation section to a supplied read-model copy only when the caller sets an explicit enable flag and PS-Q20H dry-run is ready. The helper is disabled by default and still does not invoke runtime loaders or read/write artifacts.

```text
ps_q20i_explicit_read_only_loader_binding_helper_disabled_by_default=true
explicit_helper_only=true
disabled_by_default=true
enable_explicit_read_only_loader_binding_default=false
supplied_mappings_only=true
target_loader_invoked=false
latest_prediction_artifact_read=false
latest_prediction_warroom_read_model_loader_changed=false
existing_market_snapshot_replaced=false
existing_market_state_service_changed=false
existing_warroom_runtime_rewired=false
```

## Helper contract

```text
default_state=explicit_read_only_loader_binding_helper_disabled
explicit_enabled_and_dry_run_ready=explicit_read_only_loader_binding_helper_attached
explicit_enabled_and_dry_run_not_ready=explicit_read_only_loader_binding_helper_blocked
optional_section_key=preferred_row_adapter_observation
attach_target=supplied_read_model_copy_only
original_read_model_mutated=false
market_snapshot_replaced=false
```

## Safety boundary

```text
read_only=true
non_executing=true
explicit_helper_only=true
disabled_by_default=true
supplied_mappings_only=true
target_loader_invoked=false
latest_prediction_artifact_read=false
latest_prediction_warroom_read_model_loader_changed=false
component_runtime_binding_allowed=false
ui_code_changed=false
warroom_ui_trigger_enabled=false
scheduler_enabled=false
producer_enabled=false
runtime_artifact_write_allowed=false
prediction_artifact_write_allowed=false
status_artifact_write_allowed=false
view_artifact_write_allowed=false
would_write_warroom_view_artifact=false
ps_q19r_scoring_policy_changed=false
collector_runtime_behavior_changed=false
market_state_writer_changed=false
approval_or_authorization_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```

## Non-goals

```text
no_loader_invocation
no_prediction_artifact_read
no_loader_rewire
no_default_binding
no_streamlit_or_ui_change
no_market_snapshot_replacement
no_market_state_service_change
no_scheduler_or_producer_enablement
no_artifact_write
no_ps_q19r_scoring_change
no_autotrade_or_broker_path
```

## Next likely slice

```text
PS-Q20J_DISABLED_HELPER_REAL_DATA_DRY_RUN_SAMPLE
```

Only after this disabled helper is verified should a future slice consider a real-data dry-run sample. Do not enable runtime UI, producer, scheduler, artifact writes, AutoTrade, broker/private API, or PS-Q19R scoring changes.
