# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_VS6_3_CLOSEOUT_2026-07-12.md
# desc: Records the accepted MR-VS6.3 canonical receive-only topic registration and bounded state routing.
# Prediction System MarketRegime MR-VS6.3 Closeout

Updated: 2026-07-12 JST
Status: accepted
Gate: `MR_VS6_3_CANONICAL_RECEIVE_ONLY_TOPIC_AND_STATE_ROUTING_IMPLEMENTATION_ACCEPTED`
Next gate: `MR_VS6_4_PUSH_PRIMARY_ARTIFACT_FALLBACK_SOURCE_ADAPTER_IMPLEMENTATION`

## Scope completed

MR-VS6.3 registered the canonical MarketRegime prediction-family topic and routed accepted receive-only messages into the existing immutable per-widget state store.

```text
topic=prediction.family.market_regime
widget_id=market_regime_prediction_widget
channel_group=prediction
receive_only=true
subscribe_intent_only=true
subscribe_invoked=false
mount_enabled=false
```

## Implemented production surface

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp2_widget_registry_manifest.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp5_topic_routing_subscription_plan.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp6_independent_widget_update_pipeline.py
```

## Responsibility boundary

The MarketRegime topic is registered and state-addressable, but it is not mounted into existing WarRoom render packets.

```text
receive_and_route=true
state_store_enabled=true
render_mount_enabled=false
warroom_layout_modified=false
push_primary_selection_added=false
artifact_fallback_selection_added=false
producer_wiring_added=false
classifier_invocation_added=false
prediction_invocation_added=false
```

The explicit `mount_enabled` manifest boundary prevents a receive-only registration from becoming an accidental UI feature. Existing five mounted widgets and seven bottom-chart rows remain unchanged.

## Bounded state behavior

The existing state store continues to:

- isolate updates to the target widget;
- drop raw payload fields;
- reject unknown topics;
- keep immutable previous state;
- bound top-level mappings and lists;
- retain no executable callable values.

MR-VS6.4 must validate the common prediction-family read-model contract before any push payload becomes a primary display source. String length, nested depth, and nested mapping limits remain an explicit MR-VS6.4 input-validation concern.

## Regression discovered and corrected

Initial registry integration caused the new uninitialized MarketRegime widget to flow into WP8-WP13 rendering, increasing mounted widget and chart-row counts and producing one stale row. This violated the MR-VS6.3 no-render-change boundary.

The structural correction added `mount_enabled` to the manifest and filters render-packet generation in WP6. The MarketRegime widget remains receive/state-ready but unmounted until the dedicated WarRoom connection slice.

## Guard evidence

```text
mr_vs6_3_dedicated=4_passed
previously_failing_operator_ui=23_passed
operator_ui_full_suite=1168_passed
prediction_full_suite=282_passed
wp4_receive_only_router=3_passed
compile=passed
runner_idempotence=passed
git_diff_check=passed
```

The full operator UI result includes restoration of the required Q28C D-hot read-only snapshot runner under ignored `tmp/work`. That runner writes only to `tmp/work/.../out` and does not enter the repository commit.

## Safety invariants

```text
read_only=true
receive_only=true
websocket_opened=false
subscribe_invoked=false
websocket_send_enabled=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_intent_submitted=false
prediction_requested=false
classifier_requested=false
warroom_mount_enabled=false
would_send_to_broker=false
```

## Accepted repository files

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp2_widget_registry_manifest.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp5_topic_routing_subscription_plan.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp6_independent_widget_update_pipeline.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp2_widget_registry_manifest.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp3_per_widget_state_store.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_wp5_topic_routing_subscription_plan.py
btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_receive_only_topic_routing.py
```

## Close decision

MR-VS6.3 is accepted. MR-VS6.4 may implement validated push-primary and artifact-fallback source selection, but it must not mount the MarketRegime widget or change displayed confidence semantics.

```text
current_gate=MR_VS6_3_CANONICAL_RECEIVE_ONLY_TOPIC_AND_STATE_ROUTING_IMPLEMENTATION_ACCEPTED
next_gate=MR_VS6_4_PUSH_PRIMARY_ARTIFACT_FALLBACK_SOURCE_ADAPTER_IMPLEMENTATION
family_completion_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
```
