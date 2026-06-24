# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19A_LOG_RESPONSIBILITY_AND_GIANT_FILE_GUARD_2026-06-25.md
# desc: PS-Q19A design gate for audit/telemetry responsibility split and hot giant audit file containment before WarRoom realtime prediction work.
# PS-Q19A Log responsibility and giant file guard

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 1ace155a

## Purpose

PS-Q19A is the required pre-roadmap gate before continuing WarRoom realtime prediction work.

The immediate operational concern is that the current hot audit file is too large for normal live operation and future WarRoom / prediction observation work.

```text
ps_q19a_log_responsibility_gate=true
giant_active_audit_file_observed=true
warroom_realtime_prediction_work_deferred_until_log_gate=true
runtime_behavior_changed=false
collector_behavior_changed=false
ui_code_changed=false
prediction_runtime_changed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Observed hot data facts

The hot/current root is D hot.

```text
hot_latest_live_root=D:/btc_ts_hot
active_audit_path=D:/btc_ts_hot/logs/audit.jsonl
active_audit_size_bytes_observed_over_13gb=true
active_audit_line_count_observed_over_14m=true
collector_unified_runtime_running_observed=true
```

Observed largest hot log files during this gate:

```text
D:/btc_ts_hot/logs/audit.jsonl ~= 13GB
D:/btc_ts_hot/logs/collector_vnext/archive_audit.jsonl ~= 0.94GB
D:/btc_ts_hot/logs/collector_vnext/unified_supervisor_audit.jsonl ~= 55KB
```

The active `logs/audit.jsonl` is currently serving both low-frequency audit and high-frequency telemetry-like records.

## Root cause classification

Current design issue:

```text
audit_responsibility_too_broad=true
high_frequency_success_events_written_to_audit=true
single_active_file_append_without_rotation=true
normal_mode_info_events_include_collector_success_telemetry=true
ui_and_derived_readers_must_not_depend_on_full_audit_scan=true
```

Representative high-frequency events that must not remain permanently routed to the primary audit stream:

```text
collector_vnext.unified.board_snapshot.completed
collector_vnext.unified.rest_trades.completed
collector_vnext.unified.ws_executions.message.received
collector_vnext.unified.ws_executions.trade.written
```

## Responsibility split contract

Target responsibilities:

```text
audit=important_low_frequency_human_and_safety_events
telemetry=high_frequency_collector_api_ws_latency_and_throughput_events
state=small_current_atomic_json_for_ui_and_guards
derived=bounded_ui_ready_aggregates
prediction=prediction_artifacts_status_and_warroom_read_models
raw_data=market_data_records_and_canonical_collector_outputs
```

Audit should keep:

```text
daemon_start_stop
mode_change
config_policy_change
error_warn_gap_resync_blocker
prediction_generation_success_failure_summary
prediction_stale_blocker_summary
operator_approval_decision
ledger_append
future_autotrade_gate_state_change
future_broker_execution_boundary_change
```

Telemetry should receive or aggregate:

```text
collector_success_per_poll
ws_message_received
ws_trade_written
latency_ms
rate_budget_utilization
throughput_counts
api_request_success_counts
```

State should expose small current files only:

```text
state/collector_vnext/*.json
prediction/status/*.json
derived/warroom/*.json
```

## Immediate active giant audit containment

This gate includes a guarded maintenance tool:

```text
tools/rotate_hot_audit_log_ps_q19a.py
```

The tool is designed to:

```text
acquire_same_style_audit_lock=true
require_explicit_ack=true
dry_run_default=true
move_active_audit_to_archive=true
create_new_small_active_audit=true
write_rotation_marker=true
avoid_delete_by_default=true
avoid_compress_by_default=true
allow_test_root_for_guard_only=true
```

Recommended operational action after this slice is applied and guards pass:

```text
1. run dry-run against D:/btc_ts_hot
2. if target/archive paths are correct, run execute with explicit ack
3. verify D:/btc_ts_hot/logs/audit.jsonl is small
4. verify archived file exists under D:/btc_ts_hot/logs/audit/archive/date=YYYY-MM-DD/
5. keep archived file until a separate retention/compression decision
```

This is containment, not the final responsibility split. It reduces the active giant file immediately while preserving evidence.


## Optional giant log deletion after containment

The operator may decide that old giant log files are resource waste and should be removed after containment. That is acceptable only for log artifacts, not raw market data, state, prediction artifacts, ledgers, or configuration.

This gate includes a second guarded maintenance tool:

```text
tools/prune_giant_log_candidates_ps_q19a.py
```

The pruning tool contract:

```text
prune_giant_log_candidates_tool_added=true
dry_run_default=true
require_explicit_delete_ack=true
active_hot_audit_delete_allowed=false
active_hot_audit_must_be_rotated_first=true
hot_archive_log_delete_allowed=true
cold_log_delete_allowed_with_include_cold=true
raw_market_data_delete_allowed=false
prediction_artifact_delete_allowed=false
state_artifact_delete_allowed=false
ledger_delete_allowed=false
compress_performed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

Recommended prune order:

```text
1. rotate active D:/btc_ts_hot/logs/audit.jsonl first
2. verify new active D:/btc_ts_hot/logs/audit.jsonl is small
3. run prune dry-run for D hot only
4. run prune dry-run with --include-cold for E cold logs
5. execute delete only after candidate list is acceptable
```

## Forbidden behavior in PS-Q19A

PS-Q19A must not change live trading or prediction behavior.

```text
collector_runtime_behavior_changed=false
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

## Next implementation slices

After PS-Q19A containment:

```text
PS-Q19B_AUDIT_TELEMETRY_SPLIT_MINIMAL
PS-Q19C_PREDICTION_WARROOM_READ_MODEL
PS-Q19D_WARROOM_REALTIME_PREDICTION_WIDGET_DISPLAY_ONLY
PS-Q19E_NON_UI_MANUAL_OR_SCHEDULED_REFRESH_GUARDED
```

PS-Q19B should modify runtime logging policy so high-frequency success events stop inflating the primary audit file.

WarRoom realtime prediction display should remain deferred until PS-Q19A containment is complete and PS-Q19B design boundaries are accepted.
