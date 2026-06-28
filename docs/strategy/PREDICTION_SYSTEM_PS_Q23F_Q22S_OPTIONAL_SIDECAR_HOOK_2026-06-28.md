# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23F_Q22S_OPTIONAL_SIDECAR_HOOK_2026-06-28.md
# desc: PS-Q23F optional Q22S sidecar dual-write hook, default disabled and not wired into scheduler.
# PS-Q23F Q22S optional sidecar hook

Updated: 2026-06-28 JST
Base policy: PS-Q23 distributed artifact migration
Mode: code integration prep only / default disabled / no scheduler action change

```text
ps_q23f_q22s_optional_sidecar_hook=true
q22s_sidecar_hook_added=true
sidecar_hook_default_disabled=true
exact_sidecar_confirmation_required=true
scheduler_action_changed=false
scheduled_sidecar_write_enabled=false
legacy_latest_refresh_semantics_preserved=true
broker_autotrade=false
```

## Purpose

PS-Q23F prepares Q22S for future scheduled distributed sidecar dual-write.

It adds an optional Q23B sidecar hook to Q22S. The hook runs only after the main Q22S refresh path succeeds and after the Q22S non-overlap lock has been released.

```text
Q21I latest/status refresh
Q22E status visibility restore
release Q22S lock
optional Q23B sidecar write
```

## Default behavior

Default Q22S behavior is unchanged:

```text
sidecar_dual_write_requested=false
sidecar_dual_write_executed=false
latest_manifest_written=false
run_sidecars_written=false
```

No Windows Task Scheduler action is changed in PS-Q23F.

## Gate

The optional hook requires:

```text
--enable-distributed-sidecar-dual-write
--distributed-sidecar-confirmation WRITE_D_HOT_DISTRIBUTED_PREDICTION_SIDECARS_ONCE
```

This is separate from the Q22S scheduler/tick token. Scheduled use still requires a later explicit scheduler action change gate.

## Failure policy

The sidecar hook is secondary to legacy prediction freshness. If the main Q22S tick succeeds but sidecar writing is blocked or fails, the Q22S result stays successful and reports:

```text
sidecar_dual_write_success=false
sidecar_dual_write_warning=true
```

Readers already have legacy fallback, so stale sidecars must not break the primary prediction refresh path.

## Safety boundaries

```text
scheduler_action_replacement_executed=false
scheduler_action_changed=false
trigger_added=false
scheduled_sidecar_write_enabled=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
approval_or_ledger_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```

## Next step

PS-Q23G can create a no-write scheduler action update plan/readiness check for adding the Q22S sidecar flags to the silent scheduled launcher. The actual scheduler action replacement remains a separate explicit boundary.
