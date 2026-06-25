# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19Y_ACTUAL_POINT_SELECTION_DECISION_LOCK_2026-06-25.md
# desc: PS-Q19Y decision lock for actual-point selection policy before moving to collector/reanchor/crossed-book repair.
# PS-Q19Y Actual point selection decision lock

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: a047170a

## Purpose

PS-Q19Y closes the PS-Q19R through PS-Q19X observation / diagnosis / comparison phase with a policy decision lock.

```text
ps_q19y_actual_point_selection_decision_lock=true
policy_decision_locked=true
phase_boundary_observation_diagnosis_complete=true
next_thread_starts_collector_reanchor_crossed_book_repair=true
```

## Locked decision

Do not change PS-Q19R behavior in this thread.

```text
ps_q19r_current_policy=strict_nearest_then_fail_closed_quality_gate
ps_q19r_behavior_change_allowed_now=false
nearest_quality_ok_within_tolerance_candidate_status=deferred
collector_reanchor_crossed_book_repair_preferred_next=true
```

## Rationale

PS-Q19X proved that the PS-Q19U 300s horizon had a same-second quality-ok candidate while strict nearest selected a quarantined/reanchor/crossed-book row.

```text
prediction_generated_at=2026-06-25T11:59:14Z
impacted_horizons=300
strict_nearest_quality_ok=false
strict_nearest_trust_state=quarantined
strict_nearest_interpretation_bucket=reanchor_required
strict_nearest_spread=-2.0
quality_ok_candidate_available=true
quality_ok_candidate_same_second=true
quality_ok_candidate_trust_state=trusted
quality_ok_candidate_interpretation_bucket=allow_structural_use
quality_ok_candidate_spread=2013.0
```

However, changing the actual-point selection policy would change review/scoring semantics. That should not be done at the end of a long observation thread.

## Final policy for this thread

```text
strict_fail_closed_remains_active=true
quality_rejected_records_are_not_scored=true
same_second_quality_ok_candidate_is_recorded_as_diagnostic_evidence_only=true
ps_q19r_review_scoring_policy_not_changed=true
operator_policy_decision_required_before_any_ps_q19r_behavior_change=true
```

## Next thread entry point

Start from collector / reanchor / crossed-book repair diagnostics.

```text
next_slice=PS-Q20A_COLLECTOR_REANCHOR_CROSSED_BOOK_REPAIR_DIAGNOSIS
start_from=PS-Q19W_AND_PS_Q19X_EVIDENCE
primary_question=why_same_second_market_overview_contains_quarantined_crossed_rows_and_trusted_rows
avoid_first_step=changing_ps_q19r_selection_policy
```

## Completed evidence chain

```text
PS-Q19R: prediction versus actual market review helper
PS-Q19S: repeat bounded observation review confirmed
PS-Q19T: multi-window review summary helper
PS-Q19U: partial observation accepted with market quality block recorded separately
PS-Q19V: observation outcome policy classifier
PS-Q19W: market overview quality-block diagnosis
PS-Q19X: strict nearest versus quality-ok candidate comparison
PS-Q19Y: decision lock and next-thread boundary
```

## Safety boundary

```text
read_only_policy_lock=true
runtime_artifact_write_performed_by_decision_lock=false
status_artifact_write_performed_by_decision_lock=false
prediction_artifact_write_performed_by_decision_lock=false
view_artifact_write_performed_by_decision_lock=false
collector_state_write_performed_by_decision_lock=false
ps_q19r_behavior_changed_by_decision_lock=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
ui_triggered_runner_execution=false
approval_or_authorization_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```
