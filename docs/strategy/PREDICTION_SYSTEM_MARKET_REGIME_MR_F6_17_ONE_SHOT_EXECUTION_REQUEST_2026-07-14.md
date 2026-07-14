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
append-only artifact destination
operator approval ID, requested-at, and expires-at
preflight execution timestamp
reviewer IDs and review timestamp
```

The request hash covers these identities. The horizon-facing bundle list and writer-plan bundle list may have different deterministic orders, but must contain the exact same unique IDs. Changing the batch, destination, candidate, approval, reviewer, or request time changes the request ID.

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

Incomplete review produces a blocked request. Request construction also revalidates that both the original preflight timestamp and the request timestamp are inside the same active approval window; a stale preflight cannot be converted into a ready request after approval expiry.

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

MR-F6.18 must be a separate human-approved execution boundary. It may expose a once-only execution command only after reconfirming the request hash, active approval, empty/conflict-free destination, and explicit `enabled` and `once` acknowledgements.
