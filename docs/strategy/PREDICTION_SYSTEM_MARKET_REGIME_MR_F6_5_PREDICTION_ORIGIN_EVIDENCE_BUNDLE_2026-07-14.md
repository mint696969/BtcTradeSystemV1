# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_5_PREDICTION_ORIGIN_EVIDENCE_BUNDLE_2026-07-14.md
# desc: Defines the MR-F6.5 prediction-origin evidence bundle and no-lookahead boundary.

# Prediction System MarketRegime MR-F6.5 Prediction-Origin Evidence Bundle

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

<!-- PS_MARKET_REGIME_MR_F6_5_PREDICTION_ORIGIN_EVIDENCE_BUNDLE_2026_07_14 -->

## Scope

MR-F6.5 closes the evidence-contract gap found in MR-F6.4 without enabling any live write.

At prediction origin, one pure bundle now captures:

```text
trace identity
model / logic / parameter set
target horizon and target definition
prediction origin
feature snapshot reference
full candidate probability distribution
current and previous regime
recent return
fast / slow moving average
realized volatility and thresholds
legacy current forecast-label selection
```

Candidate probabilities are derived from the same non-negative regime score set available to the MR-F5 transparent baseline model. UNKNOWN receives no probability mass.

## No-lookahead boundary

The source timestamp must not be later than prediction origin. Historical MR-F5 evidence must not be reconstructed from later market data.

## Persistence boundary

This slice does not write D-hot. It produces an immutable bundle with:

```text
append_only_required=true
canonical_isolated=true
historical_backfill_allowed=false
scheduler_registration_allowed=false
write_performed=false
```

## Next slice

MR-F6.6 will design and test a disabled-by-default, approval-gated append-only writer for these bundles. It must remain separate from canonical latest artifacts and must not be registered with a scheduler.
