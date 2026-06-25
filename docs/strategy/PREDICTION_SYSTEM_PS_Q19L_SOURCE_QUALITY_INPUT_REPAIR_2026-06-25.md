# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19L_SOURCE_QUALITY_INPUT_REPAIR_2026-06-25.md
# desc: PS-Q19L design note for repairing feature-depth source inputs in PredictionSystemResult builder.
# PS-Q19L Source quality input repair

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 8c5ecea0

## Purpose

PS-Q19L repairs the first source-quality gap found by PS-Q19K: `bitflyer_board_summary` and `bitflyer_trades` were missing from context evidence profiles even though Q10B/Q10A already read bounded hot D orderbook/trade tails.

```text
ps_q19l_source_quality_input_repair=true
feature_depth_snapshot_built_from_q10a_builder_kwargs=true
bitflyer_board_summary_input_mapped=true
bitflyer_trades_input_mapped=true
feature_depth_snapshot_passed_to_prediction_system=true
collector_behavior_changed=false
hot_file_read_scope_changed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Change

`prediction_warroom_prediction_system_result_builder_runner.py` now creates a context-only `FeatureDepthSnapshot` from existing Q10A builder kwargs:

- `rows` -> `bitflyer_trades` tradeflow window.
- `feature_depth_context_summary` -> `bitflyer_board_summary` orderbook snapshot.

The snapshot is then passed to `build_prediction_system_result(..., feature_depth_snapshot=...)`.

## Safety boundary

```text
read_only=true
non_executing=true
context_only=true
collector_behavior_changed=false
hot_file_read_scope_changed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Expected result

After PS-Q19L and one PS-Q19K producer cycle, PS-Q19K gap audit should show reduced or eliminated `missing_bitflyer_board_summary` / `missing_bitflyer_trades` counts. Tier0 source-quality status warnings may remain as a separate future repair.
