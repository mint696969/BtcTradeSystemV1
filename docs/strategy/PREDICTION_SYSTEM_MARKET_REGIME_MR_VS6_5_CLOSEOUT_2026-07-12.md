# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_VS6_5_CLOSEOUT_2026-07-12.md
# desc: Records accepted MarketRegime selected-read-model integration into WarRoom cards and explanations.
# Prediction System MarketRegime MR-VS6.5 Closeout

Updated: 2026-07-12 JST
Status: accepted
Gate: `MR_VS6_5_WARROOM_CARD_AND_EXPLANATION_INTEGRATION_IMPLEMENTATION_ACCEPTED`
Next gate: `MR_VS6_6_BROAD_GUARDS_AND_CLOSEOUT`

## Scope completed

MR-VS6.5 connected the validated MarketRegime source packet into the existing WarRoom card and explanation surface without changing confidence semantics or invoking prediction/classification logic.

```text
valid WP3 MarketRegime push state
  -> MR-VS6.4 source selector
  -> selected read-model bridge
  -> existing MarketRegime cards
  -> existing explanation surface

no valid push
  -> existing latest_cards artifact path remains active
```

## Implemented production surface

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_regime_selected_read_model_bridge.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py
```

Focused test:

```text
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_selected_read_model_integration.py
```

## Runtime behavior

The production page now inspects the actual WP3 widget store and attaches a MarketRegime source packet only when the common validator selects a valid `push` source.

```text
state_updates_are_topic_independent=true
state_updates_are_receive_driven=true
screen_rerender_is_ws_event_driven=false
screen_rerender_is_auto_refresh_cycle_driven=true
```

Therefore widget state can change independently as messages arrive, while visible Streamlit updates still occur on the configured WarRoom auto-refresh cycle. A future event-driven fragment rerun may reduce display latency, but it is not part of MR-VS6.5.

## Card and explanation contract

```text
all_eight_horizons_preserved=true
confidence_recalculated=false
drivers_preserved=true
blockers_preserved=true
warnings_preserved=true
invalidation_hints_preserved=true
run_id_preserved=true
prediction_id_preserved=true
parameter_set_id_preserved=true
selected_source_preserved=true
prediction_generated_at_preserved=true
transport_received_at_ms_preserved=true
```

The selected common read model remains the only source of displayed confidence on the push path. Push and artifact confidence values are never merged.

## Compatibility behavior

The legacy `latest_cards.json` artifact display path remains unchanged when no valid MarketRegime push is available. UI review confirmed eight cards, explanation sections, read-only markers, and existing artifact fallback rendering remained intact.

The currently observed UI continued to show:

```text
source=artifact latest_cards
```

This is expected because live delivery of `prediction.family.market_regime` was not observed during MR-VS6.5 validation.

## Delivery boundary

MR-VS6.5 completed the receive-state-to-card path, but did not add or prove a producer for the MarketRegime topic.

```text
market_regime_topic_contract_registered=true
receive_only_route_connected=true
wp3_state_to_card_connected=true
live_market_regime_topic_delivery_observed=false
producer_added=false
subscribe_send_added=false
```

If an endpoint delivers a valid `prediction.family.market_regime` push, the next WarRoom refresh cycle will render it through the selected-read-model path. MR-VS6.6 must record this remaining live-delivery gap and apply broad guards before closing the vertical slice.

## Safety boundary

```text
read_only=true
prediction_invoked=false
classifier_invoked=false
raw_market_read=false
confidence_recalculated=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_intent_submitted=false
would_send_to_broker=false
```

No prediction inference, classifier execution, producer wiring, subscription sending, broker access, AutoTrade trigger, order intent, or live parameter application was added.

## Guard evidence

```text
mr_vs6_5_final_focused_integration=27_passed
operator_ui_full_suite=1184_passed
prediction_full_suite=282_passed
operator_ui_ast_syntax_no_pyc=1000_files_passed
changed_file_py_compile=passed
production_wiring_tests=8_passed
warroom_page_fragment_regression=11_passed
market_regime_display_regression=19_passed
runner_composability=passed
runner_idempotence=passed
git_diff_check=passed
ui_visual_review=artifact_fallback_normal
```

## Close decision

MR-VS6.5 is accepted. MR-VS6.6 must run broad guards, verify the final repository boundary, record the unresolved live MarketRegime topic-delivery evidence, and close the MR-VS6 vertical slice without claiming completion of the MarketRegime family.

```text
current_gate=MR_VS6_5_WARROOM_CARD_AND_EXPLANATION_INTEGRATION_IMPLEMENTATION_ACCEPTED
next_gate=MR_VS6_6_BROAD_GUARDS_AND_CLOSEOUT
family_completion_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
```
