# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_A1_A4_THREAD_CLOSEOUT_NEXT_MR_A5_HANDOFF_2026-07-09.md
# desc: Thread closeout and next-thread handoff after MarketRegime MR-A1 through MR-A4. Locks inference-engine principles, current state, completed work, and MR-A5 outcome/calibration audit entry. Spec-only; no runtime behavior change.
# MarketRegime MR-A1-A4 Thread Closeout / Next MR-A5 Handoff

Updated: 2026-07-09 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync
Head at closeout: f0f6a528 `prediction: parameterize current L4 candle thresholds`
Mode: thread closeout / next-thread handoff / spec-only / no runtime behavior change / no UI behavior change

<!-- PS_MARKET_REGIME_MR_A1_A4_THREAD_CLOSEOUT_NEXT_MR_A5_HANDOFF_2026_07_09 -->

```text
thread_closeout=true
next_thread_entry=MR-A5_OUTCOME_RESOLVER_AND_CALIBRATION_TRUST_AUDIT
market_regime_a1_a4_completed=true
working_tree_clean_at_handoff=true
inference_engine_is_core_system=true
not_a_toy_requirement=true
responsibility_separation_required=true
folder_structure_alignment_required=true
one_file_bloat_forbidden=true
parameter_sets_per_prediction_family_required=true
parameter_set_comparison_required=true
parameter_set_rollback_required=true
outcome_calibration_before_tuning_required=true
ui_render_invokes_classifier=false
ui_chart_cosmetics_frozen=true
broker_send_enabled=false
order_intent_submitted=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
```

## 1. Purpose

This document closes the current MarketRegime implementation thread after MR-A1 through MR-A4 and gives the next GPT/thread a precise restart point.

The next thread must continue with the same design intent and technical discipline. The Prediction Inference Engine is not a decorative card feature. It is the core inference weapon of BtcTradeSystem: non-executing for now, but traceable, replayable, calibratable, extensible, and strong enough to improve by evidence.

This handoff is spec and memory synchronization only. It does not change runtime behavior, enable UI inference, write D-hot runtime artifacts, call broker APIs, submit orders, mutate AutoTrade state, or tune live parameters.

## 2. Current repository state

```text
branch: docs/phase2-handoff-sync
head: f0f6a528
latest_commit: prediction: parameterize current L4 candle thresholds
working_tree_expected: clean after this closeout commit
```

MR-A1 through MR-A4 were completed and committed before this closeout:

```text
MR-A1: stale forecast_records gate
MR-A2: current D-hot WarRoom L4 candle fallback
MR-A3: current L4 evidence diagnostic
MR-A4: current L4 thresholds moved into parameter-set contract metadata
```

The next task is:

```text
MR-A5_OUTCOME_RESOLVER_AND_CALIBRATION_TRUST_AUDIT
```

## 3. Non-negotiable guardrails for the next GPT

These are not preferences. They are operating constraints for the next thread.

```text
1. Responsibility separation is mandatory.
2. Folder structure must reflect responsibility separation.
3. One-file bloat is forbidden; split by responsibility before files become hard to review.
4. Prediction Inference Engine is core system, not a plausible-looking toy.
5. Each prediction family owns versioned parameter sets.
6. Parameter sets must be comparable, condition-aware, and rollback-capable.
7. Parameter tuning must wait until outcome/calibration trust is audited.
8. UI displays read models and push packets only; UI must not infer.
9. Collector collects and normalizes source artifacts only; Collector must not classify market regime.
10. AutoTrade, broker, private API, order intent, and execution remain disconnected until a separate explicit human gate.
11. D-hot latest/live data is the source for current runtime checks; E cold is archive/copy validation only.
12. All prediction outputs must preserve source refs, parameter_set_id, thresholds/caps used, evidence, traceability, and later outcome linkage.
```

## 4. Responsibility model to preserve

```text
Collector
  Owns market data collection, canonical source artifacts, health, freshness, and source-quality artifacts.
  Must not classify market regime, render prediction cards, trade, or mutate prediction parameters.

Prediction Inference Engine
  Owns source snapshots, feature bundles, signal votes, prediction family execution, parameter-set selection, traces, read models, outcomes, and calibration.
  Must not render UI, send orders, call broker/private APIs, start/stop Collector, or mutate AutoTrade ledgers.

Prediction Family
  Owns family-specific labels, features, signals, outcome rules, read-model fields, parameter sets, threshold contracts, and calibration interpretation.
  Must use parent engine contracts.

WarRoom UI
  Owns display only. It may show read models, push packets, trace paths, status, and review helpers.
  Must not run feature builders, classifiers, source interpretation, parameter mutation, broker calls, or AutoTrade triggers.

Outcome / Calibration
  Owns post-horizon scoring, hit/partial/miss/invalidated/unknown resolution, parameter-set comparison, source/family/horizon analysis, and rollback recommendation evidence.
  Must not auto-promote parameter sets without a human gate.

Human / GPT review
  Owns explanation, manual review, hypothesis proposal, miss analysis, and parameter-review suggestions.
  Must be recorded as evidence, not applied as hidden live logic.
```

