# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_ENGINE_TRACE_AND_CALIBRATION_SPEC_2026-07-08.md
# desc: Operator-agreed market-regime engine trace, confidence, UI-card, ledger, replay, calibration, and responsibility-separation specification. Spec-only; no runtime or UI implementation change.
# Market Regime Engine Trace and Calibration Spec

Updated: 2026-07-08 JST
Base: PS-Q27F market-regime engine architecture and roadmap
Mode: specification lock / implementation premise / no code behavior change / no runtime artifact write from this document

<!-- PS_MARKET_REGIME_ENGINE_TRACE_CALIBRATION_SPEC_LOCK_2026_07_08 -->

```text
ps_market_regime_engine_trace_calibration_spec_lock=true
market_regime_only=true
implementation_premise=true
operator_agreed=true
ui_surface_minimal=true
card_percent_meaning=market_regime_reading_confidence_not_win_rate
card_percent_explainer_location=help_button_or_detail_balloon_not_card_surface
prediction_trace_required=true
source_reference_required=true
raw_market_data_duplication_forbidden=true
market_recording_separate_from_market_regime_prediction=true
replay_and_calibration_ready=true
aI_learning_future_use_supported_by_time_series_artifacts=true
first_implementation_slice=remove_ui_render_path_classifier_and_dhot_preview_inference
read_only=true
non_executing=true
broker_send_enabled=false
order_intent_submitted=false
ledger_append_allowed=false
prediction_invoked_by_ui=false
classifier_invoked_by_ui=false
```

## 1. Purpose

This document locks the operator-agreed design direction for the market-regime prediction engine before implementation resumes.

The goal is to build a reliable, reviewable, replayable, and calibratable market-regime inference engine. It must classify current market regime, estimate future regime flow over multiple horizons, preserve the evidence used at prediction time, and allow later replay, calibration, GPT review, and AI-learning preparation without creating giant files or mixing unrelated responsibilities.

This is a specification-only lock. It does not enable broker execution, AutoTrade, UI-side inference, scheduler changes, prediction runtime writes, parameter application, or ledger mutation.

## 2. Non-negotiable implementation premise

The first implementation slice after the design discussion must be:

```text
Remove market-regime classifier / D-hot preview inference from the WarRoom UI render path.
```

The target structure is:

```text
Inference node/process -> market_regime artifacts -> UI read-only display
```

The UI must not perform market-regime feature building or classifier execution during render. The UI may render card read models and chart read models only.

## 3. Responsibility separation

The system is designed for future multi-PC separation. Components must communicate through versioned artifacts, not through hidden in-process coupling.

| Component | Owns | Must not do |
|---|---|---|
| Collector | Exchange connection, raw/canonical market artifacts, freshness, health | Predict regime, render UI, trade |
| Market recording | Market time-series artifacts and references independent of prediction | Mix raw market stream into prediction ledger rows |
| Market-regime inference | Source snapshot, feature bundle, signal votes, regime scores, transition forecast, prediction artifacts | Render UI, send orders, append AutoTrade command ledgers |
| WarRoom UI | Read latest card/read-model artifacts and render compact cards/details | Read raw market data for prediction, classify regime, write prediction artifacts |
| AutoTrade | Future gated consumption of machine-readable prediction artifacts | Invoke UI, invoke inference, bypass approval gates |
| AI / GPT support | Explain, review, compare, summarize, and propose improvements from artifacts | Become canonical live prediction source or mutate parameters without human gate |
| Outcome/calibration | Resolve horizon outcomes, analyze hits/misses/partial results, propose parameter changes | Apply live parameters without separate approval |

## 4. Card semantics and UI compactness

The market-regime card surface must remain minimal and visually scannable.

Card surface fields:

```text
horizon_label
market_regime_label
confidence_percent
short_tag
freshness_badge
background_tone
border_evidence_quality
```

The card surface must not add explanatory labels next to the percent. In particular, do not add surface text such as `見立て確度` or `地合い確度` next to `70%` because it reduces scanability.

The percent means:

```text
confidence_percent = confidence in the displayed market-regime reading for that horizon, not win rate, not direction probability, and not order recommendation.
```

This meaning must be explained in the card help button, detail balloon, or detail overlay, not on the card surface.

Recommended help/detail text:

```text
この%は勝率ではありません。
この時間軸において、表示されている地合い見立てをどの程度信頼できるかを示します。
確度は、データ鮮度、情報源の信頼度、信号強度、複数ソースの一致度、過去検証、競合シグナルをもとに算出されます。
売買判断ではなく、相場環境を読むための補助情報です。
```

