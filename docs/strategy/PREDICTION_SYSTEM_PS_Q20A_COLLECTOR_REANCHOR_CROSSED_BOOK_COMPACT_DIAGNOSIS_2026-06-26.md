# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q20A_COLLECTOR_REANCHOR_CROSSED_BOOK_COMPACT_DIAGNOSIS_2026-06-26.md
# desc: PS-Q20A compact collector/reanchor/crossed-book diagnosis contract after PS-Q19Y decision lock.
# PS-Q20A Collector reanchor / crossed-book compact diagnosis

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: b04540f4

## Purpose

PS-Q20A starts from the PS-Q19Y boundary and adds a compact, read-only collector-side diagnosis layer for same-second `market.overview` mixed quality.

```text
ps_q20a_collector_reanchor_crossed_book_compact_diagnosis=true
start_from=PS-Q19W_AND_PS_Q19X_EVIDENCE
primary_question=why_same_second_market_overview_contains_quarantined_crossed_rows_and_trusted_rows
responsibility_separated_from_ps_q19w=true
ps_q19w_existing_helper_modified=false
ps_q19r_scoring_policy_changed=false
collector_runtime_behavior_changed=false
```

## Time-axis rule

```text
canonical_timestamp_axis=UTC_ISO8601_Z
ui_display_timezone=Asia/Tokyo_JST
range_query_ui_may_accept_jst=true
range_query_internal_utc=true
jst_is_display_only=true
```

The diagnostic accepts timestamps with offsets, normalizes the analysis axis to UTC, and includes a JST display timestamp for operator readability.

## Size policy

```text
bounded_gpt_friendly_output=true
no_new_giant_files=true
summary_only_default=true
raw_full_window_records_included=false
sample_rows_default_max=20
sample_rows_hard_max=100
diagnostic_json_target_max_bytes=200000
diagnostic_json_hard_max_bytes=1000000
```

The output is counts, distributions, transition evidence, bounded samples, and repair candidates. It does not export full `market.overview` copies or unbounded JSONL extracts.

## Diagnosis responsibilities

```text
source_series_id_distribution
source_stream_session_id_distribution
trust_state_distribution
interpretation_bucket_distribution
boundary_reason_distribution
continuity_state_distribution
quality_reason_distribution
crossed_book_count
negative_spread_count
same_second_mixed_quality_detection
bad_to_good_transition_trace
repair_candidate_summary
```

## Initial repair-candidate policy

```text
separate_consumer_preferred_from_diagnostic_rows=true when same-second trusted and rejected rows coexist
quarantine_crossed_book_as_transition_diagnostic=true when crossed or negative-spread rows exist
add_row_quality_rank_and_recovery_trace=true when bad-to-good recovery is observed
quality_rejected_records_should_not_be_scored=true
```

This slice only diagnoses and recommends. It does not change collector runtime output, PS-Q19R scoring, producer scheduling, WarRoom controls, or AutoTrade behavior.

## Operator usage

Compact diagnosis with JST input accepted:

```powershell
python .\tools\diagnose_collector_reanchor_crossed_book_ps_q20a.py `
  --root D:\btc_ts_hot `
  --target-ts 2026-06-25T21:04:14+09:00 `
  --window-sec 90
```

Optional compact JSON output with byte cap:

```powershell
python .\tools\diagnose_collector_reanchor_crossed_book_ps_q20a.py `
  --root D:\btc_ts_hot `
  --target-ts 2026-06-25T21:04:14+09:00 `
  --window-sec 90 `
  --output .\tmp\work\ps_q20a_collector_reanchor_compact_diagnosis\diagnosis_ps_q20a.json `
  --output-max-bytes 200000
```

## Safety boundary

```text
read_only_diagnosis=true
bounded_gpt_friendly_output=true
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

## Next likely slice

```text
PS-Q20B_COLLECTOR_PREFERRED_ROW_AND_DIAGNOSTIC_ROW_CONTRACT
```

Only proceed to a repair contract after PS-Q20A confirms which failure bucket is dominant in real hot data.
