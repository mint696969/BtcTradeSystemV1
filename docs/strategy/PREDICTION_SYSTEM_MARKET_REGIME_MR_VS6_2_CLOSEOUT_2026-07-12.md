# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_VS6_2_CLOSEOUT_2026-07-12.md
# desc: Records the accepted MR-VS6.2 MarketRegime projection into the common prediction-family read-model contract.
# Prediction System MarketRegime MR-VS6.2 Closeout

Updated: 2026-07-12 JST
Status: accepted
Gate: `MR_VS6_2_MARKET_REGIME_PROJECTION_IMPLEMENTATION_ACCEPTED`
Next gate: `MR_VS6_3_CANONICAL_RECEIVE_ONLY_TOPIC_AND_STATE_ROUTING_IMPLEMENTATION`

## Scope completed

MR-VS6.2 introduced a pure MarketRegime projection into the accepted family-neutral read-model contract.

Implemented production surface:

- `btcts_next/src/btcts/prediction/market_regime/artifact_projection.py`
- public export from `btcts_next/src/btcts/prediction/market_regime/__init__.py`
- focused guards in `btcts_next/src/btcts/prediction/tests/test_market_regime_family_read_model_projection.py`

## Public projection

```text
build_market_regime_family_read_model
```

The projection preserves all eight horizons, run and prediction identity, model and version identity, parameter-set identity, freshness, evidence quality, drivers, blockers, warnings, invalidation hints, bounded source and trace references, and bounded MarketRegime display payload.

## Responsibility boundary

```text
projection_is_pure=true
common_contract_modified=false
classifier_behavior_modified=false
producer_wiring_modified=false
warroom_modified=false
raw_market_payload_included=false
broker_autotrade_order_modified=false
```

MarketRegime-specific values remain inside the bounded `family_payload`. The common layer does not import MarketRegime enums or classifier logic.

## Import-path correction

Initial verification exposed an import-path defect in the first patch. The projection originally imported the common builder through a top-level `btcts` absolute import. This passed tests that injected `btcts_next/src` into `sys.path` but failed under a noncanonical source-tree package import.

The production module now uses a package-relative import. The accepted runtime guard uses the repository's canonical package mode:

```text
PYTHONPATH=<repository>/btcts_next/src
import btcts.prediction.market_regime
```

The noncanonical `btcts_next.src.btcts...` import form is not an accepted repository runtime path.

## Safety invariants

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

## Guard evidence

```text
focused_projection=5_passed
common_family_contract=5_passed
direct_artifact_contract=6_passed
prediction_full_suite=282_passed
canonical_package_import=passed
compileall_prediction=passed
patch_runner_idempotence=passed
fix_runner_idempotence=passed
git_diff_check=passed
```

No skip, xfail, exclusion, historical-contract rewrite, UI change, producer change, broker change, AutoTrade change, order change, or live parameter change was used to obtain the pass.

## Accepted changed files

```text
btcts_next/src/btcts/prediction/market_regime/__init__.py
btcts_next/src/btcts/prediction/market_regime/artifact_projection.py
btcts_next/src/btcts/prediction/tests/test_market_regime_family_read_model_projection.py
```

## Close decision

MR-VS6.2 is accepted. The next independently testable slice is canonical receive-only topic registration and state routing. It must not yet add push-primary/artifact-fallback selection or WarRoom display integration.

```text
current_gate=MR_VS6_2_MARKET_REGIME_PROJECTION_IMPLEMENTATION_ACCEPTED
next_gate=MR_VS6_3_CANONICAL_RECEIVE_ONLY_TOPIC_AND_STATE_ROUTING_IMPLEMENTATION
family_completion_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
```
