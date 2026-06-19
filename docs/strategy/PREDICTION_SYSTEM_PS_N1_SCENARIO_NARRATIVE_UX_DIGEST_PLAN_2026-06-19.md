# path: ./docs/strategy/PREDICTION_SYSTEM_PS_N1_SCENARIO_NARRATIVE_UX_DIGEST_PLAN_2026-06-19.md
# desc: Plan for PS-N1 scenario narrative / UX digest refinement using existing Prediction System outputs only.

# Prediction System PS-N1 scenario narrative / UX digest plan

Updated: 2026-06-19 JST
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync

## Purpose

PS-N1 starts the next line after PS-F15.

The goal is to improve review-facing scenario narrative / UX digest clarity using already-emitted Prediction System outputs only.

This plan intentionally does not change production behavior. It defines the intended tiny production slice shape before any code changes.

## Inputs already available

```text
family_labels
scenario_lite
scenario_trace_detail
evidence_refs
lifetime refresh state
revision_summary
feature-depth context version markers
provider reliability summary
forecast_batch record count
inference_bundle family/horizon coverage
```

## Problem to solve

Current Prediction System output already contains useful data, but the top-level review surface is still scattered across:

```text
PredictionSystemResult.human_narrative_ja
PredictionSystemResult.gpt_review_digest
ScenarioCoreOutput.gpt_review_digest
HorizonGroupSummary.gpt_review_digest
HorizonGroupSummary.evidence_refs
PredictionLifetime refresh fields
```

PS-N1 should make the review-facing summary easier to consume without changing scores, labels, scenario logic, trigger eligibility, or execution behavior.

## Candidate production target

Add a deterministic review-only digest under `PredictionSystemResult.gpt_review_digest`, for example:

```text
scenario_review_summary: {
  version: ps_n1.v1,
  review_only: true,
  primary_story: ...,
  scenario_health: ...,
  evidence_support: [...],
  evidence_conflicts: [...],
  watch_next: [...],
  refresh_or_rewrite: {...},
  context_versions: {...},
  output_counts: {...},
  boundaries: {...}
}
```

This target should be built from existing fields only:

```text
scenario_core.current_regime_state
scenario_core.current_hypothesis_health
scenario_core.turning_point_risk
scenario_core.evidence_conflict_state
scenario_core.scenario_switch_hint
scenario_core.invalidation_state
scenario_core.rewrite_state
scenario_core.gpt_review_digest
scenario_core.outlooks[*].gpt_review_digest.scenario_lite
scenario_core.outlooks[*].evidence_refs
scenario_core.outlooks[*].lifetime
PredictionSystemResult.gpt_review_digest feature-depth version markers
PredictionSystemResult.forecast_batch.record_count
PredictionSystemResult.inference_bundle coverage fields
```

## Required invariants

```text
No score changes.
No family label changes.
No TriggerEligibility enablement.
No live collection.
No Collector runtime import.
No AutoTrade import.
No broker/private API import.
No external API call.
No artifact/runtime write.
No AutoTrade decision append.
No command ledger append.
No mode/grant behavior.
No primary-direction ownership from feature-depth context.
```

## Required guard shape for implementation slice

If a later PS-N1 implementation patch touches production code, it must add a focused guard that checks:

```text
scenario_review_summary.version == ps_n1.v1
scenario_review_summary.review_only is True
scenario_review_summary.boundaries.read_only is True
scenario_review_summary.boundaries.non_executing is True
scenario_review_summary.boundaries.trigger_eligibility_state == blocked
scenario_review_summary.context_versions keeps ps_e2.v1 / ps_e3.v1 / ps_e4.v1 when feature-depth snapshot is supplied
scenario_review_summary.watch_next is non-empty
scenario_review_summary.refresh_or_rewrite contains invalidation/rewrite/refresh fields
existing output count remains unchanged
existing forecast_batch record_count remains unchanged
existing PS-G-lite, PS-F12, PS-F14, and PS-F15 guards still pass
```

## Non-goals

```text
Do not change rule_based_v0 family scoring.
Do not change scenario_lite scoring/weighting.
Do not change PredictionOutput contracts.
Do not add Collector wiring.
Do not add AutoTrade wiring.
Do not persist or append runtime artifacts.
Do not convert feature-depth context into an entry trigger.
```

## Recommended next slice

```text
PS-N2: implement scenario_review_summary as top-level review-only digest field
```

Recommended implementation boundary:

```text
One helper in system.py, called near build_prediction_system_result return construction.
No system_contract change needed if gpt_review_digest remains the carrier.
One focused guard for PS-N2 narrative/digest shape.
Run PS-G-lite, PS-F12, PS-F14, PS-F15, and PS-N1 guards.
```

## PS-N1 production behavior

```text
No production code changed.
No tests alter production behavior.
This plan is documentation and guard only.
```