## 5. Folder-structure direction

Do not do a broad reshuffle first. Continue with focused, guarded slices. When responsibilities grow, split modules before they become large opaque files.

Long-term direction remains:

```text
btcts_next/src/btcts/prediction/
  engine/
    contracts.py
    family_registry.py
    source_registry.py
    horizon_policy.py
    run_context.py
    read_model_contracts.py
    push_packet_contracts.py

  parameter_sets/
    registry.py
    lifecycle.py
    comparison.py
    rollback.py

  trace/
    prediction_trace.py
    source_refs.py
    evidence_refs.py

  outcome/
    outcome_ledger.py
    resolver_contracts.py

  calibration/
    summary.py
    parameter_review.py
    replay_comparison.py

  review/
    warroom_chart_analysis_request.py
    human_review_note.py
    review_link.py
    gpt_analysis_note.py

  families/
    market_regime/
      source_snapshot.py
      features.py
      signal_registry.py
      signal_scoring.py
      classifier.py
      artifact_projection.py
      outcome_rule.py
      parameter_sets.py
      producer.py

    trend_bias/
    reversal_zone/
    breakout_false_break/
    volatility_risk/
    liquidity_execution_quality/
    macro_cross_context/
    trigger_candidate/
```

Current implementation still lives mostly under:

```text
btcts_next/src/btcts/prediction/market_regime/
```

That is acceptable for now. Move or wrap only when the slice has a clear benefit and a focused guard.

## 6. What MR-A1 through MR-A4 changed

### MR-A1: stale forecast_records gate

Problem fixed:

```text
Fresh market_regime artifacts were using stale prediction/latest_manifest.json and old forecast_records as if they were current truth.
```

Current behavior:

```text
If forecast_records are stale beyond policy, forecast-derived labels cannot become live primary labels.
Stale forecast labels are blocked or treated as context.
Confidence is capped or downgraded when current evidence is insufficient.
Warnings expose forecast_records_stale and age.
```

### MR-A2: current D-hot L4 candle fallback

Problem fixed:

```text
When forecast_records were stale, MarketRegime lacked a current price-structure source.
```

Current behavior:

```text
D-hot WarRoom 60s L4 candle store is read-only source material for current/short-horizon fallback.
current_l4_candle_window can infer RANGE / UP_TREND / DOWN_TREND / LOW_VOL_COMPRESSION / HIGH_VOL_CHOP hints.
Fallback is intentionally capped and marked PARTIAL because it is not yet fully calibrated.
```

Important source:

```text
D:/btc_ts_hot/data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/closed.jsonl
D:/btc_ts_hot/data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/forming.json
D:/btc_ts_hot/data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/meta.json
```

### MR-A3: current L4 evidence diagnostic

Problem fixed:

```text
MR-A2 could choose a current L4 fallback label, but did not expose enough compact evidence explaining why.
```

Current behavior:

```text
current_l4_candle_evidence is included in diagnostic_record.
It includes compact evidence values such as net_change_bps, range_bps, realized_volatility_bps, average_candle_range_bps, close_position, regime_hint, regime_reason, source_refs, and warnings.
raw_candle_payload_included=false.
```

### MR-A4: current L4 threshold parameter-set contract

Problem fixed:

```text
Current L4 candle hint thresholds were hard-coded opaque classifier logic.
```

Current behavior:

```text
current_l4_candle_window thresholds are present under the active MarketRegime parameter set.
current_l4_candle_evidence exposes threshold_set_id and threshold values.
threshold metadata does not mark source coverage LIVE without actual candle evidence.
live_parameter_apply_allowed=false.
```

Default threshold set:

```text
threshold_set_id=market_regime.current_l4_candle_thresholds.v1
high_vol_chop_range_bps_min=180.0
high_vol_chop_abs_net_range_ratio_max=0.35
directional_abs_net_bps_min=25.0
directional_abs_net_range_ratio_min=0.45
low_vol_range_bps_max=20.0
```

## 7. Known status after MR-A4

What is now better:

```text
stale forecast labels are gated.
current D-hot L4 candle source can provide live fallback evidence.
fallback evidence is visible and compact.
thresholds are traceable through active parameter-set metadata.
raw candle payload is not embedded in diagnostics.
UI remains display-only.
no broker/order/autotrade behavior was added.
```

What is not complete:

