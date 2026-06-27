# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q21ZB_CROSS_VENUE_MISSING_WARN_ONLY_EXPORT_PREFLIGHT_2026-06-27.md
# desc: PS-Q21ZB makes missing cross-venue summary a prediction warning instead of a payload hard blocker so bounded manual latest export preflight can proceed without enabling collection/trading.
# PS-Q21ZB cross-venue missing warn-only export preflight

Updated: 2026-06-27 JST
Branch: docs/phase2-handoff-sync
Base clean head: 2c636f44

## Purpose

PS-Q21ZA diagnostics showed that Q21I/Q21Z did not write latest prediction because the in-memory PredictionSystemResult payload had exactly one hard blocker: `cross_venue_summary_missing_or_blocked`. The payload itself was built, scenario core was present, and output_count was 110. This slice makes the missing cross-venue summary a warning/context limitation rather than a payload-wide hard blocker.

```text
ps_q21zb_cross_venue_missing_warn_only_export_preflight=true
cross_venue_summary_missing_or_blocked_is_warning_not_payload_blocker=true
prediction_payload_build_remains_non_executing=true
latest_export_preflight_can_proceed_without_cross_venue_context=true
```

## Boundary

```text
no_D_hot_write_by_this_slice
no_status_write_by_this_slice
no_producer_runner_invocation
no_scheduler_enablement
no_trigger_addition
no_recurring_enablement
no_warroom_ui_trigger
no_AutoTrade
no_broker_private_api
would_send_to_broker=false
```

## Reasoning

Cross-venue context is useful evidence, but the current local D-hot runtime does not provide all external/cross-venue sources. Other rule families already treat missing cross-venue context as warnings and score reductions. Blocking the whole latest-prediction export on this single optional context source prevents bounded manual freshness recovery even when local FX/ticker/trade/board/OHLCV and scenario outputs are available.
