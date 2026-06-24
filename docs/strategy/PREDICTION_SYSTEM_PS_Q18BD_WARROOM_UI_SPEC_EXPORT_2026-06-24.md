# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18BD_WARROOM_UI_SPEC_EXPORT_2026-06-24.md
# desc: PS-Q18BD WarRoom UI specification export after cleanup close. Records current UI, preserved contracts, and future extension boundaries.
# PS-Q18BD WarRoom UI specification export

Updated: 2026-06-24 JST
Branch: docs/phase2-handoff-sync
Base clean head: 33ecc265

## Purpose

This document exports the current WarRoom UI specification after the PS-Q18AY-BD cleanup chain. It is intended as the stable handoff reference for the next thread and future prediction / real-render / AutoTrade gate design.

This slice is documentation and guard only.

```text
warroom_ui_spec_exported=true
runtime_behavior_changed=false
ui_code_changed=false
component_modules_deleted=false
real_prediction_widget_rendering_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
```

## Current WarRoom UI state

The normal WarRoom tab is now operator-first and compact.

```text
warroom_cleanup_optimization_complete=true
normal_ui_operator_first=true
warroom_header_normal_ui_compact=true
development_preflight_sections_removed_from_normal_ui=true
warroom_page_legacy_helpers_pruned=true
component_module_delete_deferred_by_reference_audit=true
```

Visible normal UI priorities:

```text
1. compact market/header state
2. WarRoom alerts
3. AI Operator compact conclusion
4. latest prediction observation quick status
5. standard operational widgets such as market/regime/flow/risk/watch/timeline panels
```

Removed from normal UI path:

```text
Prediction WarRoom real payload review
Prediction WarRoom disabled widget skeleton review
Prediction WarRoom source readiness preflight
Prediction WarRoom source read probe status
Prediction WarRoom latest summary props candidate status
Prediction WarRoom latest summary render-disabled packet status
Prediction WarRoom latest summary mapped payload render-disabled packet status
Prediction WarRoom latest summary mapped payload values
Prediction WarRoom latest summary operator value summary
Prediction WarRoom latest summary real source handoff preflight
Prediction WarRoom latest summary safe display mount
Prediction WarRoom mount review
long WarRoom header market_reading caption
long WarRoom header operational_reading caption
long summary_widget diagnostic caption
```

## Current latest prediction observation lane

WarRoom can observe the latest prediction status through a compact quick status path, but real rendering is still blocked.

```text
latest_prediction_observation_status=ready_for_operator_review
manual_ui_smoke_result=pass
quick_status_visible=true
quick_status_searchable=true
refresh_heartbeat_advances=true
implementation_gate_review_result=blocked_not_ready_to_enable
real_rendering_enabled=false
component_runtime_binding_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
```

Known hot prediction source:

```text
hot_prediction_artifact=D:/btc_ts_hot/prediction/latest_prediction_system_result.json
forecast_batch.generated_at=2026-06-22T13:34:38Z
family_count=11
horizon_count=10
record_count=110
read_only=true
non_executing=true
would_send_to_broker=false
```

Freshness note:

```text
current_freshness_state=stale
safe_fallback_reason_codes=source_generated_at_stale
```

This means the UI can observe the source and safety state, but the artifact is not yet a live AutoTrade trigger source.

## Current safety boundary

The following are intentionally false and must remain false until an explicitly approved future design/implementation gate changes them.

```text
real_prediction_widget_rendering_allowed=false
real_prediction_widget_render_invoked=false
streamlit_real_widget_render_invoked=false
component_runtime_binding_allowed=false
component_props_bound_to_runtime=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Preserved contracts and reusable parts

The following were intentionally preserved because they may be useful for future real-render and AutoTrade gate design.

### Preserved high-level contracts

```text
latest_prediction_payload_contracts
payload_to_widget_props_mapping_contract
latest_prediction_summary_widget_props_schema
bounded_refresh_packet_builder
freshness_fallback_packet_builder
real_render_implementation_gate_docs
rollback_to_skeleton_contract
manual_ui_smoke_contract_pattern
```

### Preserved prediction widget component family

```text
components/prediction_widgets/latest_prediction_summary_widget.py
components/prediction_widgets/prediction_delta_widget.py
components/prediction_widgets/scenario_trace_widget.py
components/prediction_widgets/evidence_weighting_widget.py
components/prediction_widgets/invalidation_rewrite_widget.py
components/prediction_widgets/source_quality_freshness_widget.py
components/prediction_widgets/warning_blocker_widget.py
components/prediction_widgets/signal_strength_calibration_widget.py
components/prediction_widgets/parameter_candidate_comparison_widget.py
components/prediction_widgets/replay_outcome_calibration_widget.py
components/prediction_widgets/producer_freshness_status_widget.py
components/prediction_widgets/runtime_boundary_safety_widget.py
```

These are not legacy trash. They are reusable real widget components or skeletons for a future prediction dashboard.

### Preserved future implementation contracts / panels

```text
prediction_warroom_latest_prediction_source_review_panel
prediction_warroom_realtime_review_preflight_panel
prediction_warroom_lowered_display_packet_visibility_review_panel
prediction_warroom_actual_review_packet_live_session_seed_page_mount
prediction_warroom_latest_prediction_summary_widget_props_candidate_status_panel
prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_status_panel
prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_panel
prediction_warroom_latest_prediction_summary_widget_mapped_payload_value_rows_panel
prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel
prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel
latest_prediction_summary_widget_q18ab_safe_display_mount_panel
latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel
```

These are deferred-delete / preserve-as-spec modules. Do not physically delete them until a future zero-reference audit either migrates their contract value into docs or proves they are safe to archive.

### Later archive/delete candidates only after zero-reference audit

```text
prediction_warroom_ui_mount_presenter
prediction_warroom_prediction_widgets_disabled_section_review_panel
prediction_warroom_prediction_widget_source_readiness_preflight_panel
prediction_warroom_prediction_widget_source_read_probe_status_panel
prediction_warroom_non_ui_scheduled_producer_status_panel
```

Deletion rule:

```text
rule_1=warroom_page refs must remain zero before deletion
rule_2=runtime/app routing refs must be zero before deletion
rule_3=component tests must be retired or migrated before module deletion
rule_4=contract value must be copied into docs/spec before module deletion
rule_5=prediction_widgets real component code must not be deleted by legacy cleanup
```

## Future roadmap from this UI state

Recommended next thread topic:

```text
PS-Q19A: Prediction real-render and AutoTrade trigger roadmap gate design
```

The next design should define:

```text
1. minimal prediction widgets to show in WarRoom
2. live/stale/warning/blocker freshness and quality rules
3. prediction record to trade intent candidate mapping
4. AutoTrade trigger candidate gate
5. staged approval / ledger / rollback / kill-switch requirements
6. bitFlyer FX-only execution boundary
```

Do not jump directly from observation to broker execution. The next correct step is a design gate.

## Current status summary

```text
WarRoom UI sorting and normal UI optimization=complete
latest prediction observation lane=complete for display-only status
real prediction widget rendering=not enabled
AutoTrade trigger integration=not enabled
broker/private API integration=not enabled
future contracts/components=preserved
next recommended slice=PS-Q19A design gate
```