## 5. Market-regime labels v1

The v1 label set is:

```text
RANGE               -> レンジ
UP_TREND            -> 上昇地合い
DOWN_TREND          -> 下落地合い
LOW_VOL_COMPRESSION -> 低ボラ圧縮
BREAKOUT_WATCH      -> ブレイク監視
REVERSAL_WATCH      -> 反転警戒
HIGH_VOL_CHOP       -> 荒れ相場
UNKNOWN             -> 不明
```

`UNKNOWN` is a valid safety classification. It must be used when sources are stale, missing, contradictory, or outside calibrated confidence. Do not force a visible regime when the evidence does not justify it.

## 6. Internal prediction packet requirements

The card surface is compact, but the internal prediction packet must preserve enough context for feedback, replay, calibration, and AI/GPT analysis.

Each prediction/horizon should internally carry at least:

```text
run_id
prediction_id
generated_at_utc
exchange
symbol
timeframe_sec
horizon_sec
primary_regime
confidence_percent
evidence_quality
freshness_state
source_quality_state
main_drivers
conflicts
invalidation_conditions
watch_points
regime_scores
transition_candidates
source_contributions
source_refs
feature_bundle_ref_or_hash
signal_registry_version
source_reliability_version
parameter_set_id
calibration_version
engine_version
safety_flags
```

The system should distinguish:

```text
regime_confidence = trust in the displayed regime reading
transition_probability = probability-like score for possible regime transitions
```

Do not silently treat card percent as directional hit rate.

## 7. Source families v1

The v1 signal/source family set is:

```text
candle_structure
trend_structure
orderflow
orderbook_liquidity
volatility
cross_venue
source_quality
```

These families must be extensible through versioned registries. New sources such as funding, open interest, liquidation, external spot venues, macro/session context, or futures basis must be addable without rewriting UI contracts.

## 8. Horizon-aware source weighting

Information reliability depends on horizon.

Current to 5m:

```text
orderflow and orderbook liquidity are primary
candle structure is supporting
source freshness is a hard cap
long-horizon technical structure is low weight
```

15m to 60m:

```text
price/candle structure, VWAP/MA/ATR, volume-confirmed breaks, sustained orderflow, and cross-venue agreement are primary
instantaneous board state is supporting
```

6h to 24h:

```text
higher-timeframe structure, volatility regime, session context, cross-venue/basis, and replay-calibrated transition statistics are primary
instantaneous board and trade burst data are low-weight context only
```

Source weighting must be policy-driven and versioned. It must not be hard-coded in the UI.

## 9. Confidence calculation policy

Confidence must combine multiple factors:

```text
data_quality
source_reliability
signal_strength
source_agreement
horizon_fit
historical_calibration
conflict_penalty
```

Recommended conceptual formula:

```text
confidence = score_margin_based_confidence
           * source_quality_factor
           * source_agreement_factor
           * freshness_factor
           * historical_calibration_factor
           - conflict_penalty
```

Confidence caps are mandatory:

```text
collector_stale -> cap around 40
critical_source_missing -> cap around 50
major_signal_conflict -> cap around 60
uncalibrated_new_signal_family -> cap around 70
well-supported_and_calibrated -> may exceed 80, never 100
```

Maximum displayed confidence remains 99. 100 is forbidden.

## 10. Signal registry and explainability

The engine must use a signal registry that describes how signals vote for or against regimes.

Each signal entry should support fields equivalent to:

```text
signal_id
source_family
supports_regimes
against_regimes
horizon_weights
strength_scale
required_inputs
freshness_requirement
conflict_rules
invalidation_templates
version
```

The prediction trace must preserve the top signal votes and conflicts. This makes the engine explainable and allows later improvement.

## 11. Prediction trace ledger

Every market-regime prediction should write a lightweight time-series trace row, subject to bounded partitioning. The trace ledger is the canonical record of what the engine believed at a given time and why.

Trace rows must not inline raw market data. They store compact summaries and references.

Minimum trace row shape:

