# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_7_SHADOW_EVALUATION_AGGREGATION_AND_CANDIDATE_COMPARISON_2026-07-12.md
# desc: MR-F5.7 pure aggregation and human-gated comparison of immutable shadow future-evaluation rows.

# Prediction System MarketRegime MR-F5.7 Shadow Evaluation Aggregation and Candidate Comparison

Updated: 2026-07-12 JST
Status: implementation slice prepared

## Scoring

```text
CORRECT=1.0
PARTIAL=0.5
INCORRECT=0.0
UNRESOLVED=not scored
INVALIDATED=not scored
ABSTAINED=not scored
```

Comparison is ready only when at least two distinct `(model_id, logic_version, parameter_set_id)` candidates meet the minimum scored-sample threshold.

## Boundary

```text
pure_function=true
immutable_output=true
writes_dhot=false
ledger_append=false
parameter_auto_promotion=false
live_parameter_apply=false
human_gate_required=true
canonical_future_label_replacement=false
ui_change=false
```

The ranking is evidence for human review only. It does not produce promotion candidates and does not mutate any parameter set.
