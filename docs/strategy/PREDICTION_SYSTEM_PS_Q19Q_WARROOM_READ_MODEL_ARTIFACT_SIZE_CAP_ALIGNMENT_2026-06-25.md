# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19Q_WARROOM_READ_MODEL_ARTIFACT_SIZE_CAP_ALIGNMENT_2026-06-25.md
# desc: PS-Q19Q design note for WarRoom read-model artifact size cap alignment after bounded producer observation.
# PS-Q19Q WarRoom read model artifact size cap alignment

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 383dd52e

## Problem

After PS-Q19P bounded foreground producer smoke, PS-Q19K produced valid latest prediction artifacts and PS-Q19K gap audit passed, but PS-Q19F WarRoom smoke reported the read model as blocked.

Root cause: the latest artifact grew slightly beyond the PS-Q19C read model's 5MB cap. The artifact still contains `forecast_batch`, but `load_latest_prediction_payload` returned `{}` because the file size exceeded `DEFAULT_MAX_ARTIFACT_BYTES`.

```text
ps_q19q_warroom_read_model_artifact_size_cap_alignment=true
root_cause=latest_prediction_artifact_exceeded_ps_q19c_read_model_max_bytes
old_read_model_max_bytes=5000000
new_read_model_max_bytes=12000000
forecast_batch_artifact_valid=true
producer_smoke_failed_warroom_read_model_due_to_cap=true
```

## Change

- Increase PS-Q19C read model max artifact bytes to 12MB.
- Add payload load diagnostics to the read model: artifact size, max bytes, load ok, blocked reason.
- Tighten PS-Q19F smoke so read model not-ready or zero prediction rows fail the smoke instead of passing only on display safety boundaries.

## Safety boundary

```text
read_only=true
non_executing=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
ui_triggered_runner_execution=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

No producer behavior, scheduler, UI trigger, AutoTrade, broker, ledger, or parameter behavior is added.
