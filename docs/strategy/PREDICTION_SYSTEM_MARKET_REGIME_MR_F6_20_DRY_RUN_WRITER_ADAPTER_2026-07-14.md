# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_20_DRY_RUN_WRITER_ADAPTER_2026-07-14.md
# desc: Canonical MR-F6.20 dry-run writer-adapter responsibility, safety boundary, and acceptance evidence.

# Prediction System MarketRegime MR-F6.20 Dry-run Writer Adapter

Updated: 2026-07-14 JST
Status: accepted implementation checkpoint
Gate: MR_F6_20_DRY_RUN_WRITER_INVOCATION_ADAPTER_ACCEPTED

## 1. Responsibility

MR-F6.20 consumes one immutable MR-F6.19 execution plan and re-presents the matching writer plan, approval, and exact seven origin-evidence bundles to the public `preflight_origin_evidence_write()` contract.

The adapter is the only MR-F6.20 layer that knows the writer preflight API.

```text
MR-F6.17 immutable execution request
  -> MR-F6.18 pure execution boundary
  -> MR-F6.19 immutable dry-run execution plan
  -> MR-F6.20 public writer preflight adapter
```

MR-F6.20 does not import or call `write_origin_evidence_once()`.

## 2. Inputs and bound identity

```text
execution plan
externally confirmed execution-plan hash
writer plan
operator approval
exact seven origin-evidence bundles
executed_at
externally confirmed writer ID
externally confirmed writer contract version
```

MR-F6.19 schema v2 preserves both `approval_requested_at` and `approval_expires_at`. MR-F6.20 therefore compares the supplied approval object against the complete approval window frozen in the execution plan.

## 3. Revalidation

The adapter fails closed unless all of the following remain true:

```text
execution-plan schema and artifact kind match
execution-plan hash recomputes exactly
execution-plan ID matches its hash
external expected execution-plan hash matches
plan is ready, dry-run-only, and blocker-free
plan still carries all non-execution safety flags
writer schema, writer ID, and writer contract version match
approval ID, requested-at, expires-at, and writer scope match
planned_at <= executed_at < approval_expires_at
writer-plan row count and dedupe key match
writer-order bundle IDs match exactly
runtime bundle set matches the frozen seven-bundle identity
public preflight result path matches the frozen destination
public preflight result dedupe key, approval ID, and row count match
preflight_only=true
write_allowed=true
would_write=false
```

`write_allowed=true` is only the result of the writer's pure preflight validation. It is not permission granted by the adapter and does not imply that a filesystem write occurred.

## 4. Result artifact

The adapter returns an immutable result containing:

```text
adapter result ID and hash
execution-plan ID and hash
executed_at
writer identity
approval ID
destination artifact path
dedupe key
canonical bundle IDs and row count
immutable preflight snapshot and snapshot hash
```

The result is deterministic for identical inputs.

## 5. Safety boundary

Even when the public preflight contract succeeds:

```text
dry_run_contract_exercised=true
writer_preflight_invoked=true
writer_write_function_imported=false
writer_write_function_invoked=false
writer_invoked=false
execution_performed=false
filesystem_write_performed=false
writes_dhot=false
scheduler_enabled=false
counts_as_real_shadow_evidence=false
candidate_selection_performed=false
live_parameter_apply_allowed=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
human_gate_required=true
```

`writer_preflight_invoked=true` means only that the pure public preflight function was exercised. `writer_invoked=false` means the append-only write path was not invoked.

The adapter exposes no CLI, scheduler hook, root-path parameter, or filesystem operation.

## 6. Acceptance evidence

```text
MR-F6.20A execution-plan schema-v2 focused suite=9 passed
MR-F6.20A request/boundary connected suite=23 passed
MR-F6.20A MarketRegime suite=323 passed
MR-F6.20B writer/plan connected suite=17 passed
MR-F6.20C adapter focused suite=8 passed
MR-F6.20C connected MR-F6 suite=25 passed
MR-F6.20C MarketRegime suite=331 passed
py_compile=passed
git diff --check=passed
write function imported=false
write function invoked=false
filesystem write performed=false
D-hot modified=false
scheduler enabled=false
```

## 7. Parallel-work boundary

Acceptance of MR-F6.20 permits MR-F7 confidence-calibration work to begin in parallel because prediction calibration and execution-safety hardening have separate responsibilities.

```text
mr_f6_20_accepted=true
mr_f7_may_start_in_parallel=true
mr_f6_21_through_mr_f6_24_remain_mandatory=true
mr_f6_closeout_may_not_be_skipped=true
market_regime_ready_for_next_family=false
trend_bias_family_still_blocked=true
shared_contract_changes_require_cross-track_review=true
```

MR-F6.20 does not satisfy `MARKET_REGIME_READY_FOR_NEXT_FAMILY`. The next implementation gate on the MR-F6 execution-safety track is MR-F6.21 idempotency and duplicate-safe receipt.
