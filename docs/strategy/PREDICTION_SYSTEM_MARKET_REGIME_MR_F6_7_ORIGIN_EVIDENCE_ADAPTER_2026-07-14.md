# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_7_ORIGIN_EVIDENCE_ADAPTER_2026-07-14.md
# desc: Defines the MR-F6.7 pure connection from generated forecasts to seven origin-evidence bundles.

# Prediction System MarketRegime MR-F6.7 Origin Evidence Adapter

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Scope

Connects the generated seven-horizon future forecast packet to MR-F6 origin-evidence bundles without invoking a writer.

Inputs are explicit and no-lookahead:

```text
future shadow packet
signal score report
source timestamp
previous state
recent return
fast / slow moving average
realized volatility and thresholds
legacy forecast-label selection
```

The adapter does not guess feature names from `MarketRegimeFeatureBundle`. Missing or invalid explicit inputs fail closed.

## Safety

```text
writer invocation=false
D-hot write=false
scheduler registration=false
historical backfill=false
canonical replacement=false
live parameter apply=false
```

MR-F6.8 may connect these explicit inputs to the runtime source builder, but writer execution remains separately approved.
