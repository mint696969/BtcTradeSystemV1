# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_recovery_resume_decision.py
# desc: MR-F6.22 pure immutable recovery/resume decision from a duplicate-safe receipt. No retry or I/O.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from .future_origin_evidence_duplicate_safe_receipt import (
    DESTINATION_STATE_ABSENT,
    DESTINATION_STATE_ALREADY_SATISFIED,
    DESTINATION_STATE_CONFLICTING,
    DESTINATION_STATE_INCONSISTENT,
    MARKET_REGIME_ORIGIN_EVIDENCE_DUPLICATE_SAFE_RECEIPT_VERSION,
)

MARKET_REGIME_ORIGIN_EVIDENCE_RECOVERY_RESUME_DECISION_VERSION = (
    "prediction.market_regime.origin_evidence_recovery_resume_decision.mr_f6_22.v1"
)

RECOVERY_DISPOSITION_HUMAN_GATED_RESUME_CANDIDATE = "human_gated_resume_candidate"
RECOVERY_DISPOSITION_TERMINAL_SUCCESS_EQUIVALENT = "terminal_success_equivalent"
RECOVERY_DISPOSITION_TERMINAL_CONFLICT_BLOCKED = "terminal_conflict_blocked"
RECOVERY_DISPOSITION_REOBSERVATION_REQUIRED = "reobservation_required"


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


def _decision_for_state(destination_state: str) -> tuple[str, bool, bool, tuple[str, ...], tuple[str, ...]]:
    if destination_state == DESTINATION_STATE_ABSENT:
        return (
            RECOVERY_DISPOSITION_HUMAN_GATED_RESUME_CANDIDATE,
            True,
            False,
            (),
            (
                "reconfirm_human_gate",
                "rebuild_execution_context_from_bound_hashes",
                "reobserve_destination_before_any_execution",
            ),
        )
    if destination_state == DESTINATION_STATE_ALREADY_SATISFIED:
        return (
            RECOVERY_DISPOSITION_TERMINAL_SUCCESS_EQUIVALENT,
            False,
            True,
            ("destination_artifact_already_satisfied",),
            ("return_existing_duplicate_safe_receipt",),
        )
    if destination_state == DESTINATION_STATE_CONFLICTING:
        return (
            RECOVERY_DISPOSITION_TERMINAL_CONFLICT_BLOCKED,
            False,
            True,
            ("destination_artifact_conflict",),
            ("explicit_conflict_resolution_required",),
        )
    if destination_state == DESTINATION_STATE_INCONSISTENT:
        return (
            RECOVERY_DISPOSITION_REOBSERVATION_REQUIRED,
            False,
            False,
            ("destination_observation_inconsistent",),
            (
                "repair_or_replace_observation_source",
                "reobserve_destination",
                "build_new_duplicate_safe_receipt",
            ),
        )
    raise ValueError("origin_evidence_recovery_resume_destination_state_invalid")


