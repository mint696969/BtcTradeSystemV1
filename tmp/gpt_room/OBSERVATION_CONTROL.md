# path: ./tmp/gpt_room/OBSERVATION_CONTROL.md
# desc: Canonical current state and decision schedule for the active first bounded MR-F9 observation.

# Observation Control

Updated: 2026-07-17 JST
Canonical policy: `docs/strategy/PREDICTION_SYSTEM_LONG_RUNNING_OBSERVATION_AND_HOLD_RELEASE_POLICY_2026-07-17.md`

<!-- MR_F9_LIVE_24H_OBSERVATION_HANDOFF_2026_07_17 -->

## Active observation

```text
observation_id=mr-f9-24h-fad90fe3ed0cf9805322
family=market_regime
purpose=first_bounded_24h_production_path_and_evidence_pipeline_qualification
state=RUNNING
collection_id=mr-f9-24h-fad90fe3ed0cf9805322
runtime_pid=9048
lease_id=0a2f2050dce36f85f293287a0dd79476
repository_commit_under_test=384392793da8745e4323e4011a72fda38b6c2893
working_tree_clean_at_start=true
planned_start_utc=2026-07-17T11:19:00Z
planned_end_utc=2026-07-18T11:19:00Z
planned_end_jst=2026-07-18T20:19:00+09:00
latest_origin_expiry_utc=2026-07-19T11:19:00Z
last_checkpoint_at_utc=2026-07-17T17:45:11Z
last_checkpoint_decision=CONTINUE
missed_checkpoint_warning=true
next_check_at_utc=2026-07-17T23:19:00Z
collection_24h_started=true
collection_24h_completed=false
outcome_maturity_complete=false
evidence_review_complete=false
holds_released=false
```

## Latest known counters

```text
iteration_count=386
error_count=0
written_origin_count=177
duplicate_origin_skip_count=139
readiness_skip_count=70
latest_manifest_run_id=run-20260717T174500Z-95f75c7a78b2
manifest_payload_digest_match_count=8
last_error=
stop_requested=false
```

## Required checkpoints

```text
startup=2026-07-17T11:20:43Z CONTINUE
approximately_15_minutes=2026-07-17T11:34:00Z delayed receipt accepted CONTINUE
approximately_1_hour=2026-07-17T12:19:00Z delayed receipt accepted CONTINUE
approximately_6_hours=2026-07-17T17:19:00Z delayed receipt accepted CONTINUE
approximately_12_hours=2026-07-17T23:19:00Z
planned_end=2026-07-18T11:19:00Z
final_outcome_maturity=2026-07-19T11:19:00Z
evidence_review=after maturity
```

## Continue/stop/restart authority

```text
CONTINUE=allowed only while lease, identity, safety, source health, and integrity remain valid
PAUSE_OR_ABORT=requires explicit checkpoint decision and persisted receipt
RESTART_REQUIRED=requires identity or implementation defect that invalidates comparability
lease_recovery=forbidden while live lease heartbeat remains valid
second_producer=forbidden
```

## Held-work register

```text
hold_id=MRF9-OBS-001
work_item=apply changes to running MarketRegime logic, parameters, candidate, features, fallback, or UNKNOWN semantics
status=HELD
allowed_offline_work=implementation and repo-tmp tests not loaded by runtime
release_condition=explicit evidence-review or supersession receipt

hold_id=MRF9-OBS-002
work_item=apply changes to runtime-horizon readiness, source, timestamp, dedupe, target, cadence, or persistence semantics
status=HELD
allowed_offline_work=design and repo-tmp guarding only
release_condition=explicit evidence-review or new-observation receipt

hold_id=MRF9-OBS-003
work_item=read-only monitoring, documentation, offline analysis, and MR-F10 interface design
status=RELEASED
allowed_offline_work=read-only monitoring, receipts, offline analysis, docs, repo-tmp tests, MR-F10 schema/interface design
release_condition=already allowed
```

