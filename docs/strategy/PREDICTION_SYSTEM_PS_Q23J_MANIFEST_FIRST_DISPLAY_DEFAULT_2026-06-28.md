# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23J_MANIFEST_FIRST_DISPLAY_DEFAULT_2026-06-28.md
# desc: PS-Q23J switch WarRoom latest prediction display default loader to manifest-first read model.
# PS-Q23J manifest-first display default

Updated: 2026-06-28 JST
Base policy: PS-Q23I post-switch closeout readiness
Mode: UI read-path default switch only

```text
ps_q23j_manifest_first_display_default=true
ui_display_default_loader_manifest_first=true
ui_display_default_hot_root=D:\btc_ts_hot
legacy_loader_retained=true
read_model_injection_compatibility_retained=true
scheduler_action_changed=false
runtime_artifact_write_changed=false
broker_autotrade=false
```

## Purpose

PS-Q23J changes the WarRoom latest prediction display panel default loader from the legacy monolithic latest artifact loader to the PS-Q23D manifest-first adapter.

When a caller supplies `read_model`, existing injection behavior is preserved. The default path only changes when the panel needs to load the model itself. The default panel load passes the live D-hot root (`D:\btc_ts_hot`) to the manifest-first adapter.

## Scope

```text
changed: latest_prediction_warroom_read_model_display_panel.py
not changed: scheduler action
not changed: Q22S / Q22X / Q23B writer
not changed: latest/status/manifest/sidecar artifacts
not changed: broker / AutoTrade / ledger / parameter
```

## Expected behavior

On D-hot after PS-Q23H/I:

```text
source_artifact_mode=distributed
source_artifact_relative_path=prediction/latest_manifest.json
distributed_stale_vs_legacy=false
legacy fallback still available in adapter
```

## Safety boundaries

```text
read_only=true
non_executing=true
display_only=true
scheduler_action_changed=false
scheduler_enabled_by_this_tool=false
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
