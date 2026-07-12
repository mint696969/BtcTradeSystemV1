# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_2_TARGET_DEFINITION_AND_FEATURE_AVAILABILITY_2026-07-12.md
# desc: MR-F5.2 target-definition policy and representative repository/D-hot feature-availability audit.

# Prediction System MarketRegime MR-F5.2 Target Definition and Feature Availability

Updated: 2026-07-12 JST
Status: implementation slice prepared
Scope: pure target-definition policy and read-only legacy availability-gap audit

## Repository findings

```text
forecast_records_reader:
  filters family=market_regime
  preserves every available horizon
  does not define future targets

feature_builder:
  consumes exact-horizon labels and legacy score/strength/reference metrics
  blocks unusable records
  applies source freshness checks
  does not create outcome targets

regime_classifier:
  current horizon remains MR-F4 owned
  future exact horizon reads compatibility forecast_records
  missing exact horizon fails closed
  stale <=3600 may use bounded current-L4 compatibility fallback
  stale >3600 fails closed

outcome_resolver:
  expires generated_at + horizon_sec
  supports hit/partial/miss/invalidated/unknown
  does not currently include target_definition_version/model_id/logic_version in outcome identity
```

## Representative D-hot findings

Source root: `D:\btc_ts_hot`

```text
latest_manifest.generated_at=2026-07-10T15:27:22Z
manifest_record_count=132
forecast_records_bytes=965433
legacy_horizons_seen_in_bundle_id=15,30,60,300,600,900,1800,3600,14400,21600,43200,86400
canonical_MR-F5_horizons=300,900,1800,3600,21600,43200,86400
```

The representative MarketRegime record exposes `generated_at`, `horizon_sec`, `logic_version`, `parameter_set_id`, `primary_label`, `score`, usability/blockers, and summary features. It does not expose accepted MR-F5 `target_definition_version`, feature snapshot identity, transition path, abstain reason, or calibrated reliability. Therefore this read-only sample proves the legacy schema gap; it does not prove that every required raw feature family is continuously available for every canonical horizon.

The manifest is older than the existing six-hour forecast freshness limit at audit time. Therefore it is valid schema evidence but not live forecast evidence.

## Target semantics

Each canonical horizon uses a point-in-time future-state target:

```text
origin_time = forecast creation time
source_cutoff = origin_time, inclusive
target_time = origin_time + horizon_sec
observation = first valid state observation at/after target_time within tolerance
exact match = hit
transition-adjacent compatible state = partial
other known state = miss
invalid source/market observation = invalidated
missing or late unavailable observation = unknown
```

No source timestamp after origin may enter the forecast feature snapshot. No label from a shorter horizon may be projected into another target horizon.

## Per-horizon policy

| Horizon | Minimum history | Observation tolerance | Required feature families | Additional context |
|---|---:|---:|---|---|
| 5m | 30m | 1m | price structure, volatility, liquidity, source quality | orderflow/microprice/cross-venue optional |
| 15m | 1h | 2m | price structure, volatility, liquidity, source quality | orderflow/microprice/cross-venue optional |
| 30m | 2h | 3m | price structure, volatility, liquidity, source quality | orderflow/microprice/cross-venue optional |
| 60m | 4h | 5m | price structure, volatility, liquidity, source quality | cross-venue/change-point optional |
| 6h | 24h | 15m | common + session context | macro context optional |
| 12h | 48h | 30m | common + session context | macro context optional |
| 24h | 72h | 60m | common + session context | macro context optional |

These are first-version contract minima, not calibrated model parameters. A missing required family must cause abstention; it must not be synthesized from a shorter-horizon label. Continuous availability must be proven in a later representative source-snapshot audit before model activation.

## Replacement boundary

MR-F5.2 does not modify canonical projection or the existing outcome resolver. Later connection work must add `target_definition_version`, model identity, and feature snapshot identity to prediction/outcome trace identity without changing MR-F4 current-state behavior.

## Safety

```text
d_hot_read_only=true
d_hot_write=false
ui_change=false
scheduler_change=false
broker_private_api=false
autotrade=false
order_submission=false
parameter_promotion=false
```
