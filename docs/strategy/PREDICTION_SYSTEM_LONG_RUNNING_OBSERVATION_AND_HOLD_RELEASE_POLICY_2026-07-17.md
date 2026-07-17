# path: ./docs/strategy/PREDICTION_SYSTEM_LONG_RUNNING_OBSERVATION_AND_HOLD_RELEASE_POLICY_2026-07-17.md
# desc: Current policy for long-running observation lifecycle, periodic decisions, restart rules, and release of work held to protect evidence integrity.

# Prediction System Long-Running Observation and Hold-Release Policy

Updated: 2026-07-17 JST
Status: current
Checkpoint: PS_LONG_RUNNING_OBSERVATION_AND_HOLD_RELEASE_POLICY_ACCEPTED

<!-- PS_LONG_RUNNING_OBSERVATION_AND_HOLD_RELEASE_POLICY_2026_07_17 -->

```text
contract_status=current
historical_predecessor_preserved=true
conversation_is_not_canonical=true
repository_and_gpt_room_are_canonical=true
observation_must_not_be_left_unowned=true
periodic_decision_receipts_required=true
hold_release_requires_explicit_receipt=true
```

## 1. Purpose

Long-running prediction observations must remain understandable and controllable across thread changes and GPT changes. Starting an observation does not authorize indefinite continuation, indefinite work holds, silent test mutation, or automatic acceptance after elapsed time.

This policy defines:

```text
observation identity
scheduled checkpoints
continue / pause / abort / restart decisions
collection completion versus outcome maturity
acceptance and insufficient-evidence decisions
release of held implementation work
persistent handoff state
```

## 2. Canonical ownership

```text
current specification:
  this document and the family-specific current observation contract

current live state:
  tmp/gpt_room/OBSERVATION_CONTROL.md

immutable runtime evidence:
  collection plan, authorization package, state, progress, lease,
  manifests, payloads, completion/abort receipts, and review receipts

conversation:
  explanatory only; never the sole source of observation state
```

Every GPT continuing the work must read the current specification and `tmp/gpt_room/OBSERVATION_CONTROL.md` before interpreting a running, paused, maturing, or reviewed observation.

## 3. Observation identity

Before production observation starts, freeze at least:

```text
observation_id
family
purpose
repository_commit
working_tree_clean
collection_id
planned_start_utc
planned_end_utc
cadence_sec
source_root
destination_root
model_id
logic_version
parameter_set_id
candidate_ids
horizon_policy_version
target_definition_versions
readiness_contract_version
writer_contract_version
```

The start receipt and every periodic decision receipt must refer to this identity. Editing the repository in parallel is permitted only when the running process identity remains frozen and the edits are not applied to that process.

## 4. State machine

Allowed states:

```text
PLANNED
AUTHORIZED
RUNNING
CHECK_DUE
PAUSED
ABORTED
RESTART_REQUIRED
COLLECTION_COMPLETE
MATURING
EVIDENCE_REVIEW
ACCEPTED
INSUFFICIENT_EVIDENCE
INVALID
FOLLOWUP_OBSERVATION_PLANNED
HOLDS_RELEASED
```

Required transitions:

```text
PLANNED -> AUTHORIZED
AUTHORIZED -> RUNNING
RUNNING -> CHECK_DUE
CHECK_DUE -> RUNNING | PAUSED | ABORTED | RESTART_REQUIRED
RUNNING -> COLLECTION_COMPLETE
COLLECTION_COMPLETE -> MATURING
MATURING -> EVIDENCE_REVIEW
EVIDENCE_REVIEW -> ACCEPTED | INSUFFICIENT_EVIDENCE | INVALID
ACCEPTED -> HOLDS_RELEASED
INSUFFICIENT_EVIDENCE -> FOLLOWUP_OBSERVATION_PLANNED | HOLDS_RELEASED
INVALID -> RESTART_REQUIRED | HOLDS_RELEASED
RESTART_REQUIRED -> PLANNED
```

No GPT may infer `ACCEPTED`, `INVALID`, or `HOLDS_RELEASED` solely from elapsed time.

## 5. Mandatory checkpoint schedule

The family-specific plan may tighten this schedule. Unless tightened, a bounded observation must define:

```text
startup checkpoint:
  after lease acquisition, RUNNING persistence, and first tick result

early checkpoint:
  after enough ticks to detect path, cadence, readiness, and write failures

periodic checkpoint:
  at a fixed interval recorded in the plan

planned-end checkpoint:
  when collection duration ends

maturity checkpoint:
  after the latest eligible origin reaches the longest horizon expiry

review checkpoint:
  after required metrics and integrity checks are produced
```

For the first MR-F9 bounded 24-hour collection, the plan must explicitly record checkpoint times before start. Recommended initial checkpoints are startup, approximately 15 minutes, 1 hour, 6 hours, 12 hours, planned end, and final outcome maturity. These are operational review points, not model-quality acceptance thresholds.

A missed checkpoint is itself a recorded warning. It does not silently stop or accept the observation.

## 6. Periodic decision receipt

Every checkpoint must create or update a durable decision receipt containing:

```text
observation_id
checked_at_utc
checked_by
repository_commit_under_test
runtime_pid_and_lease
state_and_progress_paths
planned_start_and_end
actual_tick_count
written_count
duplicate_skip_count
readiness_skip_count
missing_tick_count
conflict_count
last_success_at
last_error
source_freshness
manifest_payload_integrity
identity_unchanged
working_tree_change_effect_on_runtime
outcome_maturity_status
decision
decision_reasons
next_check_at_utc
held_work_status
```

Allowed checkpoint decisions:

