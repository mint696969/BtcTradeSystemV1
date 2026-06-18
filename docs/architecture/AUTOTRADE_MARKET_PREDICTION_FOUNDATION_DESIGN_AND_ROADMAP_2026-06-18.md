# path: ./docs/architecture/AUTOTRADE_MARKET_PREDICTION_FOUNDATION_DESIGN_AND_ROADMAP_2026-06-18.md
# desc: AutoTrade market prediction foundation design and roadmap. Separates collection, inference, and trading responsibilities.

# AutoTrade Market Prediction Foundation Design and Roadmap

Updated: 2026-06-18 JST  
Profile: BtcTradeSystem  
Branch context: docs/phase2-handoff-sync  
Status: design / roadmap / non-executing

## 1. Decision

Pause deeper execution-enablement work after S117-S120 and prioritize the AutoTrade prediction foundation.

S117-S120 established a safe pre-execution chain:

```text
authorization grant/status
-> authorization record persistence preflight/status
-> mode apply preview/status
-> runtime integration readiness/status
```

The next priority is the trading brain:

```text
market data breadth
multi-horizon inference
prediction-family parameter sets
forecast outcome scoring
operator-visible reasoning
then reconnect the resulting inference bundle to AutoTrade
```

This document does not authorize broker execution, real orders, private API calls, mode apply execution, command ledger append, approval ledger append, or UI command buttons.

## 2. Final target

Build a 24-hour AutoTrade decision system that can reason like a layered market analyst while keeping responsibilities separated.

The system should answer:

```text
What market state are we in?
Which side has trend advantage?
Where are likely reaction / reversal zones?
Is volatility tradable or dangerous?
Is FX execution quality good enough?
Is the breakout real or likely a trap?
Are we waiting too much or correctly avoiding bad trades?
Do external venues confirm or reject the bitFlyer move?
Does broader macro context alter risk?
Would a human chart reader see support, resistance, breakout, or rejection?
Are algorithmic / AI participants leaving trap-like footprints?
```

## 3. Horizon design

| Layer | Horizons | Role | Typical use | Must not do |
|---|---:|---|---|---|
| Execution micro | 15s / 30s / 60s / 180s | Entry timing and veto layer | spread/slippage guard, wall flip, flow burst, cancel/reprice hint | Override the core thesis alone |
| Primary trade | 5m / 15m / 30m | Main trading thesis | long/short/range/no-edge, reversal, breakout, opportunity | Ignore execution quality |
| Context | 1h / 4h / 1d | Higher-timeframe context | major support/resistance, risk budget, large regime, daily volatility | Become an early hard blocker by default |

The data contracts should support all layers from the beginning:

```text
execution_micro_horizons_sec = (15, 30, 60, 180)
primary_trade_horizons_sec = (300, 900, 1800)
context_horizons_sec = (3600, 14400, 86400)
```

## 4. Prediction-family table

