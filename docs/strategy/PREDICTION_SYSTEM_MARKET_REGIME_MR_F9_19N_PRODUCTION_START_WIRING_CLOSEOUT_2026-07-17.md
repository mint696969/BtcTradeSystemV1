# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_19N_PRODUCTION_START_WIRING_CLOSEOUT_2026-07-17.md
# desc: Closeout for exact-human-authorized foreground production-start wiring. D-hot collection remains unstarted.

# MarketRegime MR-F9.19N Production Start Wiring Closeout

Updated: 2026-07-17 JST
Status: accepted
Checkpoint: MR-F9.19N_PRODUCTION_START_WIRING_ACCEPTED

<!-- MR_F9_19N_PRODUCTION_START_WIRING_CLOSEOUT_2026_07_17 -->

## Scope

```text
production_start_wiring_implemented=true
production_D_hot_start_executed=false
collection_24h_started=false
repository_tmp_qualification_complete=false
D_hot_read_only_prestart_gate_complete=false
```

## Accepted implementation

```text
runtime_horizon_collection_start.py
runtime_horizon_collection_loop.py
tools/runtime_horizon_collection.py
focused start/loop/tool tests
```

The start path now requires:

```text
valid collection plan
valid authorization package
exact human authorization text match
authorization text SHA-256 match
authorization TTL validity
source/destination/control-root binding
foreground-only contract
lease_required=true
manifest_recovery_required=true
planned-start anchored cadence
fresh adapter execution per tick
```

## Startup ordering

```text
validate plan/package/root/TTL/exact text
acquire single-process lease
read persisted state
perform read-only manifest recovery
persist recovered PLANNED/PAUSED/RUNNING state
enter foreground loop with the same pre-acquired lease
wait until planned_start when state is PLANNED
transition to RUNNING inside the loop
execute first fresh adapter tick
```

Recovery behavior:

```text
fresh start with no recovered runs keeps PLANNED before loop
restart with recovered runs may return PLANNED/PAUSED to RUNNING only after planned_start
recovered runs before planned_start fail closed
terminal persisted state rejects start
pre-loop failure releases the newly acquired lease
runtime abnormal-stop lease behavior remains governed by explicit stale-lease recovery
```

## Safety boundary

```text
scheduler_enabled=false
detached_process_started=false
latest_pointer_created=false
websocket_opened=false
UI_inference_allowed=false
UI_confidence_recalculation_allowed=false
broker_private_api_allowed=false
AutoTrade_trigger_allowed=false
order_submission_allowed=false
auto_promotion_allowed=false
live_parameter_apply_allowed=false
```

## Qualification evidence

```text
focused_start_path_qualification=46 passed
MarketRegime_full_regression=733 passed
py_compile=passed
git_diff_check=passed
D_hot_write_during_qualification=false
```

## Remaining mandatory gates

MR-F9.19N does not authorize or execute D-hot collection.

```text
next_slice=MR-F9.19O_PRODUCTION_PATH_REPO_TMP_QUALIFICATION
then=MR-F9.19P_D_HOT_READ_ONLY_PRESTART_GATE
then=explicit_human_authorization
```

MR-F9.19O must exercise the production CLI/start path against repository-tmp fixtures, including first write, duplicate closed-source skip, stop/resume, state-loss recovery, duplicate lease rejection, explicit stale-lease recovery, conflict fail-closed, and planned-end completion.

## Acceptance

```text
MR_F9_19N_complete=true
production_start_wiring_accepted=true
collection_24h_started=false
MR_F9_19O_not_started=true
```
