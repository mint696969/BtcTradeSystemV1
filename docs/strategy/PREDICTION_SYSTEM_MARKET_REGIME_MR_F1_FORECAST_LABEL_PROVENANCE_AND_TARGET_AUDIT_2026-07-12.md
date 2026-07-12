# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F1_FORECAST_LABEL_PROVENANCE_AND_TARGET_AUDIT_2026-07-12.md
# desc: Audits MarketRegime forecast-label provenance, target semantics, timing, outcome resolution, and leakage/circularity risks.
# Prediction System MarketRegime MR-F1 Forecast-label Provenance and Target Audit

Updated: 2026-07-12 JST
Status: accepted-with-blockers
Gate: `MR_F1_FORECAST_LABEL_PROVENANCE_AND_TARGET_AUDIT_ACCEPTED`
Next gate: `MR_F2_CURRENT_STATE_ESTIMATOR_IMPLEMENTATION`

## Audit scope

This audit traces MarketRegime labels from the generic forecast ledger through the dedicated MarketRegime classifier, read-model projection, candle-based observation evaluator, and outcome resolver.

Reviewed implementation:

```text
btcts_next/src/btcts/prediction/market_regime/sources/forecast_records_reader.py
btcts_next/src/btcts/prediction/market_regime/features/feature_builder.py
btcts_next/src/btcts/prediction/market_regime/inference/regime_classifier.py
btcts_next/src/btcts/prediction/market_regime/artifact_projection.py
btcts_next/src/btcts/prediction/market_regime/tools/write_latest.py
btcts_next/src/btcts/prediction/market_regime/observation_evaluator.py
btcts_next/src/btcts/prediction/market_regime/outcome_resolver.py
btcts_next/src/btcts/prediction/market_regime/producer_loop.py
```

Reviewed D-hot evidence:

```text
prediction/latest_manifest.json
prediction/runs/2026-07-10/152722_generated_at_2026-07-10T15_27_22Z/forecast_records.jsonl
prediction/market_regime/outcomes/date=2026-07-10/part-00001.meta.json
prediction/market_regime/outcomes/date=2026-07-10/part-00001.jsonl
```

## Provenance chain

```text
generic forecast inference
  -> forecast_records.jsonl family=market_regime
  -> feature_builder market_regime_labels_by_horizon_sec
  -> regime_classifier selected_label
  -> label_to_regime mapping
  -> MarketRegimePrediction.regime_code
  -> family read-model primary_label
```

The dedicated MarketRegime classifier does not derive every horizon label directly from raw/current market features. Its primary path reuses generic forecast-ledger labels as classifier inputs.

## D-hot forecast evidence

The latest generic prediction manifest observed during the audit was generated at `2026-07-10T15:27:22Z` and referenced 132 forecast records. Twelve records had `family=market_regime`.

Observed horizons:

```text
15s
30s
60s
300s
600s
900s
1800s
3600s
14400s
21600s
43200s
86400s
```

Representative records contained:

```text
logic_version=prediction_forecast_ledger.s130.v1
parameter_set_id=market_regime_prediction_v0_1_0
primary_label=trend_candidate or range_candidate
score=0.62 or 0.52
values_snapshot.estimated_reference_hit_rate_percent=61 or 51
values_snapshot.estimated_signal_strength_percent=61 or 51
```

No explicit target-definition version, label-window definition, training-window reference, or evaluation-window reference was present in the inspected forecast rows.

## Horizon mapping findings

The dedicated classifier uses exact generic forecast horizons when present.

For the `current` MarketRegime horizon, the classifier selects the shortest generic forecast horizon rather than a true zero-horizon current-state estimate:

```text
current -> shortest forecast label
observed shortest horizon -> 15s
selection reason -> shortest_forecast_for_current
```

This is semantically important: the existing `current` card is forecast-derived, not a standalone current-state estimator. MR-F2 must replace or clearly separate this behavior.

## Label mapping

Generic labels are normalized into MarketRegime codes:

```text
range_candidate/range/neutral_range -> RANGE
trend_candidate/up_trend/trend_up/long_bias -> UP_TREND
down_trend/trend_down/short_bias -> DOWN_TREND
volatile_or_divergent/high_vol_chop/choppy -> HIGH_VOL_CHOP
breakout/breakout_candidate -> BREAKOUT
reversal_watch/reaction_zone_watch -> REVERSAL_WATCH
unknown/unmapped -> UNKNOWN
```

