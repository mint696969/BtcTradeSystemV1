# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21G_SOURCE_MAPPING_TRUST_BLOCKER_DRILLDOWN_2026-06-26.md
# desc: PS-Q21G adds read-only stdout drilldown for source mapping and market overview trust blockers.
# PS-Q21G source mapping / trust blocker drilldown

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: c574082f

## Purpose

PS-Q21F showed that the latest prediction artifact is stale because the last bounded manual refresh was blocked. PS-Q21G drills down into the source mapping and market overview trust blockers using the existing bounded D-hot read-only probe path.

```text
ps_q21g_source_mapping_trust_blocker_drilldown=true
market_overview_trust_state_visible=true
market_overview_interpretation_bucket_visible=true
q9z_probe_readiness_visible=true
q10a_mapping_readiness_visible=true
read_only_diagnostic_only=true
```

## Diagnostic target blockers

```text
market_overview_trust_state_not_trusted
market_overview_interpretation_bucket_not_allow_structural_use
ps_q9z_probe_not_ready_for_future_prediction_source_mapping
source_mapping_runner_not_ready_for_prediction_system_result_builder
```

## Diagnostic behavior

```text
uses_existing_ps_q10b_source_mapping_probe_runner=true
bounded_hot_tail_read_only=true
hot_root_default=D:\btc_ts_hot
stdout_json_only=true
reports_market_overview_latest_part_path=true
reports_market_overview_latest_trust_state=true
reports_market_overview_latest_interpretation_bucket=true
reports_q9z_blockers=true
reports_q10a_blockers=true
reports_next_focus=true
```

## Safety boundary

```text
prediction_build_allowed=false
latest_prediction_artifact_export_allowed=false
runtime_enablement_allowed=false
scheduler_enablement_allowed=false
producer_enablement_allowed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Non-goals

```text
no_prediction_build
no_latest_prediction_artifact_write
no_status_artifact_write
no_scheduler_enablement
no_producer_enablement
no_warroom_ui_trigger
no_autotrade_or_broker_path
```

## Next likely action

Use the drilldown result to decide whether the next repair should target market overview row selection/trust state, or Q10A mapping readiness.
