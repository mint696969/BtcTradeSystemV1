# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_audit_replay_evidence.py
# desc: MR-F6.23 pure immutable audit/replay evidence for the accepted execution-safety hash chain.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from .future_origin_evidence_recovery_resume_decision import (
    MARKET_REGIME_ORIGIN_EVIDENCE_RECOVERY_RESUME_DECISION_VERSION,
)

MARKET_REGIME_ORIGIN_EVIDENCE_AUDIT_REPLAY_EVIDENCE_VERSION = (
    "prediction.market_regime.origin_evidence_audit_replay_evidence.mr_f6_23.v1"
)


def _canonical_hash(payload: Mapping[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parse_canonical_utc(value: str, error: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(error)
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(error) from exc
    if parsed.tzinfo != timezone.utc or parsed.isoformat().replace("+00:00", "Z") != value:
        raise ValueError(error)
    return parsed


def _sha256(value: Any, error: str) -> str:
    normalized = str(value or "").strip().lower()
    if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
        raise ValueError(error)
    return normalized


def build_origin_evidence_audit_replay_evidence(
    *,
    recovery_decision: Mapping[str, Any],
    recorded_at: str,
    expected_recovery_decision_hash: str,
    replay_source_id: str,
) -> Mapping[str, Any]:
    if not isinstance(recovery_decision, Mapping):
        raise ValueError("origin_evidence_audit_replay_decision_type_invalid")
    if (
        recovery_decision.get("schema_version")
        != MARKET_REGIME_ORIGIN_EVIDENCE_RECOVERY_RESUME_DECISION_VERSION
    ):
        raise ValueError("origin_evidence_audit_replay_decision_schema_mismatch")
    if recovery_decision.get("artifact_kind") != "future_origin_evidence_recovery_resume_decision":
        raise ValueError("origin_evidence_audit_replay_decision_kind_mismatch")

    recorded = _parse_canonical_utc(
        recorded_at,
        "origin_evidence_audit_replay_recorded_at_invalid",
    )
    decided_at = str(recovery_decision.get("decided_at") or "").strip()
    decided = _parse_canonical_utc(
        decided_at,
        "origin_evidence_audit_replay_decided_at_invalid",
    )
    if recorded < decided:
        raise ValueError("origin_evidence_audit_replay_before_decision")

    decision_hash = _sha256(
        recovery_decision.get("decision_hash"),
        "origin_evidence_audit_replay_decision_hash_invalid",
    )
    expected_decision_hash = _sha256(
        expected_recovery_decision_hash,
        "origin_evidence_audit_replay_expected_decision_hash_invalid",
    )
    if decision_hash != expected_decision_hash:
        raise PermissionError("origin_evidence_audit_replay_external_decision_hash_mismatch")
    if recovery_decision.get("decision_id") != f"origin-evidence-recovery-resume:{decision_hash}":
        raise ValueError("origin_evidence_audit_replay_decision_id_mismatch")

    replay_source_id = str(replay_source_id or "").strip()
    if not replay_source_id:
        raise ValueError("origin_evidence_audit_replay_source_id_missing")

    execution_plan_hash = _sha256(
        recovery_decision.get("execution_plan_hash"),
        "origin_evidence_audit_replay_execution_plan_hash_invalid",
    )
    adapter_result_hash = _sha256(
        recovery_decision.get("adapter_result_hash"),
        "origin_evidence_audit_replay_adapter_result_hash_invalid",
    )
    receipt_hash = _sha256(
        recovery_decision.get("receipt_hash"),
        "origin_evidence_audit_replay_receipt_hash_invalid",
    )
    expected_artifact_hash = _sha256(
        recovery_decision.get("expected_artifact_hash"),
        "origin_evidence_audit_replay_expected_artifact_hash_invalid",
    )
    observed_artifact_hash_raw = recovery_decision.get("observed_artifact_hash")
    observed_artifact_hash = (
        None
        if observed_artifact_hash_raw is None
        else _sha256(
            observed_artifact_hash_raw,
            "origin_evidence_audit_replay_observed_artifact_hash_invalid",
        )
    )

    artifact_relpath = str(recovery_decision.get("artifact_relpath") or "").strip()
    dedupe_key = str(recovery_decision.get("dedupe_key") or "").strip()
    destination_state = str(recovery_decision.get("destination_state") or "").strip()
    recovery_disposition = str(
        recovery_decision.get("recovery_disposition") or ""
    ).strip()
    if not artifact_relpath or not dedupe_key or not destination_state or not recovery_disposition:
        raise ValueError("origin_evidence_audit_replay_identity_missing")

    for field in (
        "automatic_retry_allowed",
        "resume_authorized_by_this_artifact",
        "conflicting_state_reclassified_as_absent",
        "inconsistent_state_reclassified_as_absent",
        "writer_write_function_imported",
        "writer_write_function_invoked",
        "writer_invoked",
        "execution_performed",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "writes_dhot",
        "scheduler_enabled",
        "counts_as_real_shadow_evidence",
        "candidate_selection_performed",
        "live_parameter_apply_allowed",
        "auto_promotion_allowed",
        "canonical_replacement_allowed",
    ):
        if recovery_decision.get(field) is not False:
            raise ValueError(f"origin_evidence_audit_replay_unsafe_decision_flag:{field}")
    if recovery_decision.get("receipt_hash_preserved") is not True:
        raise ValueError("origin_evidence_audit_replay_receipt_hash_not_preserved")
    if recovery_decision.get("human_gate_required") is not True:
        raise ValueError("origin_evidence_audit_replay_human_gate_missing")

    blockers = tuple(str(item) for item in recovery_decision.get("blockers") or ())
    recovery_actions = tuple(
        str(item) for item in recovery_decision.get("recovery_actions") or ()
    )
    replay_manifest = {
        "execution_plan_hash": execution_plan_hash,
        "adapter_result_hash": adapter_result_hash,
        "receipt_hash": receipt_hash,
        "recovery_decision_hash": decision_hash,
        "artifact_relpath": artifact_relpath,
        "dedupe_key": dedupe_key,
        "expected_artifact_hash": expected_artifact_hash,
        "observed_artifact_hash": observed_artifact_hash,
        "destination_state": destination_state,
        "recovery_disposition": recovery_disposition,
        "blockers": blockers,
        "recovery_actions": recovery_actions,
        "failure_code": recovery_decision.get("failure_code"),
        "failure_detail_hash": recovery_decision.get("failure_detail_hash"),
    }
    replay_manifest_hash = _canonical_hash(replay_manifest)
    identity = {
        "recorded_at": recorded_at,
        "replay_source_id": replay_source_id,
        "replay_manifest_hash": replay_manifest_hash,
        "decision_id": recovery_decision.get("decision_id"),
        "decision_hash": decision_hash,
    }
    evidence_hash = _canonical_hash(identity)

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_AUDIT_REPLAY_EVIDENCE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_audit_replay_evidence",
        "evidence_id": f"origin-evidence-audit-replay:{evidence_hash}",
        "evidence_hash": evidence_hash,
        "recorded_at": recorded_at,
        "replay_source_id": replay_source_id,
        "decision_id": recovery_decision.get("decision_id"),
        "recovery_decision_hash": decision_hash,
        "execution_plan_hash": execution_plan_hash,
        "adapter_result_hash": adapter_result_hash,
        "receipt_hash": receipt_hash,
        "replay_manifest": MappingProxyType(replay_manifest),
        "replay_manifest_hash": replay_manifest_hash,
        "replay_verification_only": True,
        "replay_reproduces_bound_identity": True,
        "replay_invokes_writer": False,
        "replay_reads_filesystem": False,
        "replay_writes_filesystem": False,
        "replay_writes_dhot": False,
        "replay_enables_scheduler": False,
        "replay_counts_as_real_shadow_evidence": False,
        "audit_evidence_is_authorization": False,
        "automatic_retry_allowed": False,
        "resume_authorized_by_this_artifact": False,
        "writer_write_function_imported": False,
        "writer_write_function_invoked": False,
        "writer_invoked": False,
        "execution_performed": False,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "counts_as_real_shadow_evidence": False,
        "candidate_selection_performed": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
        "human_gate_required": True,
    })
