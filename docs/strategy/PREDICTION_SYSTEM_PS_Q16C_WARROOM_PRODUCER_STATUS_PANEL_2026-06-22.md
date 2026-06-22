# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q16C_WARROOM_PRODUCER_STATUS_PANEL_2026-06-22.md
# desc: PS-Q16C WarRoom read-only producer status loader/panel for non-UI scheduled producer visibility.
# Prediction System PS-Q16C WarRoom Producer Status Panel

Updated: 2026-06-22 JST
Status: implementation + focused guard; not committed until GPT現物確認
Scope: WarRoom read-only observation of producer status artifact

## Purpose

PS-Q16C mounts read-only producer status visibility into the WarRoom prediction section.

It reads only:

```text
prediction/status/non_ui_scheduled_producer_status.json
```

It does not run the producer, enable scheduler, trigger from WarRoom UI, write status, write latest prediction artifact, apply/stage parameters, append ledgers, call broker/private APIs, or enable AutoTrade.

## WarRoom mount

```text
warroom_page_import=render_prediction_warroom_non_ui_scheduled_producer_status_panel
warroom_mount_section=Prediction WarRoom real payload review
warroom_mount_order=latest prediction source -> realtime review preflight -> producer status -> lowered display packet visibility
```

## Safety state

```text
read_only=true
non_executing=true
display_only=true
guarded_loader_only=true
warroom_ui_trigger_enabled=false
producer_runner_invoked=false
scheduler_enabled_by_this_panel=false
runtime_artifact_write_allowed=false
latest_prediction_artifact_write_allowed=false
status_artifact_write_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
```

## Missing status behavior

If the status artifact is missing, WarRoom shows:

```text
panel_state=producer_status_panel_missing
producer_status_artifact_missing=warning
force_ready=false
producer_runner_invoked=false
```

## Next safe slice

```text
PS-Q16D: bounded manual refresh runner that invokes the existing actual export runner under explicit operator flags, still without scheduler registration and without WarRoom UI trigger.
```
