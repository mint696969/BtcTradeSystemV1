# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_15_RUNTIME_TRACE_CAPTURE_AND_TARGET_OBSERVATION_ADAPTER_WIRING_2026-07-12.md
# desc: MR-F5.15 runtime trace capture and target-observation adapter design.

# Prediction System MarketRegime MR-F5.15 Runtime Trace Capture and Target-observation Adapter Wiring

Updated: 2026-07-12 JST
Status: pure runtime bridge prepared

## Scope

Bridge the existing future-shadow packet and target observation dictionaries into exact MR-F5.5 trace identities and trace-id keyed MR-F5.6 evidence inputs.

```text
MarketRegimeFutureShadowPacket
  -> deterministic MR-F5.5 trace tuple

trace-id keyed derived observation
  -> FutureShadowOutcomeEvidence

traces + evidence
  -> MR-F5.14 source-batch producer input
```

## Guards

```text
packet type exact
trace identity deterministic
trace ids unique
packet origin and snapshot preserved
unknown observation trace rejected
observation_available must be bool
observed regime must be valid enum
available observation requires source reference
missing observation keeps bridge not ready
```

## Safety

```text
pure_adapter=true
reads_dhot=false
writes_dhot=false
writer_invoked=false
scheduler_enabled=false
canonical_replacement=false
legacy_outcome_ledger_used=false
parameter_auto_promotion=false
live_parameter_apply=false
ui_change=false
```

This slice does not persist traces, read candles, invoke the writer, or register a runtime loop. It fixes the exact adapter boundary first.
