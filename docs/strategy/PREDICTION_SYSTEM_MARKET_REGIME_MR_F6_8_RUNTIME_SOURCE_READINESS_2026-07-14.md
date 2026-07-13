# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_8_RUNTIME_SOURCE_READINESS_2026-07-14.md
# desc: Records exact MR-F6.8 runtime-source provenance and unresolved canonical feature gaps.

# Prediction System MarketRegime MR-F6.8 Runtime Source Readiness

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Exact runtime sources found

```text
previous_state
  previous_current_state.regime_code

recent_return
  PRICE_STRUCTURE.current_l4_candle_net_change_bps / 10000

realized_volatility
  VOLATILITY.current_l4_candle_realized_volatility_bps / 10000

current_forecast_label_selection
  PRICE_STRUCTURE.current_l4_candle_regime_hint
```

## Unresolved canonical fields

```text
fast_ma
slow_ma
low_volatility_threshold
high_volatility_threshold
```

`ma_slope` is not a fast or slow moving-average level. `current_l4_candle_thresholds` are directional/range classification thresholds, not realized-volatility thresholds. Neither is substituted.

Therefore runtime-source readiness remains false and no evidence bundle is emitted from runtime inputs yet.

## Safety

```text
semantic_substitution_used=false
writer_invoked=false
writes_dhot=false
scheduler_enabled=false
canonical_replacement=false
live_parameter_apply_allowed=false
```
