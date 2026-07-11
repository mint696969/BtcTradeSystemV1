# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_VS6_IMPLEMENTATION_READINESS_2026-07-11.md
# desc: Freezes the MR-VS6 implementation boundary for canonical MarketRegime family read-model and receive-only push delivery.

# Prediction System MarketRegime MR-VS6 Implementation Readiness

Updated: 2026-07-11 JST
Checkpoint: MR_VS6_IMPLEMENTATION_READINESS_ACCEPTED
Accepted implementation gate: MR_VS6_1_COMMON_FAMILY_READ_MODEL_IMPLEMENTATION_ACCEPTED

<!-- PS_MARKET_REGIME_MR_VS6_IMPLEMENTATION_READINESS_2026_07_11 -->

```text
implementation_started=true
market_regime_priority=true
canonical_family_read_model_required=true
canonical_receive_only_push_required=true
artifact_fallback_preserved=true
ui_inference_forbidden=true
ui_confidence_recalculation_forbidden=true
auto_promotion_forbidden=true
broker_autotrade_order_forbidden=true
```

## 1. Purpose

MR-VS6 is the implementation-readiness slice immediately before coding the canonical MarketRegime read-model and push path.

The implementation target is:

```text
MarketRegime producer output
  -> canonical family read model
  -> canonical receive-only push message
  -> WarRoom push router / state store
  -> MarketRegime display adapter
  -> existing MarketRegime card renderer
```

Persisted D-hot artifacts remain the fallback source and audit record.

## 2. Current repository facts

The repository already contains:

```text
common prediction contracts:
  btcts_next/src/btcts/prediction/contracts.py
  btcts_next/src/btcts/prediction/horizons.py
  btcts_next/src/btcts/prediction/parameter_sets.py
  btcts_next/src/btcts/prediction/outcome_ledger.py
  btcts_next/src/btcts/prediction/scenario_parts.py

MarketRegime contracts and producer:
  btcts_next/src/btcts/prediction/market_regime/contracts.py
  btcts_next/src/btcts/prediction/market_regime/horizon_policy.py
  btcts_next/src/btcts/prediction/market_regime/artifact_contracts.py
  btcts_next/src/btcts/prediction/market_regime/artifact_projection.py
  btcts_next/src/btcts/prediction/market_regime/tools/write_latest.py
  btcts_next/src/btcts/prediction/market_regime/producer_loop.py

WarRoom receive-only path:
  btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp2_widget_registry_manifest.py
  btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp3_per_widget_state_store.py
  btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp4_receive_only_push_router.py
  btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/rt_live_receiver_bridge.py
  btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_regime_explanation_adapter.py
  btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
```

The current WarRoom MarketRegime display path is artifact-first. The push infrastructure currently carries market/receiver/summary topics, but no canonical prediction-family topic.

## 3. Completion gaps before MarketRegime can be called complete

```text
G1 canonical family read model:
  MarketRegime latest_read_model is family-specific and not wrapped by a common family envelope.

G2 canonical push message:
  no prediction.family.market_regime receive-only topic exists.

G3 primary/fallback selection:
  WarRoom does not yet select push-primary and artifact-fallback deterministically.

G4 source identity:
  push payload and artifact payload need one run_id/prediction_id/parameter_set_id identity chain.

G5 freshness boundary:
  transport freshness and prediction/source freshness must remain separate.

G6 common reuse boundary:
  common family metadata is duplicated inside MarketRegime-specific payloads.

G7 future-family validation:
  the parent contract must be reusable by trend_bias without importing MarketRegime enums or classifier logic.
```

The following are later MarketRegime completion slices and are not implemented in MR-VS6:

```text
second trusted parameter set and comparison proof
review_request / review_note / review_link loop
price_structure trusted-sample maturity
calibration maturity thresholds
other prediction-family implementation
```

## 4. Responsibility classification

### 4.1 Parent/common inference layer

The following fields and behavior belong to a common family read-model contract:

```text
schema_version
contract_version
prediction_family_id
generated_at
run_id
prediction_id
logic_version
parameter_set_id
horizon_key
horizon_sec
horizon_group
primary_label
primary_label_display
confidence_percent
confidence_kind
freshness_state
evidence_quality
drivers
blockers
warnings
invalidation_hints
source_refs
trace_refs
outcome_refs
calibration_refs
scenario_part_ref
safety
```

