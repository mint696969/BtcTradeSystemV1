# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_TERMINAL_LEASE_RELEASE_HARDENING_CLOSEOUT_2026-07-17.md
# desc: Closeout for automatic lease release on terminal collection failure and loop-runner exceptions.

# MarketRegime MR-F9 Terminal Lease Release Hardening Closeout

Updated: 2026-07-17 JST
Status: accepted
Checkpoint: MR-F9_TERMINAL_LEASE_RELEASE_HARDENING_ACCEPTED

<!-- MR_F9_TERMINAL_LEASE_RELEASE_HARDENING_CLOSEOUT_2026_07_17 -->

## Trigger

The first explicitly authorized D-hot 24-hour start attempt failed closed during its first tick because an unregistered shadow candidate label was passed as `shadow_candidate_id`.

```text
collection_id=mr-f9-24h-74312d17e2efa5715b6c
status=FAILED_CONTRACT
active=false
iteration_count=0
written_origin_count=0
runtime_horizon_artifacts_written_by_attempt=0
last_error=current_l4_origin_shadow_candidate_not_found
```

The attempt left a producer lease after entering the terminal contract-failure state. The lease was subsequently recovered explicitly after exceeding the stale threshold, and the failed attempt was preserved as `INVALID` evidence.

## Structural correction

```text
foreground_loop_terminal_state_releases_lease=true
FAILED_CONTRACT_releases_lease=true
planned_completion_releases_lease=true
paused_stop_releases_lease=true
start_wrapper_loop_exception_releases_preacquired_lease=true
release_api_idempotent=true
```

The collection loop now releases an acquired lease whenever the final state is terminal, including `FAILED_CONTRACT`. The authorized start wrapper also releases its preacquired lease when the delegated loop runner raises an exception.

## Qualification

```text
focused_loop_and_start_tests=20 passed
MarketRegime_full_regression=738 passed
py_compile=passed
git_diff_check=passed
D_hot_collection_started=false
new_runtime_horizon_artifacts_written=false
```

Added or updated assertions cover:

```text
tick exception persists FAILED_CONTRACT
terminal tick exception removes producer lease
loop runner exception removes preacquired producer lease
planned completion still removes producer lease
```

## Retry boundary

The failed collection remains preserved as terminal evidence. A retry must use a new collection ID and the registered candidate proven by MR-F9.19K:

```text
shadow_candidate_id=market_regime.origin_feature.shadow.ma_3_10.interquartile.v1
```

A retry still requires a fresh plan, a fresh authorization package with TTL no greater than 300 seconds, exact human authorization text, foreground execution, and startup receipt verification.

## Safety state

```text
human_authorization_for_retry=false
retry_collection_started=false
scheduler=false
detached_process=false
latest_pointer=false
UI_inference=false
broker_private_api=false
AutoTrade=false
order_submission=false
```
