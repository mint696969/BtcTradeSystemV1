# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_HORIZON_WEIGHT_V1_2026-07-08.md
# desc: Market-regime horizon weight v1. Spec-only; fixes initial horizon-aware weighting philosophy, liquidity/orderbook history priority, and technical-structure role.
# Market Regime Horizon Weight v1

Updated: 2026-07-08 JST
Base: Market Regime Signal Registry v1 / Market Regime Trace and Calibration Spec
Mode: horizon-weight specification lock / no runtime behavior change

<!-- PS_MARKET_REGIME_HORIZON_WEIGHT_V1_LOCK_2026_07_08 -->

```text
ps_market_regime_horizon_weight_v1_lock=true
market_regime_only=true
horizon_weight_version=market_regime_horizon_weight.2026_07_08.v1
parameter_set_overridable=true
liquidity_history_priority=true
orderbook_transition_priority=true
confirmed_technical_structure_priority=true
weights_are_initial_design_not_calibrated_truth=true
runtime_code_changed=false
ui_classifier_invocation_allowed=false
broker_send_enabled=false
order_intent_submitted=false
autotrade_trigger_allowed=false
```

## 1. Purpose

This document locks the initial horizon-aware weighting philosophy for market-regime inference.

The weights here are not eternal truth. They are the v1 design baseline. Parameter sets may override them by versioned changes, and calibration may later propose changes based on outcome/replay evidence.

## 2. Core operator thesis

The market-regime engine must treat the following as important evidence for future market reading:

```text
past-to-current liquidity behavior
orderbook/depth transition over time
spread and thin-book changes
replenishment / disappearance / absorption of liquidity
execution flow interacting with orderbook liquidity
confirmed historical price/technical structure
human-visible technical indicators that may influence participant behavior
```

Rationale:

```text
Orderbook and liquidity transitions expose immediate supply/demand pressure, participant intent, stop/run behavior, absorption, and behavior of other algorithms or AI strategies.
Confirmed historical price structure and technical indicators matter because human and systematic participants react to them.
Neither orderbook nor technicals alone are sufficient; the engine must combine them by horizon.
```

## 3. Weight scale

Use a coarse scale in v1:

```text
0.00 = unused
0.10 = minor context
0.25 = supporting
0.50 = important
0.75 = primary
1.00 = dominant / hard gate or cap
```

Exact numeric values are defaults only. Parameter sets own final active values.

## 4. Family weights by horizon

### current

```text
source_quality        = 1.00
orderbook_liquidity   = 1.00
orderflow             = 0.90
volatility            = 0.60
candle_structure      = 0.50
trend_structure       = 0.25
cross_venue           = 0.25
```

Current regime should be driven by live market truth: board, spread, liquidity, executions, and freshness. Technical structure provides context but must not override stale or broken live evidence.

### 5m

```text
source_quality        = 1.00
orderbook_liquidity   = 0.85
orderflow             = 0.85
candle_structure      = 0.60
volatility            = 0.60
trend_structure       = 0.40
cross_venue           = 0.35
```

Five-minute regime still relies heavily on orderbook and orderflow transitions, but candle/volatility confirmation becomes more important.

### 15m

```text
source_quality        = 1.00
candle_structure      = 0.80
trend_structure       = 0.75
orderflow             = 0.65
volatility            = 0.65
orderbook_liquidity   = 0.50
cross_venue           = 0.50
```

Fifteen-minute regime should combine human-visible structure with sustained flow and liquidity behavior. Instantaneous board pressure alone should not dominate.

### 30m

```text
source_quality        = 1.00
trend_structure       = 0.80
candle_structure      = 0.75
volatility            = 0.70
orderflow             = 0.55
cross_venue           = 0.55
orderbook_liquidity   = 0.35
```

Thirty-minute regime emphasizes confirmed structure, volatility state, and persistent flow. Board transitions remain useful as context or invalidation.

### 60m

```text
source_quality        = 1.00
trend_structure       = 0.85
volatility            = 0.75
candle_structure      = 0.70
cross_venue           = 0.60
orderflow             = 0.40
orderbook_liquidity   = 0.25
```

One-hour regime must not overreact to current board. It should prioritize structure, volatility, and cross-source agreement while still recording liquidity conflicts.

### 6h

```text
source_quality        = 1.00
trend_structure       = 0.90
volatility            = 0.85
candle_structure      = 0.75
cross_venue           = 0.70
orderflow             = 0.20
orderbook_liquidity   = 0.10
```

