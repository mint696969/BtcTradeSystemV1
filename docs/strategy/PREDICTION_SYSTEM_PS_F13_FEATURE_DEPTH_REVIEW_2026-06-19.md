# path: ./docs/strategy/PREDICTION_SYSTEM_PS_F13_FEATURE_DEPTH_REVIEW_2026-06-19.md
# desc: Review/planning artifact that pauses additional Prediction System feature-depth family wiring before a CC pass.

# Prediction System PS-F13 feature-depth review

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-F13 is a review/planning slice after PS-E2, PS-E3, PS-E4, and PS-F12.

It intentionally adds no new production behavior. It records the decision to pause additional feature-depth family wiring and to treat the current feature-depth path as review-stable before any further production refactor.

## Current completed feature-depth wiring

```text
PS-E1: feature-depth contracts
PS-E2: liquidity_execution_quality context/warning integration, version ps_e2.v1
PS-E3: breakout_false_break and algorithmic_participant_footprint context/warning integration, version ps_e3.v1
PS-E4: opportunity_participation wait/confirmation context integration, version ps_e4.v1
PS-F12: feature-depth integration close guard
```

## Review decision

```text
Do not add another feature-depth family behavior immediately.
Do not expand feature-depth into primary direction ownership.
Do not make opportunity_participation an execution gate or grant source.
Do not add live collection, Collector dependency, AutoTrade dependency, broker/private API, mode/grant behavior, or runtime artifact writes.
```

## Stable behavior to preserve

```text
FeatureDepthSnapshot remains context-only.
feature_depth_context.context_only=True.
feature_depth_context.primary_direction_owner=False.
feature_depth_context.usable_for_primary_short_horizon=False.
Prediction System remains standalone, read-only, and non-executing.
TriggerEligibility remains blocked.
```

## Version markers to preserve

```text
liquidity_feature_depth_context_version = ps_e2.v1
orderbook_breakout_algo_context_version = ps_e3.v1
opportunity_tradeflow_context_version = ps_e4.v1
```

## Known implementation notes

```text
rule_based_v0.py currently has two feature-depth helpers:
  _apply_liquidity_feature_depth_context
  _apply_feature_depth_context_for_family

The generic family helper has context_version='ps_e3.v1' by default and accepts explicit ps_e4.v1 for opportunity_participation.
The liquidity helper intentionally does not accept context_version and continues to emit ps_e2.v1.
```

## Recommended next options

```text
Option A: stop feature-depth wiring and move to scenario narrative / UX digest refinement.
Option B: tiny refactor-only slice to reduce duplicated feature-depth context fields, guarded by PS-F12.
Option C: no code changes; run a broader Prediction System review / CC pass over rule_based_v0.py and system.py.
```

Default recommendation:

```text
Choose Option C first. Do not touch production code unless review finds a small, concrete defect.
```

## Hard boundaries

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
```
