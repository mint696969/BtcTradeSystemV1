# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q20C_MARKET_OVERVIEW_SELECTION_REPLAY_DIAGNOSTIC_2026-06-26.md
# desc: PS-Q20C bounded market.overview selection replay diagnostic using the PS-Q20B contract.
# PS-Q20C Market overview selection replay diagnostic

Updated: 2026-06-26 JST
Branch: docs/phase2-handoff-sync
Base clean head: fc49039b

## Purpose

PS-Q20C applies the PS-Q20B consumer-row selection contract to bounded historical `market.overview` windows and reports compact evidence.

```text
ps_q20c_market_overview_selection_replay_diagnostic=true
uses_ps_q20b_consumer_row_selection_contract=true
bounded_gpt_friendly_output=true
no_new_giant_files=true
canonical_timestamp_axis=UTC_ISO8601_Z
ui_display_timezone=Asia/Tokyo_JST
ps_q19r_scoring_policy_changed=false
collector_runtime_behavior_changed=false
```

## Questions answered

```text
How many seconds contain consumer_preferred rows?
How many seconds fail-closed because no consumer_preferred row exists?
How many seconds contain both consumer_preferred and diagnostic_transition rows?
How many false-quality-block candidate seconds exist?
Which source_series_id / source_stream_session_id dominate?
Which quality reasons dominate diagnostic_transition rows?
```

## Size policy

```text
summary_only_default=true
raw_full_window_records_included=false
sample_seconds_default_max=20
sample_seconds_hard_max=100
diagnostic_json_target_max_bytes=200000
diagnostic_json_hard_max_bytes=1000000
```

## Operator usage

```powershell
python .\tools\replay_market_overview_selection_ps_q20c.py `
  --root D:\btc_ts_hot `
  --target-ts 2026-06-25T21:04:14+09:00 `
  --window-sec 90 `
  --max-second-samples 20
```

Optional compact JSON output:

```powershell
python .\tools\replay_market_overview_selection_ps_q20c.py `
  --root D:\btc_ts_hot `
  --target-ts 2026-06-25T21:04:14+09:00 `
  --window-sec 90 `
  --max-second-samples 20 `
  --output .\tmp\work\ps_q20c_market_overview_selection_replay_diagnostic\replay_ps_q20c.json `
  --output-max-bytes 200000
```

## Safety boundary

```text
read_only_replay_diagnostic=true
runtime_artifact_write_performed_by_replay=false
status_artifact_write_performed_by_replay=false
prediction_artifact_write_performed_by_replay=false
view_artifact_write_performed_by_replay=false
collector_state_write_performed_by_replay=false
collector_runtime_behavior_changed=false
ps_q19r_scoring_policy_changed=false
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
PS-Q20D_MARKET_OVERVIEW_PREFERRED_ROW_CONSUMER_INTEGRATION_DESIGN
```

Only proceed if PS-Q20C evidence shows that preferred-row separation would reduce false quality blocks without hiding diagnostic transition rows.
