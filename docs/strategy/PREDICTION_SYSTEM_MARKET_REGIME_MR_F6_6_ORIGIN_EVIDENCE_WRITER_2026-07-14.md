# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_6_ORIGIN_EVIDENCE_WRITER_2026-07-14.md
# desc: Defines the MR-F6.6 disabled approval-gated append-only origin-evidence writer.

# Prediction System MarketRegime MR-F6.6 Origin Evidence Writer

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Scope

Adds a dedicated writer for `future_origin_evidence_bundle` under:

```text
prediction/market_regime/future_origin_evidence/date=YYYY-MM-DD/batch-<dedupe>.json
```

The namespace never uses `latest` and does not overlap canonical artifacts.

## Safety

```text
disabled_by_default=true
explicit once acknowledgement required
operator approval required
append_only=true
historical_backfill_allowed=false
scheduler registration absent
CLI absent
canonical replacement=false
live parameter apply=false
counts_as_real_shadow_evidence=false
```

This slice is tested only against fixture roots. It does not approve or perform a real D-hot write.