```json
{
  "schema_version": "market_regime_trace.2026_07_08.v1",
  "ts": "2026-07-08T05:27:30Z",
  "run_id": "market_regime_20260708T052730Z_xxxxx",
  "exchange": "bitflyer",
  "symbol": "FX_BTC_JPY",
  "timeframe_sec": 60,
  "horizon_sec": 900,
  "primary_regime": "RANGE",
  "confidence_percent": 70,
  "evidence_quality": "PARTIAL",
  "freshness_state": "LIVE",
  "top_drivers": ["range_boundary_visible", "vwap_near_vwap"],
  "top_conflicts": ["sell_pressure_short_burst"],
  "invalidation": ["range_low_break_with_volume", "two_closed_candles_below_boundary"],
  "source_refs": {
    "candles": {
      "relpath": "data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/closed.jsonl",
      "start_ts": "2026-07-08T05:12:00Z",
      "end_ts": "2026-07-08T05:27:00Z"
    }
  },
  "versions": {
    "engine": "market_regime_engine.v1",
    "signal_registry": "market_regime_signal_registry.v1",
    "source_reliability": "source_reliability.v1",
    "calibration": "market_regime_calibration.v1"
  },
  "safety": {
    "read_only": true,
    "broker_send_enabled": false,
    "order_intent_submitted": false
  }
}
```

## 12. Market records are separate from market-regime predictions

Market time-series recording and market-regime prediction trace are separate artifact families.

Market records preserve market facts and references over time for replay, validation, GPT chart analysis, and future AI learning. Market-regime traces preserve inference decisions and reasoning over time.

Do not mix the two into a single giant ledger.

Recommended separation:

```text
market_records/...          = market facts, compact derived summaries, source refs, chart selections, reviewable time-series context
prediction/market_regime/... = predictions, signal votes, regime scores, trace rows, outcomes, calibration
```

Prediction trace rows may reference market records, candle stores, board/trade artifacts, or chart selections by path/time range/hash. They must not duplicate large raw payloads.

## 13. Artifact layout

Recommended market-regime artifact layout:

```text
prediction/market_regime/
  latest.json
  latest_cards.json
  latest_read_model.json
  status.json

  runs/
    date=YYYY-MM-DD/
      run_YYYYMMDDTHHMMSSZ_<id>/
        manifest.json
        source_refs.json
        feature_summary.json
        signal_votes.jsonl
        regime_scores.json
        prediction_packet.json
        card_read_model.json
        trace_summary.json
        safety.json

  ledgers/
    date=YYYY-MM-DD/
      hour=HH/
        part-00001.jsonl
        part-00001.meta.json

  outcomes/
    date=YYYY-MM-DD/
      part-00001.jsonl
      part-00001.meta.json

  calibration/
    date=YYYY-MM-DD/
      daily_summary.json
    month=YYYY-MM/
      calibration_table.json
```

Recommended separate market record layout:

```text
market_records/
  summaries/
    date=YYYY-MM-DD/hour=HH/part-00001.jsonl
  chart_selections/
    date=YYYY-MM-DD/part-00001.jsonl
  manual_reviews/
    date=YYYY-MM-DD/part-00001.jsonl
  manifests/
    date=YYYY-MM-DD/manifest.json
```

The exact layout may be refined during implementation, but separation and bounded partitioning are mandatory.

## 14. File growth and close policy

Giant files are forbidden.

Partitioning rules:

```text
JSONL ledgers partition by date/hour
open part writes to .tmp or open marker
close by atomic rename where possible
closed parts are append-immutable
part meta records row_count, bytes, first_ts, last_ts, schema_version, sha256
roll part on hour change, date change, size limit, row limit, or graceful shutdown
raw market payloads are never duplicated into prediction ledgers
```

Recommended initial limits:

```text
part_max_bytes=16MB_to_64MB
part_max_rows=bounded_by_refresh_rate_and_hour
hot_retention=short_term_operational
cold_archive=compressed_or_copied_after_close
```

## 15. Outcome ledger and calibration

Prediction quality cannot improve without recording outcomes.

For each prediction/horizon, an outcome resolver should later write:

```text
prediction_id
run_id
horizon_sec
resolved_at_utc
actual_regime
primary_result=hit|partial|miss|invalidated|unknown
invalidation_triggered
max_adverse_move
max_favorable_move
volatility_state
source_quality_at_resolution
outcome_reason_codes
```

Result meanings:

```text
hit = primary regime reading held or materialized
partial = primary failed but declared counter-scenario held
miss = primary and counter-scenario both failed
invalidated = explicit invalidation condition triggered
unknown = insufficient data to judge
```

Calibration should use outcome ledgers to adjust or propose adjustments to:

