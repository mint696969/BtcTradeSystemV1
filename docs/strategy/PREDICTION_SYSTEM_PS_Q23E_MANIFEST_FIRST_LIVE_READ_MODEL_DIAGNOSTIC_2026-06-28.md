# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23E_MANIFEST_FIRST_LIVE_READ_MODEL_DIAGNOSTIC_2026-06-28.md
# desc: PS-Q23E committed opt-in live diagnostic for manifest-first WarRoom read model adapter.
# PS-Q23E manifest-first live read-model diagnostic

Updated: 2026-06-28 JST
Base policy: PS-Q23D manifest-first adapter
Mode: committed opt-in diagnostic / read-only / no UI default switch

```text
ps_q23e_manifest_first_live_read_model_diagnostic=true
uses_q23d_manifest_first_adapter=true
ui_default_call_path_changed=false
compact_live_output=true
writes_d_hot_runtime_artifacts=false
broker_autotrade=false
```

## Purpose

PS-Q23E adds a committed diagnostic entry point for the PS-Q23D adapter:

```text
tools/diagnose_phase4a_prediction_system_ps_q23e_manifest_first_live_read_model.py
```

It reads D-hot through the manifest-first adapter and reports the selected source mode:

```text
source_artifact_mode = distributed | legacy_fallback | blocked
```

The output is intentionally compact. It does not dump forecast records.

## Selection semantics

The diagnostic follows the PS-Q23D adapter rule:

```text
distributed current enough -> distributed
distributed stale vs legacy latest -> legacy_fallback
distributed missing/invalid -> legacy_fallback when available
both unavailable -> blocked
```

## Safety

```text
read_only_diagnostic=true
latest_prediction_artifact_written=false
status_artifact_written=false
latest_manifest_written=false
run_sidecars_written=false
runtime_artifact_write_enabled=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
approval_or_ledger_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```

## Next step

After PS-Q23E is green, PS-Q23F can prepare scheduled dual-write integration so the distributed sidecars advance on every Q22S tick. That scheduled runtime artifact write change must remain explicitly gated.