```text
MarketRegime is not fully calibrated.
current L4 fallback confidence is still heuristic and capped.
outcome resolver and calibration have not been trusted/audited yet.
parameter-set comparison and rollback are contracts/foundations, not proven improvement loop.
WarRoom UI connected-done acceptance is not final.
additional families such as trend_bias/reversal_zone/breakout_false_break are not implemented.
```

## 8. Next-thread entry: MR-A5

The next GPT must start with audit, not tuning.

```text
MR-A5_OUTCOME_RESOLVER_AND_CALIBRATION_TRUST_AUDIT
```

Purpose:

```text
Verify that MarketRegime predictions can be scored honestly after horizon expiry and that calibration summaries are not self-referential or misleading.
```

First reads:

```text
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_A1_A4_THREAD_CLOSEOUT_NEXT_MR_A5_HANDOFF_2026-07-09.md
docs/strategy/PREDICTION_SYSTEM_INFERENCE_ENGINE_V1_ALIGNMENT_AND_ROADMAP_2026-07-09.md
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_PHASE1_AUDIT_2026-07-09.md
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_ROADMAP_TO_UI_CONNECTED_DONE_2026-07-08.md
btcts_next/src/btcts/prediction/market_regime/outcome_resolver.py
btcts_next/src/btcts/prediction/market_regime/calibration_summary.py
btcts_next/src/btcts/prediction/market_regime/calibration_read_model.py
btcts_next/src/btcts/prediction/market_regime/trace_ledger.py
btcts_next/src/btcts/prediction/market_regime/tools/resolve_outcomes.py
```

D-hot inspection should use `data_*` tools against hot root:

```text
D:/btc_ts_hot
```

Likely D-hot paths to inspect with bounded slices:

```text
prediction/market_regime/ledgers/date=*/hour=*/part-*.jsonl
prediction/market_regime/outcomes/date=*/part-*.jsonl
prediction/market_regime/calibration/latest_read_model.json
prediction/market_regime/latest_read_model.json
prediction/market_regime/status.json
```

## 9. MR-A5 audit questions

The next thread must answer these before changing thresholds or tuning parameters:

```text
1. Are outcome rows based on future data after prediction horizon expiry?
2. Can each outcome row link back to prediction_id, run_id, horizon, parameter_set_id, and trace row?
3. Are hit / partial / miss / invalidated / unknown rules implemented according to outcome_rule_v1?
4. Does the resolver mark judgeable=false or unknown when source data is missing?
5. Is calibration aggregating real outcomes rather than restating prediction confidence?
6. Can calibration group by horizon, primary_regime, parameter_set_id, confidence bucket, source quality, volatility, and liquidity state?
7. Does calibration preserve sample size and avoid overclaiming from tiny sample counts?
8. Are stale-source conditions represented in outcomes/calibration?
9. Can current_l4 threshold_set_id and threshold values be traced through prediction -> outcome -> calibration?
10. Is there any path that auto-promotes or auto-applies parameters? It must remain false.
```

## 10. MR-A5 implementation boundary

Start with audit and probes. Do not patch first unless a concrete defect is found.

Allowed:

```text
read outcome_resolver / calibration / trace code
read tests for outcome/calibration
inspect D-hot latest/current artifacts with data_latest/data_slice/data_read
create no-write probes under tmp/work/mr_a5_*/
write audit doc under docs/strategy if needed
add focused tests or fix minimal defects after evidence
```

Forbidden at MR-A5 entry:

```text
no parameter tuning
no threshold changes
no UI cosmetics
no chart changes
no broker/order/autotrade
no producer daemon changes unless audit proves necessary
no D-hot writes except explicit guarded resolver write slice after audit and human approval
```

## 11. Progress estimate at closeout

```text
MarketRegime first-family implementation: about 55%
MarketRegime as trustworthy inference weapon: about 40-45%
Full Prediction Inference Engine v1: about 25-30%
```

Interpretation:

```text
Source/currentness/evidence/parameter-set foundation is now significantly stronger.
Outcome/calibration/replay/parameter comparison is still the main missing loop.
Without outcome/calibration, do not claim the engine is accurate or tuned.
```

## 12. Exact next first action

In the next thread, after `project_bootstrap`, do this:

```text
1. Confirm clean repo and HEAD around f0f6a528 or later closeout commit.
2. Read this handoff doc and the alignment roadmap.
3. Read outcome_resolver.py, calibration_summary.py, calibration_read_model.py, trace_ledger.py, tools/resolve_outcomes.py.
4. Grep tests for outcome/calibration.
5. Inspect D-hot outcome/calibration/trace artifacts with bounded data tools.
6. Produce MR-A5 audit finding before changing code.
```

Do not begin with UI, chart, parameter tuning, or broad repository reshuffle.