```text
source reliability
horizon weights
confidence caps
signal strengths
conflict penalties
regime transition priors
```

Calibration may propose; it must not silently apply live parameter changes without a separate human gate.

## 16. Manual review and GPT chart selection packets

WarRoom chart selection packets are manual-review artifacts, not canonical prediction outputs.

They should be stored separately and linked by ID when useful:

```text
chart_selection_request_id
manual_review_note_id
prediction_run_id
outcome_id
```

The chart packet already includes useful fields such as selected UTC/JST range, candle store relpaths, hot/cold root policy, timeframe semantics, and safety flags. The market-regime engine may reference these review artifacts during analysis, but it must not depend on GPT review as the canonical live prediction source.

Manual review note records should be compact:

```text
review_id
created_at_utc
selection_request_id
operator_question
summary
observed_drivers
suggested_invalidation
linked_prediction_run_id
linked_outcome_id
manual_review_only=true
order_action=false
```

## 17. Replay and future AI-learning readiness

The time-series artifacts must be sufficient for later GPT analysis, replay, verification, calibration, and future AI-learning preparation.

Required replay ability:

```text
Given a prediction run/time/horizon, reconstruct:
- source references available at that time
- feature summaries used
- signal votes and conflicts
- regime scores
- confidence calculation inputs
- card read model shown to the operator
- later outcome
```

Do not require scanning one giant file. Replay should start from manifests, date/hour partitions, and run IDs.

## 18. Safety boundary

This specification does not allow execution behavior.

```text
broker_send_enabled=false
order_intent_submitted=false
ledger_append_allowed_for_autotrade=false
mode_apply_allowed=false
parameter_apply_allowed=false
autotrade_trigger_allowed=false
ui_invokes_classifier=false
ui_invokes_prediction_runtime=false
```

Prediction ledgers and outcome ledgers are analysis artifacts, not broker ledgers and not AutoTrade command ledgers.

## 19. Implementation order after design discussion

Implementation should proceed in small guarded slices:

```text
1. Remove UI render-path classifier / D-hot preview inference; UI reads market_regime card artifacts only.
2. Define market_regime latest/card/read_model artifact contracts.
3. Add bounded trace ledger writer with source refs only.
4. Add source reliability and signal registry specs/configs.
5. Add outcome resolver skeleton for closed horizons.
6. Add calibration summary/proposal path.
7. Add manual review / chart selection artifact linking.
8. Expand signal families and regime transition model.
```

Each slice must remain read-only with respect to broker/order/AutoTrade until a separate explicit gate is approved.
## 20. Shared multi-horizon prediction artifact contract
<!-- PS_PREDICTION_HORIZON_PARAMETER_SET_REGISTRY_LOCK_2026_07_08 -->

Although this document starts from market-regime prediction, the horizon and artifact rules apply to future prediction families as well.

The WarRoom card horizon set is multi-axis and may include:

```text
current
5m
15m
30m
60m
6h
12h
24h
```

Each prediction family must define its own meaning for each horizon while sharing the same artifact access discipline:

```text
prediction_family_id
prediction_type_id
horizon_key
horizon_sec
generated_at_utc
source_refs
feature_refs
parameter_set_id
engine_version
schema_version
run_id
prediction_id
```

The system must allow later GPT review, replay, validation, and calibration to reconstruct what each prediction used at the moment it was produced.

Required reconstruction question:

```text
At generated_at_utc, for prediction_family_id + horizon_key, what sources, features, source weights, parameter set, signal votes, conflicts, and calibration version produced this displayed card?
```

Market data, market summaries, chart selections, prediction traces, manual reviews, outcomes, and calibration results must remain separate artifact families. They connect by stable IDs, source refs, time ranges, and hashes, not by mixing payloads into one file.

## 21. Globally unique labels and IDs

Every prediction, source, parameter set, signal, and artifact family must have a unique stable ID. Human labels may be Japanese and UI-friendly, but machine IDs must be collision-resistant and never depend on visible card text.

Recommended ID fields:

```text
prediction_family_id       e.g. market_regime
prediction_type_id         e.g. regime_transition
signal_id                  e.g. orderflow.cvd_pressure.v1
source_id                  e.g. bitflyer.fx_btc_jpy.ws_executions
source_family              e.g. orderflow
parameter_set_id           e.g. market_regime.pset.2026_07_08.default.v1
parameter_set_version      e.g. 1
calibration_version        e.g. market_regime.calibration.2026_07_08.v1
artifact_family            e.g. prediction.market_regime.trace
schema_version             e.g. market_regime_trace.2026_07_08.v1
run_id
prediction_id
outcome_id
manual_review_id
chart_selection_request_id
```

