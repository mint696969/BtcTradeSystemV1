# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F7_CONFIDENCE_CALIBRATION_CLOSEOUT_2026-07-15.md
# desc: MR-F7 confidence-calibration implementation, empirical evidence, activation boundary, rollback point, and handoff to MR-F8.

# Prediction System MarketRegime MR-F7 Confidence Calibration Closeout

Updated: 2026-07-15 JST
Checkpoint: MR_F7_CONFIDENCE_CALIBRATION_ACCEPTED
Contract status: accepted

<!-- PS_MARKET_REGIME_MR_F7_CLOSEOUT_2026_07_15 -->

## 1. Decision

```text
mr_f7_confidence_calibration_accepted=true
mr_f7_dataset_contract_accepted=true
mr_f7_bucket_context_contract_accepted=true
mr_f7_oos_split_and_maturity_accepted=true
mr_f7_estimator_and_shrinkage_accepted=true
mr_f7_caps_and_fallback_accepted=true
mr_f7_diagnostics_accepted=true
mr_f7_forecast_projection_accepted=true
mr_f7_operator_read_model_accepted=true
mr_f7_evidence_readiness_accepted=true
mr_f7_read_only_d_hot_audit_accepted=true
runtime_calibrated_probability_activation=false
runtime_card_confidence_replacement=false
detailed_source_flag_fit_active=false
auto_parameter_update=false
live_parameter_apply=false
broker_private_api=false
autotrade=false
order_submission=false
scheduler_registration=false
next_gate=MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON
```

MR-F7 is accepted as the complete confidence-calibration architecture, evidence boundary, and fail-closed activation contract. Acceptance does not claim that current runtime cards are calibrated probabilities. Display-confidence replacement remains disabled until the relevant mature out-of-sample guard passes.

Existing D-hot history is accepted for coarse calibration analysis under available legacy dimensions. It is not accepted for detailed source/flag fitting because legacy trace rows do not contain the full contribution ledger or parameter semantics.

## 2. Accepted delivery map

```text
MR-F7.1 calibration dataset contract
  module=calibration_dataset.py
  responsibility=normalize prediction/outcome evidence without lookahead leakage

MR-F7.2 bucket context contract
  dimensions=horizon,regime,model,logic,parameter_set,session,volatility,liquidity,freshness,source_quality

MR-F7.3 OOS split and maturity
  split=time_ordered_train_validation_test
  random_split=false
  maturity=EMPTY|SPARSE|PROVISIONAL|MATURE

MR-F7.4 calibration estimator
  method=hierarchical_beta_binomial
  raw_confidence_conditioned=true
  shrinkage=true

MR-F7.5 caps and fallback
  stale,degraded,reference_only,long_horizon,sparse,provisional caps are versioned
  fallback hierarchy is explicit and auditable

MR-F7.6 diagnostics
  brier,log_loss,ece,reliability_buckets,high_confidence_misses,overconfidence,underconfidence,coverage,selective_accuracy

MR-F7.7 forecast projection
  calibrated_reliability separated from calibration_display_confidence
  probability claim requires mature uncapped OOS evidence

MR-F7.8 operator read model
  calibration state, probability claim, empirical reliability, and capped display confidence are exposed separately

MR-F7.9 evidence and closeout
  versioned source/flag contribution trace ledger
  readiness classification
  bounded read-only D-hot once audit
  acceptance and rollback boundary
```

## 3. Confidence semantics

```text
raw_model_score_or_probability
  = model or scoring output before empirical calibration

calibrated_reliability
  = empirically estimated outcome probability under the selected OOS cohort

calibration_display_confidence
  = calibrated reliability after safety caps

card confidence replacement
  = disabled by default
  = allowed only by explicit switch plus mature uncapped probability claim
```

A source is not treated as one vote. The accepted trace model preserves each computed source/flag contribution separately and rejects missing or duplicate contribution identities.

## 4. Source/flag evidence boundary

The accepted MR-F7 trace contribution ledger preserves:

```text
horizon_key
source_id
flag_id
supports_regime
strength
weighted_strength
observed_value
against_regimes
source_refs
reason
contribution_key
```

The complete-ledger contract requires `signal_votes_all`; legacy top-N votes cannot silently substitute. Persisted contribution count must equal the scoring report total vote count.

Detailed source/flag fitting additionally requires:

```text
parameter_id
parameter_version
base_reliability
signed_contribution
interaction_adjustment
quality_adjustment
freshness_adjustment
final_contribution
```

These semantics are not inferred from legacy rows. Missing and invalid fields fail closed.

## 5. D-hot empirical evidence

