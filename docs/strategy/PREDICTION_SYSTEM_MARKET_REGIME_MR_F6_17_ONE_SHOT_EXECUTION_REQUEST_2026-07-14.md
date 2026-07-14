# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_17_ONE_SHOT_EXECUTION_REQUEST_2026-07-14.md
# desc: Defines MR-F6.17 immutable human-review request construction without writer execution.

# Prediction System MarketRegime MR-F6.17 One-shot Execution Request

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Responsibility

MR-F6.17 converts one approved MR-F6.16 preflight into a deterministic human-review request bound to:

```text
prediction origin
feature snapshot
exact shadow candidate and origin-feature parameter set
seven bundle IDs in canonical horizon order
write-plan bundle IDs in deterministic writer-sort order
write-plan dedupe key
writer ID, writer contract version, and writer schema version
append-only artifact destination
operator approval ID, requested-at, and expires-at
preflight execution timestamp
reviewer IDs and review timestamp
```

The request hash covers these identities, canonical target horizons, forecast parameter-set IDs, both bundle-ID orderings, every review checklist flag, `review_complete`, request readiness, blockers, and one-shot request state. The horizon-facing bundle list and writer-plan bundle list may have different deterministic orders, but must contain the exact same unique IDs. Changing the batch, destination, candidate, approval, reviewer, review result, blocker state, or request time changes the request ID. This hash contract is schema v4.

## Human review checklist

```text
preflight reviewed
bundle identity reviewed
destination reviewed
duplicate prevention reviewed
append-only behavior reviewed
canonical isolation reviewed
one-shot scope reviewed
```

Incomplete review produces a blocked request. Request construction enforces `preflight_executed_at <= reviewed_at <= requested_at`; the request timestamp must be inside the active approval window, so review-window validity follows from the ordered chain without a duplicate review-window branch.

## Execution boundary

A complete request means only that a separate execution step may be considered. This artifact does not supply the writer's `enabled=True` or `once=True` acknowledgements and cannot authorize execution by itself.

```text
execution_authorized_by_this_artifact=false
enabled_acknowledgement_present=false
once_acknowledgement_present=false
writer_imported=false
writer_invoked=false
execution_performed=false
writes_dhot=false
scheduler_enabled=false
counts_as_real_shadow_evidence=false
candidate_selection_performed=false
live_parameter_apply_allowed=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
```

MR-F6.18 is a separate pure human-approved execution boundary. It reconfirms the request hash, active approval, empty/conflict-free destination, and explicit `enabled` and `once` acknowledgements, but exposes no writer command and performs no execution.
