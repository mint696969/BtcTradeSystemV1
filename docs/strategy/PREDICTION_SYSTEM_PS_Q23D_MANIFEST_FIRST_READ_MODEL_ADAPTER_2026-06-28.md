# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23D_MANIFEST_FIRST_READ_MODEL_ADAPTER_2026-06-28.md
# desc: PS-Q23D manifest-first read-model adapter for distributed prediction artifacts with freshness-aware legacy fallback.
# PS-Q23D manifest-first read-model adapter

Updated: 2026-06-28 JST
Base policy: PS-Q23 / PS-Q23B / PS-Q23C
Mode: read-only adapter; existing UI default remains unchanged

```text
ps_q23d_manifest_first_read_model_adapter=true
manifest_first_adapter_added=true
existing_legacy_loader_retained=true
ui_default_call_path_changed=false
freshness_arbitration_against_legacy_latest=true
writes_d_hot_runtime_artifacts=false
broker_autotrade=false
```

## Purpose

PS-Q23D adds a reusable manifest-first adapter to the WarRoom latest prediction read model module.

The existing legacy loader remains valid:

```text
load_latest_prediction_payload(...)
load_latest_prediction_warroom_read_model(...)
```

The new adapter is opt-in:

```text
load_latest_prediction_payload_status_manifest_first(...)
load_latest_prediction_warroom_read_model_manifest_first(...)
```

## Selection rule

```text
1. Try prediction/latest_manifest.json and distributed sidecars.
2. If distributed is valid and not older than legacy latest, select distributed.
3. If distributed is missing/invalid/stale versus legacy latest, select legacy latest.
4. Never silently return empty when fallback is available.
```

## Safety

```text
read_only=true
non_executing=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
ledger_append_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```

## Next step

After PS-Q23D is committed, PS-Q23E can wire this adapter into a selected diagnostic or UI read path behind a safe fallback/feature flag, then observe live behavior without removing legacy compatibility.
