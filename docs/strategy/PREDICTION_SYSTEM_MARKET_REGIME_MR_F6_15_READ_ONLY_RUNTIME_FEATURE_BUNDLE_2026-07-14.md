# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_15_READ_ONLY_RUNTIME_FEATURE_BUNDLE_2026-07-14.md
# desc: Defines MR-F6.15 explicit-candidate read-only runtime origin-feature completion.

# Prediction System MarketRegime MR-F6.15 Read-only Runtime Feature Bundle

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Responsibility

MR-F6.15 completes the four previously missing runtime-origin fields:

```text
fast_ma
slow_ma
low_volatility_threshold
high_volatility_threshold
```

Inputs are explicit:

```text
MarketRegimeFeatureBundle
previous_current_state
canonical current-L4 closed candle rows
exact shadow_candidate_id
```

The existing runtime source remains responsible for source timestamp, previous state, recent return, realized volatility, and legacy label selection. The MR-F6.9 calculator derives MA levels from the canonical close series and copies volatility thresholds from the exact MR-F6.10 shadow parameter contract.

## Candle contract

```text
exactly 60 rows
time_utc required
strictly increasing
exact 60-second adjacency
last candle <= source_timestamp
positive finite closes
source_snapshot_ok=true
SOURCE_QUALITY coverage is available and LIVE
PRICE_STRUCTURE coverage is available and LIVE
VOLATILITY coverage is available and LIVE
```

## Candidate contract

No default candidate is introduced. The exact candidate ID is mandatory and must resolve to the immutable eight-candidate shadow registry. This is feature completion for evidence collection, not runtime selection.

## Boundary

```text
candidate_selection_performed=false
writer_invoked=false
writes_dhot=false
scheduler_enabled=false
live_parameter_apply_allowed=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
```

MR-F6.16 may connect this read-only bundle to the writer preflight path for one explicit candidate and one immutable origin batch. It must still perform no write without a separately scoped human approval.
