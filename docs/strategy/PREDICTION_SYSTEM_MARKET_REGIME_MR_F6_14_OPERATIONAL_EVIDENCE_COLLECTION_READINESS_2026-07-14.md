# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_14_OPERATIONAL_EVIDENCE_COLLECTION_READINESS_2026-07-14.md
# desc: Records MR-F6.14 operational evidence collection blockers and read-only readiness plan.

# Prediction System MarketRegime MR-F6.14 Operational Evidence Collection Readiness

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## D-hot finding

The dedicated MR-F6 origin evidence namespace is currently empty:

```text
D:\btc_ts_hot\prediction\market_regime\future_origin_evidence
artifact_count=0
```

No real MR-F6 operational ranking evidence exists yet.

## Current blockers

```text
runtime source readiness is not yet connected to canonical MA and volatility-threshold signals
operator approval has not been issued
origin evidence namespace is empty
same-window observed slots have not been collected
```

Existing MR-F5 evidence must not be retroactively reconstructed from later candle data. Historical backfill remains forbidden.

## Plan contract

The read-only plan requires an explicit policy with:

```text
minimum_origin_batches
minimum_observed_slots_per_horizon
all seven canonical horizons
```

It records runtime readiness, current namespace inventory, approval presence, and exact observed-slot counts for every canonical horizon. Policy thresholds and observed counts must be strict integers, and a ready runtime source may not carry blockers. `evaluation_ready` requires both the minimum origin-batch count and the per-horizon observed-slot threshold for all seven horizons; artifact file count alone is never sufficient.

## Boundary

This slice does not activate the writer.

```text
writer_activation_performed=false
writer_invoked=false
writes_dhot=false
scheduler_enabled=false
historical_backfill_allowed=false
winner_declared=false
selection_performed=false
live_parameter_apply_allowed=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
```

## Next step

MR-F6.15 must connect the four canonical origin-feature signals into the runtime feature bundle under an explicit shadow parameter-set ID. Only after that connection passes read-only preflight may a human authorize a limited once-only collection batch.
