# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_execution_boundary.py
# desc: MR-F6.18 pure final authorization boundary for one origin-evidence request. No writer import or write.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_origin_evidence_execution_request import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION,
)

MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION = (
    "prediction.market_regime.origin_evidence_execution_boundary.mr_f6_18.v1"
)


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


def _canonical_hash(payload: Mapping[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _recompute_request_hash(request: Mapping[str, Any]) -> str:
    review = request.get("review")
    if not isinstance(review, Mapping):
        raise ValueError("origin_evidence_execution_boundary_review_missing")
    identity = {
        "prediction_origin": request.get("prediction_origin"),
        "feature_snapshot_ref": request.get("feature_snapshot_ref"),
        "shadow_candidate_id": request.get("shadow_candidate_id"),
        "origin_feature_parameter_set_id": request.get("origin_feature_parameter_set_id"),
        "target_horizons_sec": tuple(request.get("target_horizons_sec") or ()),
        "bundle_ids": tuple(request.get("bundle_ids") or ()),
        "write_plan_bundle_ids": tuple(request.get("write_plan_bundle_ids") or ()),
        "forecast_parameter_set_ids": tuple(
            request.get("forecast_parameter_set_ids") or ()
        ),
        "dedupe_key": request.get("dedupe_key"),
        "artifact_relpath": request.get("artifact_relpath"),
        "writer_id": request.get("writer_id"),
        "writer_contract_version": request.get("writer_contract_version"),
        "writer_contract_schema_version": request.get("writer_contract_schema_version"),
        "approval_id": request.get("approval_id"),
        "approval_requested_at": request.get("approval_requested_at"),
        "approval_expires_at": request.get("approval_expires_at"),
        "preflight_executed_at": request.get("preflight_executed_at"),
        "requested_at": request.get("requested_at"),
        "reviewer_ids": tuple(review.get("reviewer_ids") or ()),
        "reviewed_at": review.get("reviewed_at"),
        "preflight_reviewed": review.get("preflight_reviewed"),
        "bundle_identity_reviewed": review.get("bundle_identity_reviewed"),
        "destination_reviewed": review.get("destination_reviewed"),
        "duplicate_prevention_reviewed": review.get("duplicate_prevention_reviewed"),
        "append_only_reviewed": review.get("append_only_reviewed"),
        "canonical_isolation_reviewed": review.get("canonical_isolation_reviewed"),
        "one_shot_scope_reviewed": review.get("one_shot_scope_reviewed"),
        "review_complete": review.get("review_complete"),
        "request_ready_for_separate_execution": request.get("request_ready_for_separate_execution"),
        "blockers": tuple(request.get("blockers") or ()),
        "one_shot_execution_requested": request.get("one_shot_execution_requested"),
    }
    return _canonical_hash(identity)


def build_origin_evidence_execution_boundary(
    *,
    execution_request: Mapping[str, Any],
    evaluated_at: str,
    destination_artifact_exists: bool,
    destination_artifact_matches_request: bool,
    expected_request_hash: str,
    expected_writer_id: str,
    expected_writer_contract_version: str,
    enabled_acknowledgement: bool = False,
    once_acknowledgement: bool = False,
) -> Mapping[str, Any]:
    if not isinstance(execution_request, Mapping):
        raise ValueError("origin_evidence_execution_boundary_request_type_invalid")
    expected_request_hash = str(expected_request_hash or "").strip()
    expected_writer_id = str(expected_writer_id or "").strip()
    expected_writer_contract_version = str(expected_writer_contract_version or "").strip()
    if not expected_request_hash:
        raise ValueError("origin_evidence_execution_boundary_expected_request_hash_missing")
    if not expected_writer_id or not expected_writer_contract_version:
        raise ValueError("origin_evidence_execution_boundary_expected_writer_scope_missing")
    if execution_request.get("schema_version") != MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION:
        raise ValueError("origin_evidence_execution_boundary_request_schema_mismatch")
    if execution_request.get("artifact_kind") != "future_origin_evidence_one_shot_execution_request":
        raise ValueError("origin_evidence_execution_boundary_request_kind_mismatch")
    for field, value in (
        ("destination_artifact_exists", destination_artifact_exists),
        ("destination_artifact_matches_request", destination_artifact_matches_request),
        ("enabled_acknowledgement", enabled_acknowledgement),
        ("once_acknowledgement", once_acknowledgement),
    ):
        if type(value) is not bool:
            raise ValueError(f"origin_evidence_execution_boundary_boolean_invalid:{field}")

    if destination_artifact_matches_request and not destination_artifact_exists:
        raise ValueError(
            "origin_evidence_execution_boundary_destination_state_inconsistent"
        )

    evaluated = _parse_canonical_utc(
        evaluated_at,
        "origin_evidence_execution_boundary_evaluated_at_invalid",
    )
    requested = _parse_canonical_utc(
        str(execution_request.get("requested_at") or ""),
        "origin_evidence_execution_boundary_requested_at_invalid",
    )
    approval_requested = _parse_canonical_utc(
        str(execution_request.get("approval_requested_at") or ""),
        "origin_evidence_execution_boundary_approval_requested_at_invalid",
    )
    approval_expires = _parse_canonical_utc(
        str(execution_request.get("approval_expires_at") or ""),
        "origin_evidence_execution_boundary_approval_expires_at_invalid",
    )
    preflight_executed = _parse_canonical_utc(
        str(execution_request.get("preflight_executed_at") or ""),
        "origin_evidence_execution_boundary_preflight_executed_at_invalid",
    )
    if approval_expires <= approval_requested:
        raise ValueError("origin_evidence_execution_boundary_approval_window_invalid")

    review = execution_request.get("review")
    if not isinstance(review, Mapping):
        raise ValueError("origin_evidence_execution_boundary_review_missing")
    reviewed = _parse_canonical_utc(
        str(review.get("reviewed_at") or ""),
        "origin_evidence_execution_boundary_reviewed_at_invalid",
    )
    if preflight_executed < approval_requested or preflight_executed >= approval_expires:
        raise ValueError("origin_evidence_execution_boundary_preflight_outside_approval_window")
    if reviewed < preflight_executed:
        raise ValueError("origin_evidence_execution_boundary_review_before_preflight")
    if reviewed > requested:
        raise ValueError("origin_evidence_execution_boundary_review_after_request")

    request_hash = str(execution_request.get("request_hash") or "").strip()
    request_id = str(execution_request.get("request_id") or "").strip()
    recomputed_hash = _recompute_request_hash(execution_request)
    if request_hash != recomputed_hash:
        raise ValueError("origin_evidence_execution_boundary_request_hash_mismatch")
    if request_hash != expected_request_hash:
        raise PermissionError("origin_evidence_execution_boundary_external_request_hash_mismatch")
    if request_id != f"origin-evidence-execution-request:{request_hash}":
        raise ValueError("origin_evidence_execution_boundary_request_id_mismatch")

    writer_id = str(execution_request.get("writer_id") or "").strip()
    writer_contract_version = str(
        execution_request.get("writer_contract_version") or ""
    ).strip()
    if (
        writer_id != expected_writer_id
        or writer_contract_version != expected_writer_contract_version
    ):
        raise PermissionError("origin_evidence_execution_boundary_writer_scope_mismatch")

    horizons = tuple(execution_request.get("target_horizons_sec") or ())
    bundle_ids = tuple(str(item) for item in execution_request.get("bundle_ids") or ())
    write_plan_bundle_ids = tuple(
        str(item) for item in execution_request.get("write_plan_bundle_ids") or ()
    )
    if horizons != FUTURE_MARKET_REGIME_HORIZONS_SEC:
        raise ValueError("origin_evidence_execution_boundary_horizons_invalid")
    if (
        len(bundle_ids) != len(horizons)
        or len(set(bundle_ids)) != len(bundle_ids)
        or len(write_plan_bundle_ids) != len(bundle_ids)
        or len(set(write_plan_bundle_ids)) != len(write_plan_bundle_ids)
        or set(write_plan_bundle_ids) != set(bundle_ids)
    ):
        raise ValueError("origin_evidence_execution_boundary_bundle_identity_invalid")

    blockers: list[str] = []
    review_flags = (
        "preflight_reviewed",
        "bundle_identity_reviewed",
        "destination_reviewed",
        "duplicate_prevention_reviewed",
        "append_only_reviewed",
        "canonical_isolation_reviewed",
        "one_shot_scope_reviewed",
        "review_complete",
    )
    for field in review_flags:
        if review.get(field) is not True:
            blockers.append(f"review_not_complete:{field}")
    required_true = (
        "request_ready_for_separate_execution",
        "one_shot_execution_requested",
        "human_gate_required",
    )
    for field in required_true:
        if execution_request.get(field) is not True:
            blockers.append(f"request_not_ready:{field}")
    required_false = (
        "execution_authorized_by_this_artifact",
        "enabled_acknowledgement_present",
        "once_acknowledgement_present",
        "writer_imported",
        "writer_invoked",
        "execution_performed",
        "writes_dhot",
        "scheduler_enabled",
        "counts_as_real_shadow_evidence",
        "candidate_selection_performed",
        "live_parameter_apply_allowed",
        "auto_promotion_allowed",
        "canonical_replacement_allowed",
    )
    for field in required_false:
        if execution_request.get(field) is not False:
            blockers.append(f"unsafe_request_flag:{field}")
    if execution_request.get("blockers") != ():
        blockers.append("request_blockers_present")
    if evaluated < requested:
        blockers.append("evaluation_before_request")
    if evaluated < approval_requested:
        blockers.append("approval_not_yet_valid")
    if evaluated >= approval_expires:
        blockers.append("approval_expired")
    if not enabled_acknowledgement:
        blockers.append("enabled_acknowledgement_missing")
    if not once_acknowledgement:
        blockers.append("once_acknowledgement_missing")
    if destination_artifact_exists and not destination_artifact_matches_request:
        blockers.append("destination_artifact_conflict")
    if destination_artifact_exists and destination_artifact_matches_request:
        blockers.append("destination_artifact_already_satisfied")

    authorization_ready = not blockers
    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_one_shot_execution_boundary",
        "request_id": request_id,
        "request_hash": request_hash,
        "expected_request_hash": expected_request_hash,
        "writer_id": writer_id,
        "writer_contract_version": writer_contract_version,
        "evaluated_at": evaluated_at,
        "approval_id": execution_request.get("approval_id"),
        "approval_requested_at": execution_request.get("approval_requested_at"),
        "approval_expires_at": execution_request.get("approval_expires_at"),
        "artifact_relpath": execution_request.get("artifact_relpath"),
        "dedupe_key": execution_request.get("dedupe_key"),
        "bundle_ids": tuple(execution_request.get("bundle_ids") or ()),
        "enabled_acknowledgement_present": enabled_acknowledgement,
        "once_acknowledgement_present": once_acknowledgement,
        "destination_artifact_exists": destination_artifact_exists,
        "destination_artifact_matches_request": destination_artifact_matches_request,
        "authorization_ready_for_separate_writer_call": authorization_ready,
        "blockers": tuple(blockers),
        "decision": "separate_writer_call_may_be_considered" if authorization_ready else "no_execution",
        "execution_authorized_by_this_artifact": False,
        "writer_imported": False,
        "writer_invoked": False,
        "execution_performed": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "counts_as_real_shadow_evidence": False,
        "candidate_selection_performed": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
        "human_gate_required": True,
    })