Visible text such as `レンジ` or `方向感なし` must never be the canonical identifier. It is display text only.

## 22. Parameter-set registry and rollback

Each prediction family must support multiple parameter sets.

A parameter set contains the tunable logic used by the engine, including source priority and reliability assumptions.

Minimum parameter-set fields:

```text
parameter_set_id
prediction_family_id
created_at_utc
created_by
status=active|candidate|shadow|deprecated|rollback_target|archived
parent_parameter_set_id
change_reason
engine_compatibility
signal_registry_version
source_reliability_version
calibration_version
horizon_weights
source_priority_order_by_horizon
source_reliability_overrides
confidence_caps
conflict_penalties
regime_transition_priors
invalidation_thresholds
feature_thresholds
notes
```

A parameter set must record when and how it was used:

```text
active_from_utc
active_to_utc
shadow_from_utc
shadow_to_utc
used_run_count
used_prediction_count
last_used_at_utc
```

A parameter set must be comparable against other sets:

```text
hit_rate_by_horizon
partial_rate_by_horizon
miss_rate_by_horizon
invalidated_rate_by_horizon
unknown_rate_by_horizon
overconfidence_score
underconfidence_score
confidence_bucket_calibration
regime_specific_metrics
source_family_contribution_metrics
comparison_baseline_parameter_set_id
comparison_summary
```

Rollback must be first-class. If a new parameter set performs worse, the system must be able to deactivate it and return to a prior known-good set.

Rollback requirements:

```text
active_parameter_set_pointer_is_versioned=true
previous_active_parameter_set_retained=true
parameter_set_switch_logged=true
rollback_reason_required=true
rollback_target_must_exist=true
parameter_set_deletion_forbidden_when_used_by_trace=true
```

A parameter set that has been used by prediction traces must never be mutated in place. Create a new version instead.

## 23. Shadow comparison and safe promotion

New parameter sets should be evaluated in shadow before becoming active.

Recommended lifecycle:

```text
candidate -> shadow -> active -> deprecated|rollback_target|archived
```

Shadow mode means:

```text
produces comparison artifacts
writes bounded shadow traces if enabled
is not displayed as the canonical card output unless explicitly selected
is not consumed by AutoTrade
can be compared against active parameter set for the same source time ranges
```

Promotion to active should require a human-reviewed decision and should preserve comparison evidence.

## 24. Market-regime as tactical strategy selector

Market regime is a priority prediction family because trading tactics may depend on regime.

The market-regime engine should eventually provide a tactical context, but not an order command:

```text
regime=RANGE               -> range tactics / mean-reversion watch / breakout caution
regime=UP_TREND            -> trend-follow or pullback watch
regime=DOWN_TREND          -> return-sell watch / long caution
regime=LOW_VOL_COMPRESSION -> breakout preparation / wait for expansion
regime=BREAKOUT_WATCH      -> breakout confirmation watch / false-break risk
regime=REVERSAL_WATCH      -> reversal confirmation watch / chase caution
regime=HIGH_VOL_CHOP       -> risk reduce / no-new-entry bias
regime=UNKNOWN             -> observe only
```

This is tactical guidance for human/operator or future gated strategy selection. It is not broker execution and not AutoTrade permission.

## 25. Detail balloon / help contract

Cards should remain intuitive and compact. When a card is clicked, detail/help should reveal the deeper context.

Detail payload should include:

```text
percent_meaning_help
primary_reading
confidence_percent
main_drivers_top_n
conflicts_top_n
invalidation_conditions
watch_points
source_contribution_summary
parameter_set_id
run_id
prediction_id
outcome_status_if_available
calibration_hint_if_available
```

The card surface remains for fast visual scanning. Detail balloon/overlay is for reason inspection and feedback.

## 26. Cross-family extension rule

Future prediction families must reuse the same discipline while defining their own semantics:

```text
unique family/type IDs
family-specific labels
family-specific parameter sets
family-specific signal registry
family-specific outcome rules
shared source-ref discipline
shared bounded ledger discipline
shared parameter-set lifecycle
shared replay/calibration comparability
```

Market-regime work must not hard-code assumptions that prevent direction, volatility, liquidity, execution-quality, shock-risk, or other future cards from using the same infrastructure.
