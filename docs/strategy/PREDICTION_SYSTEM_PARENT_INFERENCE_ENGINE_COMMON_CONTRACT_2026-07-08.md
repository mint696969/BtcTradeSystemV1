# path: ./docs/strategy/PREDICTION_SYSTEM_PARENT_INFERENCE_ENGINE_COMMON_CONTRACT_2026-07-08.md
# desc: Parent inference engine common contract for multi-source, multi-family, multi-horizon prediction. Spec-only; no runtime or UI implementation change.
# Prediction System Parent Inference Engine Common Contract

Updated: 2026-07-08 JST
Base: Prediction System Inference Formal Spec / Market Regime Trace and Calibration Spec
Mode: parent contract lock / implementation premise / no runtime behavior change

<!-- PS_PARENT_INFERENCE_ENGINE_COMMON_CONTRACT_LOCK_2026_07_08 -->

```text
ps_parent_inference_engine_common_contract_lock=true
parent_inference_engine_contract=true
bitflyer_first_not_bitflyer_only=true
multi_source_ready=true
multi_prediction_family_ready=true
multi_horizon_ready=true
source_registry_required=true
prediction_family_registry_required=true
parameter_set_registry_required=true
signal_registry_required=true
lead_lag_assumption_is_hypothesis_not_truth=true
source_reliability_calibratable=true
raw_external_data_duplication_forbidden=true
ui_displays_read_models_only=true
market_regime_first_canonical_family=true
read_only=true
non_executing=true
broker_send_enabled=false
order_intent_submitted=false
autotrade_trigger_allowed=false
```

## 1. Purpose

This document fixes the parent/common contract for the Prediction Inference Engine before returning to the market-regime signal registry.

The engine starts with bitFlyer data and market-regime prediction, but the final design is not bitFlyer-only and not market-regime-only. It is a multi-source, multi-family, multi-horizon inference system that produces structured prediction artifacts, evidence, traceability, replay inputs, outcomes, and calibration proposals.

The parent engine does not trade, call broker APIs, render UI, or mutate AutoTrade ledgers. It produces evidence-based prediction artifacts and reviewable read models.

## 2. Definition

```text
Prediction Inference Engine
  = a non-executing multi-source inference system that reads time-series artifacts,
    builds feature bundles and signals,
    produces prediction-family outputs over defined horizons,
    stores traceable evidence and outcomes,
    and supports replay/calibration/parameter-set improvement.
```

The parent engine owns common contracts. Individual prediction families own family-specific labels, signals, outcome rules, and parameter sets.

## 3. Parent components

The common engine is composed of these contracts:

```text
PredictionFamilyRegistry
SourceRegistry
HorizonPolicy
SourceRefContract
FeatureBundleContract
SignalRegistry
ParameterSetRegistry
InferenceRun
PredictionTrace
OutcomeLedger
Calibration
ReadModelContract
```

These contracts must be reusable by market_regime first and later by trend_bias, reversal_zone, volatility_risk, liquidity_quality, breakout_false_break, shock_risk, and future families.

## 4. Prediction family registry

Prediction families are uniquely identified machine domains. UI labels are display-only.

Minimum fields:

```text
prediction_family_id
prediction_family_label
family_role
supported_horizons
output_artifact_family
trace_artifact_family
outcome_rule_version
signal_registry_version
parameter_set_pointer
read_model_contract_version
safety_profile
```

Initial family:

```text
prediction_family_id=market_regime
role=first_canonical_family / tactical_context_priority
```

Future families must use the same parent contracts without changing market-regime history.

## 5. Source registry

The engine must be source-registry driven. New sources must be addable without rewriting UI or existing traces.

Source families may include:

```text
exchange_internal       bitFlyer ticker/board/executions/OHLCV/FX-spot difference
cross_exchange          Binance/Coinbase/OKX/etc. BTC price/volume/spread/basis references
derivatives             futures/perpetual/funding/open_interest/liquidation/basis
macro_market            USDJPY/DXY/rates/equity indices/Nasdaq/S&P500/gold/oil
crypto_market           ETH/SOL/total crypto market/stablecoin flow/BTC dominance
onchain                 exchange flow/miner/whale/onchain summaries
session_calendar        Tokyo/Europe/US sessions/economic calendar/holidays/weekend
news_event              ETF/regulation/exchange incident/major failure/macro event
operator_manual         chart selection/manual review/GPT-assisted review notes
```

A source registry row should include:

```text
source_id
source_family
provider
instrument
canonical_symbol
timezone
update_cadence
expected_latency
freshness_threshold
retention_policy
cost_or_rate_limit
license_note
available_horizons
default_reliability
horizon_weight_hint
lead_lag_assumption
calibration_required
enabled
```

## 6. Lead/lag hypothesis rule

External information must not be assumed to be leading truth.

Allowed lead/lag states:

```text
candidate_leading
coincident
lagging
unknown
context_only
```

A source can strengthen, weaken, cap, or invalidate a prediction only according to its registered role, horizon suitability, freshness, and calibration evidence.

The engine must be able to ask later:

```text
Did this source lead, coincide with, or lag BTC behavior for this horizon/regime during replay?
```

## 7. Source use roles

External and internal sources can play several roles:

```text
support_primary_reading
support_counter_scenario
raise_conflict
lower_confidence_cap
trigger_unknown_or_no_call
supply_event_context
supply_calibration_prior
```

Do not design external sources only as confidence boosters. A good external source often lowers confidence, raises caution, or forces UNKNOWN.

## 8. Horizon-aware source semantics

The parent engine must treat source value as horizon-dependent.

