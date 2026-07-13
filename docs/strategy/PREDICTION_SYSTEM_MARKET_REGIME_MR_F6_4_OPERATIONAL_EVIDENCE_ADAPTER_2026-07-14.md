# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_4_OPERATIONAL_EVIDENCE_ADAPTER_2026-07-14.md
# desc: Records the MR-F6.4 operational evidence gap and fail-closed adapter contract.

# Prediction System MarketRegime MR-F6.4 Operational Evidence Adapter

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

<!-- PS_MARKET_REGIME_MR_F6_4_OPERATIONAL_EVIDENCE_ADAPTER_2026_07_14 -->

## Finding from D-hot inspection

Accepted MR-F5 `future_shadow_evidence_batch` rows contain trace identity, origin, horizon, predicted state, observed state, and feature snapshot reference.

They do not contain:

```text
candidate probability distribution
feature snapshot payload
recent return
fast / slow moving average
realized volatility and thresholds
legacy current forecast-label selection
```

No persisted file matching the referenced `market_regime_feature_snapshot:*` identity was found in D-hot during the MR-F6.4 entry inspection.

Therefore existing MR-F5 evaluation rows are sufficient for the MR-F5 outcome gate but are not, by themselves, sufficient for fair MR-F6 probability and simple-baseline comparison.

## Adapter behavior

The adapter is read-only and fail-closed. It:

1. selects only the explicitly accepted parameter set;
2. audits every selected evaluation row;
3. requires candidate probabilities keyed by trace;
4. requires the referenced feature snapshot payload;
5. reports missing fields instead of inventing values;
6. materializes `MandatoryBaselineEvaluationSlot` only when all required evidence exists.

## Safety

```text
read_only=true
writes_dhot=false
canonical_replacement=false
parameter_auto_promotion_allowed=false
live_parameter_apply_allowed=false
```

## Next slice

MR-F6.5 must close the evidence gap structurally. The prediction-origin path needs an append-only snapshot artifact containing the exact no-lookahead baseline inputs and candidate probability distribution. Historical MR-F5 rows must not be silently backfilled from later market data.
