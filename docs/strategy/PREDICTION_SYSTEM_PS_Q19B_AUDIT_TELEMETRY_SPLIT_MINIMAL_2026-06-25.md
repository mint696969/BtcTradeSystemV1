# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19B_AUDIT_TELEMETRY_SPLIT_MINIMAL_2026-06-25.md
# desc: PS-Q19B minimal implementation gate for splitting high-frequency Collector telemetry from primary audit before resuming WarRoom realtime prediction work.
# PS-Q19B Audit / Telemetry split minimal

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: a3ccbf4e

## Purpose

PS-Q19B is the recurrence-prevention slice after PS-Q19A. PS-Q19A rotated and pruned the existing giant hot audit files. PS-Q19B prevents the same primary-audit giant-file pattern from returning while Collector remains in long-running endurance mode.

```text
ps_q19b_audit_telemetry_split_minimal=true
primary_audit_high_frequency_success_events_removed=true
collector_telemetry_writer_added=true
telemetry_date_partitioned=true
runtime_behavior_changed=false
collector_data_collection_changed=false
ui_code_changed=false
prediction_runtime_changed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Responsibility boundary

Primary audit is for low-frequency important events:

```text
start_stop
mode_change
warn_error
reconnect_or_gap
rate_control_engaged_released
future_operator_approval
future_ledger_append
future_autotrade_gate_state_change
future_broker_boundary_change
```

Telemetry is for high-frequency success chatter:

```text
collector_success_per_poll
ws_message_received
ws_trade_written
periodic_ws_board_heartbeat
archive_copy_progress_summary_when_info
```

## Implemented routing

The following events are routed away from `logs/audit.jsonl` into telemetry:

```text
collector_vnext.unified.board_snapshot.completed
collector_vnext.unified.rest_trades.completed
collector_vnext.unified.ws_board.message.received
collector_vnext.unified.ws_executions.message.received
collector_vnext.unified.ws_executions.trade.written
```

Telemetry path contract:

```text
logs/telemetry/collector_vnext/date=YYYY-MM-DD/part-00001.jsonl
```

Archive worker INFO progress events are routed away from `logs/collector_vnext/archive_audit.jsonl` into telemetry:

```text
archive.copy.begin
archive.copy.completed
archive.gc.begin
archive.gc.completed
archive.transfer_health_summary.updated when level=INFO
```

Archive telemetry path contract:

```text
logs/telemetry/collector_vnext_archive/date=YYYY-MM-DD/part-00001.jsonl
```

The archive audit file keeps start/stop, WARN, ERROR, exception, and any non-success control events.

## Safety boundary

This slice changes logging responsibility only. It does not change collected market data, state outputs, UI render behavior, prediction artifacts, AutoTrade, broker access, approval, ledger, parameter apply, or staging.

```text
runtime_behavior_changed=false
collector_data_collection_changed=false
collector_market_data_write_changed=false
raw_market_data_deleted=false
prediction_artifact_deleted=false
state_artifact_deleted=false
ui_code_changed=false
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

After PS-Q19B, the emergency log recurrence path is closed enough to resume the WarRoom realtime prediction roadmap. AutoTrade trigger work remains deferred.
