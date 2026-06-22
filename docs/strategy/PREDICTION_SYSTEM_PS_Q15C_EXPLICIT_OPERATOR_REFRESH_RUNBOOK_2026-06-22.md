# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q15C_EXPLICIT_OPERATOR_REFRESH_RUNBOOK_2026-06-22.md
# desc: Explicit human-controlled operator-shell refresh runbook for stale WarRoom latest prediction artifact.
# Prediction System PS-Q15C Explicit Operator Refresh Runbook

Updated: 2026-06-22 JST
Status: runbook / guard-only candidate
Branch: docs/phase2-handoff-sync
Head at runbook candidate: 50ff7231

## Purpose

PS-Q15A and PS-Q15B diagnosed why the WarRoom latest prediction source is blocked/not_ready.

```text
PS-Q15A primary_root_cause=latest_prediction_artifact_stale
PS-Q15B primary_conclusion=operator_shell_refresh_path_exists_but_is_not_scheduler
```

The existing latest artifact refresh path is an explicit operator-shell path, not a WarRoom UI trigger and not a scheduler. This runbook documents the exact safe manual refresh and validation sequence, but this runbook/guard does not execute export and does not write runtime artifacts.

## Current observed stale artifact

```text
path=D:\btc_ts_hot\prediction\latest_prediction_system_result.json
exists=true
size_bytes=2981055
generated_at=2026-06-21T21:49:47Z
mtime_utc=2026-06-21T21:49:48.058117Z
freshness_max_age_sec=3600
PS-Q15B observed age_sec≈38921
```

## Existing refresh path

```text
manual_operator_runner=tmp/work/ps_q12d_refresh_latest_prediction/run_ps_q12d_export_and_smoke.py
actual_export_runner=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_actual_export_runner.py
actual_export_runner_version=prediction_warroom_latest_payload_actual_export_runner.ps_q10h.v1
latest_payload_export_runner=btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_runner.py
latest_payload_export_runner_version=prediction_warroom_latest_payload_export_runner.ps_q9y.v1
warroom_page_export_runner_mounted=false
```

The manual operator runner invokes the existing PS-Q10H non-UI actual export runner and then reruns PS-Q12C WarRoom live inference smoke. It is not imported by WarRoom and does not add UI controls.

## Explicit human-controlled refresh command

Run this only when the human operator intentionally chooses to refresh the D-hot latest prediction artifact.

```powershell
cd C:\BtcTradeSystem

python .\tmp\work\ps_q12d_refresh_latest_prediction\run_ps_q12d_export_and_smoke.py
```

Expected safe success markers:

```text
stage=ps_q12d_refresh_latest_prediction_and_smoke
ok=true
export.runner_state=latest_payload_actual_export_runner_exported
export.target_file_written=true
export.safe_flags.warroom_page_mutation_allowed_false=true
export.safe_flags.warroom_panel_mutation_allowed_false=true
export.safe_flags.ui_controls_added_false=true
export.safe_flags.ui_triggered_runner_execution_false=true
export.safe_flags.approval_or_authorization_allowed_false=true
export.safe_flags.ledger_append_allowed_false=true
export.safe_flags.autotrade_trigger_allowed_false=true
export.safe_flags.broker_private_api_allowed_false=true
export.safe_flags.would_write_collector_state_false=true
export.safe_flags.would_send_to_broker_false=true
smoke.ok=true
smoke.adapter_state=latest_prediction_source_ready
smoke.actual_file_read_succeeded=true
smoke.payload_decode_succeeded=true
smoke.loaded_payload_count=1
smoke.review_packet_ready=true
smoke.session_state_updated=true
git_status_short_after=[]
```

## Post-refresh verification commands

```powershell
cd C:\BtcTradeSystem

python .\tools\check_phase4a_prediction_system_ps_q15a_source_readiness_root_cause.py

python .\tools\check_phase4a_prediction_system_ps_q15b_source_readiness_producer_path.py

python .\tools\check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke.py

git status --short
```

Expected post-refresh direction:

```text
PS-Q15A should no longer report latest_prediction_artifact_stale if the artifact mtime is fresh.
PS-Q12C smoke should report latest_prediction_source_ready with read/decode/review/session handoff ready.
PS-Q15B should still report operator_shell_refresh_path_exists_but_is_not_scheduler because the refresh path remains manual/operator-shell, not a scheduler.
git status should remain clean because the write is to D-hot runtime data, not repository source.
```

## What this runbook does not approve

```text
It does not approve WarRoom UI export controls.
It does not approve scheduler creation.
It does not approve repeated automatic refresh.
It does not approve freshness bypass.
It does not approve force-ready behavior.
It does not approve AutoTrade.
It does not approve broker/private API.
It does not approve mode/order execution.
It does not approve approval/decision/command ledger append.
It does not approve parameter apply.
It does not approve parameter staging write.
It does not approve silent live parameter mutation.
```

## Safety boundary

```text
runbook_only=true
guard_only=true
human_shell_action_required=true
warroom_ui_trigger=false
warroom_page_mutation=false
warroom_panel_mutation=false
ui_controls_added=false
approval_or_authorization_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_write_collector_state=false
would_send_to_broker=false
mode_apply_requested=false
order_placement_requested=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
silent_live_parameter_mutation_allowed=false
```

## Decision point after this runbook

```text
Option A: human explicitly runs the one-shot operator-shell refresh command and validates with PS-Q15A/PS-Q12C.
Option B: design a separate non-UI scheduled producer, with its own contract/guard, before any runtime write automation.
Option C: keep current state blocked/not_ready and continue read-only diagnostics.
```

This runbook does not choose A/B/C automatically.
