# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23Q_SCHEDULED_TICK_COMPACT_LEGACY_AFTER_SIDECARS_2026-06-29.md
# desc: PS-Q23Q keep legacy latest compact after scheduled sidecar dual-write ticks.
# PS-Q23Q scheduled tick compact legacy after sidecars

Updated: 2026-06-29 JST
Base: PS-Q23O actual shrink showed one-time shrink is overwritten by next scheduled legacy writer
Mode: code fix / scheduled tick behavior / no scheduler action change

```text
ps_q23q_scheduled_tick_compact_legacy_after_sidecars=true
scheduled_sidecar_dual_write_required=true
compact_legacy_latest_after_sidecar=true
legacy_latest_backup_per_tick=false
latest_manifest_full_sidecars_retained=true
scheduler_action_changed=false
trigger_added=false
broker_autotrade=false
```

## Problem

PS-Q23O successfully shrank `prediction/latest_prediction_system_result.json` once, but the next recurring Q22S tick wrote a full monolithic legacy latest again. The single shrink was therefore not stable while the scheduled producer remained active.

## Fix

When Q22S runs with distributed sidecar dual-write enabled and the sidecar write succeeds, Q22S now compacts the legacy latest after sidecars are durable.

The scheduled tick order becomes:

```text
Q21I bounded full legacy latest refresh
Q22E status restore
Q23B distributed sidecar dual-write
Q23Q compact legacy latest fallback rewrite
```

The distributed sidecars remain the full source of truth. The compact legacy latest is a fallback compatibility artifact.

## Backup policy

PS-Q23Q does not create a backup on every scheduled tick. PS-Q23O already created a one-time pre-shrink backup, and full forecast records are preserved in sidecars for each run.

## Safety boundaries

```text
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
