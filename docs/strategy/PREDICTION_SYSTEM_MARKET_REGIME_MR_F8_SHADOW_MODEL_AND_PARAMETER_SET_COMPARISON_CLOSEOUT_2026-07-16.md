# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON_CLOSEOUT_2026-07-16.md
# desc: Canonical MR-F8 closeout for same-window active/shadow comparison, insufficient-evidence governance, rollback, and MR-F9 evidence handoff.

# Prediction System MarketRegime MR-F8 Shadow Model and Parameter-Set Comparison Closeout

Updated: 2026-07-16 JST
Checkpoint: `MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON_ACCEPTED`
Implementation basis HEAD: `7d9e81f4`
Decision: `insufficient_evidence`

## 1. Acceptance statement

MR-F8 is accepted as the comparison and governance boundary for MarketRegime active/shadow candidates.

Acceptance means that two parameter sets can be generated at the same prediction origin, with the same source snapshot, target definition, horizon boundary, outcome resolver, and immutable trace identity; their available outcomes can be compared without inventing missing evidence; and evidence insufficiency fails closed without candidate promotion.

Acceptance does not mean that the shadow candidate won, that displayed confidence is calibrated, or that live parameters may be changed.

## 2. Compared candidates

```text
active:
  market_regime.future.transparent_baseline.params.v1

shadow:
  market_regime.future.transparent_baseline.params.conservative.v1

rollback_candidate:
  market_regime.future.transparent_baseline.params.v1
```

The runtime shadow feature candidate remains non-canonical:

```text
market_regime.origin_feature.shadow.ma_5_20.interquartile.v1
```

## 3. Accepted implementation chain

```text
comparison_contract=16b4a6e0
paired_forecasts=3ea55a8b
outcome_join=795af90e
comparison_proposal=dbad73f9
shadow_pair_dry_run=9ece23ff
trace_plan=07401fa5
preflight_integration=9ee2f6b5
guarded_writer=751f1690
guarded_writer_cli=ec830323
runtime_preflight_bridge=b534cb7a
runtime_preflight_once=fa2be316
runtime_preflight_repair=cd4a095b
runtime_writer_handoff=3161ebcc
runtime_outcome_intake=2843e3fd
ledger_observation=583d73ac
comparison_evidence_preservation=11778737
honest_partial_comparison=7d9e81f4
```

## 4. Verified runtime evidence

The verified D-hot read-only origin was:

```text
prediction_origin=2026-07-15T09:12:33Z
source_snapshot_ok=true
runtime_source_ready=true
source_quality_ready=true
pair_count=7
forecast_count=14
trace_count=14
writer_invoked=false
writes_dhot=false
```

Evidence:

```text
tmp/work/mr_f8_8_runtime_once/dhot_runtime_preflight_verified.json
tmp/work/mr_f8_9_writer_handoff/tmp_writer_verification.json
tmp/work/mr_f8_11_ledger_observation/dhot_runtime_outcome_summary.json
tmp/work/mr_f8_13_partial_comparison/real_partial_comparison_report.json
tmp/work/mr_f8_13_partial_comparison/real_partial_comparison_summary.json
```

Canonical ledger observation resolved four horizons and left three unresolved:

```text
observed_horizons=300,900,1800,3600
unresolved_horizons=21600,43200,86400
resolved_trace_count=8
unresolved_trace_count=6
```

## 5. Same-window comparison result

```text
same_window_comparison=true
same_source_snapshot=true
pair_count=7
outcome_row_count=14
```

Active result:

```text
resolved_slot_count=4
coverage_rate=0.142857142857143
abstention_rate=0.428571428571429
unresolved_rate=0.428571428571429
accuracy_on_resolved_non_abstained=1.0
status_counts=ABSTAINED:3,CORRECT:1,UNRESOLVED:3
```

Shadow result:

```text
resolved_slot_count=4
coverage_rate=0.0
abstention_rate=0.571428571428571
unresolved_rate=0.428571428571429
accuracy_on_resolved_non_abstained=null
status_counts=ABSTAINED:4,UNRESOLVED:3
```

