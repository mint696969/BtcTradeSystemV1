# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_23_IMMUTABLE_AUDIT_AND_REPLAY_EVIDENCE_2026-07-14.md
# desc: Canonical MR-F6.23 immutable audit/replay evidence, hash-chain verification, and non-execution boundary.

# Prediction System MarketRegime MR-F6.23 Immutable Audit and Replay Evidence

Updated: 2026-07-14 JST
Status: accepted implementation checkpoint
Gate: MR_F6_23_IMMUTABLE_AUDIT_AND_REPLAY_EVIDENCE_ACCEPTED

## 1. Responsibility

MR-F6.23 consumes one immutable MR-F6.22 recovery/resume decision and produces one immutable audit/replay evidence artifact.

```text
MR-F6.22 recovery/resume decision
  + externally confirmed decision hash
  + recorded_at
  + replay source ID
  -> MR-F6.23 audit/replay evidence
```

The evidence freezes the execution-safety hash chain and a replay manifest for verification. It does not execute replay code, invoke the writer, read or write the filesystem, modify D-hot, or enable scheduling.

## 2. Bound hash chain

MR-F6.23 preserves the following chain:

```text
execution_plan_hash
  -> adapter_result_hash
  -> receipt_hash
  -> recovery_decision_hash
  -> replay_manifest_hash
  -> evidence_hash
```

The recovery-decision hash must match an external expected hash, and the decision ID must match that hash.

The replay manifest binds:

```text
execution-plan hash
adapter-result hash
receipt hash
recovery-decision hash
artifact relative path
dedupe key
expected artifact hash
observed artifact hash or null
destination state
recovery disposition
blockers
recovery actions
failure code
failure-detail hash
```

## 3. Evidence identity

The final evidence hash binds:

```text
recorded_at
replay source ID
replay-manifest hash
recovery decision ID
recovery decision hash
```

Changing the replay source changes the evidence hash without changing the replay-manifest hash. Changing any bound execution identity, observation, blocker, recovery action, or failure context changes the replay-manifest hash.

## 4. Revalidation

MR-F6.23 fails closed unless:

```text
recovery decision schema and artifact kind match MR-F6.22
recorded_at and decided_at are canonical UTC
recorded_at >= decided_at
external expected decision hash matches
recovery decision ID matches its hash
replay source ID is non-empty
execution-plan, adapter-result, receipt, decision, and artifact hashes are valid SHA-256 values
artifact path, dedupe key, destination state, and recovery disposition are present
receipt_hash_preserved=true
human_gate_required=true
all retry, resume-authorization, writer, execution, filesystem, D-hot, scheduler, promotion, and replacement flags remain false
```

Observed artifact hash may be null only when the prior accepted state permits it.

## 5. Replay meaning

Replay is identity reproduction and verification only.

```text
replay_verification_only=true
replay_reproduces_bound_identity=true
```

MR-F6.23 does not expose a replay runner, CLI, scheduler hook, writer function, root path, or filesystem API.

The artifact does not regenerate market predictions, rebuild source bundles from D-hot, call the writer, or count as real shadow evidence.

## 6. Safety boundary

For every evidence artifact:

```text
replay_invokes_writer=false
replay_reads_filesystem=false
replay_writes_filesystem=false
replay_writes_dhot=false
replay_enables_scheduler=false
replay_counts_as_real_shadow_evidence=false
audit_evidence_is_authorization=false
automatic_retry_allowed=false
resume_authorized_by_this_artifact=false
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

Audit evidence cannot authorize execution or weaken any blocker from MR-F6.21 or MR-F6.22.

## 7. Acceptance evidence

```text
MR-F6.23A import boundary=passed
MR-F6.23A connected MR-F6.22 suite=11 passed
MR-F6.23B focused audit/replay suite=10 passed
MR-F6.23B connected MR-F6.22/MR-F6.23 suite=21 passed
MR-F6.23B MarketRegime suite=365 passed
py_compile=passed
git diff --check=passed
replay runner exposed=false
writer invoked=false
filesystem read performed=false
filesystem write performed=false
D-hot modified=false
scheduler enabled=false
```

## 8. Handoff to MR-F6.24

MR-F6.24 must integrate and harden the accepted MR-F6.17 through MR-F6.23 contracts without broadening execution authority.

At minimum it must verify:

```text
public-interface and import boundaries
complete hash continuity from request through audit evidence
schema and artifact-kind compatibility
canonical UTC ordering across all stages
approval-window preservation
bundle, path, dedupe, and artifact-hash continuity
four-state idempotency and recovery dispositions
blocker preservation
immutability and deterministic reproduction
no hidden CLI, scheduler, filesystem, D-hot, promotion, or canonical-replacement surface
full MarketRegime regression suite
```

MR-F6.24 must treat any missing hash, unsafe flag, incompatible schema, state reclassification, or hidden execution surface as fail-closed.

MR-F6.23 does not satisfy `MARKET_REGIME_READY_FOR_NEXT_FAMILY`. MR-F6.24 and MR-F6 closeout remain mandatory.
