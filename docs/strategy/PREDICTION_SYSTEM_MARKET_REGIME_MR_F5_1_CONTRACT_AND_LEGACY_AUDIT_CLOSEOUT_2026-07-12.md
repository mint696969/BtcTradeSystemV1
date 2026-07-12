# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_1_CONTRACT_AND_LEGACY_AUDIT_CLOSEOUT_2026-07-12.md
# desc: Acceptance closeout for the MR-F5.1 future forecast contract and legacy-path audit.

# Prediction System MarketRegime MR-F5.1 Contract and Legacy-Path Audit Closeout

Updated: 2026-07-12 JST
Checkpoint: MR_F5_1_FUTURE_FORECAST_CONTRACT_AND_LEGACY_PATH_AUDIT_ACCEPTED
Status: accepted
Next slice: MR-F5.2 horizon target-definition and feature-availability audit

## Accepted scope

```text
immutable_future_forecast_contract=true
legacy_future_label_ownership_audited=true
seven_future_horizons_fixed=true
current_state_contract_unchanged=true
canonical_future_label_replacement=false
regime_classifier_change=false
ui_change=false
d_hot_writer_execution=false
```

## Accepted implementation

```text
contract:
  btcts_next/src/btcts/prediction/market_regime/future_forecast_contract.py

focused tests:
  btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_forecast_contract.py

legacy audit:
  docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_1_CONTRACT_AND_LEGACY_AUDIT_2026-07-12.md
```

## Contract guarantees

```text
future_horizons_sec=300,900,1800,3600,21600,43200,86400
current_horizon_excluded=true
complete_set_requires_each_horizon_once=true
origin_current_state_preserved=true
forecast_identity_required=true
target_definition_version_matches_horizon=true
abstain_requires_unknown_and_reason=true
transition_path_terminal_state_matches_prediction=true
transition_path_time_bounded=true
metadata_defensively_frozen=true
raw_score_distinct_from_calibration=true
calibrated_probability_claim_before_mr_f7=false
```

## Legacy ownership conclusion

```text
mr_f4_owns_canonical_current_state=true
forecast_records_remains_compatibility_future_input=true
regime_classifier_remains_compatibility_projection_owner=true
mr_f5_family_owned_future_forecast_not_canonical_yet=true
```

## Verification evidence

```text
focused_contract_tests=10_passed
market_regime_tests=64_passed
prediction_full_suite=330_passed
operator_ui_full_suite=1184_passed
git_diff_check=passed
patch_runner_idempotency=passed_twice
```

## Safety

```text
d_hot_modified=false
writer_executed=false
ui_inference=false
broker_private_api=false
autotrade=false
order_submission=false
parameter_auto_promotion=false
live_parameter_apply=false
```

## Known next-work requirements

MR-F5.2 must define and verify, independently for every horizon:

```text
origin timestamp semantics
evaluation timestamp semantics
observation window
outcome resolver identity
state assignment rule
partial-match rule
missing and invalid observation behavior
lookahead prevention
available feature families from representative D-hot samples
short-to-long horizon projection prohibition
```

## Acceptance decision

```text
mr_f5_1_contract_and_legacy_path_audit_accepted=true
current_gate=MR_F5_1_FUTURE_FORECAST_CONTRACT_AND_LEGACY_PATH_AUDIT_ACCEPTED
next_slice=MR-F5.2_horizon_target_definition_and_feature_availability_audit
canonical_future_label_replacement_enabled=false
```
