# path: ./docs/strategy/PREDICTION_SYSTEM_REENTRY_GATE_2026-06-19.md
# desc: Thread closeout gate that restores next-thread entry to Prediction System / Scenario Prediction Core and preserves the paused AutoTrade return bookmark.
# Prediction System Re-entry Gate

Updated: 2026-06-19 JST
Status: current / thread closeout gate
Branch: docs/phase2-handoff-sync

## Purpose

This gate closes the current Operator UI / decision policy gate visibility detour at S203 and restores the next-thread entry point to the Prediction System mainline.

The required next-thread mainline is:

```text
Prediction System / Scenario Prediction Core strengthening
```

This is not an AutoTrade execution slice and not another decision-policy visibility-chain continuation.

## Current decision

```text
S203 is the stopping point for the current visibility chain.
Do not continue to S204 automatically.
Do not resume AutoTrade main roadmap automatically.
Next thread must start from Prediction System / Scenario Prediction Core.
```

## Prediction System current truth

The current official roadmap is:

```text
tmp/gpt_room/memory/roadmaps/PHASE3_PREDICTION_PROCESS_ENTRY_ROADMAP_2026-04-16.md
```

The current reading helper is:

```text
tmp/gpt_room/memory/notes/PHASE3_CURRENT_MAINLINE_NAVIGATOR_2026-04-18.md
```

The next-thread goal is not to complete all prediction layers at once. The clean target is to strengthen Scenario Prediction Core enough that the system has a reliable inference / prediction layer before any return to AutoTrade.

## Required next-thread first reads

```text
tmp/gpt_room/02_START_HERE.md
tmp/gpt_room/08_STATUS.md
tmp/gpt_room/09_FOCUS.json
tmp/gpt_room/10_DECISIONS.md
tmp/gpt_room/11_STATE.json
docs/strategy/PREDICTION_SYSTEM_REENTRY_GATE_2026-06-19.md
docs/strategy/PREDICTION_SYSTEM_FORMAL_SPEC_BTC_BITFLYER_2026-04-16.md
docs/strategy/AI_ASSISTED_PREDICTION_SUPPORT_SPEC_BTC_BITFLYER_2026-04-16.md
tmp/gpt_room/memory/roadmaps/PHASE3_PREDICTION_PROCESS_ENTRY_ROADMAP_2026-04-16.md
tmp/gpt_room/memory/notes/PHASE3_CURRENT_MAINLINE_NAVIGATOR_2026-04-18.md
```

## Required next-thread implementation entry

Start from these implementation files:

```text
btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_system_contract.py
btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_system_input.py
btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_scenario_builder.py
btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_liquidity_board_history.py
btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_regime_turning_point.py
btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_replay_feedback.py
btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_calibration_hint_builder.py
btcts_next/src/btcts/replay/prediction_evaluation_entry.py
btcts_next/src/btcts/replay/prediction_evaluation_report.py
btcts_next/src/btcts/replay/prediction_calibration_review.py
btcts_next/src/btcts/replay/replay_prediction_artifacts.py
btcts_next/src/btcts/replay/replay_prediction_feedback.py
```

## Existing Prediction System reached state

Treat these as reached unless a guard disproves them:

```text
PredictionSystem contract skeleton
PredictionSystemInput
PredictionScenarioOutput
PredictionCalibrationHint
active evidence family: market_summary anchor
active evidence family: liquidity / board history
active evidence family: regime / turning-point
Scenario Prediction Core skeleton
replay evaluation / calibration prep
replay feedback bridge
WarRoom / advisory thin consumer first slice
```

## Next implementation priority

The next work should strengthen Scenario Prediction Core, not AutoTrade execution.

Priority order:

```text
1. Scenario Core richer evidence weighting
2. richer invalidation / rewrite state
3. richer scenario switch trace
4. advisory / WarRoom explanation strengthening using trace_focus_material
5. runtime true Scenario Core source adoption judgement
```

## Explicit non-goals for next thread

Do not start with:

```text
S204 decision policy gate catalog continuation
auto-trading execution implementation
broker integration
mode apply
order placement
approval/grant execution
full tactic engine
full position management automation
execution timing automation
online learning automation
multi-venue expansion
```

## AutoTrade return bookmark

AutoTrade main roadmap remains paused/frozen. It must not resume automatically.

When Prediction System is sufficiently built and a human explicitly approves returning to AutoTrade, resume from the stored AutoTrade bookmark:

```text
kill switch / incident / heartbeat runtime scaffolding
```

Before returning to AutoTrade, require:

```text
focused Prediction System guards green
SR-FX Data/UI closeout still valid
working tree clean
explicit human approval
broker/mode/order paths still fail-closed
```

## Clean handoff statement

The clean next-thread opening sentence is:

```text
Start from Prediction System / Scenario Prediction Core strengthening. S203 closed the visibility-chain detour; do not continue S204 unless the human explicitly redirects. AutoTrade remains paused and should only resume later from kill switch / incident / heartbeat runtime scaffolding after Prediction System completion and explicit human approval.
```
