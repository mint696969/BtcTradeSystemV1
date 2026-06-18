# path: ./docs/architecture/AUTOTRADE_PREDICTION_FOUNDATION_INTEGRATION_INDEX_2026-06-18.md
# desc: Documentation/status-only integration index for the completed S121-S135 AutoTrade prediction foundation chain.

# AutoTrade Prediction Foundation Integration Index

Updated: 2026-06-18 JST  
Profile: BtcTradeSystem  
Branch context: docs/phase2-handoff-sync  
Status: documentation / status-only / non-executing

## 1. Purpose

S121-S135 established the prediction foundation from architecture through Pre-Armed readiness. This document is the integration index before returning to AutoTrade integration work.

It records:

```text
what exists
what remains intentionally disconnected
which contracts are safe to consume later
which guards define the current boundary
which next choices are available
```

This document does not change runtime behavior and does not authorize execution.

## 2. Completed chain

| Slice | Milestone | Committed capability | Primary files | Guard status |
|---|---|---|---|---|
| S121 | GJ | Market prediction foundation roadmap | docs/architecture/AUTOTRADE_MARKET_PREDICTION_FOUNDATION_DESIGN_AND_ROADMAP_2026-06-18.md | closed |
| S122 | GK | Prediction contracts foundation | btcts_next/src/btcts/prediction/contracts.py, horizons.py | closed |
| S123 | GL | Parameter-set family skeletons | btcts_next/src/btcts/prediction/parameter_sets.py | closed |
| S124 | GM | OHLCV multi-timeframe foundation | btcts_next/src/btcts/prediction/ohlcv.py | closed |
| S125 | GN | Feature registry and source quality contracts | btcts_next/src/btcts/prediction/feature_registry.py, source_quality.py | closed |
| S126 | GO | Human technical indicators | btcts_next/src/btcts/prediction/technical.py | closed |
| S127 | GP | Cross-venue basis contracts | btcts_next/src/btcts/prediction/cross_venue.py | closed |
| S128 | GQ | Rule-based v0 prediction outputs | btcts_next/src/btcts/prediction/rule_based_v0.py | closed |
| S129 | GR | Inference bundle assembly | btcts_next/src/btcts/prediction/bundle_assembly.py | closed |
| S130 | GS | Forecast ledger contracts | btcts_next/src/btcts/prediction/forecast_ledger.py | closed |
| S131 | GT | Outcome ledger / scoring contracts | btcts_next/src/btcts/prediction/outcome_ledger.py | closed |
| S132 | GU | Calibration / missed-opportunity report contracts | btcts_next/src/btcts/prediction/calibration.py | closed |
| S133 | GV | Shadow adapter preview contracts | btcts_next/src/btcts/prediction/shadow_adapter.py | closed |
| S134 | GW | Paper/replay validation contracts | btcts_next/src/btcts/prediction/replay_validation.py | closed |
| S135 | GX | Pre-Armed readiness contracts | btcts_next/src/btcts/prediction/prearmed_readiness.py | closed |

## 3. Current contract stack

The current prediction stack is intentionally one-way and non-executing:

```text
already-provided market/reference data
-> OHLCV / technical / cross-venue / source quality helpers
-> rule-based v0 PredictionOutput objects
-> InferenceBundle
-> ForecastLedgerBatch
-> ForecastOutcomeBatch
-> PredictionCalibrationReport / MissedOpportunityReport
-> AutoTradeShadowSignalPreview
-> ReplayValidationResult
-> PredictionPreArmedReadinessSnapshot
```

The stack is not yet wired into AutoTrade runtime publication or mode application.

## 4. Boundary summary

Allowed now:

```text
import prediction contracts
build in-memory prediction outputs from already-provided objects
build inference bundles
build in-memory forecast/outcome/calibration/replay/readiness objects
serialize contract objects for tests/status review
run focused guards and close guards
```

Still forbidden unless explicitly rescoped:

```text
broker execution
real orders
private API calls
public-source collection implementation inside prediction
runtime source polling inside prediction
external API calls from prediction contracts
AutoTrade mode apply
Pre-Armed grant execution
record append execution
command ledger append
approval ledger append
actual AutoTrade publication/write
actual replay runner execution
UI command buttons
watchdog/autonomous execution loop
market manipulation
spoofing
quote stuffing
abusive order behavior
```

