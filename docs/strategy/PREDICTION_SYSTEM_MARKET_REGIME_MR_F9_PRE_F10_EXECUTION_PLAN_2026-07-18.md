# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_PRE_F10_EXECUTION_PLAN_2026-07-18.md
# desc: Ordered MR-F9 work gates that must be preserved before and while MR-F10 offline design begins.

# MarketRegime MR-F9 Pre-F10 Execution Plan

Updated: 2026-07-18 JST
Status: current

<!-- MR_F9_PRE_F10_EXECUTION_PLAN_2026_07_18 -->

## Purpose

MR-F10 may begin as offline schema and interface design, but it must not silently close or displace open MR-F9 evidence work. This plan fixes the order and concurrency boundary.

## Ordered gates

```text
Gate A — persist the accepted six-hour checkpoint
  commit and push the six-hour CONTINUE receipt
  preserve runtime identity under test at 384392793da8745e4323e4011a72fda38b6c2893

Gate B — complete the MR-F9 UI/WS timestamp trace
  trace producer -> artifact -> selected read model -> packet -> card
  record source timestamps, selection timestamps, packet timestamps, render timestamps
  verify no origin mixing, stale recurrence, UI inference, or timestamp regeneration
  keep the running producer unchanged

Gate C — continue bounded collection monitoring
  monitor cadence, missing slots, duplicate skips, conflicts, lease continuity, and errors
  remain read-only against D-hot except for the already-running producer

Gate D — record the twelve-hour checkpoint
  scheduled at 2026-07-17T23:19:00Z
  create a durable CONTINUE / PAUSE / ABORT / RESTART_REQUIRED decision receipt
```

## MR-F10 entry rule

```text
MR_F10_OFFLINE_STABLE_CONTEXT_CONTRACT_DESIGN may begin after Gate B is accepted.
Gate C and Gate D remain active MR-F9 obligations in parallel.
Starting MR-F10 does not accept or close RW-MR-003, RW-MR-003A, or RW-MR-003B.
No MR-F10 code may be loaded into PID 9048 or alter the running observation identity.
```

## Work that remains blocked on collection completion or maturity

```text
planned-end completion receipt
final 24-hour outcome maturity
execution trust / fallback / UNKNOWN evidence review
balanced accuracy and macro F1
Brier score, log loss, and ECE
churn and transition-delay analysis
promotion proposal and human review evidence
MR-F9 closeout
```

## Current next slice

```text
current_gate=MR_F9_LIVE_24H_OBSERVATION_RUNNING
next_gate=MR_F9_12_HOUR_CHECKPOINT
next_slice=MR_F9_UI_WS_TIMESTAMP_TRACE
following_parallel_slice=MR_F10_OFFLINE_STABLE_CONTEXT_CONTRACT_DESIGN
```
