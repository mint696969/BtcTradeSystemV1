# path: ./gpt_room/STATUS.md
# desc: Current cross-thread project status handoff for BTC-TS.
# BTC-TS Project Status

## Current Baseline

- Active branch: `docs/phase2-handoff-sync`
- Current HEAD: `23660311`
- Current gate: `MR_F7_CONFIDENCE_CALIBRATION_ACCEPTED`
- Next gate: `MR_F8_SHADOW_MODEL_AND_PARAMETER_SET_COMPARISON`

## MR-F7 Final Status

- Calibration dataset/context/OOS/maturity: accepted
- Hierarchical estimator, shrinkage, caps, fallback, diagnostics: accepted
- Forecast contract projection: accepted
- Operator read-model separation: accepted
- Full source/flag contribution trace ledger: accepted
- Evidence readiness contract: accepted
- D-hot complete read-only audit: accepted
- Runtime calibrated-probability claim: disabled
- Runtime card-confidence replacement: disabled
- Detailed source/flag fit: evidence accumulation pending under `RW-MR-NB-001`

## D-hot Evidence Checkpoint

- Outcome rows: 37,248
- Matched outcome rows: 37,248
- Unmatched outcome rows: 0
- Trusted/evaluable coarse rows: 36,360
- Full contribution history rows: 0
- Detailed source/flag eligible rows: 0
- Input complete: true
- Reader failures: 0

## Test Checkpoint

- Prediction full: 288 passed
- MarketRegime full: 404 passed
- Operator UI full: 1230 passed
- MR-F7 evidence once focused: 5 passed
- MR-F7 readiness connected: 12 passed
- `git diff --cached --check`: passed

## Accepted Rollback Chain

- `6487a117` MR-F7 dataset foundation
- `8737655b` MR-F7 estimator
- `615c501d` MR-F7 projection
- `b1020269` MR-F7 source/flag contribution trace
- `c708ada0` MR-F7 evidence readiness
- `23660311` MR-F7 evidence audit

## Safety Position

- No broker private API access
- No AutoTrade trigger or order submission
- No runtime calibration fit
- No card-confidence replacement
- No auto-promotion or live parameter apply
- No scheduler registration
- No D-hot mutation by MR-F7 closeout

## Next Recommended Work

1. Commit MR-F7 closeout and specification synchronization.
2. Start MR-F8 shadow model and parameter-set comparison over identical windows and sources.
3. Keep detailed source/flag activation in the MR-F9 evidence loop until mature enriched-trace outcomes exist.