Common safety must assert:

```text
read_only=true
non_executing=true
raw_market_payload_included=false
ui_render_invokes_prediction=false
ui_render_invokes_classifier=false
ui_confidence_recalculation=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_intent_submitted=false
parameter_auto_promotion_allowed=false
live_parameter_apply_allowed=false
would_send_to_broker=false
```

### 4.2 MarketRegime-specific layer

The following remain inside `btcts.prediction.market_regime`:

```text
MarketRegimeCode
TacticalHint
MarketRegime source-priority policy
MarketRegime horizon cadence
feature bundle construction
regime classifier
signal scoring
regime-specific evidence interpretation
regime-specific invalidation
regime-specific card labels and styles
```

The parent/common contract must not import MarketRegime enums.

### 4.3 WarRoom/UI layer

WarRoom owns only:

```text
receive-only message routing
bounded sanitized state retention
push-primary / artifact-fallback selection
display normalization
existing card rendering
operator explanation rendering
```

WarRoom must not own:

```text
prediction execution
classifier execution
confidence calculation
source weighting
outcome resolution
parameter comparison
parameter promotion
raw source interpretation
```

## 5. Canonical family read-model contract

Create a new common module:

```text
btcts_next/src/btcts/prediction/family_read_model.py
```

Required public builders and validators:

```text
build_prediction_family_read_model(...)
validate_prediction_family_read_model(...)
build_prediction_family_push_message(...)
validate_prediction_family_push_message(...)
```

The read model contains a bounded list of horizon rows. Each row uses family-neutral labels and may include a bounded `family_payload` mapping for family-specific display fields.

For MarketRegime, `family_payload` may contain:

```text
regime_code
regime_label
tactical_hint
source_priority_policy_id
signal_summary_ref
```

It must not contain raw candles, raw orderbook, raw executions, or unbounded diagnostic payloads.

## 6. Canonical receive-only push contract

Canonical topic:

```text
prediction.family.market_regime
```

Canonical message shape:

```text
topic_key=prediction.family.market_regime
message_kind=prediction_family_read_model
receive_only=true
value=<validated common family read model>
received_at_ms=<transport receipt time>
sequence=<monotonic producer/run sequence when available>
```

Unsafe flags remain rejected by `wp4_receive_only_push_router.py`.

The push payload must not be generated by the UI. It is projected from the same producer artifact set used for persistence.

## 7. Primary and fallback selection

WarRoom selection policy:

```text
1. Use validated push state when present and prediction-generated_at is usable.
2. Otherwise use validated persisted latest artifacts.
3. Never merge confidence values between push and artifact sources.
4. Never use transport receipt time as prediction freshness.
5. If both are invalid, return fail-closed unavailable state.
```

Required source-state metadata:

```text
selected_source=push|artifact|unavailable
push_present
push_valid
artifact_present
artifact_valid
fallback_used
fallback_reason
transport_received_at_ms
prediction_generated_at
run_id
prediction_id
```

## 8. Exact implementation boundary

### 8.1 New production files

```text
btcts_next/src/btcts/prediction/family_read_model.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_regime_read_model_source.py
```

### 8.2 Modified production files

```text
btcts_next/src/btcts/prediction/market_regime/artifact_projection.py
  add projection from MarketRegimePredictionPacket/artifacts to common family read model

btcts_next/src/btcts/prediction/market_regime/tools/write_latest.py
  build canonical family read model from the same run
  expose canonical push message in the returned artifact set
  do not add UI imports or broker behavior

btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp2_widget_registry_manifest.py
  register market_regime_prediction_widget and prediction.family.market_regime topic

btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp5_topic_routing_subscription_plan.py
  classify prediction.* as prediction channel group

btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_regime_explanation_adapter.py
  accept a prevalidated normalized family read model without recalculation

btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
  use push-primary / artifact-fallback source adapter
```

`producer_loop.py` should remain unchanged unless the canonical push delivery mechanism requires an explicit emission hook. Any such change must be reviewed as a separate sub-slice and must not open a new outbound socket from prediction code.

