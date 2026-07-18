# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_REPLACEMENT_24H_COLLECTION_START_RECEIPT_2026-07-18.md
# desc: Durable start receipt and observation schedule for the replacement MR-F9 bounded 24-hour D-hot collection.

# MarketRegime MR-F9 Replacement 24h Collection Start Receipt

Updated: 2026-07-18 JST
Status: RUNNING
Decision: CONTINUE_COLLECTION_AND_PROCEED_WITH_PARALLEL_MR_F9_P2

<!-- MR_F9_REPLACEMENT_24H_COLLECTION_START_RECEIPT_2026_07_18 -->

## Active collection identity

```text
collection_id=mr-f9-24h-5be7ba757eac727bab10
plan_sha256=beb94ca14825c848d0bc97cd6953c55b99a080c53fa1bdf4eb6f44238cfed617
repository_commit_under_test=a784526cd913f60c2afbd655a535d7ac52f9983d
shadow_candidate_id=market_regime.origin_feature.shadow.ma_3_10.interquartile.v1
runtime_pid=20176
lease_id=4283ab4f0e27b0337072c623bcf2b40f
foreground_only=true
human_authorized=true
status=RUNNING
active=true
```

## Canonical schedule

```text
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
final_24h_outcome_maturity_not_before_utc=2026-07-20T04:14:00Z
final_24h_outcome_maturity_not_before_jst=2026-07-20T13:14:00+09:00
analysis_window_opens_after=2026-07-20T04:14:00Z
```

## First observed runtime state

```text
iteration_count=5
written_origin_count=0
readiness_skip_count=5
error_count=0
last_error=
last_skip_reason=future_origin_contiguous_sixty_candles_unavailable
sparse_candle_condition_terminal=false
sparse_candle_condition_handled_as=READINESS_SKIP
```

## Safety boundary

```text
terminal_A_must_remain_open=true
ctrl_c_forbidden=true
second_producer_forbidden=true
lease_recovery_forbidden_while_live=true
scheduler_enabled=false
detached_process_started=false
websocket_opened=false
ui_inference_allowed=false
order_submission_allowed=false
```

## Parallel MR-F9 plan before MR-F10

```text
P1_runtime_horizon_read_model=COMPLETE
P2_next=MR_F9_TRUST_FALLBACK_UNKNOWN_PREMATURITY_QUALIFICATION
P3_after_P2=MR_F9_REVIEW_PROPOSAL_PREMATURITY_QUALIFICATION
P4_after_P3=MR_F9_PRE_F10_ROOM_AND_GATE_SYNC
MR_F10_entry_after_parallelizable_MR_F9_tasks=true
replacement_collection_monitoring_remains_active=true
replacement_collection_completion_remains_open_gate=true
final_outcome_maturity_remains_open_gate=true
```

## Old failed collection preservation

```text
failed_collection_id=mr-f9-24h-fad90fe3ed0cf9805322
failed_collection_status=FAILED_CONTRACT
failed_collection_written_origin_count=253
failed_collection_preserved_as_incident_evidence=true
failed_collection_restart_allowed=false
```
