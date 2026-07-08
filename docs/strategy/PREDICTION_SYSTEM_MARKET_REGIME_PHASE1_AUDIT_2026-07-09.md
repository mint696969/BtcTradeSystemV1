# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_PHASE1_AUDIT_2026-07-09.md
# desc: Phase 1 audit of current MarketRegime implementation and D-hot artifacts. Report-only; no runtime behavior change.
# MarketRegime Phase 1 Audit

Updated: 2026-07-09 JST
Profile: BtcTradeSystem
Base spec: `docs/strategy/PREDICTION_SYSTEM_INFERENCE_ENGINE_V1_ALIGNMENT_AND_ROADMAP_2026-07-09.md`
Mode: audit report / no runtime behavior change / no UI behavior change

<!-- PS_INFERENCE_ENGINE_MARKET_REGIME_PHASE1_AUDIT_2026_07_09 -->

```text
ps_inference_engine_market_regime_phase1_audit=true
market_regime_first_family=true
runtime_code_changed=false
ui_changed=false
broker_send_enabled=false
order_intent_submitted=false
autotrade_trigger_allowed=false
ui_render_invokes_classifier=false
next_step=market_regime_correction_plan_after_operator_review
```

## 1. Purpose

This report records the first MarketRegime audit after the Prediction Inference Engine v1 alignment lock.

The goal is to determine what is reusable, what needs correction, and what must not be treated as complete before implementation resumes.

This document is based on repository code inspection and D-hot runtime artifact inspection. It does not change code, runtime behavior, UI behavior, or parameters.

## 2. Inspected code surface

Current MarketRegime package:

```text
btcts_next/src/btcts/prediction/market_regime/
  artifact_contracts.py
  artifact_projection.py
  calibration_read_model.py
  calibration_summary.py
  contracts.py
  features/feature_builder.py
  features/feature_bundle.py
  freshness_policy.py
  horizon_policy.py
  hypothesis_lane.py
  inference/regime_classifier.py
  observation_evaluator.py
  operator_ui_runtime.py
  outcome_resolver.py
  parameter_set.py
  parameter_set_registry.py
  producer_loop.py
  signal_scoring.py
  source_priority_policy.py
  source_snapshot.py
  sources/*
  tools/write_latest.py
  tools/resolve_outcomes.py
  trace_ledger.py
```

Key execution path observed:

```text
producer_loop.py
  -> preflight_market_regime_latest_artifacts_once()
  -> write_market_regime_latest_artifacts_once()
  -> build_market_regime_latest_artifact_set()
  -> build_market_regime_source_snapshot()
  -> build_market_regime_feature_bundle()
  -> classify_market_regime_feature_bundle()
  -> score_market_regime_signals()
  -> build latest/latest_cards/latest_read_model/status/manifest/trace
```

## 3. Inspected D-hot artifacts

Current D-hot artifacts exist:

```text
D:/btc_ts_hot/prediction/market_regime/status.json
D:/btc_ts_hot/prediction/market_regime/latest.json
D:/btc_ts_hot/prediction/market_regime/latest_cards.json
D:/btc_ts_hot/prediction/market_regime/latest_read_model.json
D:/btc_ts_hot/prediction/market_regime/calibration/latest_read_model.json
D:/btc_ts_hot/prediction/market_regime/ledgers/date=2026-07-08/hour=*/part-00001.jsonl
D:/btc_ts_hot/prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl
D:/btc_ts_hot/prediction/market_regime/runs/market_regime_*_once/manifest.json
```

Latest observed status:

```text
artifact_kind=status
generated_at=2026-07-08T19:01:41Z
latest_cards_available=true
latest_read_model_available=true
latest_run_id=market_regime_20260708T190141Z_once
trace_ledger_available=true
outcome_resolver_available=false
status=latest_ready
```

Current source manifest:

```text
D:/btc_ts_hot/prediction/latest_manifest.json
generated_at=2026-07-02T13:20:20Z
run_dir=prediction/runs/2026-07-02/132020_generated_at_2026-07-02T13_20_20Z
forecast_records=prediction/runs/2026-07-02/132020_generated_at_2026-07-02T13_20_20Z/forecast_records.jsonl
record_count=110
```

## 4. Major finding: current loop is live, but core regime labels depend on stale forecast records

The MarketRegime producer is generating fresh `prediction/market_regime/*` artifacts, but the price-structure and volatility inputs are resolved from an older prediction manifest:

```text
prediction/latest_manifest.json generated_at=2026-07-02T13:20:20Z
forecast_records relpath=prediction/runs/2026-07-02/132020_generated_at_2026-07-02T13_20_20Z/forecast_records.jsonl
```

Current `latest_read_model.json` shows fresh generated_at, but the drivers include old forecast-derived labels:

