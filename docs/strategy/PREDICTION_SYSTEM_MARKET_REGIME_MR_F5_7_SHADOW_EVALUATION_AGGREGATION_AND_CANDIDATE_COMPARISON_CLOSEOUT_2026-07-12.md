# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_7_SHADOW_EVALUATION_AGGREGATION_AND_CANDIDATE_COMPARISON_CLOSEOUT_2026-07-12.md
# desc: Acceptance closeout for the MR-F5.7 pure shadow evaluation aggregation and human-gated candidate comparison.

# Prediction System MarketRegime MR-F5.7 Shadow Evaluation Aggregation and Candidate Comparison Closeout

Updated: 2026-07-12 JST
Checkpoint: MR_F5_7_SHADOW_EVALUATION_AGGREGATION_AND_CANDIDATE_COMPARISON_ACCEPTED
Status: accepted
Next slice: MR-F5.8 read-only comparison projection and family-completion readiness audit

## Accepted scope

```text
immutable_shadow_evaluation_aggregation=true
candidate_identity=model_id+logic_version+parameter_set_id
scored_states=CORRECT+PARTIAL+INCORRECT
unscored_states=UNRESOLVED+INVALIDATED+ABSTAINED
correct_weight=1.0
partial_weight=0.5
incorrect_weight=0.0
minimum_scored_sample_gate=true
same_horizon_coverage_gate=true
human_review_only=true
auto_promotion=false
live_parameter_apply=false
ledger_append=false
d_hot_read=false
d_hot_write=false
canonical_future_label_replacement=false
ui_change=false
```

## Accepted implementation

```text
aggregation:
  btcts_next/src/btcts/prediction/market_regime/future_shadow_evaluation.py

focused tests:
  btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_evaluation.py

design:
  docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_7_SHADOW_EVALUATION_AGGREGATION_AND_CANDIDATE_COMPARISON_2026-07-12.md
```

## Comparison guarantees

```text
input_schema_version_exact=true
artifact_family_exact=true
artifact_kind_exact=true
shadow_safety_boundary_exact=true
ledger_append_allowed_false=true
canonical_horizon_exact=true
horizon_key_exact=true
target_definition_version_exact=true
trace_id_unique=true
candidate_identity_complete=true
candidate_summary_immutable=true
horizon_summary_immutable=true
comparison_requires_two_candidates=true
comparison_requires_minimum_scored_samples=true
comparison_requires_identical_qualified_horizon_sets=true
comparison_blockers_explicit=true
promotion_candidates_empty=true
human_gate_required=true
```

## Verification evidence

```text
focused_evaluation_tests=8_passed
market_regime_tests=112_passed
prediction_full_suite=378_passed
operator_ui_full_suite=1184_passed
git_diff_check=passed
patch_runner_idempotency=passed
```

## Safety

```text
d_hot_read=false
d_hot_modified=false
writer_executed=false
outcome_resolver_executed=false
outcome_ledger_appended=false
ui_inference=false
canonical_packet_modified=false
regime_classifier_modified=false
parameter_auto_promotion=false
live_parameter_apply=false
broker_private_api=false
autotrade=false
order_submission=false
```

## Next-slice boundary

MR-F5.8 may add a read-only projection of the accepted comparison summary and audit whether the MarketRegime family has enough accepted contracts and evidence to approach `MARKET_REGIME_READY_FOR_NEXT_FAMILY`.

It must not:

```text
write D-hot artifacts
append to the existing outcome ledger
modify outcome_resolver.py
replace canonical future labels
change UI behavior
promote a candidate automatically
apply a parameter set live
claim calibrated reliability
```

## Acceptance decision

```text
mr_f5_7_shadow_evaluation_aggregation_and_candidate_comparison_accepted=true
current_gate=MR_F5_7_SHADOW_EVALUATION_AGGREGATION_AND_CANDIDATE_COMPARISON_ACCEPTED
next_slice=MR-F5.8_read_only_comparison_projection_and_family_completion_readiness_audit
canonical_future_label_replacement_enabled=false
```
