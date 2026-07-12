# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_2_TARGET_DEFINITION_AND_FEATURE_AVAILABILITY_CLOSEOUT_2026-07-12.md
# desc: Acceptance closeout for MR-F5.2 target definitions and the representative legacy feature-availability gap audit.

# Prediction System MarketRegime MR-F5.2 Target Definition and Feature Availability Closeout

Updated: 2026-07-12 JST
Checkpoint: MR_F5_2_TARGET_DEFINITION_AND_FEATURE_AVAILABILITY_ACCEPTED
Status: accepted
Next slice: MR-F5.3 family-owned transparent baseline forecast model

## Accepted scope

```text
canonical_future_horizons_fixed=true
point_in_time_target_semantics_fixed=true
lookahead_cutoff_guard_fixed=true
short_horizon_projection_forbidden=true
missing_required_feature_requires_abstain=true
legacy_schema_gap_audited=true
canonical_future_label_replacement=false
outcome_resolver_change=false
regime_classifier_change=false
ui_change=false
d_hot_write=false
```

## Accepted implementation

```text
target contract:
  btcts_next/src/btcts/prediction/market_regime/future_target_definition.py

focused tests:
  btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_target_definition.py

audit:
  docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_2_TARGET_DEFINITION_AND_FEATURE_AVAILABILITY_2026-07-12.md
```

## Contract guarantees

```text
future_horizons_sec=300,900,1800,3600,21600,43200,86400
target_time=origin_time_plus_horizon
source_timestamp_must_be_lte_origin=true
origin_cutoff_inclusive=true
exact_horizon_identity_required=true
short_horizon_label_projection=false
missing_observation_outcome=unknown
invalid_observation_outcome=invalidated
required_optional_feature_overlap=false
long_horizon_session_context_required=true
macro_context_optional_for_long_horizons=true
```

## Representative D-hot conclusion

```text
source_root=D:\btc_ts_hot
latest_manifest_generated_at=2026-07-10T15:27:22Z
legacy_horizons_seen=15,30,60,300,600,900,1800,3600,14400,21600,43200,86400
canonical_mr_f5_horizons=300,900,1800,3600,21600,43200,86400
legacy_schema_has_target_definition_version=false
legacy_schema_has_feature_snapshot_ref=false
legacy_schema_has_transition_path=false
legacy_schema_has_abstain_reason=false
legacy_schema_proves_continuous_raw_feature_availability=false
```

## Verification evidence

```text
focused_target_tests=9_passed
market_regime_tests=73_passed
prediction_full_suite=339_passed
operator_ui_full_suite=1184_passed
git_diff_check=passed
patch_runner_idempotency=passed
```

## Safety

```text
d_hot_read_only=true
d_hot_modified=false
writer_executed=false
ui_inference=false
broker_private_api=false
autotrade=false
order_submission=false
parameter_auto_promotion=false
live_parameter_apply=false
```

## Next-slice boundary

MR-F5.3 may add a family-owned transparent baseline forecast model that consumes explicit horizon evidence and returns the accepted MR-F5.1 contract. It must remain shadow-only and must not replace canonical `forecast_records` labels.

Before activation, it must:

```text
abstain_when_required_feature_missing=true
preserve_origin_current_state=true
emit_exact_target_definition_version=true
emit_feature_snapshot_ref=true
emit_transition_path_candidate=true
avoid_calibrated_probability_claim=true
avoid_current_state_behavior_change=true
```

## Acceptance decision

```text
mr_f5_2_target_definition_and_feature_availability_accepted=true
current_gate=MR_F5_2_TARGET_DEFINITION_AND_FEATURE_AVAILABILITY_ACCEPTED
next_slice=MR-F5.3_family_owned_transparent_baseline_forecast_model
canonical_future_label_replacement_enabled=false
```
