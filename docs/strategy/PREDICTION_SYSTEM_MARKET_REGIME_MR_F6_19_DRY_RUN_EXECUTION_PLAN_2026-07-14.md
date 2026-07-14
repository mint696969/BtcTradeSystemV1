# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_19_DRY_RUN_EXECUTION_PLAN_2026-07-14.md
# desc: Defines MR-F6.19 deterministic immutable dry-run execution planning without writer invocation.

# Prediction System MarketRegime MR-F6.19 Dry-run Execution Plan

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_19_DRY_RUN_EXECUTION_PLAN

## Responsibility

MR-F6.19 converts one ready MR-F6.18 boundary and its matching MR-F6.17 request into one immutable dry-run execution plan.

The plan binds:

```text
request ID and externally confirmed request hash
boundary snapshot hash
planned-at timestamp
writer ID, writer contract version, and writer schema version
approval ID and expiry
append-only destination path
dedupe key
canonical seven horizons
horizon-order bundle IDs
writer-order bundle IDs
forecast parameter-set IDs
enabled and once acknowledgements
absent and conflict-free destination state
```

## Revalidation

```text
request and boundary schemas and kinds
request ID and hash equality across request, boundary, and external confirmation
writer scope equality across request, boundary, and external confirmation
boundary ready with no blockers
both acknowledgements present
boundary remains non-executing and non-writing
planned_at >= boundary evaluated_at
planned_at < approval_expires_at
canonical seven-horizon bundle identity
destination absent and not already satisfied
approval, destination, and dedupe identity equality
```

## Boundary

Even when the plan is ready:

```text
dry_run_only=true
execution_plan_ready=true
execution_authorized_by_this_artifact=false
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

MR-F6.19 imports no writer function, exposes no CLI or scheduler hook, and performs no filesystem or D-hot operation. MR-F6.20 may consume this plan only through a separate dry-run adapter and must revalidate plan identity before exercising the public writer contract.
