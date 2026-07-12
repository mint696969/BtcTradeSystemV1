# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_1_CONTRACT_AND_LEGACY_AUDIT_2026-07-12.md
# desc: Audit and contract boundary for MR-F5.1 horizon-specific future MarketRegime forecasts.

# Prediction System MarketRegime MR-F5.1 Contract and Legacy-Path Audit

Updated: 2026-07-12 JST
Status: implementation slice prepared
Scope: pure future-forecast contract and legacy ownership audit only

## Legacy future-label ownership

```text
D-hot latest_manifest
  -> sidecars.forecast_records / forecast_records / source_records_path
  -> sources/forecast_records_reader.py
  -> source_snapshot.ForecastRecordsSnapshot.market_regime_records
  -> features/feature_builder.py
       market_regime_labels_by_horizon_sec
       forecast metrics by exact horizon
       forecast_records_current_enough
  -> inference/regime_classifier.py::_selected_label_for_horizon
       horizon=0: MR-F4 current-state estimator/policy
       exact future horizon: forecast_records compatibility label
       stale + horizon<=3600: bounded current-L4 compatibility fallback
       stale + horizon>3600: UNKNOWN / blocked
       missing exact horizon: UNKNOWN / missing
```

Ownership conclusion:

```text
MR-F4 owns canonical current state.
regime_classifier owns current compatibility projection.
forecast_records currently supplies compatibility future labels.
MR-F5 family-owned future forecasts do not yet own canonical future labels.
```

## Horizon evidence and target matrix

| Horizon | Evidence emphasis | Required broader context | Fail-closed condition | Target-definition identity |
|---|---|---|---|---|
| 5m | microstructure, orderflow, spread/liquidity, short price structure, short RV, cross-venue | no | exact-horizon evidence absent or invalid | `market_regime_target.300s.v1` |
| 15m | microstructure, orderflow, short structure/RV, liquidity, cross-venue | no | exact-horizon evidence absent or invalid | `market_regime_target.900s.v1` |
| 30m | short/medium structure, RV, liquidity transition, cross-venue | no | exact-horizon evidence absent or invalid | `market_regime_target.1800s.v1` |
| 60m | medium structure, RV state, liquidity, cross-venue | no | exact-horizon evidence absent or invalid | `market_regime_target.3600s.v1` |
| 6h | broader structure, session context, longer volatility, cross-venue | yes | broader context unavailable | `market_regime_target.21600s.v1` |
| 12h | broader structure, session context, longer volatility, cross-venue | yes | broader context unavailable | `market_regime_target.43200s.v1` |
| 24h | broad structure, multi-session context, longer volatility, macro/context when available | yes | broader context unavailable | `market_regime_target.86400s.v1` |

Every target definition must separately specify origin timestamp, evaluation timestamp, observation window, outcome resolver, assignment rule, partial-match rule, invalidated/missing observation behavior, and lookahead controls. The version strings above are identity placeholders for the first contract and are not acceptance of unresolved target semantics.

## Contract boundary

`future_forecast_contract.py` is pure and immutable. It validates:

```text
future horizons only; current excluded
all seven horizons exactly once for a complete set
origin current state retained
model, logic, parameter, feature snapshot, and target identities required
UNKNOWN represented as explicit ABSTAIN with reason
forecast path terminal state equals predicted state
path timing monotonic and bounded by target horizon
raw score constrained to [0, 1]
calibrated reliability and calibrated-probability claims forbidden before MR-F7
```

## Replacement boundary

MR-F5.1 does not modify `regime_classifier.py` or canonical artifacts. A later migration may project a validated family-owned future forecast into the existing packet only after:

```text
per-horizon target definitions accepted
feature availability proven from representative D-hot samples
outcome identity connected safely
shadow comparison available
compatibility projection tests pass
no current-state behavior changes
```

## Safety

No D-hot writes, UI changes, scheduler changes, broker/private API, AutoTrade, order submission, parameter promotion, or live apply are introduced by this slice.
