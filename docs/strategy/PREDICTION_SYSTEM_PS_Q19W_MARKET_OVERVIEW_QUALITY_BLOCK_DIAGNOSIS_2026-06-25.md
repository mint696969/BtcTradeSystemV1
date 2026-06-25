# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19W_MARKET_OVERVIEW_QUALITY_BLOCK_DIAGNOSIS_2026-06-25.md
# desc: PS-Q19W design note for read-only diagnosis of market.overview quality-block windows.
# PS-Q19W Market overview quality-block diagnosis

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 91c8448c

## Purpose

PS-Q19W adds a read-only helper to inspect the market.overview rows around a blocked prediction/review horizon.

```text
ps_q19w_market_overview_quality_block_diagnosis=true
diagnoses_market_overview_quality_window=true
same_second_mixed_quality_detection=true
read_only_diagnosis=true
runtime_artifact_write_performed_by_diagnosis=false
status_artifact_write_performed_by_diagnosis=false
prediction_artifact_write_performed_by_diagnosis=false
view_artifact_write_performed_by_diagnosis=false
collector_state_write_performed_by_diagnosis=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Why this exists

PS-Q19U produced a useful partial observation and then stopped on a market overview quality block. PS-Q19R also rejected the 300s actual point because the selected market point was quarantined / reanchor-required / negative-spread / crossed-book.

A direct D hot inspection around `2026-06-25T12:04:14Z` showed that the same second can contain both rejected and trusted market.overview rows. This helper makes that visible in a repeatable operator diagnostic packet.

## Diagnosis fields

The helper reports:

```text
trust_state_counts
interpretation_bucket_counts
semantic_observer_status_counts
spread_summary
crossed_book_count
quality_reason_counts
exact_second_mixed_quality
mixed_quality_seconds
rejected_records_sample
transition_records_sample
```

## Policy posture

```text
quality_rejected_records_should_not_be_scored=true
fail_closed_recommended=true when rejected rows are present
same_second_quality_ok_candidate_present=true when trusted and rejected records share one collector_ts
collector_side_reanchor_or_crossed_book_diagnosis_needed=true when rejected rows are present
do_not_auto_retry_or_trade_from_diagnosis=true
```

This does not change PS-Q19R scoring. It only explains why a row was rejected and whether a same-second trusted candidate existed.

## Operator usage

Exact second inspection:

```powershell
python .\tools\diagnose_market_overview_quality_block_ps_q19w.py `
  --root D:\btc_ts_hot `
  --target-ts 2026-06-25T12:04:14Z `
  --window-sec 90
```

Full window inspection:

```powershell
python .\tools\diagnose_market_overview_quality_block_ps_q19w.py `
  --root D:\btc_ts_hot `
  --target-ts 2026-06-25T12:04:14Z `
  --window-sec 90 `
  --all-window-records
```

## Safety boundary

```text
read_only_diagnosis=true
runtime_artifact_write_performed_by_diagnosis=false
status_artifact_write_performed_by_diagnosis=false
prediction_artifact_write_performed_by_diagnosis=false
view_artifact_write_performed_by_diagnosis=false
collector_state_write_performed_by_diagnosis=false
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