| ID | Prediction family | Main question | Key outputs | Main inputs | Parameter-set family |
|---:|---|---|---|---|---|
| 1 | Market-regime prediction | What kind of market is this? | regime_label, confidence, blockers, drivers | OHLCV, volatility, liquidity, pressure, Spot-FX divergence | RegimePredictionParameterSet |
| 2 | Trend-bias prediction | Long, short, range, or no edge? | trend_bias, trend_strength, expected_direction, move_bucket | returns, MA slope, trade_delta, imbalance, cross-venue lead/lag | TrendPredictionParameterSet |
| 3 | Reversal-zone prediction | Where is reaction likely? | zone_low, zone_high, invalidation_price, reaction_type | recent high/low, range boundary, VWAP, walls, absorption, volatility exhaustion | ReversalPredictionParameterSet |
| 4 | Volatility / risk prediction | Is the move tradable and how large? | volatility_state, expected_move_range, risk_level, stop_width_hint, size_multiplier_hint | realized volatility, ATR, range width, shock detection | VolatilityRiskPredictionParameterSet |
| 5 | Liquidity / execution-quality prediction | Can FX execution be safe enough? | execution_quality, spread_risk, slippage_risk, book_thinness, cancel_reprice_risk | spread, depth, wall persistence, micro flow, FX book stability | LiquidityExecutionQualityParameterSet |
| 6 | Breakout / false-break prediction | Is the break real or a trap? | breakout_probability, false_break_risk, confirmation_state | range boundary, volume, retest, wick, cross-venue confirmation | BreakoutFalseBreakPredictionParameterSet |
| 7 | Opportunity / participation prediction | Are we waiting correctly or missing edge? | opportunity_score, near_miss_reason, entry_quality_gap, exploration_candidate | blocked reasons, near-miss history, outcome ledger, threshold gaps | OpportunityParticipationParameterSet |
| 8 | Cross-venue confirmation prediction | Do global venues confirm bitFlyer? | global_agreement, bitflyer_lead_lag, basis_dislocation, external_volume_confirmation | Binance, Coinbase, Kraken, Bybit, CME references | CrossVenueConfirmationParameterSet |
| 9 | Macro-risk context prediction | Does broader risk context change trade permission? | risk_on_off, macro_event_window, usd_jpy_pressure, index_correlation_warning | USD/JPY, DXY proxy, yields, Nasdaq/S&P, Gold, calendar | MacroRiskContextParameterSet |
| 10 | Human technical structure prediction | What would a human chart reader see? | support_resistance, range_boundary, retest_state, HH/LL structure, wick_rejection | candles, volume, VWAP, MA, recent highs/lows | HumanTechnicalStructureParameterSet |
| 11 | Algorithmic participant footprint prediction | Is this move trap-like or bot-driven? | footprint_score, liquidity_mirage_risk, wall_vanish_risk, stop_run_risk, overshoot_risk, crowding_risk | orderbook updates, wall persistence, cross-venue sync, reaction speed | AlgorithmicParticipantFootprintParameterSet |

All families are signal / inference families only. They do not place orders and do not change AutoTrade modes.

## 5. Information sources

| Source family | Examples | Use | Initial boundary |
|---|---|---|---|
| bitFlyer FX execution market | FX_BTC_JPY board, executions, ticker, private state later | execution target, execution-quality inference | FX is the only planned real execution market |
| bitFlyer Spot reference | BTC_JPY board, executions, ticker | local Spot signal, Spot-FX basis | reference/signal only |
| Global spot venues | Binance, Coinbase, Kraken | global reference price, volume confirmation, lead/lag | public data only; no external execution |
| Global derivatives venues | Binance Futures, Bybit, CME BTC futures | funding, open interest, basis, futures-led moves | public data only; no external execution |
| Human chart indicators | OHLCV, support/resistance, MA, VWAP, ATR, candle shape | technical structure and longer context | deterministic feature generation first |
| Macro / risk context | USD/JPY, DXY proxy, US yields, Nasdaq/S&P, Gold, economic calendar | risk modifier, avoid-new-entry windows | context and risk gating first, not direction engine |
| News / events | exchange incidents, regulation, ETF/institutional headlines, scheduled macro events | halt/warning/context | high-noise; initially warning only |

## 6. Responsibility separation

| Layer | Responsibility | Proposed / existing package boundary | Reads | Writes | Forbidden |
|---|---|---|---|---|---|
| Collection | Acquire public and local market data, preserve raw/canonical records | existing `btcts_next/src/btcts/collector_vnext/`, existing `btcts_next/src/btcts/processing/` | external public APIs, exchange WS/REST, configured data roots | raw/canonical market data, source status, freshness status | strategy decisions, broker orders, mode changes |
| Feature generation | Convert canonical data into reusable features | existing `btcts_next/src/btcts/processing/features/`, proposed `btcts_next/src/btcts/prediction/features/` | canonical market data | feature store rows, feature diagnostics | broker calls, private account actions |
| Inference | Build prediction-family outputs and confidence/blockers | proposed `btcts_next/src/btcts/prediction/` | feature store, parameter sets, source registry | prediction snapshots, inference bundles, forecast ledgers | direct external API collection, broker orders, mode changes |
| Evaluation / learning loop | Score forecasts and parameter sets by horizon/family | proposed `btcts_next/src/btcts/prediction/evaluation/` | predictions, outcome windows, trade outcomes later | outcome ledger, calibration reports | live mutation of parameters without versioning |
| AutoTrade decision | Consume sealed inference bundle and decide WAIT/WATCH/ENTRY/EXIT candidate | existing `btcts_next/src/btcts/autotrade/` | inference bundle, runtime state, risk/account state | decision ledger, candidate action, risk result | fetching external public data directly, bypassing inference bundle |
| Execution control | Apply mode/risk/execution gates after authorization | existing `btcts_next/src/btcts/autotrade/` execution/risk/mode packages | decision, risk, operator authorization | commands / orders only after explicit later boundary | hidden execution, unapproved mode apply |
| Operator UI | Display status, inference, blockers, and review packets | existing `btcts_next/src/btcts/apps/operator_ui/` | read-only status artifacts | display state only unless later explicit UI command boundary | hidden order placement or mode buttons |

