# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_VS6_4_CLOSEOUT_2026-07-12.md
# desc: Records accepted validated push-primary and artifact-fallback source selection for MarketRegime.
# Prediction System MarketRegime MR-VS6.4 Closeout

Updated: 2026-07-12 JST
Status: accepted
Gate: `MR_VS6_4_PUSH_PRIMARY_ARTIFACT_FALLBACK_SOURCE_ADAPTER_IMPLEMENTATION_ACCEPTED`
Next gate: `MR_VS6_5_WARROOM_CARD_AND_EXPLANATION_INTEGRATION_IMPLEMENTATION`

## Scope completed

MR-VS6.4 added a pure MarketRegime source adapter that validates push and artifact candidates through the common prediction-family read-model contract and selects exactly one source.

```text
valid push -> push primary
missing or invalid push + valid artifact -> artifact fallback
both invalid -> fail-closed unavailable
```

Implemented production file:

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_regime_read_model_source.py
```

Focused test file:

```text
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_push_primary_artifact_fallback.py
```

## Contract behavior

```text
topic=prediction.family.market_regime
prediction_family_id=market_regime
common_read_model_validation_required=true
common_push_validation_required=true
confidence_merge_performed=false
confidence_recalculation_performed=false
artifact_read_performed=false
render_invoked=false
mount_enabled=false
```

The adapter accepts both a canonical push message and the actual WP3 widget-state shape. Transport receipt time remains `transport_received_at_ms`; prediction freshness remains the selected model's `generated_at` exposed as `prediction_generated_at`.

## Bounded payload behavior

Selected models are copied without mutating the source.

```text
max_text_length=512
max_depth=8
max_mapping_items=64
max_list_items=32
```

Long strings are bounded. Container nesting beyond the accepted depth rejects the selected candidate and returns fail-closed unavailable rather than silently truncating semantic structure. The bounded result is revalidated through the common read-model validator.

## Safety boundary

```text
read_only=true
non_executing=true
prediction_invoked=false
classifier_invoked=false
render_invoked=false
mount_enabled=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_intent_submitted=false
would_send_to_broker=false
```

No file I/O, D-hot write, producer wiring, UI mounting, confidence merge, inference, classifier execution, broker access, AutoTrade trigger, or order intent was added.

## Guard evidence

```text
mr_vs6_4_dedicated=8_passed
wp3_wp4_receive_only_regression=10_passed
common_family_contract_regression=10_passed
operator_ui_full_suite=1176_passed
prediction_full_suite=282_passed
operator_ui_ast_syntax_no_pyc=998_files_passed
changed_file_py_compile=passed
canonical_push_primary_smoke=passed
canonical_artifact_fallback_smoke=passed
invalid_sources_fail_closed_smoke=passed
runner_idempotence=passed
git_diff_check=passed
```

`compileall` for the complete operator UI package was not used as the final broad syntax guard because Windows failed while creating a `.pyc` temporary path for an unrelated pre-existing extremely long module filename. Full AST parsing without `.pyc` creation checked 998 Python files successfully, and the changed files passed direct `py_compile`.

## Close decision

MR-VS6.4 is accepted. MR-VS6.5 may connect the selected prevalidated read model to the existing MarketRegime card and explanation adapters. It must not recalculate confidence, invoke inference or classification, change producer behavior, or connect broker, AutoTrade, or order paths.

```text
current_gate=MR_VS6_4_PUSH_PRIMARY_ARTIFACT_FALLBACK_SOURCE_ADAPTER_IMPLEMENTATION_ACCEPTED
next_gate=MR_VS6_5_WARROOM_CARD_AND_EXPLANATION_INTEGRATION_IMPLEMENTATION
family_completion_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
```
