# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_19L_PRODUCER_CORE_CHECKPOINT_2026-07-17.md
# desc: MR-F9.19L checkpoint for the committed bounded restart-safe 24h runtime-horizon collection producer core before operator CLI and sustained D-hot start.

# Prediction System MarketRegime MR-F9.19L Producer Core Checkpoint

Updated: 2026-07-17 JST
Branch: `docs/phase2-handoff-sync`
Implementation HEAD: `9b11e2ec`
Working tree at checkpoint: clean
Status: producer core committed; operator CLI and 24h D-hot collection start remain open

## 1. Accepted checkpoint

```text
current_phase=MR-F9
current_slice=MR-F9.19L
producer_core_complete=true
operator_cli_complete=false
production_start_command_complete=false
collection_24h_started=false
collection_24h_completed=false
collector_restart_required=false
next_slice=MR-F9.19M_OPERATOR_COLLECTION_CLI_PREPARE_STATUS_STOP
next_gate=MR_F9_BOUNDED_24H_COLLECTION_PRODUCER_START
```

Commit `9b11e2ec` adds the bounded restart-safe producer core without starting a sustained writer.

## 2. Committed production modules

```text
runtime_horizon_collection_contract.py
runtime_horizon_collection_state.py
runtime_horizon_collection_tick.py
runtime_horizon_collection_loop.py
runtime_horizon_collection_adapter.py
runtime_horizon_collection_recovery.py
runtime_horizon_collection_lease.py
runtime_horizon_collection_authorization.py
runtime_horizon_collection_cadence.py
```

Accepted behavior:

```text
bounded_duration_sec=86400
cadence_sec=60
expected_tick_count=1440
maximum_loop_iterations=1442
foreground_process_only=true
single_process_lease=true
lease_heartbeat=true
stale_lease_auto_recovery=false
external_stop_request=true
restart_state_reload=true
manifest_recovery_read_only=true
closed_source_timestamp_dedupe=true
prediction_origin_dedupe_is_not_sufficient=true
same_closed_source_multiple_runs=conflict_fail_closed
manifest_written_last=true
latest_pointer_created=false
scheduler_enabled=false
detached_process_started=false
websocket_opened=false
ui_inference_allowed=false
ui_confidence_recalculation_allowed=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_submission_allowed=false
```

## 3. Critical restart-safe identity decision

`prediction_origin` is execution time and is not a stable closed-candle identity. Historical-origin rebuild is invalid because the current feature bundle depends on the current closed-source window.

The accepted restart strategy is:

```text
fresh prediction execution at each tick
  -> derive one latest closed-source timestamp from future horizons
  -> dedupe by closed-source timestamp
  -> persist exact 8 horizon payloads plus manifest
  -> after state loss scan destination manifests/payloads read-only
  -> merge recovered origin/run/closed-source identities into state
  -> never regenerate an old prediction_origin
```

Do not replace this with historical-origin regeneration or prediction-origin-only deduplication.

## 4. Qualification evidence

Focused collection-core guard:

```text
69 passed
```

Close guard before commit:

```text
market_regime_tests=722_passed
broader_prediction_market_regime_tests=964_passed_47_deselected
compileall=passed
git_diff_cached_check=clean
commit_hook=passed
working_tree=clean
```

Repository-tmp restart qualification:

```text
source_root=D:\btc_ts_hot
source_read_only=true
destination_root=C:\BtcTradeSystem\tmp\work\mr_f9_19l\qualification_output
first_event=WRITE_OK
first_written_count=9
manifest_recovery_state_merge=1
restart_event=DUPLICATE_ORIGIN_SKIP
restart_writer_invoked=false
closed_source_timestamp=2026-07-17T01:57:00Z
destination_json_file_count=9
writes_dhot=false
latest_pointer_exists=false
scheduler_enabled=false
websocket_opened=false
order_submission_allowed=false
qualification_passed=true
```

Qualification report:

```text
tmp/work/mr_f9_19l/MR_F9_19L_REPO_TMP_RESTART_QUALIFICATION.json
tmp/work/mr_f9_19l/MR_F9_19L_REPO_TMP_RESTART_QUALIFICATION.md
```

These are scratch evidence, not production D-hot collection artifacts.

## 5. Prior one-shot D-hot fact

One explicitly authorized one-shot write already occurred before this checkpoint:

```text
run_id=run-20260716T190338Z-f5de60ce29c2
prediction_origin=2026-07-16T19:03:38Z
written_count=9
duplicate_count=0
verified_horizon_count=8
manifest_written_last_verified=true
latest_pointer_exists=false
```

This one-shot write is not a 24-hour collection start.

## 6. Not implemented at this checkpoint

```text
operator_prepare_command=false
operator_status_command=false
operator_stop_command=false
operator_start_command=false
startup_recovery_orchestration=false
production_D_hot_continuous_writer_connection=false
production_path_repo_tmp_full_qualification=false
D_hot_pre_start_gate=false
collection_24h_started=false
UI_WS_timestamp_trace=false
outcome_maturation_analysis=false
```

A scratch runner exists but was not executed:

```text
tmp/work/mr_f9_19l/apply_mr_f9_19l_collection_cli_prepare_status_stop.py
```

Its presence must not be interpreted as repository implementation or acceptance.

## 7. Collector/runtime relationship

The current Collector does not import or invoke the new collection modules. Collector restart is not required for this checkpoint or the next CLI work.

```text
collector_should_remain_running=true
collector_restart_required=false
collection_producer_is_separate_foreground_process=true
```

## 8. Re-entry condition

The next thread must begin from clean HEAD `9b11e2ec`, read the new handoff, and implement only the read-only operator CLI slice first. Sustained D-hot start remains human-gated and must not be implied by CLI preparation work.
