# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_2_MANDATORY_BASELINE_GENERATORS_2026-07-14.md
# desc: Defines the MR-F6.2 deterministic mandatory baseline generator boundary.

# Prediction System MarketRegime MR-F6.2 Mandatory Baseline Generators

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

<!-- PS_MARKET_REGIME_MR_F6_2_MANDATORY_BASELINE_GENERATORS_2026_07_14 -->

## Scope

MR-F6.2 adds deterministic, pure generators for all mandatory simple baselines from one shared no-lookahead evidence record.

```text
always_range
last_state_persists
recent_return_sign
simple_ma_slope
simple_volatility_threshold
current_forecast_label_selection
```

## Input boundary

All generators receive the same prediction origin, source snapshot, source timestamp, horizon, and source-derived values. A source timestamp after prediction origin is rejected.

Missing optional evidence causes only the affected baseline to abstain. It must not make another baseline fail or invent data.

## Output boundary

Each available prediction has a normalized multiclass probability distribution whose selected state is an argmax. UNKNOWN is represented as unavailable/abstain and never receives probability mass.

## Safety

The module is pure and deterministic. It performs no D-hot reads or writes, no scheduling, no UI projection, no canonical replacement, no parameter promotion, and no live apply.

## Next slice

MR-F6.3 will adapt accepted MR-F5 evaluation evidence into the shared input contract, generate the six baselines for every identical comparison slot, and feed MR-F6.1 without changing the outcome resolver or evaluation window.
