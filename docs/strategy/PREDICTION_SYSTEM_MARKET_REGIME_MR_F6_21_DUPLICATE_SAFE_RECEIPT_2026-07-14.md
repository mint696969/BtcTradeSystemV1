# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_21_DUPLICATE_SAFE_RECEIPT_2026-07-14.md
# desc: Canonical MR-F6.21 duplicate-safe receipt state model, safety boundary, and handoff to recovery/resume.

# Prediction System MarketRegime MR-F6.21 Duplicate-safe Receipt

Updated: 2026-07-14 JST
Status: accepted implementation checkpoint
Gate: MR_F6_21_IDEMPOTENCY_AND_DUPLICATE_SAFE_RECEIPT_ACCEPTED

## 1. Responsibility

MR-F6.21 converts one accepted MR-F6.20 dry-run adapter result plus one externally observed destination state into one immutable duplicate-safe receipt.

```text
MR-F6.20 dry-run adapter result
  + destination existence observation
  + destination match observation
  + expected artifact hash
  + observed artifact hash
  -> MR-F6.21 duplicate-safe receipt
```

The receipt classifies destination state. It does not read the filesystem, invoke the writer, authorize execution, or mutate D-hot.

## 2. Destination states

### absent

```text
destination_artifact_exists=false
destination_artifact_matches_expected=false
observed_artifact_hash=null
```

Meaning:

```text
no destination artifact was observed
no duplicate or conflict was observed
write_may_be_considered_by_separate_step=true
receipt_is_authorization=false
```

### already_satisfied

```text
destination_artifact_exists=true
destination_artifact_matches_expected=true
observed_artifact_hash=expected_artifact_hash
```

Meaning:

```text
identical append-only artifact already exists
duplicate_safely_satisfied=true
no rewrite is needed
no overwrite is allowed
```

### conflicting

```text
destination_artifact_exists=true
destination_artifact_matches_expected=false
observed_artifact_hash!=expected_artifact_hash
```

Meaning:

```text
an artifact exists at the frozen destination with different content
conflict_detected=true
fail closed
no overwrite or replacement
```

### inconsistent

Examples:

```text
exists=false with observed hash present
exists=false with matches=true
exists=true with observed hash missing
matches=true while hashes differ
matches=false while hashes are equal
```

Meaning:

```text
external destination observations contradict each other
inconsistent_observation=true
fail closed
observation must be repeated or repaired by a separate recovery step
```

## 3. Bound identity

The immutable receipt binds:

```text
adapter result ID and externally confirmed adapter result hash
execution-plan hash
observed_at
frozen artifact relative path
frozen dedupe key
expected artifact SHA-256
observed artifact SHA-256 or null
existence and match observations
classified destination state
state blockers
```

The receipt hash changes whenever any bound identity or observation changes.

## 4. Revalidation

MR-F6.21 fails closed unless:

```text
adapter result schema and kind match MR-F6.20
external adapter-result hash matches
adapter result ID matches its hash
adapter confirms dry-run contract exercised
writer preflight was invoked
writer write function remained unimported and uninvoked
no execution, filesystem write, D-hot write, scheduler, promotion, or replacement occurred
expected and observed artifact hashes are valid SHA-256 hex when present
adapter result carries destination path, dedupe key, and execution-plan hash
```

## 5. Idempotency meaning

MR-F6.21 does not make the writer idempotent by itself. It defines the immutable observation and decision record required for duplicate-safe behavior.

```text
absent -> a separate write step may be considered
already_satisfied -> return success-equivalent duplicate receipt without rewrite
conflicting -> fail closed
inconsistent -> fail closed and require recovery/re-observation
```

No state permits overwrite, canonical replacement, or automatic retry.

## 6. Safety boundary

For every destination state:

```text
receipt_is_authorization=false
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

`write_may_be_considered_by_separate_step=true` is only possible for `absent`. It is not permission to invoke the writer.

## 7. Acceptance evidence

```text
MR-F6.21A contract import boundary=passed
MR-F6.21A connected MR-F6.20 suite=17 passed
MR-F6.21B focused receipt suite=13 passed
MR-F6.21B connected adapter/receipt suite=21 passed
MR-F6.21B MarketRegime suite=344 passed
py_compile=passed
git diff --check=passed
filesystem read performed=false
filesystem write performed=false
writer invoked=false
D-hot modified=false
scheduler enabled=false
```

## 8. Handoff to MR-F6.22

MR-F6.22 must consume the immutable receipt and define failure recovery and resume behavior without weakening the state model.

```text
absent -> resumable only through a separate human-gated execution path
already_satisfied -> terminal success-equivalent receipt
conflicting -> terminal fail-closed until explicit conflict resolution
inconsistent -> re-observe or repair observation source before resume
```

MR-F6.22 must preserve receipt hash, adapter-result hash, expected artifact hash, destination path, dedupe key, and all original blockers. It must not silently convert `conflicting` or `inconsistent` into `absent`.

MR-F6.21 does not satisfy `MARKET_REGIME_READY_FOR_NEXT_FAMILY`. MR-F6.22 through MR-F6.24 and MR-F6 closeout remain mandatory.