Six-hour regime treats current orderbook/orderflow as low-weight context. Long-horizon structure, volatility regime, and cross-source context dominate.

### 12h

```text
source_quality        = 1.00
trend_structure       = 0.90
volatility            = 0.85
candle_structure      = 0.70
cross_venue           = 0.75
orderflow             = 0.15
orderbook_liquidity   = 0.05
```

Twelve-hour regime should mainly read higher-timeframe structure and broader market context. Local board is not a direction owner.

### 24h

```text
source_quality        = 1.00
trend_structure       = 0.90
volatility            = 0.85
cross_venue           = 0.80
candle_structure      = 0.65
orderflow             = 0.10
orderbook_liquidity   = 0.05
```

Twenty-four-hour regime is broad context. Future macro/derivatives/session sources may become important through future registry/parameter-set versions.

## 5. Liquidity/orderbook history principle

For current through 15m, orderbook and liquidity history are not one-tick facts. They must be interpreted as transitions.

Important derived concepts:

```text
liquidity_replenishment
liquidity_disappearance
depth_imbalance_persistence
spread_widening_or_normalization
microprice_drift
absorption_against_aggressive_flow
thin_book_break_risk
range_edge_liquidity_behavior
```

The engine should prefer time-window summaries over a single current snapshot:

```text
lookback_30s
lookback_1m
lookback_3m
lookback_5m
lookback_15m
```

Do not overfit to a single board snapshot. Store source refs and compact summaries so replay can verify whether the board transition mattered.

## 6. Technical-structure principle

Confirmed historical price and technical structure are important because participants react to them.

Examples:

```text
range high / range low
recent swing high / swing low
VWAP
moving average slope
ATR / realized volatility
wick/body ratio
volume confirmation
break-and-hold / false-break behavior
support/resistance interaction
```

Technical indicators must be treated as human/systematic participant context, not magical prediction. Their importance increases with horizon from 15m onward.

## 7. Conflict behavior

When live liquidity/orderflow and confirmed structure conflict, do not force a high-confidence answer.

Examples:

```text
orderflow sells aggressively but price remains in range with buy absorption -> RANGE with downside conflict or REVERSAL_WATCH, not automatic DOWN_TREND
price breaks upward but spread widens and book thins -> BREAKOUT_WATCH with risk cap, not high-confidence UP_TREND
higher-timeframe uptrend but current board collapses -> UP_TREND broad context with short-horizon caution/conflict
```

Conflicts should appear in detail/read model and trace.

## 8. Source-quality cap

Source quality is a hard cap/veto family, not a directional family.

Default caps:

```text
required_live_source_missing -> max_confidence_50
collector_stale_for_horizon -> max_confidence_40
major_signal_conflict -> max_confidence_60
wide_spread_or_thin_book -> max_confidence_65 unless regime=HIGH_VOL_CHOP or UNKNOWN
uncalibrated_external_context_only -> max_confidence_70 when it is the main support
```

Parameter sets may tune these caps.

## 9. Trace requirements

Market-regime traces should preserve horizon weights and source-family contributions:

```text
horizon_weight_version
parameter_set_id
source_family_scores
source_family_weights_used
liquidity_history_summary_ref
orderbook_transition_summary_ref
technical_structure_summary_ref
signal_votes_top_n
signal_conflicts_top_n
confidence_caps_applied
```

This lets replay and GPT review answer:

```text
Was the prediction driven by board/liquidity, orderflow, price structure, volatility, cross-venue context, or source-quality caps?
Did the source family weight make sense for this horizon?
Should the parameter set be changed?
```

## 10. Future extension

Future source families such as derivatives, macro, FX, equities, gold, onchain, session/calendar, and news/event should be added through SourceRegistry and parameter sets.

Do not add them by changing UI card logic. Do not back-edit old traces.

Future versions may add family weights such as:

```text
derivatives_context
macro_market
session_calendar
news_event
onchain
operator_manual_review
```

v1 deliberately keeps them out of the main weight table until source acquisition and calibration exist.
## 11. Outcome rule v1 reference
<!-- PS_MARKET_REGIME_OUTCOME_RULE_V1_LOCK_2026_07_08 -->

Horizon weights must be evaluated by outcome/replay using:

```text
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_OUTCOME_RULE_V1_2026-07-08.md
```

Calibration should detect source-family overweight/underweight by horizon, regime, parameter_set_id, and confidence bucket.
