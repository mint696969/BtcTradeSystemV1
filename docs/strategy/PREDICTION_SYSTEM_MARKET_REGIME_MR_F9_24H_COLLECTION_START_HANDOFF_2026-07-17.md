# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_24H_COLLECTION_START_HANDOFF_2026-07-17.md
# desc: Canonical next-thread handoff from committed MR-F9.19L producer core to operator CLI, production-path qualification, and explicit 24h D-hot collection start.

# Prediction System MarketRegime MR-F9 24h Collection Start Handoff

Updated: 2026-07-17 JST
Branch: `docs/phase2-handoff-sync`
Reference HEAD: `9b11e2ec`
Working tree expected at handoff: clean
Current phase: `MR-F9`
Completed slice: `MR-F9.19L_BOUNDED_RESTART_SAFE_COLLECTION_PRODUCER_CORE`
Next slice: `MR-F9.19M_OPERATOR_COLLECTION_CLI_PREPARE_STATUS_STOP`
Next gate: `MR_F9_BOUNDED_24H_COLLECTION_PRODUCER_START`

## 1. Exact handoff state

```text
producer_core_complete=true
operator_cli_complete=false
production_start_command_complete=false
repo_tmp_restart_qualification_passed=true
production_path_full_qualification_passed=false
D_hot_one_shot_completed=true
collection_24h_started=false
collection_24h_completed=false
collector_running_expected=true
collector_restart_required=false
mr_f9_complete=false
market_regime_ready_for_next_family=false
trend_bias_blocked=true
```

Do not claim the 24-hour collection has started until a foreground producer process has acquired its lease, persisted `RUNNING` state, and entered its first production tick after explicit human authorization.

## 2. Repository truth to trust

```text
9b11e2ec feat(market-regime): add bounded restart-safe horizon collection core
071f2faf feat(market-regime): add authorized D-hot one-shot write CLI
```

Checkpoint:

```text
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_19L_PRODUCER_CORE_CHECKPOINT_2026-07-17.md
```

Open-work sources:

```text
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_REMAINING_WORK_REGISTER_2026-07-14.md
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_FAMILY_ROADMAP_2026-07-11.md
```

## 3. First reads in the next thread

```text
tmp/gpt_room/ENVIRONMENT_GUARDS.md
tmp/gpt_room/09_FOCUS.json
tmp/gpt_room/08_STATUS.md
tmp/gpt_room/11_STATE.json
tmp/gpt_room/DECISIONS.md
this handoff document
MR-F9.19L producer-core checkpoint
remaining-work register
family roadmap
runtime_horizon_collection_contract.py
runtime_horizon_collection_state.py
runtime_horizon_collection_tick.py
runtime_horizon_collection_recovery.py
runtime_horizon_collection_lease.py
runtime_horizon_collection_cadence.py
runtime_horizon_collection_loop.py
runtime_horizon_collection_adapter.py
runtime_horizon_collection_authorization.py
```

## 4. Non-negotiable design decisions

```text
prediction_origin_is_execution_time=true
prediction_origin_is_not_closed_candle_identity=true
historical_prediction_origin_rebuild_forbidden=true
dedupe_key=latest_closed_source_timestamp_from_future_horizons
state_loss_recovery=read_only_manifest_and_payload_scan
same_closed_source_multiple_runs=conflict_fail_closed
stale_lease_auto_recovery=false
single_process_lease_required_for_production=true
anchored_cadence_required_for_production=true
foreground_process_required=true
latest_pointer_created=false
scheduler_enabled=false
detached_process_started=false
collector_restart_required=false
websocket_opened=false
ui_inference_allowed=false
ui_confidence_recalculation_allowed=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_submission_allowed=false
human_authorization_required_before_sustained_D_hot_write=true
```

## 5. Fixed next-slice order

Do not skip or reorder these boundaries without recording a new decision.

