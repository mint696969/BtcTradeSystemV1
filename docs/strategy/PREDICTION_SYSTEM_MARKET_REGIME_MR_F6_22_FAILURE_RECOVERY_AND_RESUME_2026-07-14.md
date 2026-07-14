# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_22_FAILURE_RECOVERY_AND_RESUME_2026-07-14.md
# desc: Canonical MR-F6.22 recovery/resume disposition, hash preservation, and non-retry safety boundary.

# Prediction System MarketRegime MR-F6.22 Failure Recovery and Resume

Updated: 2026-07-14 JST
Status: accepted implementation checkpoint
Gate: MR_F6_22_FAILURE_RECOVERY_AND_RESUME_ACCEPTED

## 1. Responsibility

MR-F6.22 consumes one immutable MR-F6.21 duplicate-safe receipt and produces one immutable recovery/resume decision.

```text
MR-F6.21 duplicate-safe receipt
  + externally confirmed receipt hash
  + decided_at
  + optional failure code
  + optional failure-detail hash
  -> MR-F6.22 recovery/resume decision
```

The decision classifies whether later human-gated work may be considered. It does not retry, resume, invoke the writer, read or write the filesystem, or modify D-hot.

## 2. State-preserving dispositions

### absent

```text
recovery_disposition=human_gated_resume_candidate
resume_candidate=true
terminal=false
```

Required actions:

```text
reconfirm_human_gate
rebuild_execution_context_from_bound_hashes
reobserve_destination_before_any_execution
```

This is only a candidate for a separate execution path. The decision artifact itself does not authorize resume.

### already_satisfied

```text
recovery_disposition=terminal_success_equivalent
resume_candidate=false
terminal=true
```

The existing duplicate-safe receipt is returned as success-equivalent evidence. No rewrite, overwrite, or replayed writer call is allowed.

### conflicting

```text
recovery_disposition=terminal_conflict_blocked
resume_candidate=false
terminal=true
```

Explicit conflict resolution is required. The state is never silently reclassified as `absent`.

### inconsistent

```text
recovery_disposition=reobservation_required
resume_candidate=false
terminal=false
```

Required actions:

```text
repair_or_replace_observation_source
reobserve_destination
build_new_duplicate_safe_receipt
```

The state is never silently reclassified as `absent`.

## 3. Bound identity and failure context

The decision hash binds:

```text
receipt ID and externally confirmed receipt hash
adapter-result hash
execution-plan hash
artifact relative path
dedupe key
expected artifact hash
observed artifact hash
destination state
decided_at
optional failure code
optional failure-detail SHA-256
recovery disposition
resume-candidate and terminal flags
preserved blockers
recovery actions
```

A failure-detail hash is valid only when a non-empty failure code is present. Different failure details produce different decision hashes without exposing raw error payloads.

## 4. Revalidation

MR-F6.22 fails closed unless:

```text
receipt schema and artifact kind match MR-F6.21
external expected receipt hash matches
receipt ID matches the receipt hash
decided_at is canonical UTC and not before observed_at
receipt_is_authorization=false
all writer, execution, filesystem, D-hot, scheduler, promotion, and replacement flags remain false
human_gate_required=true
failure code and failure-detail hash are structurally valid
receipt destination state is one of the four accepted MR-F6.21 states
```

Original receipt blockers are preserved and deduplicated with state-level blockers.

## 5. Resume meaning

`resume_candidate=true` means only that a separate human-gated path may reconstruct context and re-observe the destination.

```text
resume_authorized_by_this_artifact=false
automatic_retry_allowed=false
```

MR-F6.22 does not include a retry loop, backoff policy, scheduler hook, CLI, writer API, root path, or filesystem operation.

## 6. Safety boundary

For every disposition:

```text
automatic_retry_allowed=false
resume_authorized_by_this_artifact=false
conflicting_state_reclassified_as_absent=false
inconsistent_state_reclassified_as_absent=false
receipt_hash_preserved=true
writer_write_function_imported=false
writer_write_function_invoked=false
writer_invoked=false
execution_performed=false
filesystem_read_performed=false
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

## 7. Acceptance evidence

```text
MR-F6.22A import boundary=passed
MR-F6.22A connected MR-F6.21 suite=13 passed
MR-F6.22B focused recovery/resume suite=11 passed
MR-F6.22B connected MR-F6.21/MR-F6.22 suite=24 passed
MR-F6.22B MarketRegime suite=355 passed
py_compile=passed
git diff --check=passed
automatic retry performed=false
writer invoked=false
filesystem read performed=false
filesystem write performed=false
D-hot modified=false
scheduler enabled=false
```

## 8. Handoff to MR-F6.23

MR-F6.23 must bind the accepted execution chain into immutable audit and replay evidence.

At minimum it must preserve:

```text
execution-plan hash
adapter-result hash
receipt hash
recovery/resume decision hash
artifact path and dedupe key
expected and observed artifact hashes
destination state
recovery disposition
original blockers and recovery actions
failure code and failure-detail hash
all non-execution safety flags
```

Replay must verify identity and decision reproduction without invoking the writer, reading or writing D-hot, enabling a scheduler, or treating the evidence as real shadow evidence.

MR-F6.22 does not satisfy `MARKET_REGIME_READY_FOR_NEXT_FAMILY`. MR-F6.23, MR-F6.24, and MR-F6 closeout remain mandatory.
