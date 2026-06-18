# path: ./docs/architecture/AUTOTRADE_PREDICTION_PREVIEW_CONSUMPTION_DESIGN_2026-06-18.md
# desc: Design-only packet for future AutoTrade consumption of prediction preview/readiness objects. No runtime behavior change.

# AutoTrade Prediction Preview Consumption Design Packet

Updated: 2026-06-18 JST  
Profile: BtcTradeSystem  
Branch context: docs/phase2-handoff-sync  
Status: design-only / documentation / non-executing

## 1. Purpose

S121-S136 completed and indexed the prediction foundation. S137 defines the future integration seam for AutoTrade to consume prediction preview/readiness objects without implementing that seam yet.

This packet chooses a safe first integration direction:

```text
first integrate prediction preview/readiness as read-only status/preflight context,
not as shadow-decision append logic,
not as mode apply logic,
and not as broker/execution logic.
```

No code behavior changes are authorized by this document.

## 2. Current known repo facts

Existing AutoTrade Shadow vertical slice:

```text
btcts_next/src/btcts/autotrade/live_shadow.py
```

It currently builds a market-state snapshot, forecast, candidate, risk result, decision record, and can append a shadow decision when `persist=True`.

Because it contains the append path, S137 does not choose `live_shadow.py` as the first implementation target.

Existing read-only status/gate surfaces:

```text
btcts_next/src/btcts/autotrade/health.py
btcts_next/src/btcts/autotrade/mode_runtime_gate.py
```

These are better first integration candidates because they already represent read-only status or capability gating concepts.

Existing prediction objects ready for later consumption:

```text
AutoTradeShadowSignalPreview
PredictionPreArmedReadinessSnapshot
ReplayValidationResult
PredictionCalibrationReport
```

## 3. Chosen first seam

Chosen first seam:

```text
Prediction Preview Read-Only Status / Preflight Seam
```

Initial future consumer:

```text
new read-only AutoTrade status/preflight packet, not live_shadow append path
```

Rationale:

```text
1. It can display preview/readiness without changing decisions.
2. It avoids append_decision_jsonl.
3. It avoids run_shadow_decision_from_snapshot.
4. It avoids mode apply.
5. It preserves the prediction -> AutoTrade one-way boundary.
6. It gives the operator visibility before any behavior-changing integration.
```

## 4. Future packet shape

Future implementation may introduce a read-only packet similar to:

```text
AutoTradePredictionPreviewStatus
  generated_at
  preview_id
  readiness_id
  readiness_state
  preview_action
  preview_bias
  validation_state
  average_score
  label_hit_rate
  weak_families
  blockers
  warnings
  read_only = True
  non_executing = True
  would_append_shadow_decision = False
  would_apply_mode = False
  would_send_to_broker = False
```

Possible future module target:

```text
btcts_next/src/btcts/autotrade/prediction_preview_status.py
```

This is a proposal only. S137 does not create that module.

## 5. Explicitly rejected as first implementation

Do not start with:

```text
modifying run_shadow_decision_from_snapshot
modifying run_latest_market_state_shadow_decision
calling append_decision_jsonl from prediction preview flow
feeding preview output directly into build_action_candidate
using PredictionPreArmedReadinessSnapshot to apply mode
using PredictionPreArmedReadinessSnapshot to execute a Pre-Armed grant
adding UI command buttons
```

Those may be considered later only after read-only status consumption is closed and guarded.

## 6. Boundary for future S138

Recommended next implementation slice:

```text
S138 AutoTrade prediction preview status contract
```

Allowed scope for S138:

```text
add a read-only status dataclass and builder
accept AutoTradeShadowSignalPreview and PredictionPreArmedReadinessSnapshot as already-provided objects
return an in-memory status packet
no file writes
no runtime path creation
no ledger append
no mode apply
no grant execution
no broker
```

Preferred target:

```text
btcts_next/src/btcts/autotrade/prediction_preview_status.py
```

Expected guards:

```text
focused guard confirms status object serializes
close guard confirms syntax and focused guard
guard confirms live_shadow.py is untouched
guard confirms no append_decision_jsonl, no run_shadow_decision_from_snapshot, no mode apply, no broker/private API
```

## 7. Later integration ladder

After S138, possible ladder:

```text
S139 operator/UI read-only display packet for prediction preview status
S140 optional Shadow decision context design packet
S141 Shadow decision optional context contract, still persist=False only
S142 controlled preflight for writing a preview status artifact, still no decision append
S143 later explicit decision ledger integration only if guards and operator policy allow
```

Do not jump directly to S143.

## 8. Required guard rules for future code integration

Any future code integration that consumes prediction preview/readiness must assert:

```text
read_only is True
non_executing is True
would_send_to_broker is False
would_apply_mode is False
would_append_shadow_decision is False
would_execute_prearmed_grant is False when readiness is present
broker_execution_requested is False when preview/readiness exposes it
mode_apply_requested is False when preview/readiness exposes it
command_ledger_append_requested is False when preview/readiness exposes it
```

Future code must not import private exchange clients or public-source collectors in the consumption seam.

## 9. Non-permissions

This design packet does not permit:

```text
broker execution
real orders
private API calls
public-source collection implementation
runtime source polling
external API calls
AutoTrade mode apply
Pre-Armed grant execution
record append execution
command ledger append
approval ledger append
actual AutoTrade publication/write
actual replay runner execution
append_decision_jsonl usage
run_shadow_decision_from_snapshot modification
run_latest_market_state_shadow_decision modification
build_action_candidate modification
strategy execution
UI command buttons
watchdog/autonomous execution loop
market manipulation
spoofing
quote stuffing
abusive order behavior
```

## 10. Decision

S137 chooses **read-only status/preflight consumption** as the next AutoTrade integration seam.

The next safe implementation slice is:

```text
S138 AutoTrade prediction preview status contract
```

S138 should be the first slice to touch AutoTrade code, and only by adding a new read-only status module with strong guards.