```text
CONTINUE
PAUSE
ABORT
RESTART_REQUIRED
COLLECTION_COMPLETE
WAIT_FOR_MATURITY
BEGIN_EVIDENCE_REVIEW
ACCEPT
INSUFFICIENT_EVIDENCE
INVALID
RELEASE_HOLDS
```

## 7. Continue criteria

`CONTINUE` is appropriate only when all safety-critical conditions remain valid:

```text
expected process and lease owner
frozen observation identity unchanged
source and destination ownership valid
no same-closed-source conflict
manifest-last and digest integrity valid
no unauthorized scheduler or detached duplicate
no broker, AutoTrade, or order surface
errors are absent or explicitly non-invalidating
next checkpoint scheduled
```

Low model quality, UNKNOWN, fallback, readiness skips, or insufficient coverage do not automatically invalidate evidence. They remain observable results unless caused by a contract or implementation defect.

## 8. Pause, abort, and restart rules

Use `PAUSE` when evidence remains valid but a reversible external condition requires operator intervention.

Use `ABORT` when continuation is unsafe or unauthorized, including:

```text
unexpected duplicate producer
lease ownership ambiguity
unauthorized root or path
broker/order boundary violation
unbounded writes
operator-requested stop
```

Use `RESTART_REQUIRED` when existing observations cannot be compared under one identity, including:

```text
model logic changed in the running process
parameter set changed
candidate set changed
horizon policy changed
target or outcome semantics changed
readiness or source-selection semantics changed
cadence or dedupe identity changed
persistence schema changed incompatibly
implementation defect corrupted or misidentified evidence
```

A restart must:

```text
stop the current observation explicitly
persist an abort or supersession receipt
preserve prior artifacts immutably
assign a new observation_id and collection_id
freeze the new identity
repeat pre-start qualification and authorization
```

Do not rewrite or backfill the failed observation to make it appear continuous.

## 9. Collection completion and maturity

`COLLECTION_COMPLETE` means only that the planned producer window ended and its completion receipt passed integrity checks.

It does not mean future outcomes are mature. The observation must enter `MATURING` until every eligible origin has either:

```text
resolved outcome
explicit unresolved reason
explicit invalidation reason
```

For a 24-hour horizon, final maturity may occur approximately 24 hours after the final collection origin.

## 10. Evidence review decisions

`ACCEPTED` requires integrity gates plus the family-specific evidence minima. Acceptance may still conclude that no candidate should be promoted.

`INSUFFICIENT_EVIDENCE` is a valid review result when integrity is sound but sample, coverage, condition diversity, probability semantics, or maturity is insufficient.

`INVALID` means the observation cannot support the intended claim because identity, implementation, collection, or evidence integrity failed.

Poor prediction accuracy alone is not an integrity failure. It is model-quality evidence.

## 11. Held-work register

Every observation-affecting work item must be recorded with:

```text
hold_id
work_item
reason_for_hold
observation_id
what_result_it_could_change
allowed_offline_work
release_condition
restart_condition
status
```

Statuses:

```text
HELD
OFFLINE_ONLY
READY_FOR_RELEASE
RELEASED
CANCELLED
```

Held work must not remain blocked indefinitely without a next decision point.

## 12. Hold-release rules

A hold is released only by an explicit review receipt.

Typical release paths:

```text
ACCEPTED:
  release work whose only hold reason was protecting the accepted observation

INSUFFICIENT_EVIDENCE:
  release unrelated work;
  keep only work that would invalidate a planned follow-up observation held

INVALID:
  release corrective work immediately;
  restart only after the defect and new identity are accepted

FOLLOWUP_OBSERVATION_PLANNED:
  preserve holds only for contracts frozen into that follow-up plan
```

The receipt must name each hold as `RELEASED`, `RETAINED`, or `CANCELLED`. A general statement such as “observation finished” is not enough.

## 13. Parallel implementation boundary

Allowed during observation:

```text
read-only monitoring and status
receipt and manifest verification
timestamp trace tooling
offline analysis
repo-tmp tests and fixtures
documentation
schema/interface design not applied to runtime
implementation changes kept outside the running process
```

Held from application to the running observation:

```text
prediction logic
parameters
candidate selection
features
UNKNOWN or fallback rules
readiness/source selection
timestamp and dedupe semantics
target/outcome semantics
cadence
persistence identity/schema
```

Parallel edits require a recorded statement that they were not loaded by the running process.

## 14. GPT handoff requirements

Before a thread changes while an observation is active, persistent memory must state:

```text
observation_id and state
exact runtime identity
last checkpoint decision and reasons
next_check_at_utc
current counters and warnings
collection end and maturity estimate
held-work register
which changes are offline-only
explicit continue / stop / restart authority boundary
```

The next GPT must not replace a scheduled evidence decision with a new informal interpretation.

## 15. MR-F9 application

For the first bounded MarketRegime collection:

```text
first_24h_purpose=production_path_and_evidence_pipeline_qualification
first_24h_is_not_automatic_model_acceptance=true
future_forecast_horizons=300,900,1800,3600,21600,43200,86400
current_state_horizon=0
collection_complete_separate_from_outcome_mature=true
minimum_observed_slots_and_coverage_still_required=true
insufficient_evidence_is_allowed=true
runtime_auto_promotion=false
live_parameter_apply=false
```

Observation-affecting MarketRegime changes remain held until an explicit evidence review receipt releases or supersedes each hold.

## 16. Acceptance

```text
state_machine_defined=true
checkpoint_schedule_required=true
periodic_decision_receipt_required=true
continue_pause_abort_restart_rules_defined=true
collection_and_maturity_separated=true
insufficient_evidence_supported=true
held_work_register_required=true
hold_release_receipt_required=true
gpt_handoff_requirements_defined=true
policy_accepted=true
```
