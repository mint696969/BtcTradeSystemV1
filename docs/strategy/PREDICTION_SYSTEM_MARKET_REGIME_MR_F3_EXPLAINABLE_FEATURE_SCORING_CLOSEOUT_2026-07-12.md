# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F3_EXPLAINABLE_FEATURE_SCORING_CLOSEOUT_2026-07-12.md
# desc: Closeout for explainable MarketRegime candidate scoring, coverage-aware readiness, and fail-closed shadow recommendation diagnostics.

# Prediction System MarketRegime MR-F3 Explainable Feature Scoring Closeout

Updated: 2026-07-12 JST
Checkpoint: MR_F3_EXPLAINABLE_FEATURE_SCORING_ACCEPTED
Status: accepted
Next gate: MR_F4_TRANSITION_AND_PERSISTENCE_MODEL_IMPLEMENTATION
Accepted head: 9a9d0bda

## Scope accepted

MR-F3 adds family-owned, deterministic, explainable candidate scores for the current MarketRegime state.

```text
trend_score=true
range_score=true
breakout_score=true
high_vol_chop_score=true
compression_score=true
reversal_score=true
panic_score=true
feature_group_decomposition=true
missing_feature_is_zero_evidence=false
weights_and_thresholds_parameterized=true
shadow_recommendation_explainable=true
label_selection_fail_closed=true
broker_private_api_used=false
autotrade_triggered=false
order_submission_allowed=false
```

## Accepted implementation

```text
candidate scoring:
  btcts_next/src/btcts/prediction/market_regime/feature_scoring.py

parameter contract:
  btcts_next/src/btcts/prediction/market_regime/parameter_set.py

current-state integration:
  btcts_next/src/btcts/prediction/market_regime/current_state_estimator.py

classifier diagnostics:
  btcts_next/src/btcts/prediction/market_regime/inference/regime_classifier.py

focused guards:
  btcts_next/src/btcts/prediction/tests/test_market_regime_feature_scoring.py
  btcts_next/src/btcts/prediction/tests/test_market_regime_current_state_estimator.py
  btcts_next/src/btcts/prediction/tests/test_market_regime_regime_classifier_v1.py
```

## Explainability contract

Every candidate score decomposes into the following family-owned groups:

```text
price_structure
volatility
liquidity
orderflow
cross_venue
source_quality
```

Each contribution preserves:

```text
feature_group
status
raw_support
weight
weighted_support
contradictory
```

Missing features remain missing. They are not silently converted to zero support.

```text
missing_feature_is_zero_evidence=false
available_weight_exposed=true
missing_feature_groups_exposed=true
contradictory_feature_groups_exposed=true
blockers_exposed=true
```

## Coverage-aware readiness

Candidate score availability is separate from label-selection eligibility.

```text
score_available_does_not_imply_label_eligible=true
minimum_available_weight_parameterized=true
required_feature_groups_parameterized=true
observed_ranking_preserved=true
eligible_ranking_preserved=true
```

Accepted required groups for label-selection eligibility:

```text
price_structure
volatility
liquidity
source_quality
```

Current D-hot evidence does not provide canonical orderflow quantity or cross-venue agreement inputs. Those groups remain explicit missing evidence. No synthetic proxy was introduced.

## Fail-closed readiness guards

MR-F3 does not declare score-based selection ready when any of the following holds:

```text
no eligible candidate
observed top candidate is not label-selection eligible
observed top and runner-up margin is below threshold
eligible top score is below threshold
eligible top and runner-up margin is below threshold
current source is blocked or stale
```

Accepted blocker codes include:

```text
no_label_selection_eligible_candidate
observed_top_candidate_not_label_selection_eligible
observed_runner_up_missing
observed_score_margin_below_minimum
top_score_below_minimum
eligible_runner_up_missing
score_margin_below_minimum
```

## Shadow recommendation contract

Eligible candidate names are mapped to canonical MarketRegime codes only in shadow diagnostics.

```text
range_score -> RANGE
compression_score -> LOW_VOL_COMPRESSION
high_vol_chop_score -> HIGH_VOL_CHOP
breakout_score -> BREAKOUT
reversal_score -> REVERSAL_WATCH
panic_score -> PANIC_SPIKE
trend_score -> UP_TREND or DOWN_TREND from current L4 net-change sign
```

When readiness is false, the shadow recommendation is `UNKNOWN`.

```text
shadow_recommendation_enabled=false
shadow_recommendation_applied_to_selected_label=false
would_send_to_broker=false
```

## Label ownership boundary

MR-F3 accepts the explainable scoring and recommendation foundation. It does not switch the canonical current-state label to score ownership.

The current selected label remains sourced from the dedicated MR-F2 current-L4 estimator. This is intentional because temporal persistence behavior belongs to MR-F4.

```text
current_label_source=current_l4_candle_regime_hint
score_based_label_ownership_enabled=false
reason=transition_and_persistence_model_not_yet_accepted
```

Activating score-based ownership before minimum dwell, hysteresis, transition penalties, invalid-transition guards, and persistence probability would allow unstable label churn. That activation is therefore deferred to or after MR-F4 acceptance.

## D-hot observation evidence

Read-only D-hot probes used current artifacts under `D:/btc_ts_hot` and never called a writer.

Observed behaviors included:

```text
RANGE window:
  eligible top remained range_score across multiple source cutoffs
  eligible margin exceeded configured minimum

LOW_VOL_COMPRESSION boundary:
  compression_score could lead observed ranking while remaining coverage-ineligible
  readiness was blocked when observed top was ineligible

narrow RANGE / compression boundary:
  observed margin below configured minimum blocked readiness
  shadow recommendation became UNKNOWN
```

Final representative D-hot guard:

```text
observed_score_margin=0.0228
minimum_margin=0.08
readiness_blocker=observed_score_margin_below_minimum
scoring_ready_for_label_selection=false
shadow_recommended_regime_code=UNKNOWN
shadow_recommendation_ready=false
shadow_recommendation_applied_to_selected_label=false
write_function_called=false
would_send_to_broker=false
```

## Verification evidence

```text
accepted_head=9a9d0bda
prediction_full_suite=301_passed
operator_ui_full_suite=1184_passed
focused_mr_f3_boundary=40_passed
feature_scoring_tests=12_passed
all_patch_runners_idempotent=true
git_diff_check=passed
working_tree_after_commit=clean
test_exclusions=0
```

## Safety

```text
read_only_market_sources=true
raw_market_payload_in_read_model=false
ui_inference=false
ui_confidence_recalculation=false
broker_private_api=false
autotrade=false
order_submission=false
live_parameter_apply=false
parameter_auto_promotion=false
```

## Acceptance decision

```text
mr_f3_explainable_feature_scoring_accepted=true
candidate_score_decomposition_accepted=true
missing_feature_semantics_accepted=true
coverage_aware_readiness_accepted=true
shadow_recommendation_contract_accepted=true
fail_closed_margin_and_eligibility_guards_accepted=true
score_based_label_ownership_enabled=false
current_gate=MR_F3_EXPLAINABLE_FEATURE_SCORING_ACCEPTED
next_gate=MR_F4_TRANSITION_AND_PERSISTENCE_MODEL_IMPLEMENTATION
```
