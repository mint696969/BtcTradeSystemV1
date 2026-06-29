# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q24A_AUTOTRADE_READ_ONLY_PREDICTION_CONSUMPTION_PLANNING_2026-06-29.md
# desc: PS-Q24A no-write planning/compatibility guard for AutoTrade read-only consumption of manifest-first prediction state.
# PS-Q24A AutoTrade read-only prediction consumption planning

Updated: 2026-06-29 JST
Base: PS-Q23T manifest-first steady-state guard hardening
Mode: planning / compatibility guard / no runtime behavior change

```text
ps_q24a_autotrade_read_only_prediction_consumption_planning=true
base_reentry=PS_Q23T_MANIFEST_FIRST_STEADY_STATE_GUARD_HARDENED
q23t_manifest_first_guard_ready=true
autotrade_prediction_preview_status_contract_present=true
autotrade_shadow_prediction_context_contract_present=true
autotrade_prediction_preview_artifact_preflight_contract_present=true
autotrade_consumption_chain_in_memory_only=true
legacy_latest_compact_record_count=24
manifest_record_count=110
forecast_records_line_count=110
scheduler_action_changed=false
runtime_artifact_write_changed=false
broker_autotrade=false
ledger_append=false
mode_apply=false
parameter_apply=false
```

## Purpose

PS-Q24A reconnects the modern Q23T manifest-first prediction steady state with the older AutoTrade read-only prediction consumption contracts.

The goal is not to execute AutoTrade. The goal is to prove the safe next seam exists:

```text
manifest-first prediction state is healthy
AutoTrade read-only preview/status/context/preflight contracts are available
sample consumption remains in-memory only
all execution/mode/apply/broker/ledger/write flags remain false
```

## Current repo facts

Existing safe AutoTrade contracts:

```text
btcts_next/src/btcts/autotrade/prediction_preview_status.py
btcts_next/src/btcts/autotrade/shadow_prediction_context.py
btcts_next/src/btcts/autotrade/prediction_preview_artifact_preflight.py
btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_preview_status_display.py
```

Existing latest prediction read path:

```text
PS-Q23T guard confirms WarRoom manifest-first distributed source.
latest_manifest record_count = 110.
legacy latest compact fallback record_count = 24.
forecast_records sidecar line_count = 110.
```

## Chosen seam

Chosen next seam:

```text
AutoTrade read-only prediction consumption planning packet
```

Meaning:

```text
AutoTrade may later consume a prediction preview status/context packet as operator-visible read-only context.
It must not alter Shadow decisions, append ledgers, apply modes, execute grants, write runtime artifacts, or send broker requests.
```

## Explicit non-permissions

```text
no scheduler action replacement
no trigger mutation
no recurring policy change
no D-hot prediction artifact repair/write
no latest_manifest or sidecar repair/write
no legacy latest shrink/restore
no broker/private API
no AutoTrade trigger
no Shadow decision append
no command/approval ledger append
no mode apply
no Pre-Armed grant execution
no parameter apply/staging
no UI command button enablement
```

## Recommended next lane

After PS-Q24A is committed and room-synced, the next safe implementation can be either:

```text
PS_Q24B_AUTOTRADE_READ_ONLY_PREDICTION_STATUS_DISPLAY_COMPAT_GUARD
```

or, if the operator chooses to continue planning before UI work:

```text
PS_Q24B_AUTOTRADE_OPTIONAL_CONTEXT_PREVIEW_PLAN_NO_RUNTIME_WIRING
```

Neither lane authorizes broker, AutoTrade execution, ledger append, mode apply, or parameter apply.
