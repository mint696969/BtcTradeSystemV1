# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27F_MARKET_REGIME_ENGINE_ARCHITECTURE_AND_ROADMAP_2026-07-01.md
# desc: PS-Q27F market-regime engine architecture and roadmap. Design-only; separates market-regime inference from WarRoom UI and other prediction engines.
# PS-Q27F Market-regime engine architecture and roadmap

Updated: 2026-07-01 JST
Base: PS-Q27E WarRoom card UI reuse specification
Mode: architecture / roadmap / responsibility separation only; no UI binding, no collector change, no prediction runtime change, no scheduler or producer enablement, no AutoTrade, broker, ledger, mode, or parameter behavior.

```text
ps_q27f_market_regime_engine_architecture=true
base_reentry=PS_Q27E_WARROOM_CARD_UI_REUSE_SPEC_DONE
selected_lane=MARKET_REGIME_ENGINE_ARCHITECTURE_SPEC
market_regime_only=true
other_prediction_cards_out_of_scope=true
architecture_doc_only=true
production_ui_code_changed=false
runtime_code_changed=false
collector_code_changed=false
prediction_engine_runtime_changed=false
warroom_page_changed=false
live_data_connected=false
runtime_read_allowed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
would_send_to_broker=false
```

## Purpose

This document fixes the architecture direction for completing the market-regime prediction area before any live WarRoom binding. The market-regime work must remain focused on market state classification and horizon-based regime prediction. It must not expand into unrelated prediction cards, AutoTrade, broker execution, ledger mutation, scheduler enablement, or live parameter application.

The completed market-regime area should provide:

```text
current_market_regime_nowcast
5m_to_24h_horizon_regime_predictions
source_coverage_and_missing_sources
evidence_quality_and_confidence
invalidation_hints
tactical_hints_for_operator_review
simulation_and_calibration_path
```

The UI is display-only. Inference, feature computation, source reading, simulation, calibration, and parameter proposal responsibilities live outside the Streamlit panel.

## Core architecture principles

```text
repository_is_source_of_truth=true
market_regime_first=true
one_module_one_responsibility=true
ui_displays_only=true
inference_not_in_panel=true
collector_collects_not_predicts=true
feature_layer_extracts_not_renders=true
calibration_proposes_not_applies=true
gpt_analyzes_and_proposes_not_live_mutates=true
gpt_live_parameter_apply_allowed=false
human_gate_required_for_parameter_apply=true
```

The market-regime engine should be built as a separately testable package. WarRoom only adapts its output into existing card contracts.

## Responsibility boundaries

| Area | Responsibility | Must not do |
|---|---|---|
| Collector | Collect, normalize, timestamp, and report source freshness | Classify market regime or mutate prediction parameters |
| Source readers | Read D-hot latest/manifest/nowcast artifacts read-only | Write artifacts or invoke producer/scheduler |
| Feature layer | Build market-regime feature bundles | Render UI or change runtime mode |
| Regime engine | Classify current/horizon regime and explain evidence | Send orders, append ledger, enable AutoTrade |
| Calibration | Evaluate historical outcomes and produce proposals | Apply live parameter changes |
| Simulation | Replay historical inputs and produce reports | Mutate production latest artifacts |
| WarRoom adapter | Convert engine output to card contract | Compute inference logic |
| WarRoom panel | Display card rows and diagnostics | Read/write prediction artifacts directly or infer regime |

## Proposed package layout

The market-regime engine should not be placed inside the WarRoom panel. The proposed core package is:

```text
btcts_next/src/btcts/prediction/market_regime/
  __init__.py
  contracts.py
  horizon_policy.py
  freshness_policy.py
  source_priority_policy.py
  parameter_set.py
  source_snapshot.py

  sources/
    __init__.py
    d_hot_latest_manifest.py
    d_hot_nowcast.py
    forecast_records_reader.py
    collector_state_reader.py

  features/
    __init__.py
    price_structure_features.py
    volatility_features.py
    liquidity_features.py
    orderflow_features.py
    cross_venue_features.py
    source_quality_features.py
    feature_bundle.py

  inference/
    __init__.py
    regime_classifier.py
    transition_engine.py
    confidence_model.py
    evidence_quality.py
    invalidation_hints.py
    tactical_hint_policy.py

  calibration/
    __init__.py
    outcome_labeler.py
    hit_rate_metrics.py
    parameter_proposal.py
    source_priority_proposal.py

  simulation/
    __init__.py
    replay_loader.py
    simulation_runner.py
    simulation_report.py

  diagnostics/
    __init__.py
    coverage_report.py
    missing_source_report.py
    safety_report.py
```