Hard rule:

```text
Collector does not trade.
Prediction does not trade.
AutoTrade does not scrape public market data directly.
Execution does not invent market predictions.
UI does not secretly execute.
```

## 7. Folder-structure proposal

This is a proposed target structure. It should be introduced incrementally with guards.

```text
btcts_next/src/btcts/prediction/
  __init__.py
  horizons.py
  source_registry.py
  contracts.py
  parameter_sets.py
  feature_registry.py
  inference_bundle.py
  families/
    regime.py
    trend.py
    reversal.py
    volatility_risk.py
    liquidity_execution_quality.py
    breakout_false_break.py
    opportunity_participation.py
    cross_venue_confirmation.py
    macro_risk_context.py
    human_technical_structure.py
    algorithmic_participant_footprint.py
  features/
    ohlcv.py
    basis.py
    technical.py
    volatility.py
    orderbook_dynamics.py
    tradeflow_dynamics.py
    cross_venue.py
    macro_context.py
  evaluation/
    forecast_ledger.py
    outcome_ledger.py
    scoring.py
    calibration.py
    drift.py
```

Data-artifact target layout:

```text
D:\btc_ts_hot\prediction\features\...
D:\btc_ts_hot\prediction\inference_bundles\...
D:\btc_ts_hot\prediction\forecast_ledgers\...
D:\btc_ts_hot\prediction\outcome_ledgers\...
D:\btc_ts_hot\prediction\source_status\...
E:\btc_ts\prediction_archive\...
```

Use hot root for latest runtime artifacts and cold root for archive/copy validation.

## 8. Extensibility requirements

| Requirement | Design rule | Checkpoint |
|---|---|---|
| New prediction family can be added | Family registry + common output contract | adding a family does not modify AutoTrade execution code |
| New horizon can be added | Horizon table and scoring table are data-driven | no hard-coded 5m-only contract remains in new foundation |
| New public source can be added | Source adapter + source registry + freshness contract | no direct source calls from AutoTrade |
| New indicator can be added | Feature registry with feature_family and version | indicator can be disabled without breaking inference bundle |
| New parameter set can be tested | Versioned immutable parameter-set family | no silent live mutation |
| New scoring method can be added | Outcome ledger keeps raw outcome and score metadata | old scores remain reproducible |
| New model type can be added later | Rule-based first, model metadata later | output remains explainable and comparable |
| Safety policy can veto | Inference outputs include blockers/warnings | AutoTrade can wait without losing reasons |

## 9. Extra design items beyond the prediction families

| Item | Why it matters | Initial implementation |
|---|---|---|
| Data quality scoring | Bad data creates false predictions | source freshness, continuity, trust_state, missing-window blockers |
| Feature registry | Prevent feature sprawl and hidden dependencies | feature_id, family, version, required sources, horizons |
| Experiment / evaluation registry | Avoid parameter tuning by memory | parameter set, horizon, data window, score, notes |
| Calibration report | Confidence must mean something | hit rate by confidence/family/horizon |
| Drift detection | Market microstructure changes | score degradation, source distribution shift |
| Explainability bundle | Operator must know why a trade is proposed | top drivers, blockers, horizon agreement/disagreement |
| Cost and latency model | Directional edge can be killed by spread/slippage | estimated edge minus costs and slippage |
| Fallback mode | Degraded data should produce WAIT, not unsafe trade | degraded_inference_state with blocker summary |

## 10. Roadmap

