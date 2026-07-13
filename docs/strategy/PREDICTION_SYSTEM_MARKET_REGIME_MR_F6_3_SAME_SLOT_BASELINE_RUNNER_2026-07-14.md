# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_3_SAME_SLOT_BASELINE_RUNNER_2026-07-14.md
# desc: Defines the MR-F6.3 same-slot candidate and baseline runner boundary.

# Prediction System MarketRegime MR-F6.3 Same-Slot Baseline Runner

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

<!-- PS_MARKET_REGIME_MR_F6_3_SAME_SLOT_BASELINE_RUNNER_2026_07_14 -->

## Scope

MR-F6.3 introduces the pure adapter that projects one accepted candidate prediction and the six mandatory baselines into one identical evaluation slot.

Each slot fixes:

```text
prediction origin
evaluation window
source snapshot
source timestamp
target horizon
target definition
outcome resolver
observed state
```

One slot produces exactly seven comparison rows:

```text
1 accepted candidate row
6 mandatory baseline rows
```

## Fairness boundary

All seven rows share the same comparison key. Baseline abstention caused by missing optional evidence preserves the slot and is measured as UNKNOWN/coverage loss rather than silently dropping the row.

Candidate probabilities are validated by the same MR-F6.1 row contract as baseline probabilities.

## Safety

The runner is pure and performs no filesystem access, D-hot write, scheduler registration, UI projection, canonical replacement, parameter promotion, or live apply.

## Next slice

MR-F6.4 will add a read-only adapter for accepted MR-F5 operational evidence artifacts, materialize normalized slots, produce a comparison report, and expose blockers without changing canonical behavior.
