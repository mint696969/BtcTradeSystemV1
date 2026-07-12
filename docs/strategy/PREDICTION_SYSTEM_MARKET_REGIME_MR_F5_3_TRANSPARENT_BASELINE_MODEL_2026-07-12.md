# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_3_TRANSPARENT_BASELINE_MODEL_2026-07-12.md
# desc: MR-F5.3 design and safety boundary for the family-owned transparent shadow future MarketRegime baseline.

# Prediction System MarketRegime MR-F5.3 Transparent Baseline Model

Updated: 2026-07-12 JST
Status: implementation slice prepared
Scope: pure shadow-only baseline model

## Responsibility

The model accepts explicit per-horizon regime scores, feature-family availability, source/origin timestamps, origin current state, and feature snapshot identity. It returns the accepted MR-F5.1 immutable forecast contract.

It does not read D-hot, build features, invoke the current-state estimator, project legacy `forecast_records`, write artifacts, or replace canonical labels.

## Transparent decision rule

```text
1. validate exact canonical horizon and no-lookahead timestamp cutoff
2. require every MR-F5.2 required feature family
3. rank non-UNKNOWN regime scores
4. normalize scores by positive score total
5. require minimum top score and top-vs-runner margin
6. find shortest path through explicit family-owned transition adjacency
7. emit FORECAST or explicit ABSTAIN
```

Thresholds are deterministic first-version baseline parameters:

```text
5m-60m:
  minimum_normalized_top=0.34
  minimum_normalized_margin=0.08

6h-24h:
  minimum_normalized_top=0.30
  minimum_normalized_margin=0.06
```

These are not calibrated probabilities and are not promotion criteria.

## Transition path

The path uses the accepted MR-F4 adjacency semantics but is independently owned by the future baseline. It does not mutate or persist current state. For example:

```text
LOW_VOL_COMPRESSION -> BREAKOUT -> UP_TREND
RANGE -> HIGH_VOL_CHOP -> PANIC_SPIKE
UP_TREND -> REVERSAL_WATCH -> DOWN_TREND
```

## Abstention

Explicit abstention occurs for:

```text
required feature family missing
fewer than two ranked non-UNKNOWN candidates
top score below horizon threshold
score margin below horizon threshold
no valid future transition path
```

## Safety

```text
shadow_only=true
canonical_future_label_replacement=false
current_state_behavior_change=false
d_hot_read=false
d_hot_write=false
writer_change=false
ui_change=false
scheduler_change=false
calibrated_probability_claim=false
broker_private_api=false
autotrade=false
order_submission=false
```
