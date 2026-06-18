# path: ./docs/architecture/AUTOTRADE_SHADOW_DECISION_OPTIONAL_PREDICTION_CONTEXT_DESIGN_2026-06-18.md
# desc: Design-only packet for a future optional Shadow decision prediction context. No runtime behavior change, ledger append, mode apply, grant execution, or broker behavior.

# AutoTrade Shadow Decision Optional Prediction Context Design Packet

Updated: 2026-06-18 JST  
Profile: BtcTradeSystem  
Branch context: docs/phase2-handoff-sync  
Status: design-only / documentation / non-executing

## 1. Purpose

S138 added a read-only AutoTrade prediction preview status contract. S139 added a reusable Operator/UI display packet for that status.

S140 defines the next future seam only:

```text
Shadow decision may later accept optional prediction context,
but only as already-built, read-only, non-executing context,
and not as live Shadow append behavior, mode apply behavior, Pre-Armed grant behavior, or broker behavior.
```

This document does not change runtime behavior and does not authorize any code path to append a Shadow decision.

## 2. Current repo facts

Existing Shadow decision implementation:

```text
btcts_next/src/btcts/autotrade/live_shadow.py
```

Known behavior:

```text
run_shadow_decision_from_snapshot builds forecast, action candidate, risk result, and decision record.
run_shadow_decision_from_snapshot can append a shadow decision when persist=True.
run_latest_market_state_shadow_decision loads the latest market-state snapshot and delegates to run_shadow_decision_from_snapshot.
append_decision_jsonl is already imported inside live_shadow.py.
build_action_candidate is already imported inside live_shadow.py.
```

Because `live_shadow.py` owns the existing append path, S140 must not modify `live_shadow.py` behavior.

Recently completed safe objects:

```text
AutoTradePredictionPreviewStatus
build_autotrade_prediction_preview_status
AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT
build_autotrade_prediction_preview_status_display_packet
```

These objects are read-only/non-executing and are suitable inputs for future design, but S140 does not wire them into Shadow decision execution.

## 3. Chosen S140 seam

Chosen seam:

```text
Shadow Decision Optional Prediction Context Design / Non-Executing Seam
```

Meaning:

```text
Prediction preview status can be represented as optional context beside a Shadow decision preview,
not inside the decision append path,
not as a strategy input,
not as a mode-control input,
and not as broker/execution input.
```

S140 records how a future S141 contract may look, but S140 is documentation/status-only.

## 4. Future optional context shape

A later S141 slice may introduce a pure in-memory object similar to:

```text
AutoTradeShadowPredictionContext
  context_id
  generated_at
  source_status_id
  status_state
  preview_id
  readiness_id
  readiness_state
  preview_action
  preview_bias
  preview_confidence
  validation_state
  average_score
  label_hit_rate
  weak_families
  blockers
  warnings
  read_only = True
  non_executing = True
  optional_context_only = True
  would_change_shadow_candidate = False
  would_append_shadow_decision = False
  would_apply_mode = False
  would_execute_prearmed_grant = False
  would_write_runtime_artifact = False
  would_send_to_broker = False
  broker_execution_requested = False
  mode_apply_requested = False
  command_ledger_append_requested = False
  approval_append_requested = False
```

Possible future module target:

```text
btcts_next/src/btcts/autotrade/shadow_prediction_context.py
```

This is a proposal only. S140 does not create that module.

## 5. Future S141 integration boundary

Recommended next implementation slice after S140:

```text
S141 Shadow decision optional context contract, still persist=False only
```

Allowed scope for S141, if explicitly chosen later:

```text
add a read-only optional context dataclass and builder
accept AutoTradePredictionPreviewStatus as an already-provided object
return an in-memory context packet
allow tests to inspect a persist=False Shadow preview result beside this context
no decision append
no runtime path creation
no ledger write
no mode apply
no Pre-Armed grant execution
no broker
```

S141 should still avoid changing `run_shadow_decision_from_snapshot` behavior unless explicitly rescoped. A safer first implementation is a standalone optional context builder, not `live_shadow.py` modification.

## 6. Explicitly rejected in S140

S140 does not permit:

```text
live_shadow.py behavior modification
run_shadow_decision_from_snapshot modification
run_latest_market_state_shadow_decision modification
build_action_candidate modification
append_decision_jsonl usage
Shadow decision append
persist=True usage from prediction context flow
feeding preview output directly into build_action_candidate
using prediction context to alter candidate action
using PredictionPreArmedReadinessSnapshot to apply mode
using PredictionPreArmedReadinessSnapshot to execute a Pre-Armed grant
UI command buttons
watchdog/autonomous execution loop
broker execution
real orders
private API calls
public-source collection implementation
runtime source polling
external API calls
collector imports
command ledger append
approval ledger append
actual AutoTrade publication/write
```

## 7. Required future guard rules

Any future optional context integration must assert:

```text
read_only is True
non_executing is True
optional_context_only is True
would_change_shadow_candidate is False
would_append_shadow_decision is False
would_send_to_broker is False
would_apply_mode is False
would_execute_prearmed_grant is False
would_write_runtime_artifact is False
broker_execution_requested is False
mode_apply_requested is False
command_ledger_append_requested is False
approval_append_requested is False
persist is False when a Shadow preview runner is used in tests
```

Future guards must also confirm:

```text
no append_decision_jsonl token in any new prediction-context module
no run_shadow_decision_from_snapshot behavior modification unless explicitly rescoped
no run_latest_market_state_shadow_decision behavior modification unless explicitly rescoped
no build_action_candidate behavior modification unless explicitly rescoped
no btcts.autotrade.live_shadow import in a read-only context builder unless the slice explicitly allows persist=False preview inspection
no broker/private API/external API imports
no collector imports
```

## 8. Operator meaning

For a human operator, the future optional context should answer:

```text
Was prediction preview status available?
Was readiness available?
Was the prediction status ok, review, or blocked?
Which preview action/bias/confidence was visible?
Which readiness blockers/warnings were visible?
Would this context change the Shadow action? No.
Would this context append a decision? No.
Would this context apply mode or execute a grant? No.
Would this context send anything to a broker? No.
```

## 9. Later ladder after S140

The safe ladder remains:

```text
S141 Shadow decision optional context contract, still persist=False only
S142 controlled preflight for writing a preview status artifact, still no decision append
S143 later explicit decision ledger integration only if guards and operator policy allow
```

Do not jump directly to S143.

## 10. Decision

S140 chooses **design/status-only optional Shadow decision prediction context** as the next seam.

The next safe implementation slice is:

```text
S141 Shadow decision optional context contract, still persist=False only
```

S141 should start with a standalone read-only context contract and strong guards, not with `live_shadow.py` append-path modification.
