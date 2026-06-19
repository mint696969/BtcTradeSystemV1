# path: ./docs/strategy/PREDICTION_SYSTEM_PS_E1_FEATURE_DEPTH_PLAN_BTC_BITFLYER_2026-06-19.md
# desc: PS-E1 safe feature-depth plan for standalone Prediction System contracts.

# Prediction System PS-E1 Feature-Depth Plan

Updated: 2026-06-19 JST  
Profile: BtcTradeSystem  
Scope: standalone Prediction System only  
Status: contract-only / context-only / non-executing

## Decision

PS-E1 starts feature-depth strengthening with contracts only.

The first slice adds a standalone `feature_depth.py` module for already-provided orderbook/tradeflow/liquidity-like summaries. It does not collect data and does not wire those features into rule-based direction ownership.

## Why contract first

The weak/proxy-only families after PS-F/PS-H/PS-I/PS-D are:

```text
liquidity_execution_quality
breakout_false_break
algorithmic_participant_footprint
cross_venue_confirmation lead/lag
opportunity_participation outcome/near-miss
```

Strengthening them requires orderbook/tradeflow/liquidity inputs, but adding data collection or Collector runtime dependency now would violate the standalone boundary. Therefore PS-E1 defines the safe input contract first.

## PS-E1 implementation boundary

Added:

```text
btcts_next/src/btcts/prediction/feature_depth.py
FeatureDepthInputRef
OrderBookFeatureSummary
TradeFlowFeatureSummary
FeatureDepthSnapshot
build_feature_depth_snapshot(...)
```

Exported from:

```text
btcts_next/src/btcts/prediction/__init__.py
```

## Conservative policy

```text
FeatureDepthSnapshot.primary_direction_owner=False
FeatureDepthSnapshot.usable_for_primary_short_horizon=False
FeatureDepthSnapshot.context_only=True
FeatureDepthSnapshot.read_only=True
FeatureDepthSnapshot.non_executing=True
```

The snapshot can support future rule strengthening, but it must not become the primary short-horizon direction owner in PS-E1.

## Explicit non-goals

```text
No live collection.
No external API call.
No Collector runtime import.
No AutoTrade import.
No broker/private API.
No artifact writes.
No AutoTrade decision append.
No command ledger append.
No mode apply.
No Pre-Armed grant behavior.
No direct rule_based_v0 scoring change.
```

## Next possible slices

```text
PS-E2: integrate provided FeatureDepthSnapshot as context/warning into liquidity_execution_quality only
PS-E3: add orderbook pressure context into breakout_false_break and algorithmic_participant_footprint as warnings only
PS-E4: add tradeflow context as warning/confirmation only, still not primary direction owner
```
