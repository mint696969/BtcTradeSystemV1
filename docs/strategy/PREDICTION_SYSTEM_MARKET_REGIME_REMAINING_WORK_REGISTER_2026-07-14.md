# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_REMAINING_WORK_REGISTER_2026-07-14.md
# desc: Canonical open-work register preventing deferred, parallel, blocked, and family-closeout tasks from being lost across threads.

# Prediction System MarketRegime Remaining Work Register

Updated: 2026-07-15 JST
Status: current and binding
Reference HEAD: a7299bdf

<!-- PS_MARKET_REGIME_REMAINING_WORK_REGISTER_2026_07_14 -->

## 1. Purpose

This register is the canonical source for all unfinished MarketRegime work after MR-F6 closeout.

A task may not disappear merely because work moves to another thread, starts in parallel, is deferred, or is blocked by sample maturity. Every unfinished item must remain here until one of these terminal states is recorded:

```text
accepted
cancelled_with_reason
superseded_by_named_contract
moved_to_non_blocking_research_with_owner_and_reentry_condition
```

Starting a later phase does not implicitly complete earlier open work.

## 2. Current position

```text
current_phase=MR-F8
current_gate=MR_F7_CONFIDENCE_CALIBRATION_ACCEPTED
next_gate=MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON
family_completion_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
market_regime_ready_for_next_family=false
trend_bias_blocked=true
```

## 3. Blocking roadmap work

### RW-MR-001 — MR-F7 confidence calibration

```text
status=accepted
accepted_checkpoint=MR_F7_CONFIDENCE_CALIBRATION_ACCEPTED
accepted_rollback_point=23660311
accepted_closeout_commit=a7299bdf
closeout=docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F7_CONFIDENCE_CALIBRATION_CLOSEOUT_2026-07-15.md
blocking_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
owner_phase=MR-F7
parallel_allowed=true
may_be_skipped=false
```

Required outcomes:

```text
prediction/outcome calibration dataset
horizon, regime, model, parameter-set, session, volatility, liquidity, and source-quality buckets
out-of-sample calibration
sample-size shrinkage
freshness and source-quality caps
long-horizon confidence caps
reliability-by-confidence-bucket evidence
high-confidence miss analysis
overconfidence and underconfidence analysis
abstention-quality analysis
insufficient-sample fallback
UI wording distinguishing calibrated and uncalibrated reliability
focused, connected, prediction, and operator-UI guards
canonical acceptance and rollback point
```

### RW-MR-002 — MR-F8 shadow model and parameter-set comparison

```text
status=open
blocking_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
owner_phase=MR-F8
may_start_before_mr_f7_complete=only_if_contracts_do_not_conflict
may_be_skipped=false
```

Required outcomes:

```text
at least two candidate models or parameter sets
same-window and same-source comparison
condition-specific performance
coverage, abstention, churn, transition-delay, and calibration comparison
candidate identity and rollback point
human approval contract
auto-promotion forbidden
live parameter apply forbidden
```

### RW-MR-003 — MR-F9 outcome/review/calibration evidence loop

```text
status=open
blocking_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
owner_phase=MR-F9
may_be_skipped=false
```

Required outcomes:

```text
horizon-expiry detection
outcome resolution under accepted target definitions
immutable prediction-to-outcome link
unresolved and invalid outcome states
calibration summaries
miss-concentration analysis
WarRoom review selection
review_request, review_note, and review_link contracts
parameter/model proposal evidence
proposal separated from live apply
replayable review trail
```

### RW-MR-004 — MR-F10 stable family-neutral context contract

```text
status=open
blocking_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
owner_phase=MR-F10
may_be_skipped=false
```

Required outcomes:

```text
versioned immutable family-neutral context schema
current regime and calibrated reliability
state age and stability
change-point probability
future distribution by horizon
transition risk
volatility, liquidity, and source-quality context
invalidation hints and trace refs
UNKNOWN and abstention semantics
backward compatibility
TrendBias consumer fixture and integration test
no MarketRegime implementation leakage
no trade-permission surface
```

### RW-MR-005 — Family-wide integration, hardening, and closeout

```text
status=open
blocking_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
owner_phase=family-closeout
starts_after=MR-F10 acceptance
may_be_skipped=false
```

Required outcomes:

```text
MR-F0 through MR-F10 responsibility and dependency audit
duplicate, obsolete, and unreachable contract audit
public schema and interface freeze
current-state, future-forecast, calibration, outcome, and context identity continuity
calibration-maturity consistency
shadow-comparison decision consistency
outcome/review evidence continuity
TrendBias consumer integration guard
prediction full suite
operator UI full suite
architecture, philosophy, roadmap, and project-memory synchronization
accepted model and parameter-set record
accepted target-definition record
known bad conditions and non-blocking gaps
rollback point
thread-handoff pack
```

### RW-MR-006 — MARKET_REGIME_READY_FOR_NEXT_FAMILY gate

```text
status=blocked
blocked_by=RW-MR-001,RW-MR-002,RW-MR-003,RW-MR-004,RW-MR-005
next_family=trend_bias
may_be_skipped=false
```

Acceptance requires all blocking items above plus explicit proof that no broker, AutoTrade, order, auto-promotion, or live-parameter-apply path was opened.

## 4. Deferred but non-lost work

The following may remain after the family completion gate only when explicitly reclassified with evidence:

```text
additional feature enrichment
more sample accumulation
future calibration refinement
future ensemble candidate
non-blocking model research
```

Each deferred item must record:

```text
stable ID
reason
owner or owning phase
blocking=false
reentry condition
compatibility requirement
```

No unnamed deferred task is allowed.

### RW-MR-NB-001 — MR-F7 detailed source/flag calibration evidence accumulation and activation review

```text
status=moved_to_non_blocking_research_with_owner_and_reentry_condition
blocking=false
owner_phase=MR-F9
reason=legacy history predates the complete contribution ledger
reentry_condition=trusted mature OOS outcomes exist for enriched MR-F7 trace rows and activation diagnostics pass
compatibility_requirement=preserve raw/calibrated/display confidence separation and do not silently replace card confidence
```

This item covers evidence accumulation and later activation review only. It does not reopen the accepted MR-F7 architecture and does not authorize runtime fit, auto-promotion, or live parameter application.

## 5. Parallel-work rule

```text
parallel_work_does_not_imply_completion=true
later_phase_start_does_not_close_earlier_open_items=true
shared_contract_change_requires_cross_track_review=true
all_open_items_must_remain_in_this_register=true
thread_handoff_must_read_this_register=true
```

Before beginning any slice, the next GPT must check whether the proposed change touches or depends on another open item in this register.

## 6. Update protocol

When an item changes state:

```text
1. update this register
2. update the family roadmap
3. update canonical acceptance/closeout document
4. update tmp/gpt_room/CURRENT.json
5. update tmp/gpt_room/START.md and DECISIONS.md
6. run focused and connected guards
7. record commit and rollback point
```

An item must not be removed merely because its section becomes inconvenient. Accepted or superseded items remain recorded with their terminal evidence until the family closeout is complete.
