# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q13_MAINLINE_ALIGNMENT_2026-06-22.md
# desc: Corrected mainline alignment after PS-Q11 and PS-Q12; fixes next-work entry before new implementation.
# Prediction System PS-Q13 Mainline Alignment

Updated: 2026-06-22 JST
Status: current / alignment before next implementation
Branch: docs/phase2-handoff-sync

## Purpose

This document corrects the next-work reading after PS-Q11 and PS-Q12 so the repository does not carry an outdated contradiction.

The corrected current position is:

```text
PS-Q11 Scenario Prediction Core strengthening is complete as a read-only/non-executing closeout candidate.
PS-Q12 WarRoom read-only inference display lane is complete and thread-closed at e30f12b7.
The next mainline is not AutoTrade and not a trigger bridge.
The next mainline is WarRoom operator review usability: real-time human confirmation of predictions, GPT-assisted explanation, and safe parameter-adjustment review surfaces.
```

## Corrected interpretation

The earlier open items:

```text
richer evidence weighting
richer invalidation / rewrite state
richer scenario switch trace
advisory / WarRoom explanation strengthening
```

must no longer be treated as untouched open work. They were substantially completed by PS-Q11 as:

```text
evidence_weighting_trace
invalidation_rewrite_trace
scenario_switch_trace
trace_contract_summary
advisory_output_packet_candidate
operator_review_handoff_shape
advisory_packet_summary
scenario_core_closeout_candidate
```

PS-Q12 then connected the latest PredictionSystemResult artifact into WarRoom for read-only operator review and UI Check snapshot/check automation.

## Human-priority mainline

The human-approved implementation priority before AutoTrade is:

```text
1. Make the WarRoom tab useful for humans to observe predictions derived from inference in real-time-changing conditions.
2. Let the human and GPT review explanations, warnings, blockers, signal strength, scenario traces, and parameter-adjustment candidates from the tab.
3. Keep parameter adjustment as review/proposal/staging first, not silent live mutation.
4. Improve other information sources and complete the planned inference features before AutoTrade implementation.
5. Only after the Prediction System / WarRoom review loop is robust, return to AutoTrade implementation under a separate explicit scope.
```

## Safety and responsibility boundaries

The next implementation must preserve strict responsibility separation:

```text
Prediction System owns prediction contracts, evidence, scenario traces, explanation packets, and parameter-adjustment proposal data.
WarRoom owns display, operator review, GPT-assisted explanation surfaces, and check-only UI snapshots.
Collector owns collection and hot/latest runtime data production.
AutoTrade owns trigger consumption, readiness, risk gates, approval/ledger, mode/order, and broker paths, but remains out of scope for the next work.
```

The next implementation must also preserve folder/module separation. Do not put AutoTrade trigger logic inside WarRoom components, and do not make Prediction System import UI runtime or broker/order code.

## Explicit non-goals for the next implementation thread

```text
Do not implement AutoTrade trigger consumption.
Do not implement PredictionSystemResult-to-AutoTrade bridge execution.
Do not append approval, decision, or command ledgers.
Do not add broker/private API calls.
Do not add mode apply or order placement.
Do not add WarRoom runtime artifact writes.
Do not add freshness bypass.
Do not silently mutate live parameters.
```

## Correct next-work entry

The corrected next-work entry is:

```text
PS-Q13A: WarRoom real-time prediction review and parameter-adjustment review preflight.
```

The first slice should be contract/inventory/check-only before any UI behavior expansion:

```text
read current WarRoom prediction components
read PredictionSystemResult / Scenario Core output contracts
define display-only review surfaces for real-time prediction changes
define GPT-assisted explanation and parameter-adjustment proposal boundaries
define where staged parameter proposals would live later
add focused guard that blocks AutoTrade, ledger, broker, mode/order, runtime-write, and silent live mutation behavior
```

## Working entry sentence

```text
PS-Q13 starts from WarRoom operator review usability, not AutoTrade. PS-Q11 Scenario Core strengthening and PS-Q12 WarRoom read-only inference display are complete. The next safe slice is a check-only WarRoom real-time prediction review / GPT-assisted parameter-adjustment review preflight that preserves responsibility separation and keeps AutoTrade, ledger, broker, mode/order, runtime writes, and live parameter mutation out of scope.
```
