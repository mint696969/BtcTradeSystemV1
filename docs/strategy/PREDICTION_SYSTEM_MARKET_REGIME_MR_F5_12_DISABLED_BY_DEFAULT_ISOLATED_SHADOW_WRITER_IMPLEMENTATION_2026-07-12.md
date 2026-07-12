# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_12_DISABLED_BY_DEFAULT_ISOLATED_SHADOW_WRITER_IMPLEMENTATION_2026-07-12.md
# desc: MR-F5.12 disabled-by-default isolated shadow writer implementation boundary.

# Prediction System MarketRegime MR-F5.12 Disabled-by-default Isolated Shadow Writer Implementation

Updated: 2026-07-12 JST
Status: implementation slice prepared

## Scope

Implement a callable once-only writer behind the accepted MR-F5.10 approval boundary and MR-F5.11 dry-run plan. The implementation has no CLI, scheduler registration, producer hook, UI hook, or implicit runtime root.

## Artifact layout

```text
prediction/market_regime/future_shadow/date=YYYY-MM-DD/batch-<dedupe-key>.json
```

Each batch path is immutable. Under a file lock:

```text
missing artifact -> atomic write
same artifact content -> idempotent duplicate
same dedupe path with different content -> fail closed
```

## Required execution acknowledgements

```text
enabled=true
once=true
approved boundary write_allowed=true
approved boundary decision exact
dry-run plan exact
writer id match
approval id present
row trace/hash set exact
```

## Safety

```text
disabled_by_default=true
no_cli=true
scheduler_enabled=false
writer_registered=false
canonical_isolated=true
append_only=true
atomic_write=true
dedupe_guarded=true
counts_as_real_shadow_evidence=false
parameter_auto_promotion=false
live_parameter_apply=false
ui_change=false
```

This slice implements the writer but does not execute it against D-hot. Fixture-root tests exercise the write path only. Real evidence eligibility remains false until an explicitly approved D-hot execution and MR-F5.13 evidence audit.
