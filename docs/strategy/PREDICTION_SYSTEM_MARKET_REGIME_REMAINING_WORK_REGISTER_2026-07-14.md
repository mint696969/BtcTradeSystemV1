# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_REMAINING_WORK_REGISTER_2026-07-14.md
# desc: Canonical open-work register preventing deferred, parallel, blocked, and family-closeout tasks from being lost across threads.

# Prediction System MarketRegime Remaining Work Register

Updated: 2026-07-16 JST
Status: current and binding
Reference implementation HEAD: 5ef4c03c

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
current_phase=MR-F9
current_gate=MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON_ACCEPTED
next_gate=MR_F9_OUTCOME_REVIEW_CALIBRATION_EVIDENCE_LOOP
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
status=accepted
accepted_checkpoint=MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON_ACCEPTED
accepted_implementation_basis_head=7d9e81f4
accepted_decision=insufficient_evidence
selected_candidate=null
rollback_candidate=market_regime.future.transparent_baseline.params.v1
closeout=docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON_CLOSEOUT_2026-07-16.md
blocking_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
owner_phase=MR-F8
may_be_skipped=false
```

Accepted outcomes:

```text
two parameter sets compared
same-window and same-source comparison
seven paired horizons and fourteen immutable trace identities
canonical ledger outcome resolution
coverage and abstention comparison
candidate identity and rollback point
winner/tie/insufficient-evidence contract
human approval contract
auto-promotion forbidden
live parameter apply forbidden
```

Evidence-maturity outcomes not available from the single accepted origin are explicitly transferred to `RW-MR-003`, `RW-MR-003A`, and `RW-MR-003B`:

```text
full condition-specific performance
balanced accuracy and macro F1
Brier score, log loss, and ECE
multi-origin churn
transition-detection delay
full-horizon outcome completion
promotion maturity
independent horizon-execution proof
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
continuous paired forecast generation across multiple origins
horizon-expiry detection
outcome resolution under accepted target definitions
immutable prediction-to-outcome link
unresolved and invalid outcome states
full condition-specific comparison
calibration summaries and probability metrics
miss-concentration analysis
coverage, abstention, UNKNOWN, churn, and transition-delay analysis
WarRoom review selection
review_request, review_note, and review_link contracts
parameter/model proposal evidence
proposal separated from live apply
replayable review trail
```



#### MR-F9 implementation checkpoint — 2026-07-16

```text
implementation_foundation_checkpoint=accepted
implementation_basis_head=5ef4c03c
checkpoint=docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_IMPLEMENTATION_CHECKPOINT_2026-07-16.md
operational_evidence_complete=false
status_remains=open
```

Accepted implementation foundation:

```text
horizon-specific execution evidence contracts
expiry-gated maturation and immutable snapshot persistence
multi-origin execution diagnostics
multi-snapshot unresolved/UNKNOWN/invalidated/abstention diagnostics
human-gated review_request, review_note, and review_link contracts
paired execution readiness and immutable 7-pair/14-trace runtime bridge
explicit execution-observation fact builder and one-shot JSON tool
immutable incomplete observation-request template with fixed trace identity
no scheduler, automatic writer, auto-promotion, live apply, broker, AutoTrade, or order path
```

Still required before `RW-MR-003`, `RW-MR-003A`, or `RW-MR-003B` can be accepted:

```text
production observation-source integration without inferred facts
real multi-origin D-hot evidence accumulation
mature full-horizon outcomes
condition-specific comparison
probability-semantic Brier, log loss, and ECE
balanced accuracy and macro F1
miss concentration, churn, and transition-delay evidence
minimum observed-slot and coverage policy satisfaction
mature promotion proposal and WarRoom review evidence
```

### RW-MR-003A — MR-F9 horizon-specific inference execution proof

```text
status=open
parent=RW-MR-003
blocking_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
owner_phase=MR-F9
may_be_skipped=false
```

This item records the operator's unresolved trust concern about the upstream artifacts shown by the display-only UI. Repeated short-horizon confidence values and persistent long-horizon `UNKNOWN` must not be treated as proof of independent prediction execution.

Required outcomes:

```text
one immutable trace per enabled horizon and origin
horizon-specific raw score or probability distribution
model, logic, parameter-set, snapshot, and target identity
source freshness and generated-at continuity
abstention decision
fallback-used flag and fallback reason
full-inference rate versus fallback rate by horizon
fixed-confidence persistence diagnostic across horizons and origins
stale-forecast recurrence diagnostic
long-horizon UNKNOWN persistence diagnostic
proof that agreement is independently calculated rather than copied
operator UI remains display-only and inference-free
```

Acceptance is based on traceable upstream execution evidence, not on forcing labels or confidence values to differ.

### RW-MR-003B — MR-F9 shadow promotion evidence and human-gated review

```text
status=open
parent=RW-MR-003
blocking_gate=MARKET_REGIME_READY_FOR_NEXT_FAMILY
owner_phase=MR-F9
may_be_skipped=false
```

Minimum current proposal policy:

```text
minimum_observed_slots=30
minimum_coverage_rate=0.20
minimum_accuracy_delta=0.02
maximum_brier_regression=0.01
maximum_ece_regression=0.02
maximum_unknown_rate_increase=0.05
```

Required outcomes:

```text
winner, tie, or insufficient-evidence proposal
condition-specific evidence
calibration and risk regression checks
active rollback point
human approval required
auto-promotion forbidden
live parameter apply forbidden
separately guarded activation change if approval is later granted
```

Development activity alone does not promote a candidate. Only mature OOS evidence can create a promotion proposal, and that proposal is not runtime activation.

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
blocked_by=RW-MR-003,RW-MR-003A,RW-MR-003B,RW-MR-004,RW-MR-005
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

### Deferred-work ownership crosswalk

Earlier phase documents contain deferred wording that must not become unnamed work. The canonical ownership is:

```text
changing or promoting card confidence = RW-MR-NB-001, owner MR-F9 activation review
changing UNKNOWN / 15% policy = RW-MR-005 family-wide contract hardening unless separately promoted to a named blocking item
multiple parameter-set generation and comparison = RW-MR-002
review_request / review_note / review_link persistence = RW-MR-003
same-run linkage across forecast, calibration, scorecard, and review evidence = RW-MR-003 and RW-MR-005 continuity guard
family-neutral consumer contract and parent naming reconciliation = RW-MR-004
operator UI stale-test baseline repair = RW-MR-005 full-suite closeout prerequisite
warning scorecard persistence = RW-MR-003 when used as review evidence; otherwise RW-MR-005 contract audit
price_structure signal-generation enrichment = non-blocking feature research; must receive a stable ID before implementation
additional feature enrichment or ensemble research = non-blocking research; must receive a stable ID before implementation
```

MR-F8-specific discovered risks were dispositioned at closeout:

```text
candidate-layer identity and exactly-two comparison contract = accepted under RW-MR-002
origin-feature candidate-count validation = accepted under RW-MR-002
unknown versus abstention semantics = comparison contract accepted; evidence maturity continues in RW-MR-003
winner/tie/insufficient decision contract = accepted under RW-MR-002
D-hot comparison artifact discovery and bounded read-only observation = accepted under RW-MR-002
independent horizon-execution proof and fallback diagnostics = RW-MR-003A
promotion maturity and human-gated review = RW-MR-003B
```

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
