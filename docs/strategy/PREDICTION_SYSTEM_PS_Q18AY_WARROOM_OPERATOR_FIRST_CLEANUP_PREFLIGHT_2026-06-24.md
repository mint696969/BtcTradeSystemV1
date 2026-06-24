# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18AY_WARROOM_OPERATOR_FIRST_CLEANUP_PREFLIGHT_2026-06-24.md
# desc: PS-Q18AY preflight for WarRoom operator-first cleanup and extensible future implementation preservation.
# PS-Q18AY WarRoom operator-first cleanup preflight

Updated: 2026-06-24 JST

## Purpose

PS-Q18AY defines the cleanup preflight for the current WarRoom tab after PS-Q18AX closed the latest prediction observation milestone.

This slice is docs/guard only. It does not change WarRoom rendering, does not delete code, does not enable real rendering, and does not touch execution or parameter systems.

## Human decision

The operator confirmed that development/debug/preflight information should not remain in the normal WarRoom UI if it is no longer useful for daily operation. However, reusable contracts and future implementation hooks must not be blindly deleted because prediction/WarRoom real rendering may be redesigned and implemented later.

## Cleanup goal

```text
warroom_cleanup_goal=operator_first_normal_ui_with_diagnostics_out_of_path
```

Normal WarRoom should prioritize:

```text
1. latest_prediction_quick_status
2. current_market_snapshot
3. warroom_alerts
4. ai_operator_compact_conclusion
5. optional_short_freshness_or_heartbeat_summary
```

Development/preflight details should move out of normal operator reading path before code pruning.

## Keep in normal UI

```text
latest_prediction_observation_quick_status
warroom_header_compact_market_snapshot
warroom_alert_summary
ai_operator_action_risk_mode_short_summary
bounded_refresh_heartbeat_short_status_if_needed
```

These are operator-facing and useful for situational awareness.

## Remove from normal UI path first

```text
prediction_warroom_real_payload_review
prediction_warroom_disabled_widget_skeleton_review
prediction_warroom_source_readiness_preflight
prediction_warroom_source_read_probe_status
prediction_warroom_latest_summary_props_candidate_status
prediction_warroom_latest_summary_render_disabled_packet_status
prediction_warroom_latest_summary_mapped_payload_details
prediction_warroom_legacy_safe_display_mount_details
long_warroom_reading_blocks_caption
long_summary_widget_semantic_contract_caption
long_ai_operator_explanation_context
```

Removal from normal UI path does not mean immediate physical deletion. It means the normal WarRoom render path should stop presenting these as operator-first content.

## Preserve for future implementation design

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

These are candidates to keep as specifications or reusable code because future real-render implementation may need them.

## Delete/prune only after reference audit

```text
rule_1=do_not_delete_component_modules_without_reference_audit
rule_2=remove_warroom_page_imports_helpers_after_normal_ui_path_is_cleaned
rule_3=delete_component_files_only_if_runtime_path_false_and_reference_count_zero_or_docs_only_archive_confirmed
rule_4=preserve_extension_contracts_in_docs_even_when_ui_path_is removed
```

## Proposed next slices

```text
PS-Q18AZ: WarRoom operator-first render path cleanup
PS-Q18BA: WarRoom legacy prediction dev helper/import prune
PS-Q18BB: legacy component reference audit and archive/delete decision
```

## Relative task weight

```text
PS-Q18AY preflight=low
PS-Q18AZ render path cleanup=medium
PS-Q18BA warroom_page code prune=medium_high
PS-Q18BB component delete/archive audit=high
future_real_render_gate_design=medium_high
future_real_render_enablement=high
```

## Safety boundary retained

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

## Next

Next safe slice: PS-Q18AZ WarRoom operator-first render path cleanup. It should remove development/preflight sections from the normal WarRoom render path while keeping reusable implementation contracts available for future design.
