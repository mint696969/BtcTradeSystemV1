# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q20D_PREFERRED_ROW_CONSUMER_INTEGRATION_DESIGN_2026-06-26.md
# desc: PS-Q20D preferred-row consumer integration design after PS-Q20C replay evidence.
# PS-Q20D Preferred-row consumer integration design

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: 0fe5aba1

## Purpose

PS-Q20D defines which future consumer lanes may use the PS-Q20B `consumer_preferred` row contract, without changing any runtime behavior yet.

```text
ps_q20d_preferred_row_consumer_integration_design=true
integration_design_only=true
uses_ps_q20b_consumer_row_selection_contract=true
uses_ps_q20c_hot_data_evidence=true
warroom_runtime_behavior_changed=false
prediction_producer_behavior_changed=false
collector_runtime_behavior_changed=false
market_state_writer_changed=false
ps_q19r_scoring_policy_changed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Evidence from PS-Q20C

```text
second_count=181
parsed_window_record_count=1351
consumer_preferred_row_count=1244
diagnostic_transition_row_count=107
preferred_second_count=172
fail_closed_second_count=9
mixed_preferred_and_diagnostic_second_count=8
false_quality_block_candidate_second_count=8
preferred_contract_likely_useful=true
```

This supports read-only consumer integration design, but it does not justify enabling execution, AutoTrade, broker calls, or PS-Q19R scoring changes.

## Lane policy

```text
warroom_read:
  may_use_consumer_preferred_row=true when available
  may_display_diagnostic_rows=true
  may_score_diagnostic_rows=false
  may_trigger_execution=false

prediction_producer_input:
  may_use_consumer_preferred_row=true when available
  may_display_diagnostic_rows=true
  may_score_diagnostic_rows=false
  may_trigger_execution=false

replay_analysis:
  may_use_consumer_preferred_row=true when available
  may_display_diagnostic_rows=true
  may_score_diagnostic_rows=false
  may_trigger_execution=false

strategy_candidate:
  may_use_consumer_preferred_row=true when available
  may_display_diagnostic_rows=true
  may_score_diagnostic_rows=false
  may_trigger_execution=false

execution_candidate:
  blocked_by_policy=true
  human_policy_gate_required_before_execution_use=true

autotrade_trigger:
  blocked_by_policy=true
  human_policy_gate_required_before_execution_use=true
```

## Fail-closed behavior

If no consumer-preferred row exists:

```text
consumer_preferred_market_overview_row_missing
safe_read_lanes_blocked=true
execution_lanes_still_blocked=true
continue_collector_reanchor_observation=true
```

## Non-goals

```text
no_warroom_runtime_change
no_prediction_producer_behavior_change
no_collector_runtime_change
no_market_state_writer_change
no_jsonl_schema_migration
no_ps_q19r_scoring_policy_change
no_scheduler_enablement
no_autotrade_trigger
no_broker_private_api
```

## Next likely slice

```text
PS-Q20E_WARROOM_AND_PRODUCER_READ_ONLY_PREFERRED_ROW_ADAPTER
```

Only the read-only WarRoom / producer input path should be considered next. Execution, AutoTrade trigger, and PS-Q19R scoring changes remain closed.
