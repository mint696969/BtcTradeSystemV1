# path: ./docs/strategy/PREDICTION_SYSTEM_PS_F15_NEXT_SLICE_CHECKPOINT_2026-06-19.md
# desc: No-code checkpoint selecting the next Prediction System slice after PS-F14 feature-depth review closure.

# Prediction System PS-F15 next slice checkpoint

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-F15 is a no-code checkpoint after PS-F14.

It records that feature-depth family wiring is closed for now and selects the next safe Prediction System direction without changing production behavior.

## Current completed line

```text
PS-E1: feature-depth contracts
PS-E2: liquidity feature-depth context
PS-E3: breakout/algo feature-depth context
PS-E4: opportunity tradeflow context
PS-F12: feature-depth integration close guard
PS-F13: feature-depth stop/review decision
PS-F14: review-only Code Check pass
```

## Decision

```text
Stop feature-depth expansion for now.
Do not refactor feature-depth helpers unless a concrete defect is found.
Do not add more prediction-family feature-depth consumers immediately.
Next recommended direction is scenario narrative / UX digest refinement.
```

## Candidate next production slice

```text
PS-N1: scenario narrative / UX digest refinement plan
```

Intent:

```text
Improve how existing Prediction System outputs are summarized for review.
Use already-emitted family labels, scenario_lite, scenario_trace_detail, evidence refs, lifetime refresh, and feature-depth context versions.
Do not change prediction scores, family labels, trigger eligibility, execution behavior, or data collection.
```

Initial target shape:

```text
Add or refine review-only narrative/digest fields that help a human or GPT understand:
  what is the current scenario?
  what evidence supports it?
  what evidence conflicts with it?
  what should be watched next?
  what would force refresh/rewrite?
  which context versions were present?
```

## What must not happen in PS-N1

```text
No live collection.
No external API calls.
No Collector runtime imports.
No AutoTrade imports.
No broker/private API imports.
No artifact/runtime writes.
No AutoTrade decision append.
No command ledger append.
No mode/grant behavior.
No trigger eligibility enablement.
No primary-direction ownership from feature-depth context.
No changes to score formulas unless a concrete bug is found.
```

## Required first read for PS-N1

```text
tmp/gpt_room/memory/handoffs/2026-06-19_prediction_system_ps_f14_cc_pass_committed_handoff.md
docs/strategy/PREDICTION_SYSTEM_PS_F14_CC_PASS_2026-06-19.md
docs/strategy/PREDICTION_SYSTEM_PS_F13_FEATURE_DEPTH_REVIEW_2026-06-19.md
btcts_next/src/btcts/prediction/system.py
btcts_next/src/btcts/prediction/rule_based_v0.py
btcts_next/src/btcts/prediction/system_contract.py
tools/test_prediction_system_ps_g_lite_runner_guard.py
tools/test_prediction_system_ps_f14_cc_pass_guard.py
```

## Guarding approach for any later PS-N1 production change

```text
Keep PS-N1 small.
Read target files first.
Add a focused guard for narrative/digest shape.
Run PS-G-lite guard, PS-F12 guard, PS-F14 guard, and targeted pytest.
Preserve all non-executing flags and blocked TriggerEligibility.
Commit only after guards pass and status is expected.
```

## PS-F15 production behavior

```text
No production code changed.
No tests alter production behavior.
This checkpoint is documentation and guard only.
```
