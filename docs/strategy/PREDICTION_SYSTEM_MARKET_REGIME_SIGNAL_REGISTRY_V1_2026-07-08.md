# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_SIGNAL_REGISTRY_V1_2026-07-08.md
# desc: Market-regime signal registry v1. Spec-only; defines initial explainable signal families and signal IDs for market-regime inference.
# Market Regime Signal Registry v1

Updated: 2026-07-08 JST
Base: Parent Inference Engine Common Contract / Market Regime Trace and Calibration Spec
Mode: signal registry specification lock / no runtime behavior change

<!-- PS_MARKET_REGIME_SIGNAL_REGISTRY_V1_LOCK_2026_07_08 -->

```text
ps_market_regime_signal_registry_v1_lock=true
market_regime_only=true
signal_registry_version=market_regime_signal_registry.2026_07_08.v1
explainable_signal_votes=true
parameter_set_overridable=true
cross_family_refs_supported=true
same_run_cycle_forbidden=true
ui_classifier_invocation_allowed=false
runtime_code_changed=false
broker_send_enabled=false
order_intent_submitted=false
autotrade_trigger_allowed=false
```

## 1. Purpose

This document fixes the initial market-regime signal registry before implementation.

A signal is not a final answer. A signal is an explainable vote or modifier that contributes to regime scores, confidence, conflicts, invalidation, and trace records.

The registry must remain extensible. Future sources, signal IDs, signal weights, and thresholds must be added by versioned registry / parameter-set changes, not by hidden UI logic.

## 2. Signal entry contract

Every signal entry should provide fields equivalent to:

```text
signal_id
source_family
description
supports_regimes
against_regimes
horizon_weights
required_inputs
freshness_requirement
strength_scale
conflict_rules
invalidation_templates
parameter_set_overridable
registry_version
```

Signal IDs are machine IDs. Japanese UI labels are display-only.

Signal weights in this document are default design intent. Parameter sets may override weights and thresholds by versioned changes.

## 3. Regime labels targeted by v1

```text
RANGE               -> レンジ
UP_TREND            -> 上昇地合い
DOWN_TREND          -> 下落地合い
LOW_VOL_COMPRESSION -> 低ボラ圧縮
BREAKOUT_WATCH      -> ブレイク監視
REVERSAL_WATCH      -> 反転警戒
HIGH_VOL_CHOP       -> 荒れ相場
UNKNOWN             -> 不明
```

## 4. Source/signal families v1

```text
candle_structure
trend_structure
orderflow
orderbook_liquidity
volatility
cross_venue
source_quality
```

These families are intentionally limited for v1. Parent SourceRegistry remains extensible for derivatives, macro, FX, equities, gold, onchain, session/calendar, news/event, and manual/GPT review sources.

## 5. candle_structure signals

### candle_structure.price_in_range

```text
supports=RANGE
against=BREAKOUT_WATCH,UP_TREND,DOWN_TREND
meaning=Price remains inside a recent range without confirmed break/hold.
required_inputs=OHLCV, recent_high_low, range_bounds
freshness_requirement=warm_or_better
```

Use as evidence that the market is currently range-like, especially when price returns toward the range center or VWAP after boundary tests.

### candle_structure.range_edge_pressure

```text
supports=BREAKOUT_WATCH
against=RANGE
meaning=Price repeatedly approaches or pressures recent range high/low.
required_inputs=OHLCV, range_bounds, touch_count
freshness_requirement=warm_or_better
```

This is watch evidence, not confirmed breakout evidence.

### candle_structure.range_break_hold

```text
supports=BREAKOUT_WATCH,UP_TREND,DOWN_TREND
against=RANGE
meaning=Price breaks a range boundary and holds beyond it across multiple closed candles.
required_inputs=OHLCV, closed_candles, range_bounds, volume_confirmation
freshness_requirement=warm_or_better
```

Direction-specific support depends on break direction.

### candle_structure.wick_rejection

```text
supports=REVERSAL_WATCH,RANGE
against=clean_UP_TREND,clean_DOWN_TREND
meaning=Long wick rejection appears near a boundary or important level.
required_inputs=OHLCV, wick_ratio, level_context
freshness_requirement=warm_or_better
```

Wick rejection is stronger when paired with absorption or orderflow divergence.

### candle_structure.body_expansion

```text
supports=BREAKOUT_WATCH,UP_TREND,DOWN_TREND
against=LOW_VOL_COMPRESSION
meaning=Candle body expands from compression/range and may indicate movement start.
required_inputs=OHLCV, body_size, recent_body_distribution
freshness_requirement=warm_or_better
```

Direction-specific support depends on candle direction and follow-through.

## 6. trend_structure signals

### trend_structure.higher_high_higher_low

```text
supports=UP_TREND
against=RANGE,DOWN_TREND
meaning=Higher highs and higher lows are visible.
required_inputs=OHLCV, swing_points
freshness_requirement=warm_or_better
```

### trend_structure.lower_high_lower_low

