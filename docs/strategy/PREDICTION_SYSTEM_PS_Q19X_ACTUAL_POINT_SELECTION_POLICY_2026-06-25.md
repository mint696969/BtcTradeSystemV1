# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19X_ACTUAL_POINT_SELECTION_POLICY_2026-06-25.md
# desc: PS-Q19X design note for read-only comparison of actual-point selection policies.
# PS-Q19X Actual point selection policy comparison

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 9ddd1ca5

## Purpose

PS-Q19X adds a read-only helper that compares the current PS-Q19R strict nearest actual-point policy with a candidate nearest-quality-ok-within-tolerance policy.

```text
ps_q19x_actual_point_selection_policy=true
compares_strict_nearest_vs_quality_ok_within_tolerance=true
read_only_policy_compare=true
ps_q19r_behavior_changed_by_policy_compare=false
runtime_artifact_write_performed_by_policy_compare=false
status_artifact_write_performed_by_policy_compare=false
prediction_artifact_write_performed_by_policy_compare=false
view_artifact_write_performed_by_policy_compare=false
collector_state_write_performed_by_policy_compare=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Why this exists

PS-Q19W proved that the PS-Q19U rejected 300s actual point came from a same-second mixed-quality condition: some rows were quarantined/reanchor-required/crossed/negative-spread while other same-second rows were trusted/allow-structural-use.

PS-Q19X does not change PS-Q19R. It only reports whether a quality-ok candidate exists within a bounded tolerance when the strict nearest row is rejected.

## Compared policies

```text
current_ps_q19r_policy=strict_nearest_then_fail_closed_quality_gate
candidate_policy=nearest_quality_ok_within_tolerance
```

The comparison is advisory only:

```text
quality_rejected_records_should_not_be_scored=true
quality_ok_candidate_does_not_imply_auto_rewrite=true
operator_policy_decision_required_before_ps_q19r_change=true
```

## Operator usage

For a saved observation generated at 2026-06-25T11:59:14Z:

```powershell
python .\tools\compare_actual_point_selection_policy_ps_q19x.py `
  --root D:\btc_ts_hot `
  --generated-at 2026-06-25T11:59:14Z `
  --horizons-sec 15,60,300,600,900 `
  --tolerance-sec 30
```

## Safety boundary

```text
read_only_policy_compare=true
ps_q19r_behavior_changed_by_policy_compare=false
runtime_artifact_write_performed_by_policy_compare=false
status_artifact_write_performed_by_policy_compare=false
prediction_artifact_write_performed_by_policy_compare=false
view_artifact_write_performed_by_policy_compare=false
collector_state_write_performed_by_policy_compare=false
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
