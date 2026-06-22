# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q16E_OPERATOR_SHELL_MANUAL_REFRESH_SMOKE_2026-06-22.md
# desc: PS-Q16E operator-shell manual refresh wrapper/smoke for D-hot WarRoom realtime observation.
# Prediction System PS-Q16E Operator-Shell Manual Refresh Smoke

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: operator-shell wrapper/smoke only; no scheduler and no WarRoom UI trigger

## Purpose

PS-Q16E provides a human-run operator-shell command that uses PS-Q16D against D-hot and then verifies WarRoom observation paths.

```text
operator_shell_only=true
clean_tree_precheck=true
bounded_manual_refresh_runner=prediction_warroom_bounded_manual_refresh_runner.ps_q16d.v1
hot_root=D:\btc_ts_hot
latest_prediction_artifact_relative_path=prediction/latest_prediction_system_result.json
producer_status_artifact_relative_path=prediction/status/non_ui_scheduled_producer_status.json
```

## Human command after commit

```powershell
python .\tools\check_phase4a_prediction_system_ps_q16e_operator_shell_manual_refresh_smoke.py
```

The wrapper blocks before refresh when the repository working tree is dirty.

## Verifications after manual refresh

```text
refresh.runner_state=bounded_manual_refresh_exported_status_written
refresh.actual_export_runner_invoked=true
refresh.latest_prediction_artifact_written=true
refresh.status_artifact_written=true
source_smoke.ok=true
source_smoke.adapter_state=latest_prediction_source_ready
producer_status_panel.panel_state=producer_status_panel_loaded
producer_status_panel.payload_decode_succeeded=true
```

## Safety state

```text
scheduler_registered=false
scheduled_loop_enabled=false
warroom_ui_trigger_enabled=false
approval_or_ledger_or_autotrade_or_broker=false
parameter_apply_or_staging=false
freshness_bypass_added=false
force_ready_added=false
```

## Explicitly not in this slice

```text
scheduler_registration=false
scheduled_loop=false
WarRoom UI trigger=false
automation_enablement=false
parameter_apply=false
parameter_staging_write=false
approval_or_ledger_or_autotrade_or_broker=false
```

## Next safe slice

```text
PS-Q16F: scheduler enablement preflight guard and human decision checkpoint, still disabled until explicit human approval.
```
