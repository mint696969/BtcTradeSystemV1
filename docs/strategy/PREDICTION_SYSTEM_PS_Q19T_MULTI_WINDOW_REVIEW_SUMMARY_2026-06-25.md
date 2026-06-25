# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19T_MULTI_WINDOW_REVIEW_SUMMARY_2026-06-25.md
# desc: PS-Q19T design note for read-only multi-window PS-Q19R review aggregation.
# PS-Q19T Multi-window review summary

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: fc09d557

## Purpose

PS-Q19T adds a read-only helper that aggregates multiple PS-Q19R prediction-vs-actual review JSON packets.

```text
ps_q19t_multi_window_review_summary=true
summarizes_ps_q19r_review_json=true
read_only_summary=true
runtime_artifact_write_performed_by_summary=false
status_artifact_write_performed_by_summary=false
prediction_artifact_write_performed_by_summary=false
view_artifact_write_performed_by_summary=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Scope

The helper answers questions such as:

```text
How many review windows were available?
Which horizons moved up/down/flat across windows?
How often did neutral/range expectations match or break?
Which families produced direction mismatches?
Were any windows blocked, warned, or quality-rejected?
```

It does not generate new predictions and does not read live market data. It only summarizes saved PS-Q19R JSON outputs supplied by the operator.

## Operator usage

Save PS-Q19R review outputs into files, then summarize them:

```powershell
python .	oolseview_prediction_vs_actual_market_ps_q19r.py `
  --root D:tc_ts_hot `
  --horizons-sec 15,60,300,600,900 `
  --families market_regime,trend_bias,reversal_zone,breakout_false_break,opportunity_participation,cross_venue_confirmation,human_technical_structure `
  > .	mp\work\ps_q19t_multi_window_review_summaryeview_window_latest.json

python .	ools\summarize_prediction_actual_market_reviews_ps_q19t.py `
  --review-glob .	mp\work\ps_q19t_multi_window_review_summaryeview_window_*.json
```

For a single streamed JSON packet:

```powershell
Get-Content .	mp\work\ps_q19t_multi_window_review_summaryeview_window_latest.json -Raw |
  python .	ools\summarize_prediction_actual_market_reviews_ps_q19t.py --stdin-json
```

## Current observed windows before helper

The operating room currently records two manually reviewed windows:

```text
Window A: generated_at=2026-06-25T07:33:22Z, 15s/60s flat, 300s/600s/900s up after quality gate
Window B: generated_at=2026-06-25T09:16:39Z, 15s/60s flat, 300s/600s/900s down, all actual rows available
```

PS-Q19T makes future windows comparable without turning the review into a trading instruction.

## Safety boundary

```text
read_only_summary=true
runtime_artifact_write_performed_by_summary=false
status_artifact_write_performed_by_summary=false
prediction_artifact_write_performed_by_summary=false
view_artifact_write_performed_by_summary=false
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