## 5. Responsibility separation remains active

Hard rules remain:

```text
Collector does not trade.
Prediction does not trade.
AutoTrade does not scrape public market data directly.
Execution does not invent market predictions.
UI does not secretly execute.
```

Prediction may provide sealed preview/readiness objects later. AutoTrade may consume those objects later, but only through an explicit integration slice with guards.

## 6. Integration-ready objects

| Object | Source module | Role | Safe later consumer |
|---|---|---|---|
| PredictionOutput | btcts.prediction.contracts | one family/horizon signal | inference bundle builder |
| InferenceBundle | btcts.prediction.contracts / bundle_assembly | sealed cross-family bundle | shadow adapter, forecast ledger |
| ForecastLedgerBatch | btcts.prediction.forecast_ledger | in-memory forecast records | outcome scoring |
| ForecastOutcomeBatch | btcts.prediction.outcome_ledger | in-memory outcome scoring | calibration reports |
| PredictionCalibrationReport | btcts.prediction.calibration | quality and weak-family summary | readiness / operator review |
| MissedOpportunityReport | btcts.prediction.calibration | near-miss/wait-too-much summary | readiness / operator review |
| AutoTradeShadowSignalPreview | btcts.prediction.shadow_adapter | Shadow-readable preview | future AutoTrade integration |
| ReplayValidationResult | btcts.prediction.replay_validation | consistency validation result | readiness snapshot |
| PredictionPreArmedReadinessSnapshot | btcts.prediction.prearmed_readiness | readiness/review/blocked state | future Pre-Armed integration review |

## 7. Guard chain

The prediction chain has focused and close guards from S122 onward, plus S121/S136 documentation guards.

Current terminal guard before AutoTrade reconnect:

```text
tools/test_phase4a_autotrade_milestone_gx_prearmed_readiness_guard.py
tools/test_phase4a_autotrade_milestone_gx_prearmed_readiness_close_guard.py
```

S136 adds only a documentation/status index guard:

```text
tools/test_phase4a_autotrade_milestone_gy_prediction_foundation_index_guard.py
tools/test_phase4a_autotrade_milestone_gy_prediction_foundation_index_close_guard.py
```

## 8. Recommended next implementation choices

### Option A: AutoTrade integration planning packet

Create a design-only packet for how AutoTrade will consume `AutoTradeShadowSignalPreview` and `PredictionPreArmedReadinessSnapshot`.

Expected scope:

```text
read-only adapter design
where preview objects would be passed
which existing AutoTrade layer may consume them
which guards must block writes/mode apply/orders
no code behavior change
```

### Option B: Prediction preview status artifact preflight

Create a preflight that validates what a future serialized preview artifact would contain, without writing it.

Expected scope:

```text
schema preview only
no artifact write
no runtime path creation
no AutoTrade publication
no command ledger append
```

### Option C: AutoTrade Shadow consumption contract

Add an explicit non-publishing contract in prediction or an AutoTrade read-only adapter that accepts the preview object and returns a neutral status packet.

Expected scope:

```text
no append_decision_jsonl
no run_shadow_decision_from_snapshot
no mode apply
no broker
no private API
```

## 9. Current recommendation

Use one more small planning/status slice before touching AutoTrade runtime code.

Recommended next slice:

```text
S137 AutoTrade prediction preview consumption design packet
```

Goal:

```text
identify the exact future integration seam between btcts.prediction and btcts.autotrade without changing behavior.
```

Possible future seam candidates:

```text
1. AutoTrade read-only status page consumes PredictionPreArmedReadinessSnapshot.
2. Shadow decision builder accepts AutoTradeShadowSignalPreview as an optional read-only context.
3. A new preflight packet maps preview/readiness to operator-visible status without writing ledgers.
```

Do not choose a behavior-changing seam until S137 records and guards it.

## 10. Non-permissions

This index does not permit:

```text
broker execution
real orders
private API calls
AutoTrade mode apply
Pre-Armed grant execution
record append execution
command ledger append
approval ledger append
actual AutoTrade publication/write
actual replay runner execution
UI command buttons
watchdog/autonomous execution loop
market manipulation
spoofing
quote stuffing
abusive order behavior
```
