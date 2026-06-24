# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18AV_WARROOM_OBSERVATION_QUICK_STATUS_MANUAL_UI_SMOKE_PACKET_2026-06-24.md
# desc: PS-Q18AV manual UI smoke packet for WarRoom latest prediction observation quick status.
# PS-Q18AV WarRoom observation quick status manual UI smoke packet

Updated: 2026-06-24 JST

## Purpose

PS-Q18AV defines the manual UI smoke packet for the PS-Q18AU WarRoom latest prediction observation quick status.

This slice does not modify WarRoom runtime behavior. It only fixes the operator check contract for the next manual UI smoke.

## Launch command

```powershell
Set-Location C:\BtcTradeSystem
$ErrorActionPreference = "Stop"

.\tools\run_operator_ui_sr_fx_dhot.ps1 -Port 501
```

## Manual checks

On the WarRoom page, verify:

```text
1. section title visible: Prediction WarRoom latest summary observation quick status
2. browser find hit: PS_Q18AU_OBSERVATION_QUICK_STATUS
3. browser find hit: latest_prediction_observation_status
4. browser find hit: implementation_gate=blocked_not_ready_to_enable
5. browser find hit: real_render=false
6. browser find hit: component_runtime_binding=false
7. browser find hit: autotrade=false
8. browser find hit: broker=false
9. refresh_heartbeat_utc value advances after waiting 10-15 seconds
10. no broad page whiteout or full reload is observed
```

## Expected classification

```text
manual_ui_smoke_expected_result=pass_if_all_checks_true
```

## Evidence to collect

```text
screenshots: quick status block and browser find hits
optional_uicheck: tmp/uicheck/*_warroom.json
repo_head: git rev-parse --short HEAD
repo_status: git status --short
```

## Safety boundary retained

```text
real_prediction_widget_rendering_allowed=false
real_prediction_widget_render_invoked=false
streamlit_real_widget_render_invoked=false
component_runtime_binding_allowed=false
component_props_bound_to_runtime=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Next

After manual UI evidence is supplied, record PS-Q18AW manual UI smoke execution result. Keep real rendering and trading/execution behavior disabled.