### 8.3 New tests

```text
btcts_next/src/btcts/prediction/tests/test_prediction_family_read_model.py
btcts_next/src/btcts/prediction/tests/test_market_regime_family_read_model_projection.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_family_push_route.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_push_primary_artifact_fallback.py
```

### 8.4 Existing tests directly affected

```text
btcts_next/src/btcts/prediction/tests/test_market_regime_write_latest_mvp.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_prediction_card_bridge.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_explanation_adapter.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_explanation_ui.py
```

## 9. Implementation order

```text
MR-VS6.1 common family read-model contract and validators
MR-VS6.2 MarketRegime projection into common contract
MR-VS6.3 canonical receive-only topic registration and state routing
MR-VS6.4 push-primary / artifact-fallback source adapter
MR-VS6.5 WarRoom card and explanation integration
MR-VS6.6 broad guards and closeout
```

Each sub-slice must be independently testable and revertible.

## 10. Acceptance guards

Focused guards:

```text
family read-model validation accepts MarketRegime projection
family read-model validation rejects raw payload keys
family push validation rejects unsafe true flags
MarketRegime run identity is preserved across artifact and push projection
all eight MarketRegime horizons are preserved
UNKNOWN / 15% remains unchanged
push transport receipt time does not replace prediction freshness
invalid push falls back to artifact
valid push is preferred over artifact
no confidence merge or recalculation occurs
unknown prediction topic remains safely isolated
```

Safety guards:

```text
prediction_invoked=false
classifier_invoked=false
ui_confidence_recalculation=false
raw_market_data_read=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_intent_submitted=false
parameter_auto_promotion_allowed=false
live_parameter_apply_allowed=false
would_send_to_broker=false
```

Broad guards:

```text
pytest -q btcts_next/src/btcts/apps/operator_ui/tests
pytest -q btcts_next/src/btcts/prediction
git diff --check
```

No test exclusion, skip, xfail, or historical-contract rewriting is allowed to obtain a pass.

## 10.1 Contract-change policy

MR-VS6 implementation must follow:

`docs/strategy/PREDICTION_SYSTEM_CONTRACT_CHANGE_AND_TEST_GUARD_POLICY_2026-07-11.md`

Any change to schema, ownership, topic, fallback behavior, or safety behavior must update implementation, current specification, current guard, affected full suites, and handoff state in the same slice.

## 11. Non-goals

MR-VS6 must not:

```text
add trend_bias or another prediction family
replace displayed confidence with shadow confidence
auto-promote a parameter set
write from UI to D-hot
invoke MarketRegime inference from UI
open broker/private APIs
submit orders
connect AutoTrade
remove persisted artifacts
remove existing card UI
expose internal diagnostic captions in the normal field
```

## 11.1 Canonical family roadmap

MR-VS6 is phase `MR-F0` of the current authoritative family roadmap:

`docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_FAMILY_ROADMAP_2026-07-11.md`

MR-VS6 completion does not complete the MarketRegime family. After MR-VS6.6, continue with forecast-label provenance, current-state estimator separation, explainable scoring, transition modeling, horizon-specific future forecasting, baseline comparison, calibration, shadow comparison, and stable context publication before another family starts.

## 12. Implementation-start decision

```text
completion_gap_reviewed=true
common_vs_family_responsibility_fixed=true
canonical_family_read_model_contract_fixed=true
canonical_push_topic_fixed=true
primary_fallback_policy_fixed=true
exact_file_boundary_fixed=true
test_boundary_fixed=true
implementation_ready=true
implementation_started=true
next_checkpoint=MR_VS6_2_MARKET_REGIME_PROJECTION_IMPLEMENTATION
```

## Implementation follow-through

MR-VS6.1 has been implemented and accepted.

```text
accepted_gate=MR_VS6_1_COMMON_FAMILY_READ_MODEL_IMPLEMENTATION_ACCEPTED
closeout=docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_VS6_1_CLOSEOUT_2026-07-11.md
prediction_full_suite=277_passed
next_gate=MR_VS6_2_MARKET_REGIME_PROJECTION_IMPLEMENTATION
```