```text
generated_at=2026-07-08T19:01:41Z
drivers include:
  forecast_label:range_candidate
  forecast_horizons:15,30,60,300,600,900,1800,3600,14400,86400
  volatility_state:compressed
  cross_venue_agreement:confirmed
```

This means the loop is operational, but the market-regime family is not yet a fully current inference engine. It is mixing fresh nowcast/liquidity state with stale forecast labels from 2026-07-02.

Severity:

```text
High for prediction quality.
Low for safety because broker/order/autotrade remains disabled.
```

## 5. Major finding: primary label selection can ignore stronger current signal scoring

Current `latest_read_model.json` shows signal scoring can favor `HIGH_VOL_CHOP` due to wide spread / thin book, while the displayed primary regime remains `RANGE` due to the old forecast label.

Observed current horizon example:

```text
horizon=current
primary_regime=RANGE
confidence_percent=70
selected_forecast_label=range_candidate
selected_forecast_score=0.52
selected_signal_strength_percent=51.0
selected_reference_hit_rate_percent=51.0

regime_scores:
  HIGH_VOL_CHOP=0.6248
  RANGE=0.25
  UP_TREND=-0.3124
  DOWN_TREND=-0.3124

top signal:
  signal_id=spread_bps
  source_family=liquidity
  supports_regime=HIGH_VOL_CHOP
  value=7.497390990128467
  reason=wide spread / thin book reduces directional quality
```

This is a correctness issue: the signal layer identifies strong caution/high-vol-chop evidence, but the classifier's primary label is still anchored to stale forecast `range_candidate`.

Severity:

```text
High for usefulness.
This is exactly the kind of plausible-looking output that must not be treated as complete.
```

## 6. Major finding: confidence is partially calibrated from old forecast metrics

For current through 60m, confidence/evidence are marked as forecast-metric calibrated:

```text
confidence_calibrated_from_forecast_metric=true
evidence_quality_calibrated_from_forecast_metric=true
selected_forecast_score=0.52
selected_signal_strength_percent=51.0
selected_reference_hit_rate_percent=51.0
```

The visible `70%` is therefore influenced by stale forecast record metrics, not only current D-hot evidence.

For 6h/12h, the classifier falls back:

```text
label_selection_reason=latest_label_fallback
confidence_calibrated_from_forecast_metric=false
evidence_quality_reason=legacy_source_fallback_strong
confidence_percent=78
```

This makes long-horizon confidence look stronger despite missing exact forecast metrics for 6h/12h. That is not acceptable as a finished behavior.

Severity:

```text
High for operator trust.
```

## 7. Current design strengths to keep

These components are useful and should be reused or wrapped into the parent engine direction.

