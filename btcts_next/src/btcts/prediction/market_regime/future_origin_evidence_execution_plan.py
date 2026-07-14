# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_execution_plan.py
# desc: MR-F6.19 deterministic immutable dry-run execution plan. No writer import or execution.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_origin_evidence_execution_boundary import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION,
)
from .future_origin_evidence_execution_request import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION,
)

MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_PLAN_VERSION = (
    "prediction.market_regime.origin_evidence_execution_plan.mr_f6_19.v2"
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


def _boundary_snapshot_hash(boundary: Mapping[str, Any]) -> str:
    payload = {
        "schema_version": boundary.get("schema_version"),
        "artifact_kind": boundary.get("artifact_kind"),
        "request_id": boundary.get("request_id"),
        "request_hash": boundary.get("request_hash"),
        "expected_request_hash": boundary.get("expected_request_hash"),
        "writer_id": boundary.get("writer_id"),
        "writer_contract_version": boundary.get("writer_contract_version"),
        "evaluated_at": boundary.get("evaluated_at"),
        "approval_id": boundary.get("approval_id"),
        "approval_requested_at": boundary.get("approval_requested_at"),
        "approval_expires_at": boundary.get("approval_expires_at"),
        "artifact_relpath": boundary.get("artifact_relpath"),
        "dedupe_key": boundary.get("dedupe_key"),
        "bundle_ids": tuple(boundary.get("bundle_ids") or ()),
        "enabled_acknowledgement_present": boundary.get("enabled_acknowledgement_present"),
        "once_acknowledgement_present": boundary.get("once_acknowledgement_present"),
        "destination_artifact_exists": boundary.get("destination_artifact_exists"),
        "destination_artifact_matches_request": boundary.get("destination_artifact_matches_request"),
        "authorization_ready_for_separate_writer_call": boundary.get("authorization_ready_for_separate_writer_call"),
        "blockers": tuple(boundary.get("blockers") or ()),
        "decision": boundary.get("decision"),
    }
    return _canonical_hash(payload)


def build_origin_evidence_dry_run_execution_plan(
    *,
    execution_request: Mapping[str, Any],
    execution_boundary: Mapping[str, Any],
    planned_at: str,
    expected_request_hash: str,
    expected_writer_id: str,
    expected_writer_contract_version: str,
) -> Mapping[str, Any]:
    if not isinstance(execution_request, Mapping):
        raise ValueError("origin_evidence_execution_plan_request_type_invalid")
    if not isinstance(execution_boundary, Mapping):
        raise ValueError("origin_evidence_execution_plan_boundary_type_invalid")
    if execution_request.get("schema_version") != MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION:
        raise ValueError("origin_evidence_execution_plan_request_schema_mismatch")
    if execution_request.get("artifact_kind") != "future_origin_evidence_one_shot_execution_request":
        raise ValueError("origin_evidence_execution_plan_request_kind_mismatch")
    if execution_boundary.get("schema_version") != MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION:
        raise ValueError("origin_evidence_execution_plan_boundary_schema_mismatch")
    if execution_boundary.get("artifact_kind") != "future_origin_evidence_one_shot_execution_boundary":
        raise ValueError("origin_evidence_execution_plan_boundary_kind_mismatch")

    planned = _parse_canonical_utc(
        planned_at,
        "origin_evidence_execution_plan_planned_at_invalid",
    )
    evaluated_at = str(execution_boundary.get("evaluated_at") or "").strip()
    evaluated = _parse_canonical_utc(
        evaluated_at,
        "origin_evidence_execution_plan_boundary_evaluated_at_invalid",
    )
    approval_expires_at = str(execution_request.get("approval_expires_at") or "").strip()
    approval_expires = _parse_canonical_utc(
        approval_expires_at,
        "origin_evidence_execution_plan_approval_expires_at_invalid",
    )
    if planned < evaluated:
        raise ValueError("origin_evidence_execution_plan_before_boundary")
    if planned >= approval_expires:
        raise PermissionError("origin_evidence_execution_plan_approval_expired")

    expected_request_hash = str(expected_request_hash or "").strip()
    expected_writer_id = str(expected_writer_id or "").strip()
    expected_writer_contract_version = str(expected_writer_contract_version or "").strip()
    if not expected_request_hash:
        raise ValueError("origin_evidence_execution_plan_expected_request_hash_missing")
    if not expected_writer_id or not expected_writer_contract_version:
        raise ValueError("origin_evidence_execution_plan_expected_writer_scope_missing")

    request_id = str(execution_request.get("request_id") or "").strip()
    request_hash = str(execution_request.get("request_hash") or "").strip()
    if not request_id or not request_hash:
        raise ValueError("origin_evidence_execution_plan_request_identity_missing")
    if request_hash != expected_request_hash:
        raise PermissionError("origin_evidence_execution_plan_external_request_hash_mismatch")
    if execution_boundary.get("request_id") != request_id:
        raise ValueError("origin_evidence_execution_plan_boundary_request_id_mismatch")
    if execution_boundary.get("request_hash") != request_hash:
        raise ValueError("origin_evidence_execution_plan_boundary_request_hash_mismatch")
    if execution_boundary.get("expected_request_hash") != expected_request_hash:
        raise ValueError("origin_evidence_execution_plan_boundary_expected_hash_mismatch")

    writer_id = str(execution_request.get("writer_id") or "").strip()
    writer_contract_version = str(
        execution_request.get("writer_contract_version") or ""
    ).strip()
    if writer_id != expected_writer_id or writer_contract_version != expected_writer_contract_version:
        raise PermissionError("origin_evidence_execution_plan_writer_scope_mismatch")
    if execution_boundary.get("writer_id") != writer_id:
        raise ValueError("origin_evidence_execution_plan_boundary_writer_id_mismatch")
    if execution_boundary.get("writer_contract_version") != writer_contract_version:
        raise ValueError("origin_evidence_execution_plan_boundary_writer_contract_mismatch")

    required_true = (
        "authorization_ready_for_separate_writer_call",
        "enabled_acknowledgement_present",
        "once_acknowledgement_present",
        "human_gate_required",
    )
    for field in required_true:
        if execution_boundary.get(field) is not True:
            raise ValueError(f"origin_evidence_execution_plan_boundary_not_ready:{field}")
    required_false = (
        "execution_authorized_by_this_artifact",
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
        if execution_boundary.get(field) is not False:
            raise ValueError(f"origin_evidence_execution_plan_unsafe_boundary_flag:{field}")
    if execution_boundary.get("blockers") != ():
        raise ValueError("origin_evidence_execution_plan_boundary_blockers_present")
    if execution_boundary.get("decision") != "separate_writer_call_may_be_considered":
        raise ValueError("origin_evidence_execution_plan_boundary_decision_invalid")
    if execution_boundary.get("destination_artifact_exists") is not False:
        raise ValueError("origin_evidence_execution_plan_destination_not_absent")
    if execution_boundary.get("destination_artifact_matches_request") is not False:
        raise ValueError("origin_evidence_execution_plan_destination_match_invalid")

    horizons = tuple(execution_request.get("target_horizons_sec") or ())
    bundle_ids = tuple(str(item) for item in execution_request.get("bundle_ids") or ())
    write_plan_bundle_ids = tuple(
        str(item) for item in execution_request.get("write_plan_bundle_ids") or ()
    )
    boundary_bundle_ids = tuple(
        str(item) for item in execution_boundary.get("bundle_ids") or ()
    )
    if horizons != FUTURE_MARKET_REGIME_HORIZONS_SEC:
        raise ValueError("origin_evidence_execution_plan_horizons_invalid")
    if (
        len(bundle_ids) != len(horizons)
        or len(set(bundle_ids)) != len(bundle_ids)
        or len(write_plan_bundle_ids) != len(bundle_ids)
        or len(set(write_plan_bundle_ids)) != len(write_plan_bundle_ids)
        or set(write_plan_bundle_ids) != set(bundle_ids)
        or boundary_bundle_ids != bundle_ids
    ):
        raise ValueError("origin_evidence_execution_plan_bundle_identity_invalid")

    approval_id = str(execution_request.get("approval_id") or "").strip()
    approval_requested_at = str(
        execution_request.get("approval_requested_at") or ""
    ).strip()
    if execution_boundary.get("approval_requested_at") != approval_requested_at:
        raise ValueError(
            "origin_evidence_execution_plan_boundary_identity_mismatch:approval_requested_at"
        )
    artifact_relpath = str(execution_request.get("artifact_relpath") or "").strip()
    dedupe_key = str(execution_request.get("dedupe_key") or "").strip()
    writer_contract_schema_version = str(
        execution_request.get("writer_contract_schema_version") or ""
    ).strip()
    if (
        not approval_id
        or not approval_requested_at
        or not artifact_relpath
        or not dedupe_key
        or not writer_contract_schema_version
    ):
        raise ValueError("origin_evidence_execution_plan_identity_missing")
    for field, value in (
        ("approval_id", approval_id),
        ("artifact_relpath", artifact_relpath),
        ("dedupe_key", dedupe_key),
    ):
        if execution_boundary.get(field) != value:
            raise ValueError(f"origin_evidence_execution_plan_boundary_identity_mismatch:{field}")

    boundary_hash = _boundary_snapshot_hash(execution_boundary)
    identity = {
        "request_id": request_id,
        "request_hash": request_hash,
        "boundary_snapshot_hash": boundary_hash,
        "planned_at": planned_at,
        "writer_id": writer_id,
        "writer_contract_version": writer_contract_version,
        "writer_contract_schema_version": writer_contract_schema_version,
        "approval_id": approval_id,
        "approval_requested_at": approval_requested_at,
        "approval_expires_at": approval_expires_at,
        "artifact_relpath": artifact_relpath,
        "dedupe_key": dedupe_key,
        "target_horizons_sec": horizons,
        "bundle_ids": bundle_ids,
        "write_plan_bundle_ids": write_plan_bundle_ids,
        "forecast_parameter_set_ids": tuple(
            execution_request.get("forecast_parameter_set_ids") or ()
        ),
        "enabled_acknowledgement_present": True,
        "once_acknowledgement_present": True,
        "destination_artifact_exists": False,
        "destination_artifact_matches_request": False,
    }
    plan_hash = _canonical_hash(identity)

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_PLAN_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_dry_run_execution_plan",
        "execution_plan_id": f"origin-evidence-execution-plan:{plan_hash}",
        "execution_plan_hash": plan_hash,
        "request_id": request_id,
        "request_hash": request_hash,
        "boundary_snapshot_hash": boundary_hash,
        "planned_at": planned_at,
        "writer_id": writer_id,
        "writer_contract_version": writer_contract_version,
        "writer_contract_schema_version": writer_contract_schema_version,
        "approval_id": approval_id,
        "approval_requested_at": approval_requested_at,
        "approval_expires_at": approval_expires_at,
        "artifact_relpath": artifact_relpath,
        "dedupe_key": dedupe_key,
        "target_horizons_sec": horizons,
        "bundle_ids": bundle_ids,
        "write_plan_bundle_ids": write_plan_bundle_ids,
        "forecast_parameter_set_ids": identity["forecast_parameter_set_ids"],
        "enabled_acknowledgement_present": True,
        "once_acknowledgement_present": True,
        "destination_artifact_exists": False,
        "destination_artifact_matches_request": False,
        "dry_run_only": True,
        "execution_plan_ready": True,
        "blockers": (),
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
