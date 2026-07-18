# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_P1_RUNTIME_HORIZON_READ_MODEL_QUALIFICATION_2026-07-18.md
# desc: Offline qualification receipt for projecting MR-F9 runtime-horizon artifacts into the family-neutral read model and existing WarRoom bridge.

# MarketRegime MR-F9 P1 Runtime-Horizon Read-Model Qualification

Updated: 2026-07-18 JST
Status: accepted
Decision: PROCEED_TO_P2_TRUST_FALLBACK_UNKNOWN_QUALIFICATION

<!-- MR_F9_P1_RUNTIME_HORIZON_READ_MODEL_QUALIFICATION_2026_07_18 -->

## Qualified boundary

```text
runtime-horizon manifest + 8 payloads
  -> pure read-only projector
  -> prediction_family_read_model
  -> existing artifact fallback selector
  -> existing selected read-model card bridge
```

## Repository changes

```text
btcts_next/src/btcts/prediction/market_regime/runtime_horizon_read_model.py
btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_runtime_horizon_read_model_mr_f9_p1.py
```

## Live D-hot qualification

```text
collection_id=mr-f9-24h-fad90fe3ed0cf9805322
run_id=run-20260717T190000Z-fb7c2cc20e9b
prediction_origin=2026-07-17T19:00:00Z
horizon_count=8
payload_digest_match_count=8
selected_source=artifact
card_count=8
```

## Safety and semantics

```text
read_only=true
non_executing=true
prediction_invoked=false
classifier_invoked=false
confidence_recalculated=false
source_merge_performed=false
writes_dhot=false
mount_enabled=false
would_send_to_broker=false
```

## Test evidence

```text
focused_test_count=13
result=PASS
```

## Decision

```text
P1_status=COMPLETE
P2_next=MR_F9_TRUST_FALLBACK_UNKNOWN_PREMATURITY_QUALIFICATION
MR_F9_collection_monitoring_remains_active=true
MR_F9_12_hour_checkpoint_remains_required=true
MR_F10_entry_remains_allowed_after_parallelizable_MR_F9_tasks_complete=true
```
