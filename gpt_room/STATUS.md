# path: ./gpt_room/STATUS.md
# desc: Current cross-thread project status handoff for BTC-TS.
# BTC-TS Project Status

## Current Baseline

- Active branch: `docs/phase2-handoff-sync`
- Current HEAD: `bffb802a`
- Current gate: `MR_F5_OPERATIONAL_EVIDENCE_AND_CANONICAL_MIGRATION_REVIEW_ACCEPTED`
- Next gate: `MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON`

## MR-F5 Final Status

- MR-F5 implementation: complete
- 24-hour operational evidence window: complete
- Original origin batches: 20
- Supplemental origin batches: 2
- Selected evaluation rows: 288
- Scored rows: 282
- Unresolved audit rows: 6
- Invalidated rows: 0
- All 14 candidate/horizon cells have at least 20 scored rows
- Candidate comparison: ready
- Canonical migration review: complete
- Canonical promotion: deferred
- Live parameter apply: false
- Scheduler registration: false

## Model Findings Carried Forward

- Baseline and conservative parameter sets did not separate in the accepted window.
- 43,200-second and 86,400-second horizons were weak and must not be promoted canonically.
- MR-F6 must compare the accepted MR-F5 path against mandatory simple baselines over identical evidence windows.

## Test Checkpoint

- Future shadow adapter focused: 8 passed
- Future baseline focused: 9 passed
- MarketRegime full: 192 passed
- Prediction full: 461 passed
- Operator UI full: 1230 passed
- Operator UI post-header focused: 58 passed
- `git diff --check`: passed

## Recent Commits

- `bffb802a` docs(prediction): close MR-F5 operational evidence gate
- `05756700` fix(prediction): abstain on invalid MR-F5 regime scores
- `11da64fa` feat(operator-ui): finalize Health telemetry views and UI readability

## Safety Position

- MR-F5 evidence remains isolated under the future-shadow namespace.
- No canonical forecast replacement occurred.
- No broker-send, autotrade trigger, or order-submission path was enabled.
- D-hot operational evidence remains outside Git.

## Next Recommended Work

1. Start MR-F6 mandatory simple-baseline comparison in a new thread.
2. Reuse the accepted MR-F5 evidence contract without changing targets or outcome rules.
3. Keep canonical promotion disabled until later comparison and calibration gates are accepted.