```text
supports=DOWN_TREND
against=RANGE,UP_TREND
meaning=Lower highs and lower lows are visible.
required_inputs=OHLCV, swing_points
freshness_requirement=warm_or_better
```

### trend_structure.vwap_upper_persistence

```text
supports=UP_TREND
against=DOWN_TREND
meaning=Price persists above VWAP and pullbacks find support.
required_inputs=OHLCV, VWAP, pullback_context
freshness_requirement=warm_or_better
```

### trend_structure.vwap_lower_persistence

```text
supports=DOWN_TREND
against=UP_TREND
meaning=Price persists below VWAP and rebounds are sold.
required_inputs=OHLCV, VWAP, rebound_context
freshness_requirement=warm_or_better
```

### trend_structure.mean_reversion_to_vwap

```text
supports=RANGE
against=clean_UP_TREND,clean_DOWN_TREND
meaning=Price repeatedly reverts toward VWAP after excursions.
required_inputs=OHLCV, VWAP, excursion_distance
freshness_requirement=warm_or_better
```

## 7. orderflow signals

### orderflow.aggressive_buy_pressure

```text
supports=UP_TREND,BREAKOUT_WATCH
against=DOWN_TREND
meaning=Aggressive buy flow, buy trade streaks, or buy-side volume acceleration appears.
required_inputs=trade_flow_summary, buy_sell_aggressor_estimate, volume_acceleration
freshness_requirement=live_or_warm
```

### orderflow.aggressive_sell_pressure

```text
supports=DOWN_TREND,BREAKOUT_WATCH
against=UP_TREND
meaning=Aggressive sell flow, sell trade streaks, or sell-side volume acceleration appears.
required_inputs=trade_flow_summary, buy_sell_aggressor_estimate, volume_acceleration
freshness_requirement=live_or_warm
```

### orderflow.flow_absorption_buy_side

```text
supports=REVERSAL_WATCH,RANGE
against=DOWN_TREND_continuation
meaning=Sell pressure appears but price fails to progress lower, implying buy-side absorption.
required_inputs=trade_flow_summary, price_response, local_low_context
freshness_requirement=live_or_warm
```

### orderflow.flow_absorption_sell_side

```text
supports=REVERSAL_WATCH,RANGE
against=UP_TREND_continuation
meaning=Buy pressure appears but price fails to progress higher, implying sell-side absorption.
required_inputs=trade_flow_summary, price_response, local_high_context
freshness_requirement=live_or_warm
```

### orderflow.cvd_price_divergence

```text
supports=REVERSAL_WATCH,HIGH_VOL_CHOP
against=clean_UP_TREND,clean_DOWN_TREND
meaning=Cumulative flow and price movement diverge.
required_inputs=CVD_or_proxy, price_response
freshness_requirement=live_or_warm
```

## 8. orderbook_liquidity signals

### orderbook_liquidity.depth_imbalance_bid

```text
supports=short_horizon_UP_TREND,RANGE_support_reaction
against=immediate_DOWN_TREND
meaning=Bid-side depth/replenishment is stronger than ask-side.
required_inputs=orderbook_depth_summary, replenishment_summary
freshness_requirement=live
```

### orderbook_liquidity.depth_imbalance_ask

```text
supports=short_horizon_DOWN_TREND,RANGE_resistance_reaction
against=immediate_UP_TREND
meaning=Ask-side depth/replenishment is stronger than bid-side.
required_inputs=orderbook_depth_summary, replenishment_summary
freshness_requirement=live
```

### orderbook_liquidity.microprice_up_bias

```text
supports=short_horizon_UP_TREND,BREAKOUT_WATCH
against=DOWN_TREND
meaning=Microprice or queue pressure leans upward.
required_inputs=best_bid_ask, depth_summary, microprice
freshness_requirement=live
```

### orderbook_liquidity.microprice_down_bias

```text
supports=short_horizon_DOWN_TREND,BREAKOUT_WATCH
against=UP_TREND
meaning=Microprice or queue pressure leans downward.
required_inputs=best_bid_ask, depth_summary, microprice
freshness_requirement=live
```

### orderbook_liquidity.wide_spread_or_thin_book

```text
supports=HIGH_VOL_CHOP,UNKNOWN
against=high_confidence_clean_regimes
meaning=Spread is wide, depth is thin, or slippage risk is elevated.
required_inputs=spread, depth_summary, liquidity_state
freshness_requirement=live
```

### orderbook_liquidity.liquidity_absorption

```text
supports=REVERSAL_WATCH,RANGE
against=clean_breakout
meaning=Liquidity absorbs one-sided market orders instead of allowing clean continuation.
required_inputs=orderbook_depth_summary, trade_flow_summary, price_response
freshness_requirement=live
```

## 9. volatility signals

### volatility.atr_compression

```text
supports=LOW_VOL_COMPRESSION
against=HIGH_VOL_CHOP
meaning=ATR, true range, candle bodies, or realized volatility compress.
required_inputs=OHLCV, ATR_or_realized_volatility
freshness_requirement=warm_or_better
```

