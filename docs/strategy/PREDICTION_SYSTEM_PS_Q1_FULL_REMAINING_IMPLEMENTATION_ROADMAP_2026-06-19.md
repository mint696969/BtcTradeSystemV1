# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q1_FULL_REMAINING_IMPLEMENTATION_ROADMAP_2026-06-19.md
# desc: Full remaining Prediction System implementation roadmap and next-thread start gate after PS-P12.

# Prediction System PS-Q1 full remaining implementation roadmap / start gate

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-Q1 corrects and closes the current thread context before starting the remaining Prediction System implementation work in the next thread.

The intended remaining roadmap is not limited to PS-P12 evaluation/calibration. The target is the full Prediction System implementation quality needed for:

```text
WarRoom tab read-only prediction display.
Prediction outputs that are high quality enough to become future AutoTrade trigger candidates.
Other information-source acquisition / ingestion coverage described in the Prediction System standalone roadmap.
Scenario Prediction Core strengthening beyond lite/basic behavior.
Replay/evaluation/calibration evidence quality sufficient to support future human-reviewed production calibration design.
```

## Corrected interpretation

The phrase "Prediction System roadmap remaining tasks" means the remaining work required to reach a usable Prediction System, not just the PS-P evaluation/calibration line.

Correct target:

```text
Build Prediction System to a level where WarRoom can display current predictions and supporting evidence.
Build Prediction System to a level where AutoTrade may later consume prediction outputs as trigger candidates after a separate explicit return gate.
Implement or connect the information-source coverage needed by the roadmap, while preserving Collector / Prediction / AutoTrade separation.
```

Important boundary:

```text
"Trigger candidate quality" does not mean enabling AutoTrade triggers now.
TriggerEligibility remains blocked until a separate human-reviewed AutoTrade return gate.
```

## Current completed state after PS-P12

```text
Standalone Prediction System runner exists.
All 11 rule_based_v0 families emit outputs.
Scenario Core lite exists.
Scenario trace detail and lightweight evidence refs exist.
Lifetime refresh-lite and revision-lite exist.
Provider reliability registry skeleton exists and is conservative/context-only.
Feature-depth contracts exist and are conservative/context-only.
scenario_review_summary exists as top-level review-only digest.
PredictionEvaluationReport exists as offline/replay-only in-memory evidence.
PredictionCalibrationReview exists as advisory-only in-memory review.
PS-P12 stopped before production calibration behavior changes.
```

## Remaining implementation work packages

### PS-Q2: source / artifact input coverage start

Goal:

```text
Start implementation from the data/input side.
Define and guard which external/public information sources are represented as Prediction System input artifacts or explicit contracts.
```

Coverage target:

```text
bitFlyer Spot / FX ticker, trades, board-derived summaries.
OHLCV across required horizons including 10m mapping or support.
Global spot venue references.
Global derivatives / funding / basis / liquidation context where available.
Macro / session / calendar context.
Exchange incident / news / status context.
Provider/source reliability state for every non-local source.
```

Boundary:

```text
Prediction core must not import Collector runtime workers or own collection loops.
Data acquisition should be separated through Collector-owned artifacts, explicit provider snapshots, or portable input contracts.
```

### PS-Q3: provider reliability and source quality hardening

Goal:

```text
Turn provider reliability from skeleton/context-only into a practical read-only quality gate for Prediction System inputs.
```

Required behavior:

```text
freshness / stale state
missing window count
gap count
outage / rate-limit state
trust / usable state
blockers and warnings
per-source contribution visibility
```

### PS-Q4: feature construction from provided artifacts

Goal:

```text
Strengthen weak/proxy-only families using provided source artifacts without making feature-depth the primary direction owner prematurely.
```

Target families:

```text
liquidity_execution_quality
breakout_false_break
algorithmic_participant_footprint
cross_venue_confirmation
opportunity_participation
macro_risk_context
```

Feature targets:

```text
orderbook spread/depth/thin-book/liquidity deterioration
tradeflow pressure / participation / absorption context
cross-venue divergence / lead-lag context
derivatives/funding/basis/liquidation context
macro/session/event risk context
incident/status context
```

### PS-Q5: Scenario Prediction Core strengthening

Goal:

```text
Move beyond Scenario Core lite toward a real scenario prediction core.
```

Missing or weak fields to strengthen:

```text
continuation_vs_reversal_balance
turning_point_risk
invalidation_state
rewrite_state
scenario_switch_hint
evidence_weighting_summary
evidence_conflict_state
what_to_watch_next
refresh_required reasoning
previous prediction diff / revision explanation
```

