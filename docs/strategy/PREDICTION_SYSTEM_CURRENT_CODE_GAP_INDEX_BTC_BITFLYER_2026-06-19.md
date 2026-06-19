# path: ./docs/strategy/PREDICTION_SYSTEM_CURRENT_CODE_GAP_INDEX_BTC_BITFLYER_2026-06-19.md
# desc: PS-B current code inventory and gap index for standalone Prediction System implementation.

# Prediction System PS-B Current Code Inventory and Gap Index

Updated: 2026-06-19 JST  
Profile: BtcTradeSystem  
Phase: PS-B current code inventory and gap index  
Base design: `docs/strategy/PREDICTION_SYSTEM_STANDALONE_DESIGN_AND_ROADMAP_BTC_BITFLYER_2026-06-19.md`  
Scope: `btcts_next/src/btcts/prediction/`

## 1. Decision summary

The current `btcts.prediction` package is a useful non-executing prediction foundation, but it is not yet a usable standalone Prediction System.

Current state:

```text
contracts / skeletons / helper features exist
11 prediction families exist as enum / parameter-set / feature-registry concepts
only 5 families have rule_based_v0 output logic
multi-horizon contracts exist, but the rule-based runner is single-horizon
there is no top-level PredictionSystemInput / PredictionSystemResult orchestrator
there is no Scenario Core in btcts.prediction
there is no re-prediction / expiry / revision tracking
there is no provider reliability registry
there is no parameter-set lifecycle/comparison/rollback implementation
hit/miss scoring exists, but hit/miss explanation does not yet exist
AutoTrade preview/readiness helpers are mixed into the prediction package
Collector runtime imports were not found in btcts.prediction current files
```

Therefore PS-B confirms the user's concern:

```text
Prediction System itself is still mostly foundation-level.
The next implementation should build standalone Prediction System core, not continue AutoTrade integration.
```

## 2. Current module inventory

Current files under `btcts_next/src/btcts/prediction/`:

| File | Current role | Standalone core status |
|---|---|---|
| `__init__.py` | public exports for current prediction package | exports both core-like and AutoTrade preview objects; needs boundary cleanup later |
| `contracts.py` | `PredictionFamily`, `PredictionOutput`, `InferenceBundle`, source/parameter identity | useful base, but missing lifetime, horizon group, evidence refs, trigger eligibility, narrative, run identity |
| `horizons.py` | horizon contracts | useful base; missing 10m horizon and explicit now/short/mid/long group mapping |
| `parameter_sets.py` | parameter-set skeletons for all 11 families | useful base; contract-only; missing version registry, comparison, activation, rollback, GPT/human review metadata |
| `feature_registry.py` | feature registry skeletons | useful base; implementation_status defaults contract_only; no actual features for many listed families |
| `source_quality.py` | source freshness/trust diagnostics | useful base; provider reliability registry is missing |
| `ohlcv.py` | deterministic OHLCV aggregation from already-provided rows | useful base; missing 10m timeframe; not yet connected to PredictionSystemInput |
| `technical.py` | human technical summary over OHLCV candles | useful base; simple deterministic v1 candidate |
| `cross_venue.py` | cross-venue and Spot-FX basis over provided snapshots | useful base; lead/lag is only snapshot skeleton |
| `rule_based_v0.py` | initial 5-family rule outputs | partial; only 5 of 11 families and single horizon |
| `bundle_assembly.py` | bundle existing PredictionOutput records | useful base; cross-family logic is basic and not Scenario Core |
| `forecast_ledger.py` | in-memory forecast ledger records | useful base; no append/write; missing prediction_run_id and expiry fields |
| `outcome_ledger.py` | in-memory realized outcome scoring | useful base; direction mapping is basic; no hit/miss reason explanation |
| `calibration.py` | calibration and missed-opportunity report from outcomes | useful base; no parameter proposal lifecycle yet |
| `shadow_adapter.py` | AutoTrade Shadow preview from inference bundle/reports | not standalone core; should move to bridge/consumer boundary later |
| `replay_validation.py` | validation over preview/forecast/outcome/calibration objects | partially useful, but currently depends on AutoTrade preview object; bridge-facing |
| `prearmed_readiness.py` | Pre-Armed readiness contract from validation/preview/calibration | not standalone core; AutoTrade/Pre-Armed bridge-facing |

## 3. Existing contracts inventory

### 3.1 Existing useful base contracts

Already available:

```text
PredictionFamily
PredictionConfidence
SourceIdentity
ParameterSetIdentity
PredictionOutput
InferenceBundle
PredictionHorizon
PredictionParameterSetBase
SourceQualityStatus
OHLCVCandle
HumanTechnicalSummary
CrossVenueReferenceSummary
ForecastLedgerRecord / ForecastLedgerBatch
RealizedOutcome / ForecastOutcomeRecord / ForecastOutcomeBatch
PredictionCalibrationReport
MissedOpportunityReport
```

These are valuable starting points and should be reused where possible.

### 3.2 Missing top-level standalone contracts

Missing for PS-C:

