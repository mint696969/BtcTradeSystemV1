# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_START_AUDIT_2026-07-16.md
# desc: MR-F9 start audit for repository truth, execution-evidence boundaries, deferred activation, and safety.

# Prediction System MarketRegime MR-F9 Start Audit

Updated: 2026-07-16 JST
Basis HEAD: `52a1fb00`
Current gate: `MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON_ACCEPTED`
Target gate: `MR_F9_OUTCOME_REVIEW_CALIBRATION_EVIDENCE_LOOP`

## Confirmed repository truth

- MR-F8 active/shadow pairing, immutable trace identity, expiry-gated observation polling, outcome joining, and fail-closed proposal policy exist.
- `raw_model_score_or_probability` is defined by MR-F7 as model/scoring output before empirical calibration. It is not automatically a calibrated probability.
- Existing trace identity intentionally excludes raw output and fallback facts. Changing the accepted MR-F5 trace ID would risk breaking MR-F8 artifact compatibility.
- Paired generation is owned by `future_shadow_candidate_pairing.py`; no `future_shadow_pair.py` module exists.
- MR-F9 requires explicit horizon execution proof including raw output semantics, source freshness, abstention, fallback truth, and continuity.

## Resolved design boundary

MR-F9.1A adds a separate immutable execution-evidence contract linked by the accepted `trace_id`.

```text
trace identity = what forecast is this
execution evidence = how was this horizon forecast produced
```

The accepted trace identity remains unchanged. Raw output defaults to `UNSPECIFIED` semantics and may not be treated as probability without an explicit upstream semantic contract. Full inference and fallback fields are mutually exclusive and validated fail-closed.

## Deferred until evidence contract is guarded

- D-hot writing or scheduler registration
- producer-loop integration
- probability-distribution synthesis
- Brier/log-loss activation for rows without probability semantics
- runtime card confidence replacement
- parameter promotion or live activation

## Safety

```text
pure_contract=true
D_hot_write=false
scheduler=false
UI_change=false
broker_private_api=false
AutoTrade=false
order_submission=false
parameter_auto_promotion=false
live_parameter_apply=false
```
