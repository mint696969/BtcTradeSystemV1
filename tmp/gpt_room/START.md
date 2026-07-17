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

MR-F9 UI/WS timestamp trace is the next active slice. After that trace is accepted, MR-F10 offline design may proceed in parallel while MR-F9 collection monitoring and scheduled checkpoints remain active. MR-F9 remains open until collection completion, final outcome maturity, evidence review, and explicit hold-release decisions. TrendBias remains blocked until `MARKET_REGIME_READY_FOR_NEXT_FAMILY`.
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
