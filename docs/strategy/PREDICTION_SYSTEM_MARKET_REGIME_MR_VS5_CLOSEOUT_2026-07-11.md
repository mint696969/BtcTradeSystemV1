# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_VS5_CLOSEOUT_2026-07-11.md
# desc: Records the accepted MR-VS5 WarRoom MarketRegime explanation closeout and verification evidence.
# Prediction System MarketRegime MR-VS5 Closeout

Updated: 2026-07-11 JST
Checkpoint: MR_VS5_CONNECTED_UI_CLOSEOUT_ACCEPTED

<!-- PS_MARKET_REGIME_MR_VS5_CLOSEOUT_2026_07_11 -->

```text
mr_vs5_connected_ui_complete=true
market_regime_only=true
warroom_reads_normalized_explanation_packet=true
ui_prediction_invoked=false
ui_classifier_invoked=false
ui_raw_market_read=false
ui_confidence_recalculated=false
ui_writes_dhot=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_intent_submitted=false
parameter_auto_promotion_allowed=false
live_parameter_apply_allowed=false
normal_field_internal_diagnostics_hidden=true
explanation_kept_inside_details=true
head_baseline_new_regressions=0
existing_operator_ui_baseline_clean=false
```

## 1. Completed scope

MR-VS5 connects a read-only MarketRegime confidence and evidence explanation path to WarRoom.

Implemented files:

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_regime_explanation_adapter.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_explanation_adapter.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_explanation_ui.py
btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_prediction_card_bridge.py
```

The implementation reads persisted MarketRegime artifacts only. It does not invoke source snapshot construction, feature generation, classification, confidence estimation, calibration production, parameter mutation, broker APIs, AutoTrade, or D-hot writes.

## 2. Display contract

The card surface remains unchanged.

```text
display confidence remains the existing card value
shadow confidence remains diagnostic only
display_confidence_replaced=false
shadow_only=true
UNKNOWN / 15% policy remains unchanged
```

The explanation detail separates:

```text
display confidence
shadow confidence
confidence cap
source configured weight
source signal strength
source quality score
weighted numerator
source quality
source freshness
historical reliability
trusted sample count
minimum trusted sample count
remaining trusted samples
calibration score
parameter comparison readiness
```

`weighted numerator` is not rendered as a percentage.

## 3. Calibration cohort selection

The current logic uses `primary_current` as the canonical evaluation cohort.

Verified D-hot values:

```text
cohort=primary_current
sample_count=56
calibration_score=0.5536
hit=6
partial=50
miss=0
interpretation=not_win_rate
```

Compatibility values remain separate references:

```text
primary compatibility reference:
  sample_count=8874
  calibration_score=0.1178

trusted legacy reference:
  sample_count=8818
  calibration_score=0.115
```

Schema behavior:

```text
current schema + primary_current present:
  use primary_current

current schema + primary_current missing:
  fail closed
  do not fall back to primary

legacy schema without current-schema marker:
  preserve CP26 compatibility
```

## 4. Source evidence status

Verified current D-hot source fields include:

```text
market_regime.source_quality:
  quality_score_percent=3.125
  weighted_numerator=93.75

market_regime.price_structure:
  trusted_sample_count=0
  minimum_trusted_sample_count=20
  remaining_trusted_samples=20
  ready=false
```

Not-ready sources remain visible in details. They are not hidden, inferred, or treated as calibrated.

## 5. Parameter comparison status

```text
active_parameter_set_id=market_regime_engine_parameter_set.v1
trusted_parameter_set_count=1
comparison_ready=false
best_parameter_set_claim_allowed=false
promotion_recommendation_allowed=false
auto_promotion_allowed=false
```

MR-VS5 does not claim that the active parameter set is superior.

## 6. WarRoom visual policy

Normal WarRoom fields avoid internal diagnostics and roadmap commentary.

Hidden from normal display:

```text
entry-gate and bridge version captions
prediction/classifier internal safety captions
future prediction-row reservation captions
adapter/read-only implementation commentary
```

Detailed evidence remains under the compact `地合い詳細` disclosure only.

Machine-readable safety fields remain in the returned render packet and tests even when not shown in the normal field.

## 7. Safety boundary

Verified adapter safety packet:

```text
read_only=true
writes_dhot=false
prediction_invoked=false
classifier_invoked=false
raw_market_read=false
confidence_recalculated=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
order_intent_submitted=false
parameter_auto_promotion_allowed=false
live_parameter_apply_allowed=false
would_send_to_broker=false
```

The adapter also rejects persisted artifacts that contain forbidden execution flags set to true.

## 8. Verification evidence

Focused directly affected guard:

```text
25 passed
```

The guard covers:

```text
adapter normalization
malformed and oversized artifact handling
required artifact absence
safety violation detection
current-primary cohort selection
legacy-schema compatibility
current-schema fail-closed behavior
WarRoom detail rendering
normal-field diagnostic suppression
prediction-card bridge machine boundary
calibration status
parameter comparison status
parent scenario guidance status
artifact-only MarketRegime card reads
```

D-hot smoke verified:

```text
packet_ok=true
horizon_count=8
current display confidence=65
current shadow confidence=1
current calibration sample=56
current calibration score=0.5536
price_structure=0/20, remaining=20, ready=false
safety_violations=[]
```

Browser inspection verified:

```text
existing card layout remains intact
current-primary summary is visible
65% and shadow 1% are separated in detail
calibration 56 / 0.5536 is visible in detail
price_structure readiness is visible in detail
normal-field diagnostic noise is suppressed
```

## 9. Broad HEAD baseline comparison

Compared against HEAD:

```text
HEAD=e0d09cf5bfb18a4b97b92e0f0cb3b30cf777b713
```

Results:

```text
operator_ui_all:
  HEAD problems=1
  worktree problems=1
  new=0
  resolved=0

operator_ui_without_q29c_collection_blocker:
  HEAD problems=32
  worktree problems=31
  new=0
  resolved=1

prediction_all:
  HEAD problems=0
  worktree problems=0
  new=0
  resolved=0
```

Decision:

```text
new_worktree_problem_count=0
mr_vs5_baseline_regression_free=true
existing_baseline_is_clean=false
```

Existing operator UI baseline failures are not reclassified as passing and are not repaired inside MR-VS5. They remain a separate repository-maintenance slice.

Evidence files:

```text
tmp/work/mr_vs5_baseline_compare/results/comparison.md
tmp/work/mr_vs5_baseline_compare/results/comparison.json
tmp/work/mr_vs5_baseline_compare/results/head/*.log
tmp/work/mr_vs5_baseline_compare/results/worktree/*.log
```

## 10. Deferred work

MR-VS5 does not include:

```text
changing card confidence values
promoting shadow confidence
changing UNKNOWN / 15% policy
creating additional parameter sets
changing price_structure signal production
starting another prediction family
producer restart or schedule changes
AutoTrade or broker integration
operator UI stale-test baseline repair
```

## 11. Closeout decision

```text
mr_vs5_contract_review_complete=true
mr_vs5_adapter_complete=true
mr_vs5_connected_ui_complete=true
mr_vs5_visual_inspection_complete=true
mr_vs5_safety_boundary_complete=true
mr_vs5_head_baseline_comparison_complete=true
mr_vs5_new_regressions=0
mr_vs5_close_guard_accepted=true
```
