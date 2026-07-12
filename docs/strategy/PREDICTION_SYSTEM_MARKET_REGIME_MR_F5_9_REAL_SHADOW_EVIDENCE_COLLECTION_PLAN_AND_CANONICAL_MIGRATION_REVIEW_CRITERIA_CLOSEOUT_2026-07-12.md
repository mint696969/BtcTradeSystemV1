# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_9_REAL_SHADOW_EVIDENCE_COLLECTION_PLAN_AND_CANONICAL_MIGRATION_REVIEW_CRITERIA_CLOSEOUT_2026-07-12.md
# desc: Acceptance closeout for the MR-F5.9 real shadow evidence collection plan and canonical migration review criteria.

# Prediction System MarketRegime MR-F5.9 Real Shadow Evidence Collection Plan and Canonical Migration Review Criteria Closeout

Updated: 2026-07-12 JST
Checkpoint: MR_F5_9_REAL_SHADOW_EVIDENCE_COLLECTION_PLAN_AND_CANONICAL_MIGRATION_REVIEW_CRITERIA_ACCEPTED
Status: accepted_with_evidence_pending
Family completion: not ready
Next slice: MR-F5.10 shadow evidence execution boundary and operator approval checklist

## Accepted scope

```text
real_shadow_evidence_acceptance_contract=true
canonical_migration_review_criteria=true
all_canonical_horizons_required=true
minimum_candidates=2
minimum_scored_rows_per_candidate_horizon=20
minimum_observation_window_sec=86400
lookahead_violations_allowed=0
long_horizon_session_context_required=true
legacy_canonical_records_count_as_shadow_evidence=false
source_role=hot_data_root
physical_runtime_path_in_core_contract=false
auto_promotion=false
live_parameter_apply=false
canonical_replacement=false
ui_change=false
```

## Accepted implementation

```text
evidence_plan:
  btcts_next/src/btcts/prediction/market_regime/future_shadow_evidence_plan.py

focused tests:
  btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_evidence_plan.py

design:
  docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_9_REAL_SHADOW_EVIDENCE_COLLECTION_PLAN_AND_CANONICAL_MIGRATION_REVIEW_CRITERIA_2026-07-12.md
```

## Evidence guarantees

```text
strict_integer_counts=true
canonical_utc_z_timestamps=true
feature_time_order_checked=true
coverage_time_order_checked=true
observation_window_matches_timestamps=true
candidate_horizon_total_consistency=true
duplicate_feature_horizon_rejected=true
duplicate_candidate_horizon_rejected=true
all_horizons_required_per_candidate=true
feature_source_refs_required=true
evaluation_refs_required=true
reviewer_identity_required=true
review_artifact_refs_required=true
review_booleans_strictly_typed=true
public_plan_immutable=true
```

## D-hot observation

Read-only inspection found current canonical prediction material and legacy-compatible `market_regime` records, but no accepted MR-F5 `future_shadow` artifact identity. Therefore:

```text
real_shadow_feature_evidence_collected=false
real_shadow_outcome_coverage_collected=false
canonical_migration_review_completed=false
family_ready_for_next_family=false
```

## Verification evidence

```text
focused_evidence_plan_tests=8_passed
market_regime_tests=127_passed
market_regime_pure_contract_policy_tests=6_passed
prediction_full_suite=393_passed
operator_ui_full_suite=1184_passed
git_diff_check=passed
patch_runner_idempotency=passed
```

## Safety

```text
d_hot_read_only=true
d_hot_modified=false
writer_executed=false
evidence_manufactured=false
outcome_resolver_executed=false
outcome_ledger_appended=false
ui_modified=false
canonical_packet_modified=false
regime_classifier_modified=false
parameter_auto_promotion=false
live_parameter_apply=false
broker_private_api=false
autotrade=false
order_submission=false
```

## Next-slice boundary

MR-F5.10 may define the exact execution boundary and operator approval checklist required before any real shadow evidence collector is added or enabled.

It must explicitly separate:

```text
read-only evidence discovery
approved shadow artifact writer design
operator approval
retention and rollback
canonical migration review
```

It must not:

```text
execute a D-hot writer without explicit approval
count legacy canonical records as shadow evidence
replace canonical labels
change UI behavior
promote a candidate automatically
apply a parameter set live
mark MARKET_REGIME_READY_FOR_NEXT_FAMILY
```

## Acceptance decision

```text
mr_f5_9_evidence_plan_and_migration_review_criteria_accepted=true
current_gate=MR_F5_9_REAL_SHADOW_EVIDENCE_COLLECTION_PLAN_AND_CANONICAL_MIGRATION_REVIEW_CRITERIA_ACCEPTED
family_completion_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
family_ready_for_next_family=false
next_slice=MR-F5.10_shadow_evidence_execution_boundary_and_operator_approval_checklist
canonical_future_label_replacement_enabled=false
```