## Next required action

```text
next_observation_action=perform 12-hour checkpoint read-only at 2026-07-17T23:19:00Z
next_parallel_work=MR-F10_offline_design_with_MR-F9_observation_and_UI_integration_follow_up
collection_terminal_action=none
```

<!-- MR_F9_DELAYED_EARLY_CHECKPOINT_RECEIPT_2026_07_17 -->
## Delayed early checkpoint decision

```text
checked_at_utc=2026-07-17T14:53:08Z
scheduled_15m=2026-07-17T11:34:00Z missed_receipt_warning=true
scheduled_1h=2026-07-17T12:19:00Z missed_receipt_warning=true
decision=CONTINUE
iteration_count=214
written_origin_count=78
readiness_skip_count=70
error_count=0
latest_manifest_run_id=run-20260717T145300Z-08193b88b338
manifest_payload_digest_match_count=8
next_check_at_utc=2026-07-17T17:19:00Z
```

<!-- MR_F9_6_HOUR_CHECKPOINT_RECEIPT_2026_07_17 -->
## Six-hour checkpoint decision

```text
scheduled_checkpoint_utc=2026-07-17T17:19:00Z
checked_at_utc=2026-07-17T17:45:11Z
late_checkpoint_warning=true
decision=CONTINUE
iteration_count=386
written_origin_count=177
readiness_skip_count=70
error_count=0
latest_manifest_run_id=run-20260717T174500Z-95f75c7a78b2
manifest_payload_digest_match_count=8
next_check_at_utc=2026-07-17T23:19:00Z
```

<!-- MR_F9_PRE_F10_EXECUTION_PLAN_2026_07_18 -->
## Pre-F10 ordered work

```text
next_slice=MR_F9_UI_WS_TIMESTAMP_TRACE
following_parallel_slice=MR_F10_OFFLINE_STABLE_CONTEXT_CONTRACT_DESIGN
MR_F10_entry_condition=UI_WS_timestamp_trace_accepted
MR_F9_collection_monitoring_remains_active=true
MR_F9_12_hour_checkpoint_remains_required=true
later_phase_start_does_not_close_earlier_open_items=true
```

<!-- MR_F9_UI_WS_TIMESTAMP_TRACE_RECEIPT_2026_07_18 -->
## UI/WS timestamp trace decision

```text
status=accepted_with_limitation
decision=PROCEED_TO_MR_F10_OFFLINE_DESIGN
collection_lane_directly_rendered=false
current_dhot_market_regime_push_present=false
selected_artifact_fallback_wired_from_page=false
latest_cards_direct_render_fallback_present=true
observed_latest_cards_generated_at=2026-07-17T18:24:40Z
observed_latest_cards_run_id=market_regime_20260717T182440Z_once
ui_prediction_invoked=false
ui_classifier_invoked=false
integration_follow_up_required=true
MR_F9_collection_monitoring_remains_active=true
MR_F9_12_hour_checkpoint_remains_required=true
```

<!-- MR_F9_P1_RUNTIME_HORIZON_READ_MODEL_QUALIFICATION_2026_07_18 -->
## MR-F9 P1 qualification

```text
P1_status=COMPLETE
qualified_live_run_id=run-20260717T190000Z-fb7c2cc20e9b
qualified_prediction_origin=2026-07-17T19:00:00Z
horizon_count=8
payload_digest_match_count=8
selected_source=artifact
card_count=8
prediction_invoked=false
classifier_invoked=false
confidence_recalculated=false
writes_dhot=false
mount_enabled=false
next_slice=MR_F9_TRUST_FALLBACK_UNKNOWN_PREMATURITY_QUALIFICATION
MR_F9_collection_monitoring_remains_active=true
```

<!-- MR_F9_SPARSE_CANDLE_INCIDENT_AND_RESTART_DECISION_2026_07_18 -->
## MR-F9 sparse-candle incident

