# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q20B_MARKET_OVERVIEW_CONSUMER_ROW_SELECTION_CONTRACT_2026-06-26.md
# desc: PS-Q20B market.overview consumer preferred-row / diagnostic-row separation contract.
# PS-Q20B Market overview consumer row selection contract

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: e3ced1df

## Purpose

PS-Q20B turns the PS-Q20A evidence into a reusable market-state contract: distinguish consumer-preferred `market.overview` rows from diagnostic transition rows.

```text
ps_q20b_market_overview_consumer_row_selection_contract=true
consumer_preferred_row_contract=true
diagnostic_transition_row_contract=true
responsibility_market_engine_market_state=true
collector_runtime_behavior_changed=false
ps_q19r_scoring_policy_changed=false
```

## Why this exists

D hot evidence around `2026-06-25T12:04:14Z` showed same-second `market.overview` rows containing both:

```text
quarantined / reanchor_required / crossed-book / negative-spread rows
trusted / allow_structural_use / positive-spread rows
```

PS-Q19R remains strict nearest + fail-closed. PS-Q20B does not change that. It creates a contract that future WarRoom, producer, replay, or later review code can use without confusing diagnostic rows with consumer-preferred rows.

## Responsibility boundary

```text
market_engine.market_state.consumer_row_selection owns row role classification
collector runtime output remains unchanged
writer remains unchanged
PS-Q19W diagnosis remains unchanged
PS-Q20A compact diagnosis remains unchanged
PS-Q19R actual-point scoring remains unchanged
```

## Contract behavior

```text
trusted + allow_structural_use + healthy + non-crossed + non-negative-spread:
  row_role=consumer_preferred
  usable_for_prediction=true
  usable_for_strategy_candidate=true
  usable_for_execution_candidate=false

quarantined / reanchor_required / broken / crossed / negative-spread / missing top book:
  row_role=diagnostic_transition
  usable_for_prediction=false
  diagnostic_visible=true
```

If no consumer-preferred row exists, the selector fail-closes:

```text
selection_state=fail_closed
selected_row_index=null
blocked_reasons=consumer_preferred_market_overview_row_missing
```

## Non-goals

```text
no_collector_runtime_change
no_writer_change
no_jsonl_schema_migration
no_ps_q19r_scoring_policy_change
no_auto_retry
no_producer_schedule_enablement
no_warroom_control_enablement
no_autotrade_trigger
no_broker_private_api
```

## Safety boundary

```text
read_only_contract=true
runtime_artifact_write_performed_by_contract=false
collector_state_write_performed_by_contract=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Next likely slice

```text
PS-Q20C_MARKET_OVERVIEW_SELECTION_REPLAY_DIAGNOSTIC
```

Use the contract on bounded hot-data slices to summarize how often diagnostic rows coexist with consumer-preferred rows and whether the preferred-row contract would reduce false quality blocks without changing PS-Q19R scoring yet.
