# path: ./docs/strategy/PREDICTION_SYSTEM_PS_O1_ROADMAP_CHECKPOINT_2026-06-19.md
# desc: No-code roadmap checkpoint for current Prediction System state and next candidate work after PS-N4.

# Prediction System PS-O1 roadmap checkpoint

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-O1 is a no-code roadmap checkpoint after PS-N4.

It summarizes the current stable Prediction System surface and chooses the next safe candidate direction before any more production behavior is added.

## Current stable surface

```text
Standalone Prediction System runner exists.
Prediction System remains separate from Collector and AutoTrade.
All 11 rule_based_v0 families emit outputs.
Scenario Core lite is deterministic.
Scenario trace detail and lightweight evidence refs are emitted.
Lifetime refresh-lite and revision-lite are emitted.
Provider reliability registry skeleton is present and conservative/context-only.
Feature-depth contracts are present and conservative/context-only.
Liquidity consumes provided feature-depth snapshot as context/warning only.
Breakout and algorithmic footprint consume provided feature-depth snapshot as context/warning only.
Opportunity participation consumes provided feature-depth snapshot as wait/confirmation context only.
scenario_review_summary is emitted as a top-level review-only digest.
TriggerEligibility remains blocked.
```

## Completed line through PS-O1

```text
PS-A: roadmap
PS-C1: contracts
PS-G-lite: standalone runner
PS-F: complete review
PS-H1: Scenario Core lite
PS-H2: scenario trace detail / evidence refs
PS-I1: revision lifetime refresh-lite
PS-D1: provider reliability registry skeleton
PS-E1: feature-depth contracts
PS-E2: liquidity feature-depth context
PS-E3: orderbook breakout / algorithmic footprint feature context
PS-E4: opportunity tradeflow feature context
PS-F12: feature-depth integration close guard
PS-F13: feature-depth stop / review decision
PS-F14: feature-depth CC pass
PS-F15: next-slice checkpoint
PS-N1: scenario narrative / UX digest plan
PS-N2: scenario_review_summary top-level review-only digest
PS-N3: scenario_review_summary CC pass
PS-N4: narrative line close checkpoint
PS-O1: roadmap checkpoint
```

## Current stop decisions

```text
Do not add more scenario narrative / UX digest production behavior immediately.
Do not rename scenario_review_summary fields immediately.
Do not refactor scenario_review_summary helper immediately.
Do not change ps_n1.v1 schema marker immediately.
Do not expand feature-depth family wiring immediately.
Do not resume AutoTrade automatically.
Do not wire Collector runtime into Prediction System.
```

## Candidate next directions

### Option A: whole-surface Code Check pass

```text
Review current Prediction System standalone surface end-to-end.
Check contracts, system runner, rule_based_v0 families, source quality/provider reliability, feature-depth, forecast ledger, scenario digest, and guards.
No production code changes unless a concrete defect is found.
```

Why this is safe:

```text
The Prediction System now has several layered slices. A whole-surface CC pass can catch naming drift, guard overlap, or hidden coupling before more production behavior is added.
```

### Option B: evaluation / replay-feedback roadmap

```text
Plan how to evaluate predictions against later outcomes without trading.
Keep it offline / replay-only / no broker / no live collection.
Do not write runtime artifacts from the Prediction System runner.
```

Why this is useful:

```text
The current system can emit structured predictions, but the next major quality step is measuring prediction usefulness over replay/evaluation data.
```

### Option C: calibration / confidence roadmap

```text
Plan how confidence and caution labels should be calibrated from evidence and later outcomes.
No score formula changes in the planning slice.
No live behavior changes.
```

Why this is useful:

```text
The current confidence/caution logic is deterministic and conservative. Calibration should be deliberate and evidence-driven, not patched opportunistically.
```

### Option D: UX documentation only

```text
Document how a human or GPT should read scenario_review_summary fields.
Clarify evidence_support / evidence_conflicts semantics.
No production code changes.
```

Why this is useful:

```text
The field names are stable for now, but human-facing interpretation may need documentation before UI or report work.
```

## Default next recommendation

```text
Choose Option A first: PS-O2 whole-surface Code Check pass.
```

Rationale:

```text
The current Prediction System has enough slices that a broad review-only pass is safer than immediately adding evaluation, calibration, or UX behavior.
```

## Hard boundaries to preserve

```text
No live collection.
No external API calls.
No Collector runtime imports.
No AutoTrade imports.
No broker/private API imports.
No artifact/runtime writes from Prediction System runner.
No AutoTrade decision append.
No command ledger append.
No mode/grant behavior.
No trigger eligibility enablement.
No primary-direction ownership from feature-depth context.
No score formula changes unless a concrete reviewed defect is found.
No rule_based_v0 label changes unless a concrete reviewed defect is found.
```

## Required guard baseline for later work

```text
PS-G-lite runner guard.
PS-F12 feature-depth integration close guard.
PS-N2 scenario_review_summary guard.
PS-N3 scenario_review_summary CC guard.
PS-N4 narrative close checkpoint guard.
PS-O1 roadmap checkpoint guard.
```

## PS-O1 production behavior

```text
No production code changed.
No tests alter production behavior.
This checkpoint is documentation and guard only.
```
