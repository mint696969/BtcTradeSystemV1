# path: ./tmp/gpt_room/START.md
# desc: Current startup handoff while the first bounded MR-F9 D-hot 24-hour observation is actively running.

# Start Here — Active MR-F9 bounded 24h observation

Updated: 2026-07-17 JST
Repository HEAD under test: `38439279`
Active checkpoint: `MR_F9_LIVE_24H_OBSERVATION_RUNNING`

## Mandatory first reads

1. `tmp/gpt_room/ENVIRONMENT_GUARDS.md`
2. `tmp/gpt_room/OBSERVATION_CONTROL.md`
3. `tmp/gpt_room/CURRENT.json`
4. `tmp/gpt_room/08_STATUS.md`
5. `tmp/gpt_room/POLICY.md`
6. `tmp/gpt_room/DECISIONS.md`
7. `docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_LIVE_24H_OBSERVATION_HANDOFF_2026-07-17.md`
8. `docs/strategy/PREDICTION_SYSTEM_LONG_RUNNING_OBSERVATION_AND_HOLD_RELEASE_POLICY_2026-07-17.md`
9. `docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_FAMILY_ROADMAP_2026-07-11.md`
10. `docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_TERMINAL_LEASE_RELEASE_HARDENING_CLOSEOUT_2026-07-17.md`

Do not create or present a runner before reading `ENVIRONMENT_GUARDS.md`.

## Current live position

```text
current_family=market_regime
current_phase=MR-F9
current_gate=MR_F9_LIVE_24H_OBSERVATION_RUNNING
observation_id=mr-f9-24h-fad90fe3ed0cf9805322
collection_id=mr-f9-24h-fad90fe3ed0cf9805322
repository_commit_under_test=384392793da8745e4323e4011a72fda38b6c2893
runtime_pid=9048
lease_id=0a2f2050dce36f85f293287a0dd79476
status=RUNNING
active=true
planned_start_utc=2026-07-17T11:19:00Z
planned_end_utc=2026-07-18T11:19:00Z
planned_end_jst=2026-07-18T20:19:00+09:00
final_outcome_maturity_utc=2026-07-19T11:19:00Z
collection_24h_started=true
collection_24h_completed=false
outcome_maturity_complete=false
human_authorization_issued=true
mr_f9_complete=false
market_regime_ready_for_next_family=false
trend_bias_blocked=true
```

## Immediate authority boundary

```text
continue_authority=read-only monitoring and scheduled CONTINUE decisions only while integrity remains valid
stop_authority=explicit human/GPT checkpoint decision only
restart_authority=only after persisted RESTART_REQUIRED decision
lease_recovery_authority=forbidden while current lease is live
second_producer_authority=forbidden
```

Keep the dedicated foreground terminal open. Do not send Ctrl+C, restart Collector/producer, or run another collection producer.

## Current observation behavior

At the latest durable checkpoint:

```text
checked_at_utc=2026-07-17T17:45:11Z
decision=CONTINUE
iteration_count=386
error_count=0
written_origin_count=177
duplicate_origin_skip_count=139
readiness_skip_count=70
latest_manifest_run_id=run-20260717T174500Z-95f75c7a78b2
manifest_payload_digest_match_count=8
last_error=
```

The observation is actively writing bounded read-only runtime-horizon artifacts. This is not a stopped process and not a contract failure.

## Next checkpoint schedule

```text
15m=2026-07-17T11:34:00Z
1h=2026-07-17T12:19:00Z
6h=2026-07-17T17:19:00Z
12h=2026-07-17T23:19:00Z
planned_end=2026-07-18T11:19:00Z
final_maturity=2026-07-19T11:19:00Z
```

The six-hour checkpoint is accepted with `decision=CONTINUE`. The next canonical checkpoint is the 12-hour check at `2026-07-17T23:19:00Z`.

## Parallel work

Allowed now:

```text
read-only monitoring
checkpoint receipts
manifest/digest verification
offline analysis
repo-tmp-only tests
documentation
MR-F10 context contract/interface design not applied to runtime
```

Held from application:

```text
prediction logic or parameters
candidate selection
features
UNKNOWN/fallback rules
readiness/source semantics
timestamp/dedupe semantics
target/outcome semantics
cadence
persistence identity/schema
Collector/producer restart or configuration
```

## Roadmap

MR-F9 UI/WS timestamp trace is accepted with an explicit integration limitation. MR-F10 offline design may now proceed in parallel while MR-F9 collection monitoring, the 12-hour checkpoint, and the collection-to-card integration follow-up remain active. MR-F9 remains open until collection completion, final outcome maturity, evidence review, and explicit hold-release decisions. TrendBias remains blocked until `MARKET_REGIME_READY_FOR_NEXT_FAMILY`.
## Durable project-memory rule

```text
gpt_room_runtime_path=tmp/gpt_room
gpt_room_move_forbidden_without_profile_backend_migration=true
tracked_allowlist=config/gpt_room_tracked_files.json
persistence_guard=python scripts/check_gpt_room_persistence.py
durability_requires=commit_and_remote_push
```

Canonical room files are intentionally tracked inside the otherwise ignored `tmp/` tree. Successor GPTs must update and commit them with checkpoint or policy changes; generated indexes, history, backups, self-tests, logs, and `tmp/work` remain untracked.

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