```text
failed_collection_id=mr-f9-24h-fad90fe3ed0cf9805322
failed_status=FAILED_CONTRACT
failed_at_utc=2026-07-17T22:22:00Z
written_origin_count=253
error=origin_feature_runtime_bundle_candle_row_count_not_sixty
root_cause=valid_absent_candle_gap_policy_vs_contiguous_sixty_window_boundary
fix=known_sparse_condition_to_READINESS_SKIP
focused_test_count=31
same_collection_id_restart_allowed=false
replacement_collection_required=true
old_253_origins_preserved=true
next_slice=MR_F9_SPARSE_CANDLE_INCIDENT_COMMIT_AND_REPLACEMENT_PRESTART_GATE
parallel_slice=MR_F9_TRUST_FALLBACK_UNKNOWN_PREMATURITY_QUALIFICATION
```

<!-- MR_F9_SPARSE_CANDLE_INCIDENT_FIX_COMMIT_RECORDED_2026_07_18 -->
## MR-F9 sparse-candle incident fix commit

```text
incident_fix_commit=fead05b6c24e458d54a5758f908b93d413de99f6
remote_push_verified=true
incident_status=qualified_fix_committed
current_gate=MR_F9_REPLACEMENT_COLLECTION_PRESTART_GATE
next_slice=MR_F9_REPLACEMENT_COLLECTION_READ_ONLY_PRESTART_GATE
parallel_slice=MR_F9_TRUST_FALLBACK_UNKNOWN_PREMATURITY_QUALIFICATION
```

<!-- MR_F9_REPLACEMENT_24H_COLLECTION_START_RECEIPT_2026_07_18 -->
## MR-F9 replacement 24h collection

```text
collection_id=mr-f9-24h-5be7ba757eac727bab10
status=RUNNING
active=true
repository_commit_under_test=a784526cd913f60c2afbd655a535d7ac52f9983d
runtime_pid=20176
lease_id=4283ab4f0e27b0337072c623bcf2b40f
planned_start_utc=2026-07-18T04:14:00Z
planned_start_jst=2026-07-18T13:14:00+09:00
checkpoint_6h_utc=2026-07-18T10:14:00Z
checkpoint_6h_jst=2026-07-18T19:14:00+09:00
checkpoint_12h_utc=2026-07-18T16:14:00Z
checkpoint_12h_jst=2026-07-19T01:14:00+09:00
checkpoint_18h_utc=2026-07-18T22:14:00Z
checkpoint_18h_jst=2026-07-19T07:14:00+09:00
planned_end_utc=2026-07-19T04:14:00Z
planned_end_jst=2026-07-19T13:14:00+09:00
final_outcome_maturity_not_before_utc=2026-07-20T04:14:00Z
final_outcome_maturity_not_before_jst=2026-07-20T13:14:00+09:00
next_slice=MR_F9_TRUST_FALLBACK_UNKNOWN_PREMATURITY_QUALIFICATION
next_observation_gate=MR_F9_REPLACEMENT_6_HOUR_CHECKPOINT
terminal_A_must_remain_open=true
```

<!-- MR_F9_P2_TRUST_FALLBACK_UNKNOWN_QUALIFICATION_2026_07_18 -->
## MR-F9 P2 trust / fallback / UNKNOWN qualification

```text
status=qualified_pending_test_and_commit
fallback_truth_required=true
unknown_preserved=true
prematurity_preserved=true
confidence_recalculated=false
classifier_invoked=false
writes_dhot=false
runtime_collection_mutated=false
next=MR_F9_P3_REVIEW_PROPOSAL_PREMATURITY_QUALIFICATION
```

<!-- MR_F9_P2_ACCEPTED_AFTER_24_TESTS_2026_07_18 -->
## MR-F9 P2 accepted

```text
status=accepted
focused_test_count=24
focused_tests_passed=true
structural_validation_passed=true
next=MR_F9_P3_REVIEW_PROPOSAL_PREMATURITY_QUALIFICATION
```
