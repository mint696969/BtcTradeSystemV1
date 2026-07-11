# path: ./docs/strategy/PREDICTION_SYSTEM_CONTRACT_CHANGE_AND_TEST_GUARD_POLICY_2026-07-11.md
# desc: Defines how current specifications, historical documents, automated guards, and handoffs must remain synchronized when behavior changes.

# Prediction System Contract Change and Test Guard Policy

Updated: 2026-07-11 JST
Checkpoint: PS_CONTRACT_CHANGE_AND_TEST_GUARD_POLICY_ACCEPTED

<!-- PS_CONTRACT_CHANGE_AND_TEST_GUARD_POLICY_2026_07_11 -->

```text
current_contract_must_be_explicit=true
historical_contracts_are_immutable_evidence=true
historical_contracts_are_not_automatic_current_guards=true
implementation_spec_guard_same_slice_required=true
full_affected_suite_required=true
skip_xfail_exclusion_as_pass_strategy_forbidden=true
handoff_sync_required=true
```

## 1. Purpose

This policy prevents contract drift where production behavior changes but current specifications, automated guards, or thread handoffs continue to assert an older design.

It applies to prediction, operator UI, Collector, WarRoom, runtime, artifact, launch, route, localization, and safety-boundary changes.

## 2. Contract classes

Every behavior document or test guard must be treated as one of these classes:

```text
current:
  authoritative for the current implementation

historical:
  evidence of an earlier accepted state
  retained for audit and evolution history

superseded:
  no longer authoritative
  must identify the current replacement when one exists
```

A historical document must not be silently rewritten to describe a newer behavior.

A current automated guard must not derive its expected behavior solely from a historical document.

## 3. Required same-slice synchronization

When observable behavior, ownership, version, route, artifact shape, launch default, or safety behavior changes, the same implementation slice must update:

```text
1. production implementation
2. current contract/specification
3. current automated guard
4. affected focused tests
5. affected full package suites
6. checkpoint/handoff state
```

When production behavior is intentionally unchanged and only a stale guard is repaired, the slice must record:

```text
production_runtime_code_changed=false
current_guard_synchronized=true
historical_contract_preserved=true
```

## 4. Specification requirements

A current specification for changed behavior must state:

```text
checkpoint or contract version
current responsibility owner
inputs and outputs
primary and fallback paths
safety and prohibited actions
failure and fail-closed behavior
superseded behavior or historical predecessor
acceptance guards
```

For data-dependent prediction behavior, it must also state:

```text
missing-data behavior
stale-data behavior
UNKNOWN / abstain behavior
confidence semantics
outcome/calibration relationship
```

## 5. Automated guard design

Current guards should prefer:

```text
public API behavior
responsibility and ownership boundaries
machine-readable safety flags
versioned runtime behavior
artifact or packet schema
fail-closed behavior
identity and trace preservation
primary/fallback selection
```

Current guards should not rely solely on:

```text
fixed visible wording
private helper names
source formatting
obsolete route labels
historical version constants
arbitrary source-line limits
broad import prohibition when a bounded ownership exception exists
```

Visible wording may be asserted when wording itself is the contract, such as localization, legal, risk, or operator-safety text. In that case the specification must identify it as wording-sensitive.

## 6. Historical-test handling

When an old test fails after a legitimate contract change:

```text
1. confirm current repository implementation
2. identify the current authoritative specification
3. determine whether the test is current, historical, or superseded
4. preserve historical evidence
5. update or replace only the current guard
6. strengthen the replacement around current responsibilities and safety
7. run the full affected suite without exclusions
```

Do not obtain a pass by:

```text
adding skip or xfail
excluding the failing file
weakening safety assertions
removing identity or trace assertions
changing production behavior solely to satisfy a superseded private-detail test
```

## 7. Version and supersession markers

When a contract replaces an earlier contract, the current document should include machine-readable markers where practical:

```text
contract_status=current
supersedes=<checkpoint-or-document>
historical_predecessor_preserved=true
current_guard=<test-path-or-suite>
```

Historical documents may add a non-destructive note pointing to a successor only when repository policy permits; their original accepted claims must remain intact.

## 8. Full-suite expectations

The minimum broad guard is the full package directly affected by the change.

Examples:

```text
operator UI behavior:
  pytest -q btcts_next/src/btcts/apps/operator_ui/tests

prediction contract:
  pytest -q btcts_next/src/btcts/prediction

cross-layer prediction-to-WarRoom change:
  both suites
```

Collection errors count as failures. Test exclusions do not count as a clean baseline.

## 9. Handoff requirements

Before a thread or implementation phase closes, persistent project memory must identify:

```text
current clean HEAD
current checkpoint
next checkpoint
canonical current specification
first implementation boundary
explicit non-goals and prohibited actions
accepted broad-suite evidence
```

Conversation context alone is not canonical project memory.

## 10. Current adoption evidence

This policy was extracted from the operator UI stale-contract repair that resolved:

```text
initial collection blocker=1
initial post-collection problems=31
final operator UI suite=1164 passed
final prediction suite=272 passed
production runtime code changed=false
skip/xfail/exclusion added=false
```

## 11. Acceptance decision

```text
contract_classes_defined=true
same_slice_sync_required=true
specification_requirements_defined=true
guard_design_rules_defined=true
historical_test_handling_defined=true
full_suite_policy_defined=true
handoff_policy_defined=true
contract_change_policy_accepted=true
```
