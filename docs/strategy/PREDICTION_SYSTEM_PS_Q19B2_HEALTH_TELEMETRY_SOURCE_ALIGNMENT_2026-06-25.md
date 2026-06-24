# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19B2_HEALTH_TELEMETRY_SOURCE_ALIGNMENT_2026-06-25.md
# desc: PS-Q19B2 Health tab source alignment after audit/telemetry split.
# PS-Q19B2 Health telemetry source alignment

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 019ba218

## Purpose

PS-Q19B moved high-frequency Collector success events out of `logs/audit.jsonl` and into `logs/telemetry/collector_vnext/date=YYYY-MM-DD/part-00001.jsonl`. The Health tab still used an audit-tail read model for activity charts and continuity rails, which made the UI show stale / misleading coverage warnings after the split.

```text
ps_q19b2_health_telemetry_source_alignment=true
health_activity_source_uses_telemetry=true
health_primary_audit_no_longer_required_for_success_activity_graph=true
health_coverage_warning_label_updated=true
runtime_trading_behavior_changed=false
collector_data_collection_changed=false
ui_render_structure_changed=false
prediction_runtime_changed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Correct Health source rule

Primary audit is not the correct source for high-frequency success activity after PS-Q19B.

```text
health_activity_graph_source=bounded_health_event_input
bounded_health_event_input=audit_primary + telemetry_collector_vnext
telemetry_collector_vnext_path=logs/telemetry/collector_vnext/date=YYYY-MM-DD/part-00001.jsonl
audit_primary_path=logs/audit.jsonl
```

Health charts may use telemetry success events for activity counts. Health anomaly feeds may still use the same bounded input and filter down to WARN/ERROR/gap/resync/rate-mode rows.

## Safety boundary

This slice changes Operator UI read-model source alignment only. It does not change Collector runtime behavior, collected market data, state output, prediction artifacts, AutoTrade, broker access, approval, ledger, parameter apply, or staging.

```text
runtime_behavior_changed=false
runtime_trading_behavior_changed=false
collector_data_collection_changed=false
collector_market_data_write_changed=false
raw_market_data_deleted=false
prediction_artifact_deleted=false
state_artifact_deleted=false
ui_render_structure_changed=false
warroom_real_prediction_widget_enabled=false
real_prediction_widget_rendering_allowed=false
real_prediction_widget_render_invoked=false
streamlit_real_widget_render_invoked=false
component_runtime_binding_allowed=false
runtime_artifact_write_allowed=false
prediction_artifact_write_allowed=false
status_artifact_write_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Next recommended slice

```text
PS-Q19C_PREDICTION_WARROOM_READ_MODEL
```
