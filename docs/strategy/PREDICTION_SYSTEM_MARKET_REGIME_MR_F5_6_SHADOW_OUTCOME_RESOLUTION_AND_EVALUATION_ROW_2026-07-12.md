# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_6_SHADOW_OUTCOME_RESOLUTION_AND_EVALUATION_ROW_2026-07-12.md
# desc: MR-F5.6 pure shadow outcome-resolution contract and immutable evaluation-row projection.

# Prediction System MarketRegime MR-F5.6 Shadow Outcome Resolution and Evaluation Row

Updated: 2026-07-12 JST
Status: implementation slice prepared

## States

```text
UNRESOLVED
INVALIDATED
ABSTAINED
CORRECT
PARTIAL
INCORRECT
```

Observation evidence is accepted only at or after expiry and within the target-definition tolerance. Transition-adjacent observed states are PARTIAL; non-adjacent mismatches are INCORRECT. Abstained forecasts are never scored.

## Boundary

The evaluation row preserves the complete MR-F5 trace identity and is immutable. It explicitly sets `ledger_append_allowed=false`.

```text
existing_outcome_resolver_modified=false
existing_outcome_resolver_executed=false
outcome_ledger_append=false
d_hot_read=false
d_hot_write=false
canonical_future_label_replacement=false
ui_change=false
```
