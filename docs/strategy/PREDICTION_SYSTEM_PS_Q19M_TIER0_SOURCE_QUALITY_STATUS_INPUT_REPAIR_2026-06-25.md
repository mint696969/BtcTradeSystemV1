# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19M_TIER0_SOURCE_QUALITY_STATUS_INPUT_REPAIR_2026-06-25.md
# desc: PS-Q19M design note for repairing Tier0 source-quality status inputs in PredictionSystemResult builder.
# PS-Q19M Tier0 source-quality status input repair

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 0282512e

## Purpose

PS-Q19M repairs the second source-quality gap found after PS-Q19L: `source_quality_by_id` was still `None`, causing Tier0 provider/source quality to remain unknown even after board/trade evidence reached PredictionSystemResult.

```text
ps_q19m_tier0_source_quality_status_input_repair=true
source_quality_by_id_built_from_q10a_builder_kwargs=true
bitflyer_trades_quality_status_mapped=true
bitflyer_board_summary_quality_status_mapped=true
bitflyer_fx_ticker_quality_status_mapped=true
provider_source_reliability_state_status_mapped=true
source_quality_by_id_passed_to_prediction_system=true
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

`prediction_warroom_prediction_system_result_builder_runner.py` now creates conservative `SourceQualityStatus` objects from already-supplied Q10A builder kwargs only:

- `rows` -> `bitflyer_trades` quality status.
- `feature_depth_context_summary` -> `bitflyer_board_summary` quality status.
- `venue_snapshots` -> `bitflyer_fx_ticker` quality status.
- in-memory derived summary -> `provider_source_reliability_state` quality status.

These statuses are passed to `build_prediction_system_result(..., source_quality_by_id=...)`.

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

After PS-Q19M and one PS-Q19K producer cycle, PS-Q19K gap audit should show a reduction in Tier0 provider/source-quality unknown warnings. Long-horizon `macro_context` and `session_calendar_context` may remain for a later slice.
