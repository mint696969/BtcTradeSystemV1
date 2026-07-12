# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_5_SHADOW_TRACE_AND_OUTCOME_IDENTITY_2026-07-12.md
# desc: MR-F5.5 design and safety boundary for immutable shadow forecast trace identity and pure outcome-resolver projection.

# Prediction System MarketRegime MR-F5.5 Shadow Trace and Outcome Identity

Updated: 2026-07-12 JST
Status: implementation slice prepared
Scope: pure identity contract and resolver-input projection

## Purpose

The existing outcome resolver accepts compact prediction mappings but does not preserve the complete MR-F5 identity tuple. MR-F5.5 adds an immutable trace contract without modifying or invoking the existing resolver.

## Identity tuple

```text
origin_timestamp
expiry_at
target_horizon_sec
target_horizon_key
target_definition_version
model_id
logic_version
parameter_set_id
feature_snapshot_ref
predicted_future_state
forecast_status
```

A deterministic SHA-256 trace ID is derived from the material forecast identity. Any material identity change produces a different trace ID.

## Resolver projection

`to_outcome_resolver_prediction()` returns an immutable mapping compatible with the current resolver input shape while retaining MR-F5 identity fields for later resolver extension.

This slice does not call the resolver and does not append an outcome row.

## Safety

```text
shadow_only=true
canonical_replacement=false
existing_outcome_resolver_modified=false
outcome_ledger_append=false
d_hot_read=false
d_hot_write=false
writer_change=false
ui_change=false
broker_private_api=false
autotrade=false
order_submission=false
```
