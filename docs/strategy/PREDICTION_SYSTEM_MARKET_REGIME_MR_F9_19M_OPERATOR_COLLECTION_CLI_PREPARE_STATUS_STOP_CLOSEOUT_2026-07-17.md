# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_19M_OPERATOR_COLLECTION_CLI_PREPARE_STATUS_STOP_CLOSEOUT_2026-07-17.md
# desc: Closeout for the MR-F9.19M operator CLI slice. Prepare/status/stop are accepted; production start remains fail-closed.

# MarketRegime MR-F9.19M Operator Collection CLI Closeout

Updated: 2026-07-17 JST
Status: accepted
Checkpoint: MR-F9.19M_OPERATOR_COLLECTION_CLI_PREPARE_STATUS_STOP_ACCEPTED

<!-- MR_F9_19M_OPERATOR_COLLECTION_CLI_CLOSEOUT_2026_07_17 -->

## Scope

```text
implemented=prepare,status,stop
start_implemented=false
start_fail_closed=true
production_collection_started=false
D_hot_prediction_writer_invoked=false
scheduler_enabled=false
detached_process_started=false
broker_or_order_surface=false
```

## Accepted implementation

```text
btcts_next/src/btcts/prediction/market_regime/tools/runtime_horizon_collection.py
btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_tool.py
```

The CLI provides:

```text
prepare:
  build and validate one bounded collection plan
  build an unsigned/unapproved start authorization package
  atomically persist plan.json and start_authorization.json
  print the exact expected authorization text and expiry

status:
  validate the plan
  read state and lease
  optionally perform read-only manifest recovery inspection
  never invoke the writer

stop:
  validate the plan
  persist an atomic stop request through the collection state contract
  never invoke the writer

start:
  raise runtime_horizon_collection_start_not_implemented_fail_closed
```

## Safety boundary

```text
prepare_does_not_start_collection=true
prepare_human_authorized=false
status_read_only=true
status_optional_recovery_read_only=true
stop_only_requests_existing_state_stop=true
start_not_wired=true
writes_dhot=false
latest_pointer=false
scheduler=false
detached_process=false
UI_inference=false
confidence_recalculation=false
broker_API=false
AutoTrade=false
order_submission=false
```

## Qualification evidence

```text
focused_operator_cli_tests=4 passed
collection_core_regression_tests=69 passed
py_compile=passed
start_cli_fail_closed=passed
start_fail_closed_returncode=1
start_fail_closed_marker=runtime_horizon_collection_start_not_implemented_fail_closed
git_diff_check=passed
```

The non-zero return code is expected. Acceptance depends on the explicit fail-closed marker and absence of production start behavior.

## Observation governance

The first bounded 24-hour MarketRegime observation remains unstarted.

```text
observation_state=PLANNED
collection_24h_started=false
collection_24h_completed=false
outcome_maturity_complete=false
evidence_review_complete=false
observation_affecting_work_held=true
```

Canonical governance:

```text
docs/strategy/PREDICTION_SYSTEM_LONG_RUNNING_OBSERVATION_AND_HOLD_RELEASE_POLICY_2026-07-17.md
tmp/gpt_room/OBSERVATION_CONTROL.md
```

## Next boundary

```text
next_slice=MR-F9.19N_PRODUCTION_START_WIRING
start_authorization_remains_human_gated=true
production_D_hot_start_not_in_this_closeout=true
```

MR-F9.19N must revalidate the plan, authorization package, exact human authorization text, TTL, source/destination roots, recovery state, required lease, anchored cadence, and foreground-only execution. It must not bypass MR-F9.19O repo-tmp qualification or MR-F9.19P read-only D-hot pre-start gate.

## Acceptance

```text
operator_prepare_accepted=true
operator_status_accepted=true
operator_stop_accepted=true
operator_start_fail_closed_accepted=true
MR_F9_19M_complete=true
MR_F9_19N_not_started=true
collection_24h_started=false
```
