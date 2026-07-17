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
last_checkpoint_at_utc=2026-07-17T11:20:43Z
last_checkpoint_decision=CONTINUE
next_check_at_utc=2026-07-17T11:34:00Z
collection_24h_started=true
collection_24h_completed=false
outcome_maturity_complete=false
evidence_review_complete=false
holds_released=false
```

## Latest known counters

```text
iteration_count=56
error_count=0
written_origin_count=0
duplicate_origin_skip_count=0
readiness_skip_count=56
last_skip_reason=source_not_current:300,900,1800,3600,21600,43200,86400
last_error=
stop_requested=false
```

## Required checkpoints

```text
startup=2026-07-17T11:20:43Z CONTINUE
approximately_15_minutes=2026-07-17T11:34:00Z due/passed; receipt pending
approximately_1_hour=2026-07-17T12:19:00Z
approximately_6_hours=2026-07-17T17:19:00Z
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
next_observation_action=create durable approximately-15-minute checkpoint receipt read-only
next_parallel_work=begin MR-F10 stable context contract offline design only
collection_terminal_action=none
```