The accepted decision is:

```text
decision=insufficient_evidence
selected_candidate_id=null
rollback_candidate_id=market_regime.future.transparent_baseline.params.v1
human_approval_required=true
auto_promotion_allowed=false
live_parameter_apply_allowed=false
proposal_is_not_runtime_activation=true
```

Blockers preserved rather than inferred away:

```text
minimum_observed_slots_not_met
full_horizon_window_incomplete
probability_metrics_unavailable_for_legacy_origin
multi_origin_churn_and_transition_delay_unavailable
```

## 6. Promotion policy carried into MR-F9

The current proposal policy requires at least:

```text
minimum_observed_slots=30
minimum_coverage_rate=0.20
minimum_accuracy_delta=0.02
maximum_brier_regression=0.01
maximum_ece_regression=0.02
maximum_unknown_rate_increase=0.05
```

Meeting numeric thresholds creates a review proposal only. It never authorizes automatic promotion or live parameter mutation. A shadow winner still requires human approval, an explicit rollback point, and a separately guarded activation change.

Continuing development alone does not promote a candidate. MR-F9 must accumulate trustworthy, mature, out-of-sample paired outcomes across multiple origins and conditions.

## 7. Upstream prediction-execution trust concern carried into MR-F9

The operator UI remains display-only. UI inference and UI confidence recalculation remain forbidden.

The unresolved concern is upstream artifact generation: repeated short-horizon cards with the same confidence value and persistent long-horizon `UNKNOWN` must not be accepted as proof that independent horizon-specific prediction executed correctly.

MR-F9 must prove, for every enabled horizon:

```text
separate immutable trace_id
prediction_origin and target_horizon_sec
model_id, logic_version, and parameter_set_id
feature_snapshot_ref and source freshness
raw horizon-specific score or probability distribution
calibration input and output when mature
abstention decision
fallback_used and fallback_reason
artifact generated_at and update continuity
```

MR-F9 must distinguish:

```text
independent horizon inference that happens to agree
from
one current-state or fallback value projected into multiple horizons
```

Required diagnostics include:

```text
full-inference rate versus fallback rate by horizon
persistence of identical confidence values across horizons and origins
prediction-origin update continuity
stale forecast recurrence
long-horizon UNKNOWN persistence
probability-distribution availability
confidence provenance and calibration maturity
```

A changing UI display is not the acceptance criterion. Traceable proof of independent upstream prediction execution is the acceptance criterion.

## 8. MR-F9 ownership

The following evidence-maturity work is transferred without loss to MR-F9:

```text
multiple-origin paired forecast accumulation
horizon-expiry outcome completion
condition-specific comparison
balanced accuracy and macro F1
Brier score, log loss, and ECE
state churn and transition-detection delay
confidence calibration maturity
winner, tie, or insufficient-evidence proposal
human-gated promotion review
independent horizon-inference proof
fallback and fixed-confidence diagnostics
long-horizon UNKNOWN investigation
```

Canonical register ownership:

```text
RW-MR-003=MR-F9 outcome/review/calibration evidence loop
RW-MR-003A=MR-F9 horizon-specific inference execution proof
RW-MR-003B=MR-F9 shadow promotion evidence and human-gated review
```

## 9. Safety and rollback

```text
D_hot_modified_by_closeout=false
fixture_evidence_written_to_D_hot=false
scheduler_enabled=false
broker_private_api=false
autotrade=false
order_submission=false
parameter_auto_promotion=false
live_parameter_apply=false
runtime_card_confidence_replacement=false
```

Rollback remains the active parameter set and implementation basis HEAD `7d9e81f4`. No canonical runtime candidate changed during MR-F8 closeout.

## 10. Handoff

```text
current_gate=MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON_ACCEPTED
next_gate=MR_F9_OUTCOME_REVIEW_CALIBRATION_EVIDENCE_LOOP
current_phase=MR-F9
market_regime_ready_for_next_family=false
trend_bias_blocked=true
```

MR-F8 has no remaining implementation task. Its unresolved evidence questions are explicitly owned by named MR-F9 work and may not disappear during thread handoff.
