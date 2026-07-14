# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_duplicate_safe_receipt.py
# desc: MR-F6.21 pure immutable duplicate-safe destination receipt. No filesystem read or writer invocation.

from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .future_origin_evidence_dry_run_writer_adapter import (
    MARKET_REGIME_ORIGIN_EVIDENCE_DRY_RUN_WRITER_ADAPTER_VERSION,
)

MARKET_REGIME_ORIGIN_EVIDENCE_DUPLICATE_SAFE_RECEIPT_VERSION = (
    "prediction.market_regime.origin_evidence_duplicate_safe_receipt.mr_f6_21.v1"
)

DESTINATION_STATE_ABSENT = "absent"
DESTINATION_STATE_ALREADY_SATISFIED = "already_satisfied"
DESTINATION_STATE_CONFLICTING = "conflicting"
DESTINATION_STATE_INCONSISTENT = "inconsistent"


def _canonical_hash(payload: Mapping[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalized_sha256(value: str | None, error: str) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if len(normalized) != 64 or any(ch not in "0123456789abcdef" for ch in normalized):
        raise ValueError(error)
    return normalized


def _classify_destination_state(
    *,
    destination_artifact_exists: bool,
    destination_artifact_matches_expected: bool,
    expected_artifact_hash: str,
    observed_artifact_hash: str | None,
) -> tuple[str, tuple[str, ...]]:
    if type(destination_artifact_exists) is not bool:
        raise ValueError("origin_evidence_duplicate_receipt_destination_exists_type_invalid")
    if type(destination_artifact_matches_expected) is not bool:
        raise ValueError("origin_evidence_duplicate_receipt_destination_match_type_invalid")

    if not destination_artifact_exists:
        if destination_artifact_matches_expected or observed_artifact_hash is not None:
            return (
                DESTINATION_STATE_INCONSISTENT,
                ("destination_artifact_state_inconsistent",),
            )
        return DESTINATION_STATE_ABSENT, ()

    if observed_artifact_hash is None:
        return (
            DESTINATION_STATE_INCONSISTENT,
            ("destination_artifact_hash_missing",),
        )

    hashes_match = observed_artifact_hash == expected_artifact_hash
    if destination_artifact_matches_expected and hashes_match:
        return (
            DESTINATION_STATE_ALREADY_SATISFIED,
            ("destination_artifact_already_satisfied",),
        )
    if destination_artifact_matches_expected != hashes_match:
        return (
            DESTINATION_STATE_INCONSISTENT,
            ("destination_artifact_match_claim_inconsistent",),
        )
    return (
        DESTINATION_STATE_CONFLICTING,
        ("destination_artifact_conflict",),
    )


def build_origin_evidence_duplicate_safe_receipt(
    *,
    adapter_result: Mapping[str, Any],
    observed_at: str,
    destination_artifact_exists: bool,
    destination_artifact_matches_expected: bool,
    expected_adapter_result_hash: str,
    expected_artifact_hash: str,
    observed_artifact_hash: str | None,
) -> Mapping[str, Any]:
    if not isinstance(adapter_result, Mapping):
        raise ValueError("origin_evidence_duplicate_receipt_adapter_result_type_invalid")
    if (
        adapter_result.get("schema_version")
        != MARKET_REGIME_ORIGIN_EVIDENCE_DRY_RUN_WRITER_ADAPTER_VERSION
    ):
        raise ValueError("origin_evidence_duplicate_receipt_adapter_schema_mismatch")
    if (
        adapter_result.get("artifact_kind")
        != "future_origin_evidence_dry_run_writer_adapter_result"
    ):
        raise ValueError("origin_evidence_duplicate_receipt_adapter_kind_mismatch")

    expected_adapter_result_hash = str(expected_adapter_result_hash or "").strip().lower()
    adapter_result_hash = str(adapter_result.get("adapter_result_hash") or "").strip().lower()
    if not expected_adapter_result_hash:
        raise ValueError("origin_evidence_duplicate_receipt_expected_adapter_hash_missing")
    if adapter_result_hash != expected_adapter_result_hash:
        raise PermissionError("origin_evidence_duplicate_receipt_external_adapter_hash_mismatch")
    if adapter_result.get("adapter_result_id") != (
        f"origin-evidence-dry-run-writer-adapter:{adapter_result_hash}"
    ):
        raise ValueError("origin_evidence_duplicate_receipt_adapter_result_id_mismatch")

    for field in (
        "dry_run_contract_exercised",
        "writer_preflight_invoked",
        "human_gate_required",
    ):
        if adapter_result.get(field) is not True:
            raise ValueError(f"origin_evidence_duplicate_receipt_adapter_not_ready:{field}")
    for field in (
        "writer_write_function_imported",
        "writer_write_function_invoked",
        "writer_invoked",
        "execution_performed",
        "filesystem_write_performed",
        "writes_dhot",
        "scheduler_enabled",
        "counts_as_real_shadow_evidence",
        "candidate_selection_performed",
        "live_parameter_apply_allowed",
        "auto_promotion_allowed",
        "canonical_replacement_allowed",
    ):
        if adapter_result.get(field) is not False:
            raise ValueError(f"origin_evidence_duplicate_receipt_unsafe_adapter_flag:{field}")

    expected_artifact_hash_normalized = _normalized_sha256(
        expected_artifact_hash,
        "origin_evidence_duplicate_receipt_expected_artifact_hash_invalid",
    )
    if expected_artifact_hash_normalized is None:
        raise ValueError("origin_evidence_duplicate_receipt_expected_artifact_hash_missing")
    observed_artifact_hash_normalized = _normalized_sha256(
        observed_artifact_hash,
        "origin_evidence_duplicate_receipt_observed_artifact_hash_invalid",
    )

    destination_state, blockers = _classify_destination_state(
        destination_artifact_exists=destination_artifact_exists,
        destination_artifact_matches_expected=destination_artifact_matches_expected,
        expected_artifact_hash=expected_artifact_hash_normalized,
        observed_artifact_hash=observed_artifact_hash_normalized,
    )

    artifact_relpath = str(adapter_result.get("artifact_relpath") or "").strip()
    dedupe_key = str(adapter_result.get("dedupe_key") or "").strip()
    execution_plan_hash = str(adapter_result.get("execution_plan_hash") or "").strip()
    if not artifact_relpath or not dedupe_key or not execution_plan_hash:
        raise ValueError("origin_evidence_duplicate_receipt_adapter_identity_missing")

    write_may_be_considered = destination_state == DESTINATION_STATE_ABSENT
    duplicate_safely_satisfied = (
        destination_state == DESTINATION_STATE_ALREADY_SATISFIED
    )
    conflict_detected = destination_state == DESTINATION_STATE_CONFLICTING
    inconsistent_observation = destination_state == DESTINATION_STATE_INCONSISTENT

    identity = {
        "adapter_result_id": adapter_result.get("adapter_result_id"),
        "adapter_result_hash": adapter_result_hash,
        "execution_plan_hash": execution_plan_hash,
        "observed_at": observed_at,
        "artifact_relpath": artifact_relpath,
        "dedupe_key": dedupe_key,
        "expected_artifact_hash": expected_artifact_hash_normalized,
        "observed_artifact_hash": observed_artifact_hash_normalized,
        "destination_artifact_exists": destination_artifact_exists,
        "destination_artifact_matches_expected": destination_artifact_matches_expected,
        "destination_state": destination_state,
        "blockers": blockers,
    }
    receipt_hash = _canonical_hash(identity)

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_DUPLICATE_SAFE_RECEIPT_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_duplicate_safe_receipt",
        "receipt_id": f"origin-evidence-duplicate-safe-receipt:{receipt_hash}",
        "receipt_hash": receipt_hash,
        "adapter_result_id": adapter_result.get("adapter_result_id"),
        "adapter_result_hash": adapter_result_hash,
        "execution_plan_hash": execution_plan_hash,
        "observed_at": observed_at,
        "artifact_relpath": artifact_relpath,
        "dedupe_key": dedupe_key,
        "expected_artifact_hash": expected_artifact_hash_normalized,
        "observed_artifact_hash": observed_artifact_hash_normalized,
        "destination_artifact_exists": destination_artifact_exists,
        "destination_artifact_matches_expected": destination_artifact_matches_expected,
        "destination_state": destination_state,
        "blockers": blockers,
        "write_may_be_considered_by_separate_step": write_may_be_considered,
        "duplicate_safely_satisfied": duplicate_safely_satisfied,
        "conflict_detected": conflict_detected,
        "inconsistent_observation": inconsistent_observation,
        "receipt_is_authorization": False,
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