def build_origin_evidence_recovery_resume_decision(
    *,
    receipt: Mapping[str, Any],
    decided_at: str,
    expected_receipt_hash: str,
    failure_code: str | None = None,
    failure_detail_hash: str | None = None,
) -> Mapping[str, Any]:
    if not isinstance(receipt, Mapping):
        raise ValueError("origin_evidence_recovery_resume_receipt_type_invalid")
    if receipt.get("schema_version") != MARKET_REGIME_ORIGIN_EVIDENCE_DUPLICATE_SAFE_RECEIPT_VERSION:
        raise ValueError("origin_evidence_recovery_resume_receipt_schema_mismatch")
    if receipt.get("artifact_kind") != "future_origin_evidence_duplicate_safe_receipt":
        raise ValueError("origin_evidence_recovery_resume_receipt_kind_mismatch")

    _parse_canonical_utc(decided_at, "origin_evidence_recovery_resume_decided_at_invalid")
    observed_at = str(receipt.get("observed_at") or "").strip()
    observed = _parse_canonical_utc(
        observed_at,
        "origin_evidence_recovery_resume_receipt_observed_at_invalid",
    )
    decided = _parse_canonical_utc(decided_at, "origin_evidence_recovery_resume_decided_at_invalid")
    if decided < observed:
        raise ValueError("origin_evidence_recovery_resume_before_receipt_observation")

    expected_receipt_hash = str(expected_receipt_hash or "").strip().lower()
    receipt_hash = str(receipt.get("receipt_hash") or "").strip().lower()
    if not expected_receipt_hash:
        raise ValueError("origin_evidence_recovery_resume_expected_receipt_hash_missing")
    if receipt_hash != expected_receipt_hash:
        raise PermissionError("origin_evidence_recovery_resume_external_receipt_hash_mismatch")
    if receipt.get("receipt_id") != f"origin-evidence-duplicate-safe-receipt:{receipt_hash}":
        raise ValueError("origin_evidence_recovery_resume_receipt_id_mismatch")

    if receipt.get("receipt_is_authorization") is not False:
        raise ValueError("origin_evidence_recovery_resume_receipt_authorization_invalid")
    for field in (
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
        if receipt.get(field) is not False:
            raise ValueError(f"origin_evidence_recovery_resume_unsafe_receipt_flag:{field}")
    if receipt.get("human_gate_required") is not True:
        raise ValueError("origin_evidence_recovery_resume_human_gate_missing")

    failure_code_normalized = None if failure_code is None else str(failure_code).strip()
    if failure_code is not None and not failure_code_normalized:
        raise ValueError("origin_evidence_recovery_resume_failure_code_invalid")
    failure_detail_hash_normalized = None
    if failure_detail_hash is not None:
        failure_detail_hash_normalized = str(failure_detail_hash).strip().lower()
        if (
            len(failure_detail_hash_normalized) != 64
            or any(ch not in "0123456789abcdef" for ch in failure_detail_hash_normalized)
        ):
            raise ValueError("origin_evidence_recovery_resume_failure_detail_hash_invalid")
    if failure_code_normalized is None and failure_detail_hash_normalized is not None:
        raise ValueError("origin_evidence_recovery_resume_failure_detail_without_code")

    destination_state = str(receipt.get("destination_state") or "").strip()
    disposition, resume_candidate, terminal, state_blockers, recovery_actions = _decision_for_state(
        destination_state
    )
    receipt_blockers = tuple(str(item) for item in receipt.get("blockers") or ())
    blockers = tuple(dict.fromkeys((*receipt_blockers, *state_blockers)))

    identity = {
        "receipt_id": receipt.get("receipt_id"),
        "receipt_hash": receipt_hash,
        "adapter_result_hash": receipt.get("adapter_result_hash"),
        "execution_plan_hash": receipt.get("execution_plan_hash"),
        "artifact_relpath": receipt.get("artifact_relpath"),
        "dedupe_key": receipt.get("dedupe_key"),
        "expected_artifact_hash": receipt.get("expected_artifact_hash"),
        "observed_artifact_hash": receipt.get("observed_artifact_hash"),
        "destination_state": destination_state,
        "decided_at": decided_at,
        "failure_code": failure_code_normalized,
        "failure_detail_hash": failure_detail_hash_normalized,
        "recovery_disposition": disposition,
        "resume_candidate": resume_candidate,
        "terminal": terminal,
        "blockers": blockers,
        "recovery_actions": recovery_actions,
    }
    decision_hash = _canonical_hash(identity)

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_RECOVERY_RESUME_DECISION_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_recovery_resume_decision",
        "decision_id": f"origin-evidence-recovery-resume:{decision_hash}",
        "decision_hash": decision_hash,
        "receipt_id": receipt.get("receipt_id"),
        "receipt_hash": receipt_hash,
        "adapter_result_hash": receipt.get("adapter_result_hash"),
        "execution_plan_hash": receipt.get("execution_plan_hash"),
        "artifact_relpath": receipt.get("artifact_relpath"),
        "dedupe_key": receipt.get("dedupe_key"),
        "expected_artifact_hash": receipt.get("expected_artifact_hash"),
        "observed_artifact_hash": receipt.get("observed_artifact_hash"),
        "destination_state": destination_state,
        "decided_at": decided_at,
        "failure_code": failure_code_normalized,
        "failure_detail_hash": failure_detail_hash_normalized,
        "recovery_disposition": disposition,
        "resume_candidate": resume_candidate,
        "terminal": terminal,
        "blockers": blockers,
        "recovery_actions": recovery_actions,
        "automatic_retry_allowed": False,
        "resume_authorized_by_this_artifact": False,
        "conflicting_state_reclassified_as_absent": False,
        "inconsistent_state_reclassified_as_absent": False,
        "receipt_hash_preserved": True,
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
