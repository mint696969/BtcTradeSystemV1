# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_9_REAL_SHADOW_EVIDENCE_COLLECTION_PLAN_AND_CANONICAL_MIGRATION_REVIEW_CRITERIA_2026-07-12.md
# desc: MR-F5.9 exact evidence criteria for real shadow collection and canonical migration review.

# Prediction System MarketRegime MR-F5.9 Real Shadow Evidence Collection Plan and Canonical Migration Review Criteria

Updated: 2026-07-12 JST
Status: implementation slice prepared

## D-hot finding

Read-only inspection of the hot data root (`D:\btc_ts_hot`) found current canonical prediction artifacts, including legacy-compatible `market_regime` records, but no artifact whose key or path establishes accepted MR-F5 `future_shadow` identity. Existing canonical records therefore do not count as MR-F5 shadow evidence.

## Evidence minima

```text
source_role=hot_data_root
all_canonical_horizons_required=300,900,1800,3600,21600,43200,86400
minimum_scored_rows_per_candidate_horizon=20
minimum_observation_window_sec=86400
minimum_candidates=2
same_candidate_horizon_coverage_required=true
feature_snapshot_refs_required=true
evaluation_artifact_refs_required=true
lookahead_violations_allowed=0
long_horizon_session_context_required=true
```

These are first operational acceptance minima, not calibrated model thresholds. They may be tightened later, but must not be weakened ad hoc to force readiness.

## Canonical migration review

Human review must explicitly verify:

```text
current_state_behavior_unchanged
exact_horizon_projection_verified
legacy_fallback_removal_plan_reviewed
rollback_plan_verified
operator_ui_impact_reviewed
outcome_identity_compatibility_verified
calibrated_probability_claim_absent
```

Passing this plan means only that the evidence package is ready for family-completion review. It does not itself replace canonical labels or activate `trend_bias`.

## Safety

```text
read_only_plan=true
writes_dhot=false
manufactures_evidence=false
canonical_replacement=false
parameter_auto_promotion=false
live_parameter_apply=false
ui_change=false
human_gate_required=true
```