```text
PredictionSystemInput
PredictionSystemResult
PredictionRunIdentity
HorizonGroup
HorizonGroupSummary
ScenarioCoreOutput
PredictionLifetime
PredictionRevisionSummary
PredictionEvidenceRef
PredictionTriggerEligibility
PredictionHumanNarrative
PredictionGptReviewDigest
ProviderReliabilityStatus
ProviderRegistry
ParameterSetRegistry
ParameterSetComparisonRecord
ParameterAdjustmentProposal
HumanParameterReviewRecord
HitMissExplanation
```

### 3.3 Current `PredictionOutput` gaps

`PredictionOutput` is useful but currently lacks several design-required fields:

```text
horizon_group
caution_level
evidence_refs
source_quality_notes
parameter_set_version explicit field beyond identity
valid_from
valid_until
stale_after_sec
refresh_required
refresh_reason
trigger_eligibility_state
human_narrative_ja
gpt_review_digest
prediction_run_id
previous_prediction_run_id
```

Recommendation for PS-C:

```text
Do not overload the existing PredictionOutput immediately.
Add wrapper/top-level result contracts that can hold the richer fields while preserving backward compatibility.
```

## 4. Existing feature helpers inventory

### 4.1 Implemented helpers

Implemented deterministic helpers:

```text
aggregate_ohlcv_from_rows
build_human_technical_summary
build_cross_venue_reference_summary
assess_source_quality
build_default_feature_registry
```

### 4.2 Feature gaps

Missing or only registry-level:

```text
10m OHLCV timeframe support
provider reliability registry
orderbook pressure feature builder
liquidity execution quality feature builder
tradeflow dynamics feature builder
breakout / retest feature builder
opportunity / near-miss feature builder
macro risk context feature builder
session / calendar context feature builder
exchange status / incident feature builder
derivatives liquidation context feature builder
options-derived context feature builder
stablecoin / USD liquidity stress feature builder
funding / carry context feature builder
on-chain / mempool stress feature builder
algorithmic participant footprint feature builder
feature snapshot / digest contract
```

## 5. Existing rule_based_v0 coverage

`rule_based_v0.py` defines `INITIAL_FAMILIES` as:

```text
market_regime
trend_bias
volatility_risk
cross_venue_confirmation
human_technical_structure
```

Implemented functions:

```text
_market_regime
_trend_bias
_volatility_risk
_cross_venue_confirmation
_human_technical_structure
build_rule_based_v0_outputs
```

Current limitations:

```text
single horizon only via horizon_sec parameter
no horizon-group mapping
no 10m horizon support through current horizons.py
no explicit flat/no_change/status_quo vocabulary except neutral-ish labels
no reversal_zone output
no liquidity_execution_quality output
no breakout_false_break output
no opportunity_participation output
no macro_risk_context output
no algorithmic_participant_footprint output
no evidence_refs / source_quality_notes / lifetime / refresh fields
no scenario integration
```

## 6. Missing 6-family logic index

The following families are defined in contracts and parameter sets, but not implemented in `rule_based_v0.py`:

| Family | Current status | Needed first v1 behavior |
|---|---|---|
| `reversal_zone` | parameter set and feature registry only | detect support/resistance/VWAP/wick/range-boundary reaction risk |
| `liquidity_execution_quality` | parameter set and registry only | spread/depth/thin book/slippage/cancel-reprice warning from provided board snapshot/summary |
| `breakout_false_break` | parameter set and registry only | breakout confirmed/watch/false-break risk from range, wick, retest, volume/cross confirmation |
| `opportunity_participation` | parameter set and registry only | near-miss / wait-too-much / overfilter watch from forecast/outcome/calibration summaries |
| `macro_risk_context` | parameter set and registry only | warning/context first; event/risk-on/off context, not primary short-horizon direction |
| `algorithmic_participant_footprint` | parameter set and registry only | warning/context first; wall vanish/stop-run/crowding/avoid-chase style diagnostics |

## 7. Missing orchestrator index

There is no standalone top-level pipeline.

Missing PS-C/PS-G target:

```text
build_prediction_system_result(...)
```

Expected orchestration:

```text
provided rows / candles / snapshots / source-quality summaries / optional previous run / optional calibration context
-> feature building / feature snapshot
-> family outputs over horizons
-> inference bundle
-> Scenario Core output
-> forecast ledger preview
-> GPT/human digest
-> PredictionSystemResult
```

No current module owns this flow.

Recommended files:

```text
btcts_next/src/btcts/prediction/system_contract.py
btcts_next/src/btcts/prediction/system.py
```

## 8. Missing multi-horizon behavior index

Existing horizon constants:

```text
execution_micro: 15s / 30s / 60s / 180s
primary_trade: 5m / 15m / 30m
context: 1h / 4h / 1d
```

Design-required horizons:

```text
execution_micro: 15s / 30s / 60s / 180s
primary_trade: 5m / 10m / 15m / 30m
context: 1h / 4h / 1d
```

Current gaps:

```text
10m missing from PredictionHorizon and OHLCV timeframe constants
no now/short/mid/long group mapping
rule_based_v0 emits one horizon per call
bundle can contain multiple horizons, but no runner builds them
no per-horizon parameter selection behavior
no per-horizon lifetime / stale_after / refresh_required
```

## 9. Missing parameter-set lifecycle index

`parameter_sets.py` is a good skeleton, but currently provides static default dataclasses.

Existing:

```text
PredictionParameterSetBase
family-specific parameter-set dataclasses for all 11 families
status enum with draft / shadow / paper / live_active / retired / rollback_candidate
activate_shadow()
retire()
default_prediction_parameter_set_for_family()
build_default_prediction_parameter_sets()
```

Missing:

```text
horizon_specific_thresholds
horizon_specific_weights
feature/source weights by horizon
change_hypothesis
expected_improvement
expected_risk
validation_window
rollback_condition
parent_parameter_set_id
rollback_target_id
human_review_status / human approval metadata
gpt_review_id / gpt_summary_ref
parameter-set registry
comparison records
activation gate
rollback decision records
immutable evaluated-version store
GPT proposal packet
human review record
```

Recommendation:

```text
Do not mutate existing default dataclasses silently.
Add lifecycle/comparison contracts around them in PS-K.
```

## 10. Collector dependency gap check

Current grep result:

```text
collector_vnext hits in btcts_next/src/btcts/prediction/*.py: 0
```

Current status:

```text
No direct Collector runtime import was found in current btcts.prediction files.
```

However future guards should still enforce:

```text
no btcts.collector_vnext worker/daemon/watchdog import in Prediction System core
no Collector process start/stop
no Collector runtime state writes
artifact/snapshot/contract boundary only
```

## 11. AutoTrade boundary gap check

Current grep result for `AutoTrade` in `btcts_next/src/btcts/prediction/*.py` found AutoTrade-facing content in:

```text
__init__.py
shadow_adapter.py
replay_validation.py
prearmed_readiness.py
```

Important distinction:

```text
These files are non-executing and guard many false flags, but they are not standalone Prediction System core.
```

Recommended future boundary:

```text
btcts_next/src/btcts/prediction/                 # standalone core
btcts_next/src/btcts/prediction/bridges/         # optional future bridge contracts
or btcts_next/src/btcts/autotrade/prediction_*   # AutoTrade consumer side
```

For now, PS-C should avoid importing these AutoTrade-facing prediction helpers into the new standalone core contracts.

## 12. Current quality summary by PS-B checkpoint

| Checkpoint | Status | Evidence |
|---|---|---|
| PS-B1 module inventory | complete | 17 current files listed |
| PS-B2 existing contracts inventory | complete | contracts/horizons/parameter/source/outcome/report contracts identified |
| PS-B3 feature helper inventory | complete | OHLCV, technical, cross-venue, source-quality helpers identified |
| PS-B4 rule_based_v0 family coverage | complete | 5/11 families implemented |
| PS-B5 missing 6-family logic | complete | six missing families listed |
| PS-B6 missing orchestrator | complete | no `system.py` / top-level result builder exists |
| PS-B7 missing multi-horizon behavior | complete | 10m and runner missing; single-horizon current behavior |
| PS-B8 missing parameter-set lifecycle | complete | skeleton only; lifecycle/comparison/rollback missing |
| PS-B9 Collector dependency gap | complete | collector_vnext grep hit count 0 |

## 13. Recommended next phase: PS-C

Next phase should be:

```text
PS-C: standalone contracts and result shape
```

Do not start with family logic expansion yet.

Reason:

```text
The system needs a stable top-level result shape before filling the missing family logic.
Otherwise each family will invent incompatible fields for horizon group, lifetime, refresh, evidence, narrative, GPT digest, and trigger eligibility.
```

Recommended PS-C slice:

```text
PS-C1: Add system_contract.py with top-level dataclasses only.
```

Candidate dataclasses:

```text
PredictionRunIdentity
PredictionLifetime
PredictionRevisionSummary
PredictionEvidenceRef
PredictionTriggerEligibility
HorizonGroupSummary
ScenarioCoreOutput
PredictionSystemInput
PredictionSystemResult
```

Initial PS-C should be contract-only / serialization-only and should not change existing `rule_based_v0` behavior yet.

## 14. PS-C guard requirements

PS-C guard should verify:

```text
new contracts serialize with to_dict
no btcts.autotrade import
no btcts.collector_vnext import
no broker/private API import
no append/mode/grant behavior
horizon group labels exist: nowcast / short_horizon / mid_horizon / long_horizon
PredictionSystemResult can carry outputs, scenario, forecast refs, human_narrative_ja, gpt_review_digest
read_only and non_executing safety fields are present
```

## 15. PS-B conclusion

PS-B confirms that the current codebase has a good non-executing foundation, but the standalone Prediction System is not yet usable as a full prediction pipeline.

The correct implementation order is:

```text
PS-C: standalone contracts and result shape
PS-G-lite: runner over existing 5-family logic once contracts exist
PS-F: implement missing 6 families
PS-H: Scenario Core integration
PS-I/J/K/L: refresh, outcome explanation, parameter lifecycle, GPT digests
```
