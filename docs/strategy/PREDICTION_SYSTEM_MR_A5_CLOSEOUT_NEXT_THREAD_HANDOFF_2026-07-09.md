# path: ./docs/strategy/PREDICTION_SYSTEM_MR_A5_CLOSEOUT_NEXT_THREAD_HANDOFF_2026-07-09.md
# desc: Closeout and next-thread handoff after MarketRegime MR-A5. Locks responsibility separation, folder-structure discipline, non-toy inference-engine quality bar, parameter-set governance, and next checkpoint selection. Spec/memory sync only; no runtime behavior change.
# Prediction System MR-A5 Closeout / Next Thread Handoff

Updated: 2026-07-09 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync
Head at closeout: 1dff6edd `prediction: clarify market regime trace generated time`
Mode: thread closeout / next-thread handoff / spec-only / no runtime behavior change / no UI behavior change

<!-- PS_MR_A5_CLOSEOUT_NEXT_THREAD_HANDOFF_2026_07_09 -->

```text
thread_closeout=true
checkpoint=MR-A5_CLOSE_GUARD_ACCEPTED
next_checkpoint_candidate=PS_INFERENCE_ENGINE_NEXT_DIRECTION_AFTER_MR_A5
working_tree_clean_at_closeout=true
responsibility_separation_required=true
folder_structure_alignment_required=true
one_file_bloat_forbidden=true
inference_engine_is_core_system=true
not_a_toy_requirement=true
strong_weapon_requirement=true
parameter_sets_per_prediction_family_required=true
parameter_set_comparison_required=true
parameter_set_rollback_required=true
human_gpt_review_loop_required=true
ui_displays_read_models_only=true
collector_does_not_predict=true
broker_send_enabled=false
order_intent_submitted=false
autotrade_trigger_allowed=false
parameter_auto_promotion_allowed=false
```

## 1. Purpose

This document closes the MR-A5 thread and gives the next GPT/thread a precise restart point.

The main instruction to preserve is that the Prediction Inference Engine is the core of the system. It must not become a plausible-looking toy that renders attractive cards without reliable evidence. It must become a strong, useful, extensible, traceable, replayable, calibratable, and reviewable weapon for manual trading support while remaining non-executing until a separate future human gate.

This document changes no runtime behavior, writes no D-hot artifacts, enables no broker/API calls, submits no orders, mutates no AutoTrade state, and applies no live parameter changes.

## 2. Current repository state

```text
branch: docs/phase2-handoff-sync
head: 1dff6edd
latest_commit: prediction: clarify market regime trace generated time
checkpoint: MR-A5_CLOSE_GUARD_ACCEPTED
working_tree_expected: clean after this closeout commit
```

MR-A5 close guard evidence:

```text
py_compile_core_files=passed
focused_pytest=47 passed in 0.67s
trace_outcome_no_write_audit_trace_rows=2619
trace_outcome_no_write_audit_candidates=12018
trace_outcome_no_write_audit_duplicates=1372
trace_outcome_no_write_audit_valid=true
trace_outcome_no_write_audit_all_after_expiry=true
calibration_trust_no_write_audit_rows=1372
calibration_trust_no_write_audit_primary=candle_summary
calibration_trust_no_write_audit_promotion_candidates=0
git_status_clean=true
```

## 3. Non-negotiable continuation principles

These must be preserved by the next GPT/thread with the same strength and granularity.

```text
1. Responsibility separation is mandatory.
2. Folder structure must express responsibility boundaries.
3. One-file bloat is forbidden. Split by responsibility before files become hard to review.
4. The inference engine is the system core, not a toy or decoration.
5. The engine must be useful as a strong manual-trading support weapon.
6. Each prediction family must own versioned parameter sets.
7. Parameter sets must be comparable by family, horizon, regime, time/session, source quality, and outcome.
8. Rollback must be supported by evidence, not memory or guesswork.
9. Human/GPT review can produce hypotheses and parameter-review suggestions, but cannot auto-apply live logic.
10. UI displays read models and push packets only. UI must not infer, classify, tune, or reinterpret sources.
11. Collector collects and normalizes source artifacts only. Collector must not predict or classify market regime.
12. Broker, order, AutoTrade, and parameter auto-promotion remain disconnected without a separate explicit human gate.
13. Unknown / insufficient evidence must be allowed and visible. Do not hide no-edge states behind pretty cards.
14. Every prediction must preserve run identity, source refs, evidence, parameter_set_id, thresholds/caps used, trace refs, outcome refs, and calibration refs.
```

## 4. Responsibility model to keep

```text
Collector
  Owns exchange/public data collection, canonical market artifacts, health, freshness, and source-quality artifacts.
  Must not classify market regime, render prediction cards, trade, mutate prediction parameters, or start prediction-family logic.

Prediction Inference Engine
  Owns source snapshots, feature bundles, signal votes, prediction family execution, parameter-set selection, traces, read models, outcomes, calibration, review links, and push packet contracts.
  Must not render UI, send orders, call broker/private APIs, start/stop Collector, or mutate AutoTrade ledgers.

Prediction Family
  Owns family-specific labels, feature requirements, signals, classifier/rules, outcome rules, read-model fields, parameter sets, threshold contracts, and calibration interpretation.
  Must use parent engine contracts and not create isolated one-off formats.

WarRoom UI
  Owns display only. It may show read models, push packets, trace paths, status, review helpers, and human-readable evidence.
  Must not run feature builders, classifiers, source interpretation, parameter mutation, broker calls, or AutoTrade triggers.

Outcome / Calibration
  Owns post-horizon scoring, hit/partial/miss/invalidated/unknown resolution, parameter-set comparison, source/family/horizon analysis, overconfidence/underconfidence analysis, and rollback recommendation evidence.
  Must not auto-promote parameter sets without a human gate.

Human / GPT Review
  Owns explanation, manual review, hypothesis proposal, miss analysis, and parameter-review suggestions.
  Must be recorded as evidence and review notes, not applied as hidden live logic.
```

