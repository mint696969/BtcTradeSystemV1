# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19K_NON_UI_PERIODIC_PRODUCER_AND_SOURCE_QUALITY_GAP_AUDIT_2026-06-25.md
# desc: PS-Q19K design note for guarded non-UI periodic prediction producer and source-quality gap audit.
# PS-Q19K Non-UI periodic prediction producer and source-quality gap audit

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 821bb457

## Purpose

PS-Q19K moves from manual-only refresh toward automatic prediction generation, without touching AutoTrade or broker execution.

```text
ps_q19k_non_ui_periodic_producer_and_source_quality_gap_audit=true
periodic_producer_entrypoint_added=true
source_quality_gap_audit_added=true
q16d_bounded_refresh_runner_reused=true
default_dry_run_no_write=true
explicit_ack_required=true
periodic_producer_ack=PS_Q19K_RUN_BOUNDED_PERIODIC_PREDICTION_PRODUCER
bounded_periodic_loop_only=true
lock_file=prediction/status/periodic_producer_ps_q19k.lock
stop_file=prediction/status/stop_periodic_producer_ps_q19k.flag
scheduler_install_performed=false
scheduler_enabled=false
scheduled_loop_enabled=false
warroom_ui_trigger_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Operator command shape

Dry-run:

```powershell
python .\tools\run_prediction_warroom_periodic_producer_ps_q19k.py --root D:\btc_ts_hot
```

Bounded foreground producer loop, explicitly ACK gated:

```powershell
python .\tools\run_prediction_warroom_periodic_producer_ps_q19k.py `
  --root D:\btc_ts_hot `
  --execute-periodic-producer `
  --ack PS_Q19K_RUN_BOUNDED_PERIODIC_PREDICTION_PRODUCER `
  --max-cycles 12 `
  --interval-sec 300
```

Stop file path:

```text
D:/btc_ts_hot/prediction/status/stop_periodic_producer_ps_q19k.flag
```

Source-quality gap audit:

```powershell
python .\tools\check_prediction_source_quality_gaps_ps_q19k.py --root D:\btc_ts_hot
```

## Safety boundary

```text
read_only_gap_audit=true
runtime_artifact_write_performed_by_gap_audit=false
status_artifact_write_performed_by_gap_audit=false
scheduler_install_performed=false
scheduler_enabled=false
scheduled_loop_enabled=false
warroom_ui_trigger_enabled=false
ui_triggered_runner_execution=false
approval_or_authorization_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```

The periodic producer writes latest prediction and producer status artifacts only when explicitly ACKed and only through the existing Q16D bounded refresh runner. It does not install a scheduler or daemon.

## Next recommended slice

```text
PS-Q19L_SOURCE_QUALITY_INPUT_REPAIR
```

Use the gap audit output to repair missing or degraded evidence sources that cap prediction strength.
