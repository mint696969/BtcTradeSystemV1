# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19P_PERIODIC_PRODUCER_SCHEDULING_DECISION_2026-06-25.md
# desc: PS-Q19P design note for ACK-gated bounded foreground producer scheduling decision.
# PS-Q19P Periodic producer scheduling decision

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: f478738b

## Purpose

PS-Q19P decides whether the Prediction System can move from one-shot manual refresh to ACK-gated bounded foreground periodic producer observation.

This does not install a scheduler, daemon, Windows Task, service, WarRoom UI trigger, AutoTrade, broker, ledger, or parameter behavior.

```text
ps_q19p_periodic_producer_scheduling_decision=true
scheduling_decision_helper_added=true
allowed_mode=ack_gated_bounded_foreground_observation
scheduler_install_performed=false
scheduler_enabled=false
scheduled_loop_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
ui_triggered_runner_execution=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Decision gates

The helper reads the latest prediction artifact, producer status, and PS-Q19K gap audit. It allows a bounded foreground observation command only when:

```text
latest_prediction_artifact_readable=true
tier0_source_quality_warnings_present=false
context_profile_minimum_sources_missing=false
signal_strength_cap_reasons_absent=true
producer_consecutive_failure_count=0
scheduler_enabled=false
producer_enabled=false
lock_file_absent=true
```

## Operator command shape if allowed

```powershell
python .	oolsun_prediction_warroom_periodic_producer_ps_q19k.py `
  --root D:tc_ts_hot `
  --execute-periodic-producer `
  --ack PS_Q19K_RUN_BOUNDED_PERIODIC_PREDICTION_PRODUCER `
  --max-cycles 12 `
  --interval-sec 300
```

## Safety boundary

```text
read_only_decision_helper=true
runtime_artifact_write_performed_by_decision_helper=false
status_artifact_write_performed_by_decision_helper=false
scheduler_install_performed=false
scheduler_enabled=false
scheduled_loop_enabled=false
producer_enabled=false
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

The actual bounded producer still writes prediction/status artifacts only after the separate explicit PS-Q19K ACK command.
