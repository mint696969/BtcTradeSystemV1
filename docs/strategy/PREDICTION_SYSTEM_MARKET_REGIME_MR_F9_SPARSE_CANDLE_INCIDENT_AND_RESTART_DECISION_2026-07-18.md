# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_SPARSE_CANDLE_INCIDENT_AND_RESTART_DECISION_2026-07-18.md
# desc: MR-F9 incident receipt for sparse WarRoom candles, fail-closed collection termination, qualified readiness-skip fix, and restart decision.

# MarketRegime MR-F9 Sparse-Candle Incident and Restart Decision

Updated: 2026-07-18 JST
Status: qualified_fix_committed
Decision: PROCEED_TO_REPLACEMENT_COLLECTION_PRESTART_GATE

<!-- MR_F9_SPARSE_CANDLE_INCIDENT_AND_RESTART_DECISION_2026_07_18 -->

## Incident facts

```text
collection_id=mr-f9-24h-fad90fe3ed0cf9805322
status=FAILED_CONTRACT
active=false
updated_at=2026-07-17T22:22:00Z
iteration_count=663
written_origin_count=253
duplicate_origin_skip_count=340
readiness_skip_count=70
error_count=1
last_error=ValueError:origin_feature_runtime_bundle_candle_row_count_not_sixty
lease_present=false
```

Tick accounting remained exact:

```text
253 + 340 + 70 = 663
```

## Root cause

The WarRoom candle source intentionally omits empty one-minute periods and does not synthesize null candles:

```text
gap_policy=absent_candles_no_synthetic_null
missing_periods_error=false
```

The MR-F9 future-origin feature contract requires one contiguous 60-candle window. At the failing tick, no such window was available in the bounded source tail. The source behavior was valid, but the collection adapter incorrectly allowed this known temporary input unavailability to become a terminal contract exception.

## Qualified structural fix

```text
known exact error:
  origin_feature_runtime_bundle_candle_row_count_not_sixty
    -> collection_preflight_unavailable_reason
    -> READINESS_SKIP
    -> loop remains non-terminal

all other exceptions:
    -> propagate unchanged
    -> existing FAILED_CONTRACT behavior remains
```

Safety remains unchanged:

```text
synthetic_candle_created=false
candle_interpolation_allowed=false
writer_invoked_on_skip=false
writes_dhot_on_skip=false
scheduler_enabled=false
detached_process_started=false
websocket_opened=false
ui_inference_allowed=false
order_submission_allowed=false
```

## Qualification evidence

```text
focused_test_count=31
result=PASS
git_diff_check=PASS
gpt_room_persistence_guard=PASS
```

The qualification proves that the known sparse-candle condition becomes `READINESS_SKIP`, keeps `error_count=0`, and allows the foreground loop to continue until a normal operator stop. Unknown `ValueError` instances still propagate.

## Restart decision

The failed collection state is terminal. Repository contract rejects authorized start when persisted state is `FAILED_CONTRACT`.

```text
same_collection_id_restart_allowed=false
failed_state_manual_rewrite_allowed=false
lease_recovery_needed=false
replacement_collection_required=true
old_253_origins_preserved=true
old_collection_used_as_incident_evidence=true
```

Correct restart procedure:

```text
1. commit and push the qualified fix
2. run a fresh read-only D-hot pre-start gate
3. prepare a new bounded collection plan and collection_id
4. create a new short-lived authorization package
5. obtain exact human authorization
6. start one foreground producer under the fixed commit
7. preserve the failed collection separately
```

## Parallel work decision

```text
MR_F9_P2_offline_qualification_allowed=true
MR_F10_entry_after_parallelizable_F9_tasks_allowed=true
replacement_collection_monitoring_remains_MR_F9_open_gate=true
```

## Durable fix commit

<!-- MR_F9_SPARSE_CANDLE_INCIDENT_FIX_COMMIT_RECORDED_2026_07_18 -->

```text
incident_fix_commit=fead05b6c24e458d54a5758f908b93d413de99f6
incident_fix_commit_short=fead05b6
remote_push_verified=true
next_gate=MR_F9_REPLACEMENT_COLLECTION_PRESTART_GATE
```