## 5. Folder-structure discipline

Do not perform a broad package reshuffle only for cosmetics. But do not keep adding responsibilities to large files.

Target direction remains:

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

Current implementation still mostly lives under:

```text
btcts_next/src/btcts/prediction/market_regime/
```

This is acceptable only while slices remain focused. When common concepts are reused by more than MarketRegime, move or wrap them under parent-engine modules with tests.

## 6. MR-A5 completed outcomes

MR-A5 changed MarketRegime from a plausible artifact chain into a more trustworthy measurement loop foundation.

Completed commits:

```text
9d97fca8 prediction: guard market regime calibration trust boundary
ab46fd37 prediction: tolerate transient candle read locks
1e3b95cc prediction: include parameter set in market regime outcome identity
d6b448db prediction: expose market regime outcome resolver status
30139cc8 prediction: require trace outcome observation source in CLI
6d864e79 prediction: decouple candle trace outcomes from latest cards
2ebf7b56 prediction: prefer latest market regime trace rows
1dff6edd prediction: clarify market regime trace generated time
```

Important MR-A5 facts:

```text
calibration_trusted_source=candle_summary
latest_cards_current_reference_only=true
trace_ledger_cli_observation_source_explicit_required=true
candle_summary_trace_outcomes_require_latest_cards=false
outcome_identity_includes_parameter_set_id=true
duplicate_detection_compatible_with_existing_rows=true
trace_scan_latest_first_under_max_rows=true
candle_read_transient_lock_tolerated=true
status_artifact_exposes_outcome_resolver_available_when_refreshed=true
parameter_auto_promotion_allowed=false
```

## 7. What is possible now

The system can now support these next steps safely:

```text
- Evaluate expired MarketRegime predictions with candle_summary trusted observations.
- Keep latest_cards_current as explicit reference-only observation source.
- Aggregate calibration from trusted rows without self-referential score inflation.
- Preserve parameter_set_id in outcome identity so future active/shadow/candidate sets can be compared.
- Avoid accidental trace-ledger writes from the CLI without explicit observation source.
- Continue no-write D-hot trust audits before enabling operational writes.
```

This does not mean MarketRegime prediction quality is finished. It means the engine now has enough trust boundary to continue improvement without lying to itself.

## 8. What is still not complete

Do not treat the following as done:

```text
- Full parent inference-engine contract skeleton.
- Parameter-set comparison and rollback read model.
- Multiple parameter-set shadow/paper comparison.
- MarketRegime v1 source/feature/classifier correction.
- Signal-to-primary-label reconciliation.
- Confidence calibration quality.
- Long-horizon evidence quality.
- Prediction push packet primary UI path.
- Review request / review note / review link artifact loop.
- Additional prediction families.
- Any broker/order/AutoTrade integration.
```

## 9. Recommended next checkpoint

No explicit MR-A6 marker was found in current docs/room at MR-A5 closeout.

Recommended next checkpoint:

```text
PS_PARAMETER_SET_COMPARISON_READ_MODEL_V1
```

Reason:

MR-A5 made trusted outcomes/calibration possible. The next safest value step is to make parameter-set comparison visible and structured without changing live parameters.

Expected scope:

```text
- Read trusted calibration/outcome rows.
- Aggregate by prediction_family, horizon, predicted_regime, observed_regime, parameter_set_id, confidence bucket, and date range.
- Expose trusted sample counts and insufficient-sample flags.
- Expose comparison_ready=false when there is only one trusted parameter set.
- Preserve promotion_candidates=0 unless comparable trusted evidence exists.
- Shape rollback / keep_testing / shadow_only recommendations as read-model fields only.
- No parameter auto-promotion.
- No D-hot write unless explicitly approved after no-write probe.
```

Alternative next checkpoint:

```text
PS_PARENT_ENGINE_CONTRACT_SKELETON_V1
```

Use this instead if the operator wants to establish parent-engine structure before more MarketRegime-specific comparison work.

## 10. First reads for next GPT/thread

```text
tmp/gpt_room/02_START_HERE.md
tmp/gpt_room/MR_A5_STATUS_2026-07-09.md
docs/strategy/PREDICTION_SYSTEM_MR_A5_CLOSEOUT_NEXT_THREAD_HANDOFF_2026-07-09.md
docs/strategy/PREDICTION_SYSTEM_INFERENCE_ENGINE_V1_ALIGNMENT_AND_ROADMAP_2026-07-09.md
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_PHASE1_AUDIT_2026-07-09.md
btcts_next/src/btcts/prediction/market_regime/calibration_summary.py
btcts_next/src/btcts/prediction/market_regime/calibration_read_model.py
btcts_next/src/btcts/prediction/market_regime/outcome_resolver.py
btcts_next/src/btcts/prediction/market_regime/tools/resolve_outcomes.py
```

## 11. Safety state at closeout

```text
websocket_send_enabled=false
broker_send_enabled=false
broker_private_api_allowed=false
order_intent_submitted=false
autotrade_trigger_allowed=false
prediction_invoked_by_ui=false
classifier_invoked_by_ui=false
parameter_auto_promotion_allowed=false
live_parameter_apply_allowed=false
```

