# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19N_PROVIDER_FAMILY_MAPPING_AND_SOURCE_QUALITY_COMPLETION_2026-06-25.md
# desc: PS-Q19N design note for completing provider-family mapping and OHLCV source quality statuses.
# PS-Q19N Provider-family mapping and source-quality completion

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: f8186b53

## Purpose

PS-Q19N repairs the remaining Tier0 provider/source quality gap after PS-Q19M. PS-Q19M started passing `source_quality_by_id`, but `bitflyer_trades` and `bitflyer_board_summary` could still fall into `unknown_provider`, and OHLCV sources derived from Q10A rows had no SourceQualityStatus.

```text
ps_q19n_provider_family_mapping_and_source_quality_completion=true
bitflyer_trades_provider_family_mapped=true
bitflyer_board_summary_provider_family_mapped=true
prediction_ohlcv_provider_family_mapped=true
ohlcv_source_quality_statuses_built_from_q10a_rows=true
ohlcv_1m_quality_status_mapped=true
ohlcv_5m_quality_status_mapped=true
ohlcv_10m_quality_status_mapped=true
ohlcv_15m_quality_status_mapped=true
ohlcv_30m_quality_status_mapped=true
ohlcv_1h_quality_status_mapped=true
ohlcv_4h_quality_status_mapped=true
ohlcv_1d_quality_status_mapped=true
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

- `source_quality.py` maps bitFlyer trade/orderbook aliases and prediction OHLCV aliases to non-unknown provider families.
- Q10D builder adds SourceQualityStatus entries for `ohlcv_1m` through `ohlcv_1d` from already-supplied Q10A rows.

OHLCV SourceQualityStatus represents input freshness/lineage only. Candle sufficiency and long-MA sufficiency remain handled by the technical layer.

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

After PS-Q19N and one PS-Q19K producer cycle, PS-Q19K gap audit should show reduced `unknown_provider_context_only`, reduced `tier0_source_quality_status_missing`, and ideally reduced Tier0 source-quality cap pressure. Macro/session calendar gaps may remain for a later slice.