| Milestone | Goal | Scope | Checkpoints | Guard / exit criteria |
|---|---|---|---|---|
| GJ / S121 | Fix architecture and roadmap | this document + guard | all horizons, 11 families, separation, extensibility, no execution | structural guard closes |
| GK / S122 | Prediction contracts foundation | horizon model, prediction family enum, common prediction output, inference bundle skeleton | micro/core/context horizons represented; outputs include confidence/blockers/drivers | unit tests for serialization and no autotrade execution imports |
| GL / S123 | Parameter-set family skeletons | 11 versioned parameter-set dataclasses / defaults | immutable, status/version fields, family IDs | tests prove each family has parameter set and no silent mutation |
| GM / S124 | OHLCV multi-timeframe foundation | 1m/5m/15m/30m/1h/4h/1d candle aggregation contract | candle rows with source, freshness, gaps | guard with synthetic trades/ticks validates candles |
| GN / S125 | Feature registry and source quality | source registry, feature registry, data-quality score | trust/freshness/continuity blockers visible | tests for missing/stale/gapped data |
| GO / S126 | Human technical indicators | support/resistance, range, MA slope, VWAP, ATR, wick/body features | deterministic features with horizon metadata | tests for simple known candle patterns |
| GP / S127 | Cross-venue public data foundation | public source adapter contracts and stored source status | external data is reference-only; no external execution config | guard blocks private/execution credentials and broker calls |
| GQ / S128 | Spot-FX basis and divergence features | bitFlyer Spot/FX and global reference basis | basis, lead/lag, premium/discount | tests for divergence cases |
| GR / S129 | Prediction-family rule-based v0 | implement simple v0 outputs for 11 families | every family returns horizon-indexed output with drivers/blockers | tests for ready/blocked and explainability |
| GS / S130 | Multi-horizon forecast ledger | record predictions by family/horizon/source/parameter set | forecast IDs, target times, non-mutating append policy | dry-run/preflight first, then controlled append later |
| GT / S131 | Outcome ledger and scoring | score 15s..1d predictions after target horizon | hit/miss/partial, MFE/MAE, usefulness, calibration | tests with synthetic outcomes |
| GU / S132 | Calibration and missed-opportunity reports | reports by family/horizon/regime/parameter set | wait-too-much, near-miss, blocked reason ranking | report guard produces stable summary |
| GV / S133 | Inference bundle to AutoTrade Shadow | AutoTrade consumes sealed inference bundle, not raw sources | decision rationale includes prediction family outputs | no broker, no mode apply, decision ledger only |
| GW / S134 | Paper / replay validation | replay predictions and decisions against historical windows | family contribution and cost-aware performance | replay guard and performance report |
| GX / S135 | Pre-Armed integration return | reconnect prediction readiness to S117-S120 chain | operator readiness includes inference quality | still no live execution unless later explicit boundary |

## 11. Connection back to AutoTrade

AutoTrade should consume one sealed inference bundle:

```text
InferenceBundle
  generated_at
  source_quality_summary
  horizon_summary
  family_outputs
  cross_family_agreement
  risk_context
  operator_explanation
  blockers
  warnings
```

Then AutoTrade strategy/risk can map it to candidate decisions:

| Inference condition | AutoTrade response |
|---|---|
| trend long, regime trend, execution quality good, context not dangerous | ENTRY_BUY candidate |
| trend short, regime trend, execution quality good, context not dangerous | ENTRY_SELL candidate |
| false-break risk high | WATCH only or avoid chase |
| reversal zone near with weak trend | wait for reaction / WATCH_REVERSE |
| volatility shock or liquidity poor | NO_NEW_ENTRY / HALT_NEW depending severity |
| opportunity score high but one blocker remains | WATCH with near-miss reason |
| data quality poor | WAIT with explicit data blocker |
| algorithmic footprint trap risk high | reduce size / wait confirmation / avoid chase |

The connection must remain one-way:

```text
collection -> features -> prediction/inference -> autotrade decision -> risk/execution gates
```

No lower layer should call upward into AutoTrade.

## 12. Non-permissions

This roadmap does not permit:

```text
broker execution
real orders
private API calls
mode apply execution
record append execution
command ledger append execution
approval ledger append execution
UI command buttons
watchdog/autonomous execution loop
market manipulation
spoofing
quote stuffing
abusive order behavior
```

Algorithmic participant footprint prediction may observe suspected algorithmic behavior, but BTC-TS must not imitate manipulative behavior.