The WarRoom-facing package should remain display/adaptation only:

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/
  __init__.py
  card_adapter.py
  display_packet.py
  panel_binding.py
```

The existing card contract remains the visual contract:

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/market_regime_card_contract.py
```

## Module size and file-growth guard

Avoid creating a single giant market-regime file. Split responsibilities early:

```text
contracts.py=types/enums/packets only
horizon_policy.py=horizon list and cadence only
source_priority_policy.py=per-horizon source weighting only
parameter_set.py=versioned tunable parameters only
sources/*.py=read-only source adapters only
features/*.py=feature extraction by category only
inference/*.py=classification/transition/confidence/explanation only
simulation/*.py=replay and reports only
calibration/*.py=outcome metrics and proposals only
operator_ui/.../market_regime/*.py=display adaptation only
```

No Streamlit import should exist in the core `btcts.prediction.market_regime` package.

## Horizon and update cadence policy

Use separate clocks for observation, prediction, and tactical switching.

```text
observation_clock=current_nowcast_fast
prediction_clock=horizon_appropriate
strategy_clock=debounced_operator_tactical_state
```

Recommended cadence:

| Target | Role | Normal refresh | Stale caution |
|---|---:|---:|---:|
| Current | nowcast / board / executions / freshness | 1-3s | 10-15s |
| 5m | short-horizon regime | 15-30s | 90-120s |
| 15m | short structure | 30-60s | 3-5m |
| 30m | range/breakout transition | 1-2m | 5-10m |
| 60m | medium regime | 3-5m | 10-15m |
| 6h | medium-long regime | 10-15m | 30-60m |
| 12h | medium-long regime | 15-30m | 1-2h |
| 24h | broad regime | 30-60m | 2-4h |

Event-driven refresh candidates may accelerate short-to-medium horizons only:

```text
spread_widening
orderbook_imbalance_jump
large_trade_burst
range_high_low_approach
breakout_candidate
collector_gap_or_resync
spot_fx_basis_jump
```

Tactical hints must not flip on every observation tick. Use debounce and hysteresis, for example:

```text
last_n_predictions_minimum=3
required_consensus=2
minimum_confidence_percent=65
minimum_evidence_quality=PARTIAL
collector_freshness_required=LIVE
spread_wide_caution_blocks_aggressive_hint=true
gap_or_resync_blocks_aggressive_hint=true
```

## Source priority policy

Source priority must be policy-driven, not hard-coded in the classifier. Different horizons should use different weights.

```text
short_horizon_priority=orderbook_depth,tradeflow,spread,current_nowcast,cross_venue
mid_horizon_priority=price_structure,volatility,vwap,orderflow,cross_venue
long_horizon_priority=candle_structure,volatility_regime,macro_context,cross_venue,source_quality
```

The initial missing-source closure candidates are:

```text
orderbook_depth_and_imbalance
spot_btc_jpy_reference
long_candle_history
orderflow_aggregate
outcome_ledger
```

## Feature bundle v1

The engine should expose feature groups explicitly:

```text
price_structure_features
volatility_features
liquidity_features
orderflow_features
cross_venue_features
source_quality_features
```

Each group should report both values and coverage:

```text
available=true_or_false
freshness_state
used_sources
missing_sources
warnings
feature_version
```

The engine must avoid hiding missing inputs. Unknown should be reduced over time by diagnostics, not by guessing.

## Regime vocabulary

The initial regime vocabulary remains aligned with the existing card contract:

```text
UP_TREND
DOWN_TREND
RANGE
LOW_VOL_COMPRESSION
HIGH_VOL_CHOP
BREAKOUT
PANIC_SPIKE
REVERSAL_WATCH
UNKNOWN
```

The classifier output must include:

```text
horizon
horizon_sec
regime_code
confidence_percent
evidence_quality
freshness_badge
short_tag
drivers
warnings
missing_sources
invalidation_hints
tactical_hint
parameter_set_id
source_priority_policy_id
feature_bundle_hash
read_only=true
non_executing=true
would_send_to_broker=false
```

Confidence means classification certainty, not win rate and not a trading edge.

## Simulation and calibration path

The market-regime system must be designed for historical replay and improvement.

Simulation records should preserve:

```text
prediction_generated_at
horizon_sec
predicted_regime
actual_later_regime
match_state
partial_match_reason
miss_reason
used_sources
missing_sources
parameter_set_id
source_priority_policy_id
feature_bundle_hash
warnings
```

Calibration should measure:

```text
horizon_hit_rate
regime_hit_rate
confidence_calibration
unknown_rate
missing_source_impact
warning_predictiveness
false_break_frequency
source_priority_sensitivity
parameter_set_comparison
```

## GPT-assisted analysis policy

GPT may analyze and propose. GPT must not silently apply live changes.

```text
gpt_allowed=simulation_report_summary,miss_reason_analysis,missing_source_analysis,parameter_proposal,source_priority_proposal,collector_gap_recommendation
gpt_forbidden=live_parameter_apply,scheduler_enablement,broker_access,autotrade_trigger,ledger_append,production_artifact_mutation
human_review_required_before_apply=true
new_parameter_sets_are_immutable_versions=true
```

The improvement loop should be:

```text
simulation_or_outcome_analysis
  -> gpt_analysis_packet
  -> parameter_or_source_priority_proposal
  -> human_review
  -> guard_tests
  -> new_immutable_parameter_set_version
```

## Roadmap

### M0 Architecture spec

This PS-Q27F document fixes responsibility boundaries, folder structure, cadence, simulation/calibration direction, and GPT proposal policy.

### M1 Pure contract and policy

Create the core package skeleton and pure contracts only:

```text
contracts.py
horizon_policy.py
freshness_policy.py
source_priority_policy.py
parameter_set.py
```

No D-hot read, no UI binding, no runtime write.

### M2 Source snapshot adapters

Create read-only adapters:

```text
sources/d_hot_nowcast.py
sources/d_hot_latest_manifest.py
sources/forecast_records_reader.py
sources/collector_state_reader.py
```

### M3 Feature bundle v1

Implement feature groups with explicit source coverage and missing-source reporting.

### M4 Regime engine v1

Implement rule-based ensemble:

```text
regime_classifier
transition_engine
confidence_model
evidence_quality
invalidation_hints
tactical_hint_policy
```

### M5 WarRoom card adapter

Convert engine output to the existing market-regime card contract. Keep UI display-only.

### M6 WarRoom read-only binding

Replace sample cards with real read-only cards, with diagnostic fallback. Do not add other prediction card types.

### M7 Simulation and calibration

Add replay, outcome labeling, hit-rate metrics, parameter proposal, and source-priority proposal.

### M8 Collector gap closure

Based on missing-source and simulation evidence, add only the Collector sources that improve regime clarity.

## Completion definition

The market-regime area is complete when:

```text
current_card_uses_nowcast_fast_refresh=true
5m_to_24h_cards_use_horizon_appropriate_cadence=true
6h_and_12h_are_supported_as_explicit_horizons=true
cards_show_regime_confidence_evidence_freshness_warnings_missing_sources=true
unknown_and_low_confidence_have_diagnostic_records=true
warroom_ui_displays_only=true
simulation_and_calibration_path_exists=true
gpt_can_propose_but_not_apply_parameters=true
autotrade_broker_ledger_parameter_runtime_write_remain_false=true
```

## Safety boundary

PS-Q27F is design-only. It changes no production UI behavior, no runtime behavior, no Collector behavior, no prediction producer/scheduler behavior, no artifacts, no AutoTrade, no broker, no ledger, no mode, and no parameter behavior.
## 2026-07-08 operator-agreed market-regime trace/calibration lock
<!-- PS_MARKET_REGIME_ENGINE_TRACE_CALIBRATION_SPEC_LOCK_2026_07_08 -->

The operator-agreed implementation premise is now fixed in:

```text
docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_ENGINE_TRACE_AND_CALIBRATION_SPEC_2026-07-08.md
```

Key locks:

```text
first_implementation_slice=remove_ui_render_path_classifier_and_dhot_preview_inference
card_percent_meaning=market_regime_reading_confidence_not_win_rate
card_percent_explainer_location=help_button_or_detail_balloon_not_card_surface
market_records_and_market_regime_prediction_traces_are_separate=true
prediction_trace_required=true
raw_market_data_duplication_forbidden=true
giants_files_forbidden=true
bounded_date_hour_partitioned_ledgers_required=true
outcome_and_calibration_ledgers_required=true
chart_selection_packets_are_manual_review_artifacts_not_canonical_predictions=true
```

This update does not change code or runtime behavior. It fixes the design baseline before implementation resumes.
