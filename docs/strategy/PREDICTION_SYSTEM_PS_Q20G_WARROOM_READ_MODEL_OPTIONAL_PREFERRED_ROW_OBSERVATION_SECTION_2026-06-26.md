# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q20G_WARROOM_READ_MODEL_OPTIONAL_PREFERRED_ROW_OBSERVATION_SECTION_2026-06-26.md
# desc: PS-Q20G optional read-only preferred-row observation section for latest prediction WarRoom read models.
# PS-Q20G WarRoom read-model optional preferred-row observation section

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: ecdc78cc

## Purpose

PS-Q20G adds a pure helper that can attach an optional preferred-row observation section to a copy of the latest prediction WarRoom read model. It does not change the existing read-model loader or runtime wiring.

```text
ps_q20g_warroom_read_model_optional_preferred_row_observation_section=true
optional_section=true
read_only_section=true
explicit_attach_required=true
uses_ps_q20e_preferred_row_adapter=true
uses_ps_q20f_binding_design=true
latest_prediction_warroom_read_model_loader_changed=false
existing_market_snapshot_replaced=false
existing_market_state_service_changed=false
existing_warroom_runtime_rewired=false
```

## Section contract

```text
section_key=preferred_row_adapter_observation
section_state=preferred_row_observation_section_ready when adapter is allowed and selected row exists
section_state=preferred_row_observation_section_not_attached when adapter packet is absent
section_state=preferred_row_observation_section_blocked when adapter is fail-closed
selected_row_summary=compact_display_safe_fields_only
selected_row_summary_market_uid_fallback=existing_market_snapshot
market_snapshot_replaced_by_preferred_row_observation=false
```

## Safety boundary

```text
read_only_section=true
optional_section=true
additive_only=true
explicit_attach_required=true
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
no_loader_wiring
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
PS-Q20H_READ_ONLY_LOADER_BINDING_DRY_RUN_CONTRACT
```

Only after this section helper is verified should a future slice consider a dry-run loader binding contract. Do not enable runtime UI, producer, scheduler, artifact writes, AutoTrade, broker/private API, or PS-Q19R scoring changes.
