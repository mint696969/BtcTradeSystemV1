# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19V_OBSERVATION_OUTCOME_POLICY_2026-06-25.md
# desc: PS-Q19V policy note for bounded observation outcome classification and market-overview quality blocks.
# PS-Q19V Observation outcome policy

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 8328cdbf

## Purpose

PS-Q19V adds a read-only classifier for bounded observation outcomes. It distinguishes full completion from partial success with a market-overview quality block.

```text
ps_q19v_observation_outcome_policy=true
classifies_bounded_observation_outcome=true
partial_success_with_market_quality_block_supported=true
read_only_classifier=true
runtime_artifact_write_performed_by_classifier=false
status_artifact_write_performed_by_classifier=false
prediction_artifact_write_performed_by_classifier=false
view_artifact_write_performed_by_classifier=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Why this exists

PS-Q19U showed that a bounded observation can produce useful prediction artifacts and still stop later when a market overview point becomes unsafe:

```text
producer_successful_cycle_count=7
blocked_cycle_index=7
market_overview_trust_state_not_trusted
market_overview_interpretation_bucket_not_allow_structural_use
```

PS-Q19R also showed the same safety posture at review time: a 300s horizon was visible but not scored because the market point was quarantined, reanchor-required, crossed, and negative spread.

## Outcome classes

```text
complete_success
partial_success_with_market_quality_block
partial_success_with_non_quality_block
blocked_without_success
review_only_observation
unclassified
```

The important new class is:

```text
partial_success_with_market_quality_block
```

This means successful cycles can be reviewed, but the blocked cycle must be recorded separately and must not be silently treated as a normal completed observation.

## Policy

```text
complete_success_requires_all_requested_cycles_written=true
partial_success_can_be_accepted_for_review=true when successful_cycles>0 and review_usable=true
quality_rejected_horizons_are_not_scored=true
quality_block_should_not_trigger_auto_retry_or_trade=true
operator_should_record_block_class_separately=true
```

## Operator usage

Save producer/review/summary JSON packets, then classify:

```powershell
python .\tools\classify_prediction_observation_outcome_ps_q19v.py `
  --producer-path .\tmp\work\ps_q19v_observation_outcome_policy\producer_ps_q19u.json `
  --review-path .\tmp\work\ps_q19u_multi_review_input\review_window_ps_q19u_latest_clean.json `
  --summary-path .\tmp\work\ps_q19v_observation_outcome_policy\summary_ps_q19u_two_windows.json
```

## Safety boundary

```text
read_only_classifier=true
runtime_artifact_write_performed_by_classifier=false
status_artifact_write_performed_by_classifier=false
prediction_artifact_write_performed_by_classifier=false
view_artifact_write_performed_by_classifier=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
ui_triggered_runner_execution=false
approval_or_authorization_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```