| Component | Status | Reason |
|---|---|---|
| `artifact_contracts.py` | keep | versioned latest/latest_cards/latest_read_model/status/manifest contracts exist |
| `artifact_projection.py` | keep with modification | compact card/read-model projection exists; UI-friendly, non-executing |
| `producer_loop.py` | keep with guard review | controlled loop, preflight, status/heartbeat/control design exists |
| `tools/write_latest.py` | keep with correction | good non-UI artifact writer path; needs source/currentness correction |
| `trace_ledger.py` | keep | compact trace rows, raw payload duplication guard, append-only ledger path |
| `outcome_resolver.py` | keep with audit | outcome labels and safety are useful; observation logic must be verified |
| `calibration_summary.py` / `calibration_read_model.py` | keep with audit | needed for parameter-set improvement loop; current scores must not be overtrusted |
| `parameter_set.py` / `parameter_set_registry.py` | keep and extend | active/candidate/rollback concepts exist; needs regime/time applicability metadata |
| `signal_scoring.py` | keep with correction | explains signal votes by horizon; already exposes stronger evidence than displayed primary label |
| `horizon_policy.py` | keep | current/5m/15m/30m/60m/6h/12h/24h policy aligns with spec |
```

## 8. Components requiring correction before completion

| Area | Current issue | Correction direction |
|---|---|---|
| Source snapshot | uses `prediction/latest_manifest.json` from 2026-07-02 as forecast source | detect stale manifest; either block, downgrade, or replace with current L4 source-derived features |
| Feature builder | price_structure/volatility/cross_venue derive heavily from old `forecast_records` | build current features from D-hot L4 candles, collector market state, and current artifacts |
| Classifier primary label | selected forecast label dominates primary regime | combine forecast label, signal scores, stale-source gating, and conflict rules; allow UNKNOWN/HIGH_VOL_CHOP |
| Confidence | visible 70/78% can be stale-metric/legacy fallback driven | make confidence explicitly explainable and capped by source age, conflicts, and sample quality |
| Long horizons | 6h/12h use latest-label fallback yet produce stronger 78% | cap or mark low confidence when exact horizon evidence is missing |
| Signal-to-card coherence | signal scoring can say HIGH_VOL_CHOP while card says RANGE | card primary label must reconcile or expose conflict prominently |
| Parameter sets | only default active set exists | add condition/performance metadata later per alignment spec |
| Outcome/calibration | `outcome_resolver_available=false` in status | verify outcome runner wiring and avoid self-referential calibration claims |
| Push/UI connection | current UI still relies on artifact read/fallback path | later connect true prediction push packet after engine correction |

## 9. Items not safe to treat as complete

Do not treat the following as completed implementation quality:

```text
RANGE/70% card surface
6h/12h 78% confidence
latest_read_model confidence values
calibration score as proof of accuracy
current producer loop as proof of correct inference
old forecast_records as live market regime truth
```

These may be useful for wiring and display tests, but not for real decision-support trust yet.

## 10. Use / Fix / Discard table

| Item | Decision | Notes |
|---|---|---|
| MarketRegime package as first family | fix and keep | correct foundation, but needs source and classifier repair |
| Current artifacts path `prediction/market_regime/*` | keep | good artifact family boundary |
| Current card schema | keep with extensions | add review links, condition metadata, stronger conflict display later |
| Current producer loop | keep with safety review | operational; ensure status path and control path are visible to Operator UI |
| Current forecast_records dependency | fix | must not silently use stale 2026-07-02 predictions as current truth |
| Current classifier label mapping | fix | primary label must not ignore stronger live signal scoring |
| Current signal scoring | keep and improve | useful explainability; make it authoritative or reconcile with classifier |
| Current parameter registry | keep and extend | add regime/time-window applicability, comparison, rollback evidence |
| Current UI integration | fix later | after engine correctness; push packet should become primary path |
| Current calibration score | audit before trust | may be useful but not proof yet |
| Old standalone `btcts.prediction.rule_based_v0` family outputs | reuse selectively | useful historical source, but not canonical current MarketRegime source |

## 11. Recommended correction order

Do not start with UI. Recommended next implementation slices:

### MR-A1: Stale source gate

Add source-age awareness around `prediction/latest_manifest.json` and forecast records.

Expected behavior:

```text
If forecast_records are stale beyond policy, classifier cannot treat them as live price_structure truth.
Stale forecast-derived labels can be context-only or blocked.
Confidence must be capped or UNKNOWN when current features are insufficient.
```

### MR-A2: Current L4 candle feature source

Use current D-hot L4 candle store and market state to produce minimal current price_structure features.

Required source alignment:

```text
data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/closed.jsonl
data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/forming.json
state/collector_vnext/unified_market_state_status.json
state/collector_vnext/unified_health.json
state/collector_vnext/unified_executions_status.json
```

### MR-A3: Classifier/signal reconciliation

Make primary regime selection reconcile:

```text
forecast/source labels
live signal scores
staleness gate
conflict level
source quality
horizon suitability
```

If HIGH_VOL_CHOP score dominates due to spread/liquidity, the card must not silently show RANGE without warning.

### MR-A4: Confidence cap and reason trace

Confidence must expose:

```text
confidence inputs
caps applied
stale-source cap
conflict cap
missing-horizon cap
parameter_set_id
review/outcome refs later
```

### MR-A5: Outcome/calibration trust audit

Before parameter tuning, verify:

```text
outcome rows are future-horizon based
calibration is not self-referential
unknown/invalidated are handled honestly
condition-specific performance can be aggregated
```

## 12. Suggested guard style for next implementation work

Use operator-preferred error-stopping PowerShell blocks.

Example shape:

```powershell
function Invoke-Step {
  param(
    [Parameter(Mandatory=$true)] [string]$Name,
    [Parameter(Mandatory=$true)] [scriptblock]$Block
  )
  Write-Host ""
  Write-Host "===== $Name =====" -ForegroundColor Cyan
  & $Block
  if ($LASTEXITCODE -ne 0) {
    Write-Host "FAILED: $Name" -ForegroundColor Red
    exit $LASTEXITCODE
  }
}
```

Each slice should run:

```text
1. py_compile patch runner
2. apply patch runner
3. py_compile changed modules
4. targeted pytest or structural checks
5. log/status check
6.現物 artifact/source check
7. git diff --check
8. git status --short
```

## 13. Phase 1 conclusion

MarketRegime is not worthless. It has useful contracts, artifacts, trace, parameter registry, signal scoring, and a controlled producer loop.

However, it is not yet the strong market-regime inference family agreed in the v1 alignment. The most important defects are stale forecast-record dependency, primary label/signal-score mismatch, and confidence values that can look stronger than the actual current evidence deserves.

Next safe task:

```text
PS-MR-A1_STALE_SOURCE_GATE_AND_CURRENTNESS_AUDIT_FIX
```

Scope:

```text
Add explicit currentness/staleness gate for latest_manifest / forecast_records.
Do not change UI.
Do not add new prediction families.
Do not tune parameters yet.
```
