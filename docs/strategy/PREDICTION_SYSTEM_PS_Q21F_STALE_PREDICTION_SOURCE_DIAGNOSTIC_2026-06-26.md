# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21F_STALE_PREDICTION_SOURCE_DIAGNOSTIC_2026-06-26.md
# desc: PS-Q21F adds a read-only stdout diagnostic for stale WarRoom prediction source artifacts.
# PS-Q21F stale prediction source diagnostic

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: 449c56ae

## Purpose

PS-Q21A through PS-Q21E confirmed the WarRoom prediction panel is refreshing and now visibly separates panel liveness from prediction-data freshness. The manual UI smoke showed the panel heartbeat changes but prediction data remains stale. PS-Q21F adds a read-only stdout diagnostic for that condition.

```text
ps_q21f_stale_prediction_source_diagnostic=true
panel_refresh_liveness_not_same_as_prediction_data_freshness=true
latest_prediction_artifact_path=prediction/latest_prediction_system_result.json
producer_status_artifact_path=prediction/status/non_ui_scheduled_producer_status.json
default_hot_root=D:\btc_ts_hot
cold_archive_root_not_used_by_default=E:\btc_ts
read_only_diagnostic_only=true
```

## Current hot evidence

```text
latest_prediction_generated_at=2026-06-25T11:59:14Z
producer_state=manual_refresh_blocked_status_written
producer_enabled=false
scheduler_enabled=false
last_failure_at=2026-06-25T12:04:14Z
actual_export_runner_did_not_write_latest_prediction_artifact=true
source_mapping_blocked=true
market_overview_trust_or_interpretation_blocked=true
```

## Diagnostic behavior

```text
stdout_json_only=true
reads_latest_prediction_artifact=true
reads_non_ui_scheduled_producer_status=true
reports_latest_prediction_age_sec=true
reports_blockers_and_warnings=true
reports_next_recommended_action=true
```

## Safety boundary

```text
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
no_scheduler_enablement
no_producer_enablement
no_manual_refresh_execution
no_latest_prediction_artifact_write
no_status_artifact_write
no_warroom_ui_trigger
no_autotrade_or_broker_path
```

## Next likely action

Use the diagnostic result to decide the next implementation slice: source mapping / trust blocker repair before any scheduler or producer enablement.
