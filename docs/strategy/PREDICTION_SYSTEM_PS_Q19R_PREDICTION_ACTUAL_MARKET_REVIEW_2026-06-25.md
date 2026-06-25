# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19R_PREDICTION_ACTUAL_MARKET_REVIEW_2026-06-25.md
# desc: PS-Q19R design note for read-only prediction versus actual market movement review.
# PS-Q19R Prediction versus actual market review

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: db5f1f5d

## Purpose

PS-Q19R adds a read-only helper for operator review of the latest Prediction System artifact against realized FX_BTC_JPY market movement from D hot market overview data.

```text
ps_q19r_prediction_actual_market_review=true
latest_prediction_vs_actual_market_review_helper_added=true
reads_latest_prediction_artifact=true
reads_market_overview_jsonl=true
actual_market_point_quality_gate=true
read_only_review=true
runtime_artifact_write_performed_by_review=false
status_artifact_write_performed_by_review=false
prediction_artifact_write_performed_by_review=false
view_artifact_write_performed_by_review=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Scope

The helper compares selected prediction families and horizons with realized mid-price movement at matching future timestamps.

Default horizons:

```text
15,60,300,600,900 seconds
```

Default families:

```text
market_regime
trend_bias
reversal_zone
breakout_false_break
opportunity_participation
cross_venue_confirmation
human_technical_structure
```

This is an observation review, not a trading signal, not a calibration write, and not a command ledger append.

## Operator command

```powershell
python .	ools
eview_prediction_vs_actual_market_ps_q19r.py --root D:tc_ts_hot
```

For a narrower review:

```powershell
python .	ools
eview_prediction_vs_actual_market_ps_q19r.py `
  --root D:tc_ts_hot `
  --horizons-sec 15,60,300,600 `
  --families market_regime,trend_bias,reversal_zone,breakout_false_break,opportunity_participation
```

## Interpretation

The output is deliberately conservative:

- directional labels are compared to realized up/down/flat buckets;
- neutral/range/watch labels are treated as range/neutral expectations;
- non-directional labels are reported but not treated as a trade-quality score;
- unavailable horizons are reported as unavailable rather than guessed.


## Actual market point quality gate

A realized market point is counted as `actual_available=true` only when all of the following are true:

```text
trust_state=trusted
continuity_state=continuous
interpretation_bucket=allow_structural_use
spread>=0 when spread is present
best_bid<=best_ask when both sides are present
```

If a point is `quarantined`, `reanchor_required`, crossed, or has negative spread, it remains visible in `actual_by_horizon` but is treated as unavailable for alignment scoring.

## Safety boundary

```text
read_only_review=true
runtime_artifact_write_performed_by_review=false
status_artifact_write_performed_by_review=false
prediction_artifact_write_performed_by_review=false
view_artifact_write_performed_by_review=false
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