The generic label `trend_candidate` maps only to `UP_TREND`; it does not encode direction independently. This mapping must not be treated as a fully specified supervised target without an explicit directional target contract.

## Target and observation semantics

The outcome evaluator derives an observed regime from closed WarRoom candles in the window:

```text
start = prediction.generated_at
end = generated_at + horizon_sec
```

Timeframe selection:

```text
horizon <= 10m -> 60s candles
horizon <= 60m -> 300s candles
horizon <= 6h  -> 900s candles
longer          -> 3600s candles
```

Observed regime rules are threshold-based:

```text
wide range and weak net direction -> HIGH_VOL_CHOP
large directional net move        -> UP_TREND or DOWN_TREND
small range                        -> LOW_VOL_COMPRESSION
otherwise                          -> RANGE
```

The observation rule is implemented, but a canonical `target_definition_version` is not propagated into forecast records, read models, or outcome rows. The outcome row records only:

```text
observation_evaluator_version
outcome_rule_version
```

## Outcome evidence

The D-hot outcome ledger for `2026-07-10` contained:

```text
row_count=8874
bytes=20500811
first_ts=2026-07-10T15:51:18Z
last_ts=2026-07-10T15:51:18Z
```

Representative rows showed:

```text
generated_at=2026-07-10T00:00:26Z
expiry_at=generated_at+horizon_sec
observation_at=2026-07-10T15:51:18Z
observation_source=candle_summary
```

The resolver correctly blocks evaluation when `observation_at < expiry_at`.

## Critical blocker: UNKNOWN predictions counted as misses

Representative D-hot rows showed:

```text
predicted_regime_code=UNKNOWN
observed_regime_code=DOWN_TREND/RANGE/UP_TREND
outcome_label=miss
```

The current resolver returns `miss` whenever the observed regime is known and differs from the predicted code, including when the prediction is `UNKNOWN`.

This behavior can inflate miss counts and corrupt hit-rate or calibration summaries. `UNKNOWN` predictions must be excluded, separately classified, or resolved as `unknown`; they must not enter ordinary miss-rate denominators without an explicit policy.

MR-F2 and later calibration work must treat this as a blocking correction before any performance claim.

## Leakage and circularity assessment

### Confirmed

```text
forecast labels are reused as MarketRegime classifier inputs
current uses the shortest future forecast label
forecast records and outcome rows do not carry a canonical target_definition_version
```

### Not proven safe

```text
forecast record cutoff relative to dedicated prediction generated_at
same-run versus prior-run forecast reuse
strict event-time availability of all feature sources
training/evaluation window separation
label generation independence from later outcome artifacts
```

### No direct leakage observed in reviewed evaluator

The candle evaluator reads only the closed-candle window from prediction generation time through expiry. It does not read post-expiry candles for the computed summary window, although resolution may occur later.

## MR-F1 decision

MR-F1 is accepted as an audit, not as approval of the existing label system for training or calibration claims.

Accepted facts:

```text
provenance path identified=true
current-is-shortest-forecast identified=true
target-definition gap identified=true
UNKNOWN-as-miss blocker identified=true
outcome timing path identified=true
live D-hot evidence inspected=true
```

Blocked claims:

```text
supervised target is fully specified=false
lookahead safety is proven=false
training/evaluation separation is proven=false
UNKNOWN rows are calibration-safe=false
current card is a true current-state estimator=false
```

## MR-F2 entry conditions

MR-F2 must implement a true current-state estimator that:

```text
does not reuse a future forecast label as the current label
uses only source data available at evaluation time
records estimator_version and source cutoff time
keeps forecast horizons separate from current-state estimation
returns UNKNOWN when evidence is insufficient
never converts UNKNOWN into an ordinary miss for calibration
```

The existing forecast-derived current behavior may remain as a compatibility diagnostic, but it must not be labeled as the canonical current-state estimate.

```text
current_gate=MR_F1_FORECAST_LABEL_PROVENANCE_AND_TARGET_AUDIT_ACCEPTED
next_gate=MR_F2_CURRENT_STATE_ESTIMATOR_IMPLEMENTATION
family_completion_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
```
