# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_9_CURRENT_L4_ORIGIN_FEATURE_PARAMETERS_2026-07-14.md
# desc: Defines the MR-F6.9 explicit parameter contract for MA levels and volatility thresholds.

# Prediction System MarketRegime MR-F6.9 Current L4 Origin Feature Parameters

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## D-hot evidence

The live WarRoom candle store contains a continuous one-minute closed-candle series. The existing MarketRegime feature path consumes the latest 60 closed rows, which gives a canonical close series for MA calculation.

## Boundary

This slice does not choose production values for:

```text
fast_ma_window_rows
slow_ma_window_rows
low_volatility_threshold_bps
high_volatility_threshold_bps
```

All four are mandatory explicit parameters. No default 5/20 window or volatility threshold is introduced into production behavior.

The pure calculator returns MA price levels from exact tail windows and carries the explicit volatility thresholds alongside the observed realized volatility.

## Safety

```text
feature builder unchanged
active parameter set unchanged
writer invocation=false
D-hot write=false
scheduler registration=false
semantic substitution=false
```

MR-F6.10 must add these fields to a named shadow parameter set before feature-builder integration.
