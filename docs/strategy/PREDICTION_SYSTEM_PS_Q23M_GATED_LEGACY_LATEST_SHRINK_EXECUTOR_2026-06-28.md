# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23M_GATED_LEGACY_LATEST_SHRINK_EXECUTOR_2026-06-28.md
# desc: PS-Q23M gated no-default-write executor for shrinking legacy latest prediction artifact.
# PS-Q23M gated legacy latest shrink executor

Updated: 2026-06-28 JST
Base policy: PS-Q23L legacy widget refs retired / PS-Q23K shrink readiness
Mode: gated executor added; default is blocked no-write

```text
ps_q23m_gated_legacy_latest_shrink_executor=true
legacy_latest_shrink_default_blocked=true
legacy_latest_shrink_executed=false
explicit_confirmation_required=SHRINK_D_HOT_LEGACY_LATEST_TO_COMPACT_READ_MODEL_COMPAT_ONCE
backup_before_replace_required=true
compact_read_model_compatible_payload=true
scheduler_action_changed=false
runtime_artifact_write_changed=false
broker_autotrade=false
```

## Purpose

PS-Q23M adds the executor that can later shrink `prediction/latest_prediction_system_result.json` from the full monolithic payload into a compact, read-model-compatible legacy payload.

The executor is gated. Without the exact confirmation token and execution flags it must remain no-write.

## Compact legacy shape

The future compact legacy payload keeps enough data for the existing WarRoom read model fallback:

```text
forecast_batch.generated_at
forecast_batch.records[] selected compact records
read_only=true
non_executing=true
broker_execution_requested=false
command_ledger_append_requested=false
approval_append_requested=false
```

The compact payload is not intended to preserve all forecast records. The full record set remains in distributed sidecars referenced by `prediction/latest_manifest.json`.

## Safety boundaries

```text
legacy_latest_shrink_executed=false
latest_prediction_artifact_written=false
status_artifact_written=false
latest_manifest_written=false
run_sidecars_written=false
runtime_artifact_write_enabled=false
scheduler_action_changed=false
scheduler_enabled_by_this_tool=false
trigger_added=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
approval_or_ledger_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```
