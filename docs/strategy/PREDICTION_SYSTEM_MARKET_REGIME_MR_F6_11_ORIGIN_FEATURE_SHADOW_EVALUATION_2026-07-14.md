# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_11_ORIGIN_FEATURE_SHADOW_EVALUATION_2026-07-14.md
# desc: Defines the MR-F6.11 same-slot evaluation projection for all origin-feature shadow candidates.

# Prediction System MarketRegime MR-F6.11 Origin Feature Shadow Evaluation

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Responsibility

The eight MR-F6.10 entries are origin-feature parameter candidates, not forecast-model candidates. This slice therefore does not inject them into `candidate_model_id`.

For one immutable evaluation slot, it calculates each candidate's:

```text
fast MA level
slow MA level
low volatility threshold
high volatility threshold
```

It then generates the same six mandatory baseline predictions using the same:

```text
prediction origin
evaluation window
source snapshot
target horizon
target definition
outcome resolver
observed state
```

All eight projections must share one comparison key.

Each candle row must carry `time_utc`. The rows must be strictly increasing, exactly 60 seconds apart, contain at least 60 rows, and end no later than the slot source timestamp. This prevents future-candle use and gap-crossing MA calculations.

## Output boundary

The projection records per-baseline predicted state, probability distribution, availability, reason code, observed state, and optional hit status.

It does not aggregate across slots and does not rank or select candidates. Multi-slot metrics belong to MR-F6.12.

## Safety

```text
selection_performed=false
selected_candidate_id=null
writes_dhot=false
scheduler_enabled=false
live_parameter_apply_allowed=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
```
