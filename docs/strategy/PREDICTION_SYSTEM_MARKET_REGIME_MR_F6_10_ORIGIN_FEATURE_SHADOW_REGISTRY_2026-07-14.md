# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_10_ORIGIN_FEATURE_SHADOW_REGISTRY_2026-07-14.md
# desc: Defines the MR-F6.10 analysis-backed shadow-only registry for origin feature parameters.

# Prediction System MarketRegime MR-F6.10 Origin Feature Shadow Registry

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Analysis evidence

Source:

```text
D:\btc_ts_hot\data\derived\warroom\candles\exchange=bitflyer\symbol=FX_BTC_JPY\timeframe=60s\closed.jsonl
```

Persisted analysis evidence:

```text
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_10_ORIGIN_FEATURE_PARAMETER_ANALYSIS_EVIDENCE_2026-07-14.md
```

Evidence summary:

```text
source rows: 20160
analysis window: 2026-06-29T07:38:00Z .. 2026-07-13T23:05:00Z
contiguous segments: 420
usable segments: 71
rolling volatility samples: 10516
```

## Registry candidates

Four MA pairs are crossed with two volatility bands, producing eight explicit shadow candidates.

```text
MA pairs:
  3 / 10
  5 / 20
  10 / 30
  15 / 60

volatility bands:
  interquartile = p25 / p75 = 4.47257112 / 7.35462997 bps
  central_80_percent = p10 / p90 = 3.79525581 / 10.04311125 bps
```

No candidate is active or selected for runtime. Retrieval requires an exact candidate ID.

## Safety

```text
active_candidate_count=0
runtime_selected_candidate_count=0
live_parameter_apply_allowed=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
feature_builder unchanged
D-hot write=false
scheduler registration=false
```

MR-F6.11 may evaluate these eight candidates against the mandatory baselines. It must not select a runtime candidate without same-window evidence.
