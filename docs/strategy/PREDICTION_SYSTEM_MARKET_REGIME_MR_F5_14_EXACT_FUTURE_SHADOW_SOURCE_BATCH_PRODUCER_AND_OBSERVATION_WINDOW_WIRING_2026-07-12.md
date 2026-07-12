# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_14_EXACT_FUTURE_SHADOW_SOURCE_BATCH_PRODUCER_AND_OBSERVATION_WINDOW_WIRING_2026-07-12.md
# desc: MR-F5.14 exact future-shadow source-batch producer and observation-window design.

# Prediction System MarketRegime MR-F5.14 Exact Future-shadow Source Batch Producer and Observation-window Wiring

Updated: 2026-07-12 JST
Status: pure producer slice prepared

## Scope

Build exact MR-F5.6 evaluation rows only from immutable MR-F5.5 traces and trace-id keyed target observations.

```text
forecast origin -> MR-F5.5 trace identity
target timestamp reached -> observation evidence
trace + evidence -> MR-F5.6 outcome
eligible resolved outcome -> source batch row
```

## Eligibility

Rows are emitted only for:

```text
CORRECT
PARTIAL
INCORRECT
```

The following remain visible in counts but are not emitted as evidence rows:

```text
UNRESOLVED
INVALIDATED
ABSTAINED
```

## Observation-window gate

```text
exact row count >= minimum resolved rows
no trace evidence missing
no unresolved trace remains
```

Only then may `write_approval_candidate=true`. This is not operator approval and does not invoke the MR-F5.12 writer.

## Safety

```text
pure_projection=true
reads_dhot=false
writes_dhot=false
writer_invoked=false
scheduler_enabled=false
canonical_replacement=false
legacy_rows_accepted=false
parameter_auto_promotion=false
live_parameter_apply=false
ui_change=false
```
