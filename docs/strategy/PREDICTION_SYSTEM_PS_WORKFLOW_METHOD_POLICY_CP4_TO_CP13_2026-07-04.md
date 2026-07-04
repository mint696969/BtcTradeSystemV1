# path: ./docs/strategy/PREDICTION_SYSTEM_PS_WORKFLOW_METHOD_POLICY_CP4_TO_CP13_2026-07-04.md
# desc: Prediction System workflow method policy for CP4-CP13. Fixes the fast traceable checkpoint method and separates danger-zone handling.

# Prediction System workflow method policy CP4-CP13

Date: 2026-07-04
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync
Scope: WarRoom v2 WebSocket receiver-only client continuation after CP6

## Decision

The CP4-CP6 working method is the preferred default for non-dangerous receiver work because it delivered fast progress without losing traceability.

## Default method for safe metadata-only checkpoints

```text
- Use one checkpoint-level patch when the scope is non-dangerous and cohesive; avoid needless micro-slicing.
- Inside the checkpoint, keep explicit traceability slices such as Q36R-Q36Y with module/test/doc for each slice.
- Create idempotent tmp/work/<slice>/apply_*.py runners and focused fix_*.py runners only when needed.
- Every checkpoint must include strict traceability runner, slice unit tests, focused previous-to-current guard, CP1-to-current focused guard, close guard, py_compile, git diff --check, gpt_room sync, commit, and clean working tree confirmation.
- Do not call a checkpoint complete before commit hash and clean working tree are confirmed.
- Use repo truth over conversation memory; use gpt_room as persistent project memory; do not rely on broad repo listing when targeted reads/grep are enough.
```

## Danger-zone exception

```text
- Danger zones are not handled with the fast checkpoint-level compression used for safe metadata-only work.
- Danger zones include real WebSocket open/connect, real network, endpoint/token/callable handling, auto-start, visible controls that trigger live behavior, broker/order/ledger, prediction generation/inference, classifier invocation, reconnect/heartbeat/backpressure, and operator-facing live receiver mode.
- Danger zones must use smaller slices, explicit approval gates, default-off behavior, no-send proof, redaction proof, and reversible dry-run first.
- No secret values, endpoint values, token values, callable values, raw payloads, or send-capable objects may be surfaced in docs, tests, state readback, or UI.
```

## Non-negotiable completion gate

```text
strict_traceability=passed
slice_unit=passed
focused_previous_to_current=passed
cp1_to_current_focused=passed
close_guard=passed
py_compile=passed
git_diff_check=passed
gpt_room_sync=applied_or_already_applied
commit=created
working_tree=clean
```

A checkpoint is not complete until commit and clean working tree are confirmed.
