# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_LIVE_24H_OBSERVATION_HANDOFF_2026-07-17.md
# desc: Canonical handoff for the active first bounded MR-F9 D-hot 24-hour observation across GPT/thread changes.

# MarketRegime MR-F9 Live 24h Observation Handoff

Updated: 2026-07-17 JST
Status: active
Checkpoint: MR-F9_LIVE_24H_OBSERVATION_RUNNING

<!-- MR_F9_LIVE_24H_OBSERVATION_HANDOFF_2026_07_17 -->

## Active identity

```text
observation_id=mr-f9-24h-fad90fe3ed0cf9805322
collection_id=mr-f9-24h-fad90fe3ed0cf9805322
family=market_regime
purpose=production_path_and_evidence_pipeline_qualification
repository_commit_under_test=384392793da8745e4323e4011a72fda38b6c2893
runtime_pid=9048
lease_id=0a2f2050dce36f85f293287a0dd79476
shadow_candidate_id=market_regime.origin_feature.shadow.ma_3_10.interquartile.v1
parameter_set_id=market_regime.origin_feature.shadow.ma_3_10.interquartile.v1
source_root=D:\btc_ts_hot
destination_root=D:\btc_ts_hot
cadence_sec=60
planned_start_utc=2026-07-17T11:19:00Z
planned_end_utc=2026-07-18T11:19:00Z
planned_end_jst=2026-07-18T20:19:00+09:00
final_outcome_maturity_utc=2026-07-19T11:19:00Z
final_outcome_maturity_jst=2026-07-19T20:19:00+09:00
```

## Startup receipt

```text
checked_at_utc=2026-07-17T11:20:43Z
status=RUNNING
active=true
iteration_count=1
written_origin_count=0
readiness_skip_count=1
last_error=
decision=CONTINUE
next_check_at_utc=2026-07-17T11:34:00Z
scheduler_enabled=false
latest_pointer_exists=false
human_authorized=true
collection_24h_started=true
```

## Latest known live state at handoff preparation

```text
status=RUNNING
active=true
iteration_count=56
error_count=0
written_origin_count=0
readiness_skip_count=56
last_skip_reason=source_not_current:300,900,1800,3600,21600,43200,86400
last_error=
stop_requested=false
```

Readiness skips are observable evidence and are not by themselves an integrity failure. Continue while lease ownership, frozen identity, safety boundaries, source health, and error-free loop state remain valid.

## Mandatory checkpoints

```text
startup=2026-07-17T11:20:43Z completed CONTINUE
approximately_15_minutes=2026-07-17T11:34:00Z due/passed; durable checkpoint receipt still required
approximately_1_hour=2026-07-17T12:19:00Z
approximately_6_hours=2026-07-17T17:19:00Z
approximately_12_hours=2026-07-17T23:19:00Z
planned_end=2026-07-18T11:19:00Z
final_outcome_maturity=2026-07-19T11:19:00Z
evidence_review=after maturity and integrity checks
```

## Runtime ownership

```text
foreground_terminal_must_remain_open=true
runtime_process_must_not_be_restarted=true
Ctrl_C_requires_explicit_stop_decision=true
scheduler=false
detached_process=false
duplicate_producer_forbidden=true
```

The dedicated terminal running PID 9048 is the owner. Do not close it, send Ctrl+C, start another producer, recover its lease, or reuse its control directory while the observation remains valid and RUNNING.

## Held work

The following must not be applied to the running process:

```text
MarketRegime prediction logic
candidate selection or parameter set
feature semantics
UNKNOWN or fallback rules
readiness or source-selection semantics
timestamp or dedupe semantics
target or outcome semantics
cadence
runtime-horizon persistence identity or schema
Collector or producer restart/configuration changes
```

Allowed parallel work:

```text
read-only checkpoint monitoring
receipt and manifest verification
offline analysis
repo-tmp tests and fixtures
documentation
timestamp trace tooling
MR-F10 family-neutral context schema/interface design not applied to runtime
implementation changes isolated from the running process and explicitly marked offline-only
```

## Roadmap continuation

MR-F9 is not complete merely because collection is running. Collection completion, longest-horizon maturity, evidence review, and hold-release decisions remain separate gates.

Parallel offline continuation may prepare MR-F10's stable family-neutral context contract, but must not apply changes to the running MarketRegime process. TrendBias remains blocked until MR-F9, MR-F10, family-wide integration/hardening/closeout, and `MARKET_REGIME_READY_FOR_NEXT_FAMILY` are accepted.

## GPT/thread handoff rule

Every successor GPT must first read:

```text
tmp/gpt_room/ENVIRONMENT_GUARDS.md
tmp/gpt_room/START.md
tmp/gpt_room/OBSERVATION_CONTROL.md
tmp/gpt_room/CURRENT.json
this document
long-running observation policy
```

Then inspect D-hot state, progress, lease, and latest manifests read-only before making a decision. Conversation history alone is not canonical.