### volatility.atr_expansion_with_direction

```text
supports=UP_TREND,DOWN_TREND,BREAKOUT_WATCH
against=RANGE,LOW_VOL_COMPRESSION
meaning=Volatility expands with directional follow-through.
required_inputs=OHLCV, ATR_or_realized_volatility, direction_context
freshness_requirement=warm_or_better
```

### volatility.atr_expansion_without_direction

```text
supports=HIGH_VOL_CHOP
against=clean_UP_TREND,clean_DOWN_TREND,RANGE
meaning=Volatility expands but direction is unstable or reversing frequently.
required_inputs=OHLCV, ATR_or_realized_volatility, chop_context
freshness_requirement=warm_or_better
```

### volatility.post_spike_instability

```text
supports=HIGH_VOL_CHOP,UNKNOWN
against=high_confidence_normal_regimes
meaning=Immediately after a spike, conditions are unstable and strong predictions should be capped.
required_inputs=OHLCV, spike_detection, spread/liquidity_context
freshness_requirement=warm_or_better
```

## 10. cross_venue signals

v1 treats cross-venue signals as optional/contextual until external source coverage and calibration are stronger.

### cross_venue.venue_agreement

```text
supports=current_primary_regime
against=UNKNOWN
meaning=External venues agree with the local bitFlyer reading.
required_inputs=cross_venue_price_volume_summary
freshness_requirement=warm_or_better
```

### cross_venue.venue_divergence

```text
supports=UNKNOWN,REVERSAL_WATCH,HIGH_VOL_CHOP
against=high_confidence_clean_trend
meaning=bitFlyer and external venues diverge in price/structure/volume behavior.
required_inputs=cross_venue_price_volume_summary, divergence_metric
freshness_requirement=warm_or_better
```

### cross_venue.basis_or_fx_spot_divergence

```text
supports=REVERSAL_WATCH,HIGH_VOL_CHOP,UNKNOWN
against=clean_high_confidence_regime
meaning=FX/spot/external basis divergence makes local-only reading risky.
required_inputs=spot_fx_basis_summary, external_reference_summary
freshness_requirement=warm_or_better
```

## 11. source_quality signals

Source-quality signals are not direction owners. They control confidence caps, UNKNOWN/no-call, and warnings.

### source_quality.live_complete

```text
supports=confidence_cap_release
against=none
meaning=Required inputs are fresh, continuous, and usable.
required_inputs=source_quality_summary
freshness_requirement=live
```

### source_quality.stale_input

```text
supports=UNKNOWN
against=all_high_confidence_regimes
meaning=Input age is too old for the target horizon or family.
required_inputs=source_quality_summary
freshness_requirement=quality_state_only
```

### source_quality.missing_required_source

```text
supports=UNKNOWN
against=all_high_confidence_regimes
meaning=A required source is missing for this horizon/family.
required_inputs=source_quality_summary
freshness_requirement=quality_state_only
```

### source_quality.signal_conflict

```text
supports=UNKNOWN,HIGH_VOL_CHOP
against=high_confidence_primary_regime
meaning=Major signal families disagree and the primary reading should be capped or withheld.
required_inputs=signal_vote_summary
freshness_requirement=quality_state_only
```

## 12. Signal interaction rule

Signals may influence each other through regime scoring, confidence, conflict, and invalidation logic. They must not create hidden recursive computation.

Allowed:

```text
orderflow.aggressive_sell_pressure increases DOWN_TREND vote
orderbook_liquidity.liquidity_absorption weakens clean DOWN_TREND continuation
candle_structure.price_in_range and mean_reversion_to_vwap strengthen RANGE
source_quality.signal_conflict caps confidence and may push UNKNOWN
```

Forbidden:

```text
signal computation calls a family classifier directly
signal A recursively recomputes signal B which recomputes signal A
unrecorded signal influence
```

## 13. Trace requirements

A market-regime trace should preserve at least:

```text
signal_registry_version
parameter_set_id
signal_votes_top_n
signal_conflicts_top_n
source_quality_caps
cross_family_refs_if_used
primary_regime
counter_scenarios
confidence_percent
evidence_quality
invalidation_conditions
watch_points
```

The trace should enable replay to answer:

```text
Which signals drove this regime reading?
Which signals conflicted?
Which signals capped confidence?
Which version of the registry and parameter set were used?
```

## 14. v1 restraint

Do not over-expand v1. Keep the first implementation explainable and testable. Add macro, derivatives, onchain, and news/event signals later through SourceRegistry + signal_registry_v2+ after acquisition and replay/calibration evidence exist.
## 15. Horizon weight v1 reference
<!-- PS_MARKET_REGIME_HORIZON_WEIGHT_V1_LOCK_2026_07_08 -->

Default horizon-aware family weights are fixed in:

```text
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_HORIZON_WEIGHT_V1_2026-07-08.md
```

Signal registry entries define what a signal means. Horizon-weight policy defines how much each family should matter by horizon. Parameter sets may override both weights and thresholds through versioned changes.