```text
current_to_5m:
  local executable market truth, orderbook, executions, spread, freshness dominate.
  external sources mostly detect divergence, shock, or abnormal context.

15m_to_60m:
  local structure, sustained flow, cross-exchange agreement, derivatives/basis, and volume confirmation become important.

6h_to_24h:
  higher-timeframe structure, volatility regime, derivatives, macro/session context, and replay-calibrated transition statistics dominate.
  instantaneous board/trade bursts are context only.
```

These are policy defaults, not hard-coded classifier constants. Parameter sets may adjust them with versioned evidence.

## 9. Source refs and no raw duplication

Prediction traces must not inline raw market, macro, or external source payloads.

They must store:

```text
source_id
artifact_family
relpath_or_uri
time_range_utc
snapshot_id_or_manifest_ref
schema_version
summary_hash_or_sha256
compact_summary_if_needed
freshness_state
quality_state
```

Raw/canonical source artifacts remain owned by their producing collector/provider artifact family. Prediction artifacts reference them.

## 10. Parameter sets and source reliability

Each prediction family has one active parameter set pointer and may have candidate/shadow sets.

Parameter sets own tunable assumptions:

```text
source_priority_by_horizon
source_reliability_overrides
horizon_weights
confidence_caps
conflict_penalties
feature_thresholds
signal_weights
transition_priors
lead_lag_weighting
calibration_version
```

Used parameter sets are immutable. Changing any of the above creates a new parameter-set version.

## 11. Calibration and source promotion

A source may start as disabled, context-only, candidate, or low-weight. It should earn influence through replay/outcome calibration.

Calibration should answer:

```text
Which horizon does this source help?
Which regime does this source help?
Does it improve hit/partial rates or reduce overconfidence?
Does it create false confidence?
Should it be promoted, demoted, capped, or disabled?
```

Promotion to higher influence should be human-reviewed and recorded in the parameter-set history.

## 12. Read model boundary

The UI reads read models only. It must not recalculate source reliability, feature bundles, classifier output, or parameter-set comparisons during render.

Typical read models:

```text
prediction/<family>/latest.json              machine-readable latest family output
prediction/<family>/latest_cards.json        UI card read model
prediction/<family>/latest_read_model.json   GPT/operator explanation read model
```

## 13. Market-regime as first canonical family

Market-regime is the first family because it is tactical context for other predictions and future strategy selection.

It may inform tactics such as range, trend-follow, breakout watch, reversal watch, risk reduction, or observe-only. It does not itself authorize execution.

```text
market_regime_is_tactical_context=true
market_regime_is_not_order_command=true
market_regime_does_not_grant_autotrade_permission=true
```

## 14. Extension rule

Adding a new source or prediction family must not break old traces.

Required compatibility rules:

```text
new_source_gets_new_source_id
new_signal_gets_new_signal_id
new_parameter_set_gets_new_parameter_set_id
old_parameter_sets_remain_readable
old_traces_keep their original versions
schema changes are additive or versioned
UI labels are not canonical IDs
```

## 15. Implementation order

After this parent contract is locked, return to market-regime design in this order:

```text
1. market_regime signal_registry_v1
2. market_regime horizon_weight_v1
3. market_regime outcome_rule_v1
4. implementation first slice: remove UI render-path classifier / D-hot preview inference
```

No runtime or broker/AutoTrade behavior is enabled by this document.
## 16. Cross-family influence and cycle prevention
<!-- PS_CROSS_FAMILY_INFLUENCE_NO_CYCLE_LOCK_2026_07_08 -->

Prediction families may influence each other, but circular inference inside the same run is forbidden.

The intended model is not isolated independent cards. The intended model is a coordinated inference graph:

```text
market_regime may influence trend_bias / reversal_zone / volatility_risk / liquidity_quality / execution_quality.
trend_bias, volatility_risk, liquidity_quality, and other family outputs may also become context for market_regime.
```

However, this must be implemented as an acyclic, versioned, snapshot-based graph.

Hard rule:

```text
same_run_circular_dependency_forbidden=true
```

Allowed dependency forms:

```text
1. Prior snapshot dependency
   A family may read another family's latest closed artifact from a previous run or previous generation time.

2. Two-pass orchestrated dependency
   Parent engine may run base families first, freeze their outputs, then run dependent families using the frozen snapshot.

3. Context-only dependency
   A family may use another family output only as a confidence cap, conflict, scenario context, or source_ref, not as recursive live input.

4. Parameter-set declared dependency
   Cross-family dependency must be declared in parameter_set / family registry and preserved in trace.
```

Forbidden dependency forms:

```text
market_regime_current_run -> trend_bias_current_run -> market_regime_current_run
ui_render -> family_A_classifier -> family_B_classifier -> family_A_classifier
implicit import-time dependency between family classifiers
unrecorded use of another family output
```

Each family trace must record cross-family references:

```text
cross_family_refs:
  - family_id
  - prediction_id
  - run_id
  - generated_at_utc
  - horizon_key
  - artifact_ref
  - use_role=context|support|conflict|confidence_cap|invalidation|tactical_context
  - dependency_policy=prior_snapshot|two_pass_frozen|context_only
```

The parent orchestrator owns dependency order. Family classifiers do not call each other recursively.

Recommended initial dependency graph:

```text
source_quality -> all families as cap/veto
market_regime -> trend_bias / reversal_zone / breakout_false_break / liquidity_quality as tactical context
volatility_risk -> market_regime as conflict/cap/context
liquidity_quality -> market_regime as conflict/cap/context
trend_bias -> market_regime as prior-snapshot context only
```

Market-regime remains the first canonical family, but it is not an isolated truth source. It participates in a controlled inference graph.