Read-only complete audit artifact:

```text
tmp/work/mr_f7_evidence_once/d_hot_report_complete.json
```

Audit result on 2026-07-15:

```text
report_ok=true
input_complete=true
reader_ok=true
outcome_files=3
outcome_rows=37248
outcome_bytes=85692421
outcome_truncated=false
trace_files=159
trace_lines_scanned=18262
trace_rows_retained=6050
trace_rows_filtered=12212
trace_bytes=385389377
trace_truncated=false
reader_failures=0
matched_outcome_rows=37248
unmatched_outcome_rows=0
legacy_coarse_trace_outcomes=37248
full_contribution_trace_outcomes=0
trusted_evaluable_coarse_rows=36360
detailed_source_flag_rows=0
coarse_calibration_ready=true
detailed_source_flag_calibration_ready=false
detailed_blocker=full_contribution_ledger_missing
```

Interpretation:

```text
legacy history is usable for coarse OOS calibration analysis
legacy history is not usable for detailed source/flag fitting
no missing contribution is synthesized
new enriched traces must accumulate trusted candle outcomes before detailed activation
```

## 6. Activation and maturity policy

MR-F7 acceptance separates implementation completion from runtime probability activation.

```text
implementation_complete=true
coarse_evidence_available=true
runtime_probability_claim=false
runtime_display_replacement=false
detailed_fit_waits_for_new_evidence=true
```

Reentry condition for detailed source/flag calibration:

```text
full contribution ledger active in trace
required parameter and contribution semantics present and valid
trusted candle outcomes accumulated
minimum maturity threshold satisfied under time-ordered OOS split
diagnostics and caps pass
human review accepts activation evidence
```

Until then, the UI must expose `UNCALIBRATED`, `INSUFFICIENT_SAMPLE`, `PROVISIONAL`, or `CAPPED` as appropriate and must not describe the percentage as a calibrated probability.

## 7. Accepted implementation and rollback points

```text
mr_f7_dataset_foundation_commit=6487a117
mr_f7_estimator_commit=8737655b
mr_f7_projection_commit=615c501d
mr_f7_source_flag_trace_commit=b1020269
mr_f7_evidence_readiness_commit=c708ada0
mr_f7_evidence_audit_commit=23660311
```

Accepted rollback point:

```text
rollback_commit=23660311
rollback_behavior=retain MR-F7 contracts and read-only evidence tools while keeping runtime probability activation disabled
card_confidence_replacement=false
runtime_fit=false
D_hot_write=false
scheduler=false
auto_promotion=false
live_parameter_apply=false
```

## 8. Verification evidence

```text
calibration_dataset_focused=10_passed
calibration_estimator_focused=11_passed
projection_state_operator_focused=20_passed
trace_contribution_focused=7_passed
trace_connected=23_passed
evidence_readiness_focused=5_passed
evidence_once_focused=5_passed
evidence_once_connected=12_passed
latest_market_regime_suite=404_passed
prediction_full_suite=288_passed
operator_ui_full_suite=1230_passed
py_compile=passed
git_diff_check=passed
D_hot_complete_read_only_audit=passed
```

Final closeout guards were rerun on 2026-07-15 and passed. MR-F7 may advance to MR-F8 planning while runtime calibrated-probability activation remains disabled.

## 9. Deferred non-blocking continuation

```text
stable_id=RW-MR-NB-001
name=MR-F7 detailed source/flag calibration evidence accumulation and activation review
blocking=false
owner=MR-F9 outcome/review/calibration evidence loop
reason=legacy history predates the complete contribution ledger
reentry_condition=trusted mature OOS outcomes exist for enriched trace rows and activation diagnostics pass
compatibility_requirement=do not change accepted confidence semantics or silently replace card confidence
```

This continuation may refine reliability and contribution parameters but may not auto-promote, live-apply, or mutate runtime confidence without a new acceptance decision.

## 10. Safety proof

```text
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_submission_allowed=false
parameter_auto_promotion_allowed=false
live_parameter_apply_allowed=false
scheduler_registration_allowed=false
runtime_calibration_fit_enabled=false
runtime_card_confidence_replacement_enabled=false
D_hot_modified_by_closeout=false
```

## 11. MR-F8 handoff

```text
current_gate=MR_F7_CONFIDENCE_CALIBRATION_ACCEPTED
next_gate=MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON
market_regime_ready_for_next_family=false
trend_bias_blocked=true
```

MR-F8 must compare at least two candidate models or parameter sets over identical windows and sources. It must preserve MR-F7 raw/calibrated/display-confidence separation, require human approval, and keep auto-promotion and live parameter application disabled.
