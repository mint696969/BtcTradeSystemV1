# path: ./docs/architecture/AUTOTRADE_PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_DESIGN_SPEC_2026-06-18.md
# desc: Specification-only design for the Pre-Armed Dry Run authorization grant boundary after the S111-S114 chain stop.

# AutoTrade Pre-Armed Dry Run authorization grant design spec

Updated: 2026-06-18 JST  
Status: Specification-only boundary after S115  
Scope: Authorization grant design; no implementation grant yet

---

## 1. Purpose

This document defines the **authorization grant boundary** that comes after the S111-S114 review-only chain and the S115 chain boundary specification.

It is intentionally specification-only. It does not add a grant runner, grant append, record persistence, mode apply, broker execution, UI command button, watchdog loop, or any live/armed authorization.

Explicitly: this S116 slice has no implementation grant yet, no grant append, no record persistence, no mode apply, no broker execution, and no UI command buttons.

The goal is to make the next real system boundary explicit before implementation begins.

---

## 2. Prior anchors

The prior canonical anchors are:

```text
S114: authorization request/status packet chain stop
S115: authorization_request chain boundary spec
```

S115 established that a `ready_not_authorized_not_recorded_not_executed` status is not an approval and that recursive `authorization_request` chains are stopped.

This S116 document starts a new boundary: an explicit, separate, human-controlled authorization grant design.

---

## 3. Grant boundary definition

An authorization grant is a future explicit decision packet that may state:

```text
which operator granted
what scope was granted
which ready authorization request/status packet was referenced
which review acknowledgements were provided
which safety constraints remain in force
when the grant expires or becomes invalid
```

A grant must be separate from status readiness. A status packet becoming ready must never create a grant by itself.

---

## 4. Required inputs for a future grant

A future grant packet must reference all of the following:

```text
source_authorization_request_status_path
source_authorization_request_status_report_version
source_authorization_request_status_decision
source_authorization_request_status_ready
source_commit_head
requested_scope
operator_identity
granted_by
requested_at
granted_at
grant_expires_at or explicit non-expiring policy marker
acknowledgements
safety_boundary_snapshot
```

The source status must be ready, but ready is only a precondition. Ready is not approval.

---

## 5. Mandatory acknowledgement set

A future grant request must include acknowledgements equivalent to:

```text
confirm_s114_authorization_request_status_reviewed
confirm_ready_status_is_not_itself_approval
confirm_grant_is_explicit_human_decision
confirm_grant_does_not_send_orders
confirm_grant_does_not_apply_mode
confirm_grant_does_not_append_command_ledger
confirm_record_persistence_or_mode_apply_requires_separate_slice
confirm_broker_execution_requires_later_explicit_armed_or_live_boundary
```

The exact names may change during implementation, but these meanings must remain present.

---

## 6. Grant scopes

Initial grant scope names should be narrow and explicit. Candidate scopes:

```text
PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_REVIEW_ONLY
PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_RECORD_PREVIEW_ONLY
PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_RECORD_APPEND_PRECHECK_ONLY
```

The first implementation should use a review-only or preview-only scope. It must not jump directly to append execution or mode apply.

---

## 7. Explicit non-permissions

Even after this grant design exists, the repository still does not permit:

```text
broker execution
real orders
private API calls
Armed Dry Run authorization
Live authorization
autotrade resume authorization
authorization grant execution
authorization record append execution
approval ledger append execution
command ledger append
mode-change request
mode apply
UI command buttons
watchdog/autonomous execution loop
```

A future grant design or preview may reduce ambiguity, but it still does not execute anything.

---

## 8. Future grant output shape

A future grant packet should be a JSON object with these conceptual fields:

```text
ok
tool
report_version
generated_at
decision
authorization_grant_ready
authorization_grant_blockers
authorization_grant_granted
authorization_grant_executed
authorization_grant_recorded
source_summary
grant_summary
checks
warnings
operator_safety_lock
```

In the first dry-run/review implementation, these fields should remain false unless explicitly designed otherwise:

```text
authorization_grant_granted=False
authorization_grant_executed=False
authorization_grant_recorded=False
approval_ledger_appended=False
command_ledger_appended=False
mode_change_requested=False
mode_changed=False
would_send_to_broker=False
pre_armed_dry_run_authorized=False
live_authorized=False
```

---

## 9. Blocker requirements

A future grant status must be blocked when:

```text
source authorization request/status is not ready
source status has unexpected authorization/execution/record flags
operator identity is missing
granted_by is missing
scope is unsupported
acknowledgement set is incomplete
source commit/head is missing
safety boundary snapshot is missing
request attempts to append record or apply mode
request attempts broker/private API execution
operator safety lock is not clear
```

Blocked grants must remain visible and non-mutating.

---

## 10. Relationship to record persistence

Record persistence is the next distinct boundary after grant design. This spec does not create durable records.

A later persistence slice must define:

```text
record schema
append-only path
idempotency key
source grant reference
validation before append
rejection representation
audit fields
```

No persistence append should be implemented inside the design-only grant spec.

---

## 11. Relationship to mode apply preview

Mode apply preview is also a later distinct boundary. This spec does not request or apply modes.

A later preview slice must define:

```text
source grant reference
intended mode transition
preconditions
postconditions
human-visible preview
still no broker send
still no command execution
```

No mode apply should be implemented inside the design-only grant spec.

---

## 12. First implementation recommendation

The next implementation after this spec should be a grant **status dry-run packet**, not a grant append or mode apply.

Recommended next slice:

```text
S117: authorization grant status dry-run packet
input: S114 authorization request/status JSON + explicit grant review JSON
output: readiness/blocker status only
forbidden: append, mode apply, broker execution, UI buttons
```

This keeps the system moving toward real grant handling without skipping the safety boundary.

---

## 13. Safety boundary remains closed

The current safety boundary remains:

```text
broker-free; no broker execution; no real orders; no mode apply; no UI command buttons; no Armed Dry Run authorization; no Live authorization; no watchdog loop; no authorization request recording; no record execution; no authorization grant execution; no approval append; no command ledger append; no mode-change request.
```
