# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_13_EVIDENCE_SUFFICIENCY_AND_SHADOW_RANKING_2026-07-14.md
# desc: Defines MR-F6.13 explicit evidence sufficiency and tie-preserving deterministic shadow ranking.

# Prediction System MarketRegime MR-F6.13 Evidence Sufficiency and Shadow Ranking

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Ranking scope

Origin-feature candidates affect only:

```text
simple_ma_slope
simple_volatility_threshold
```

The other four mandatory baselines are identical across all eight candidates. They are preserved in MR-F6.12 audit output but excluded from ranking metrics to avoid diluting candidate differences.

## Explicit sufficiency policy

The ranking function requires an explicit policy containing:

```text
policy_id
minimum_evaluation_slots
minimum_observed_slots_per_baseline
minimum_scored_slots_per_baseline
minimum_coverage_rate
```

No production default is introduced in this slice.

A candidate is comparable only when both parameter-sensitive baselines meet every threshold. Before sufficiency is evaluated, MR-F6.13 revalidates the canonical eight-candidate registry, the complete six-baseline matrix, count ordering, and recalculates coverage, accuracy, and unknown rate from integer counts. Aggregated rates are not trusted without this arithmetic check.

## Deterministic ranking

Comparable candidates are grouped by the following descending metric key:

```text
mean accuracy across the two sensitive baselines
minimum accuracy across the two sensitive baselines
mean coverage across the two sensitive baselines
minimum scored-slot count
```

Exact metric ties remain one rank group. Candidate ID is used only to provide stable display order inside a tie and never to claim superiority.

## Boundary

```text
winner_declared=false
selection_performed=false
selected_candidate_id=null
promotion_candidates=[]
human_gate_required=true
writes_dhot=false
scheduler_enabled=false
live_parameter_apply_allowed=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
```

MR-F6.14 must define and collect sufficient same-window operational evidence before any human review can consider a candidate. Ranking output alone is not promotion evidence.