```text
MR-F9.19M
  read-only operator CLI:
    prepare
    status
    stop
    start remains fail-closed
  focused guards
  commit

MR-F9.19N
  production start wiring:
    exact authorization text verification
    authorization TTL verification
    plan/package/root binding
    startup read-only manifest recovery
    recovered state merge
    lease_required=true
    cadence_anchored=true
    foreground process only
    fresh per-tick preflight/readiness/writer adapter
  focused guards
  commit

MR-F9.19O
  production-path repository-tmp qualification:
    prepare
    start
    first write
    same closed-source skip
    stop
    resume
    state-loss recovery
    duplicate lease rejection
    explicit stale-lease recovery
    conflict fail-closed
    planned-end completion
  full MarketRegime guards
  commit

MR-F9.19P
  D-hot read-only pre-start gate:
    Collector/source freshness
    destination conflict scan
    existing collection state
    existing lease
    exact planned start/end
    authorization context
    disk/path ownership
    clean working tree
    no latest/scheduler/UI/broker/order surfaces
  no D-hot write

HUMAN GATE
  display exact authorization text
  obtain explicit authorization
  start separate foreground PowerShell process
  verify lease acquired
  verify state RUNNING
  verify first tick receipt or readiness skip
  only then set collection_24h_started=true
```

## 6. Scratch runner warning

The previous thread created but did not execute:

```text
tmp/work/mr_f9_19l/apply_mr_f9_19l_collection_cli_prepare_status_stop.py
```

It is not committed implementation. The next GPT must read current repository files first, review the runner against this handoff, and either use it through the normal patch workflow or replace it with a minimal corrected runner. Do not assume it is accepted merely because it exists.

## 7. Production start requirements

The production `start` path must enforce all of the following:

```text
source_root=D:\btc_ts_hot
destination_root=D:\btc_ts_hot
control_root_bound_explicitly=true
collection_plan_valid=true
collection_authorization_package_valid=true
exact_human_authorization_text_match=true
authorization_not_expired=true
startup_recovery_completed_before_loop=true
recovered_state_persisted_before_loop=true
lease_required=true
cadence_anchored=true
foreground_process=true
fresh_preflight_per_tick=true
readiness_required_per_tick=true
manifest_last_required=true
closed_source_dedupe_required=true
conflict_fail_closed=true
external_stop_observable=true
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

## 8. Collector guidance

Collector and completed runtime components are expected to stay running while this work continues.

```text
collector_restart_required=false
collector_should_remain_running=true
```

Re-evaluate restart need only if a future slice changes Collector code, Collector configuration, or its entrypoint. The current collection producer is a separate foreground process reading Collector outputs from D-hot.

## 9. After the 24h collection starts

Immediately synchronize:

```text
collection ID
planned start/end
lease ID and PID
state path
progress path
first tick event
first written or duplicate/readiness-skip counts
collection_24h_started=true
latest_pointer_exists=false
scheduler_enabled=false
```

Then continue in parallel while collection runs:

```text
UI/WS producer -> artifact -> selected read model -> packet -> card timestamp trace
multi-origin cadence/missing/conflict monitoring
24h outcome maturation preparation
```

After maturity:

```text
execution trust / fallback / UNKNOWN diagnostics
calibration / accuracy / churn / transition analysis
proposal / human review evidence
integration hardening
MR-F9 closeout
```

## 10. Exact startup prompt for the next thread

```text
BtcTradeSystemのMarketRegime MR-F9を続けてください。
project_bootstrapから開始し、branch docs/phase2-handoff-sync、HEAD 9b11e2ec、working tree cleanを確認してください。
最初にtmp/gpt_room/09_FOCUS.json、08_STATUS.md、11_STATE.json、DECISIONS.md、
PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_24H_COLLECTION_START_HANDOFF_2026-07-17.md、
MR-F9.19L producer-core checkpoint、remaining-work register、family roadmapを読んでください。
現在はMR-F9.19L producer coreだけが完成しており、24時間collectionは未開始です。
次はMR-F9.19M read-only operator CLIのprepare/status/stopだけを進め、startはfail-closedのままにしてください。
過去prediction_originの再生成、prediction-origin-only dedupe、stale lease自動回収、scheduler、detached process、latest pointer、
Collector再起動、UI inference、confidence再計算、broker、AutoTrade、order path、明示承認前のD-hot sustained writeは禁止です。
各sliceをfocused guardsとclean commitで閉じ、D-hot開始直前にread-only gateとexact human authorizationを要求してください。
```

## 11. Clean transfer condition

This handoff is valid only when:

```text
handoff_docs_committed=true
room_memory_synchronized=true
working_tree=clean
collection_24h_started=false
```
