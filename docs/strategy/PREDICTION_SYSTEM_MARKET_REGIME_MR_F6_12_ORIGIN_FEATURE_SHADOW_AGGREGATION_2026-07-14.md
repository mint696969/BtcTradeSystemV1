# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_12_ORIGIN_FEATURE_SHADOW_AGGREGATION_2026-07-14.md
# desc: Defines MR-F6.12 multi-slot candidate-by-baseline aggregation without ranking or selection.

# Prediction System MarketRegime MR-F6.12 Origin Feature Shadow Aggregation

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Responsibility

MR-F6.12 consumes multiple immutable MR-F6.11 same-slot evaluations and aggregates all:

```text
8 origin-feature shadow candidates
x
6 mandatory baselines
=
48 candidate-baseline pairs
```

For each pair it reports:

```text
slot count
observed slot count
scored slot count
hit count
unknown count
coverage rate
accuracy
unknown rate
```

## Same-comparison contract

All input slots must use the same:

```text
evaluation_window_ref
target_horizon_sec
target_definition_version
outcome_resolver_version
candidate registry
mandatory baseline registry and order
```

Prediction origin and source snapshot may differ per slot. Duplicate slot IDs and duplicate comparison keys are rejected.

The aggregator revalidates strict boolean availability, canonical candidate IDs, candidate-to-parameter-set identity, calculated feature parameter fields, shadow-only flags, predicted-state types, and recomputes each scored `hit` from predicted and observed states. Input-provided labels and hit values are never trusted without these checks.

## Boundary

This slice performs no ranking and no candidate selection. It does not create a winner, active parameter set, runtime selection, or canonical replacement.

```text
ranking_performed=false
selection_performed=false
selected_candidate_id=null
writes_dhot=false
scheduler_enabled=false
live_parameter_apply_allowed=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
```

MR-F6.13 may add evidence sufficiency and deterministic ranking criteria, but must remain shadow-only and human-gated.