### PS-Q6: replay-data quality guard / evidence quality gate

Goal:

```text
Continue with read-only replay/evaluation quality guards before any production calibration behavior.
```

Required checks:

```text
not_evaluable skew by family / horizon / confidence / caution
missing outcome skew
record/outcome key matching quality
evaluation summary schema drift
calibration review missing-summary behavior
confidence/caution candidate evidence quality
```

Boundary:

```text
No score/confidence/caution/family/TriggerEligibility changes.
No AutoTrade decision append.
No runtime writes from Prediction System runner.
```

### PS-Q7: WarRoom prediction tab read-only display path

Goal:

```text
Expose Prediction System outputs to WarRoom as a read-only prediction tab or packet.
```

Display targets:

```text
current scenario
horizon group summaries
family outputs
evidence support/conflicts
source quality / provider reliability warnings
scenario invalidation / rewrite / watch-next
forecast/evaluation/calibration review status
```

Boundary:

```text
No command buttons.
No forms/toggles that mutate state.
No mode/grant behavior.
No AutoTrade decision append.
No broker/private API.
WarRoom displays Prediction System output; it does not recalculate prediction meaning.
```

### PS-Q8: AutoTrade trigger-candidate contract readiness

Goal:

```text
Define the contract by which AutoTrade may later consume Prediction System outputs as trigger candidates.
```

Required state:

```text
trigger candidate is advisory until return gate.
TriggerEligibility remains blocked by default.
No AutoTrade execution or append is enabled.
No command ledger append is enabled.
All broker/mode/grant flags remain false.
```

### PS-Q9: explicit AutoTrade return gate / trigger integration design

Goal:

```text
Only after PS-Q2 through PS-Q8 are stable, design any AutoTrade trigger integration separately with human review.
```

Required before implementation:

```text
human approval
exact trigger semantics
safety/rollback plan
guard coverage
no-live-trading gate
separation from broker/private API
clear failure/blocker behavior
```

## Recommended next-thread start

Start next thread from:

```text
PS-Q2: source / artifact input coverage start
```

Why PS-Q2 first:

```text
WarRoom display and trigger-candidate quality depend on reliable input coverage.
Scenario Core strengthening also depends on better source artifacts and source-quality state.
Replay/calibration quality depends on knowing which records and outcomes are trustworthy.
```

Do not start next thread by enabling AutoTrade triggers.
Do not start next thread by changing score/confidence/caution production behavior.

## Next-thread first reads

```text
docs/strategy/PREDICTION_SYSTEM_PS_Q1_FULL_REMAINING_IMPLEMENTATION_ROADMAP_2026-06-19.md
docs/strategy/PREDICTION_SYSTEM_STANDALONE_DESIGN_AND_ROADMAP_BTC_BITFLYER_2026-06-19.md
docs/strategy/PREDICTION_SYSTEM_CURRENT_CODE_GAP_INDEX_BTC_BITFLYER_2026-06-19.md
docs/strategy/PREDICTION_SYSTEM_PS_P12_STOP_REVIEW_CHECKPOINT_2026-06-19.md
tmp/gpt_room/memory/handoffs/2026-06-19_prediction_system_ps_p12_stop_review_checkpoint_committed_handoff.md
btcts_next/src/btcts/prediction/system.py
btcts_next/src/btcts/prediction/system_contract.py
btcts_next/src/btcts/prediction/source_quality.py
btcts_next/src/btcts/prediction/feature_depth.py
```

## Hard boundaries to preserve

```text
No score changes unless explicitly designed and human-reviewed later.
No confidence behavior changes unless explicitly designed and human-reviewed later.
No caution behavior changes unless explicitly designed and human-reviewed later.
No family label changes unless explicitly designed and human-reviewed later.
No TriggerEligibility enablement.
No AutoTrade trigger enablement in PS-Q2.
No live trading.
No broker/private API import.
No AutoTrade decision append.
No command ledger append.
No mode/grant behavior.
No Collector runtime import into Prediction core.
No Prediction core ownership of collection loops.
No runtime artifact writes from the Prediction System runner.
```

## Thread closing decision

```text
This thread should close by committing PS-Q1.
Next thread should start implementation from PS-Q2 source / artifact input coverage.
```

## PS-Q1 production behavior

```text
No production code changed.
No tests alter production behavior.
This slice is documentation and guard only.
```
