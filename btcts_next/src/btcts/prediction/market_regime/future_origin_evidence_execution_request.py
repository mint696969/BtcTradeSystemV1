# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_execution_request.py
# desc: MR-F6.17 immutable human-review request for one explicit origin-evidence batch. No writer import or execution.

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_origin_evidence_writer_preflight import (
    MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_PREFLIGHT_VERSION,
)

MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION = (
    "prediction.market_regime.origin_evidence_execution_request.mr_f6_17.v4"
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


@dataclass(frozen=True)
class OriginEvidenceExecutionReview:
    reviewer_ids: Tuple[str, ...]
    reviewed_at: str
    preflight_reviewed: bool
    bundle_identity_reviewed: bool
    destination_reviewed: bool
    duplicate_prevention_reviewed: bool
    append_only_reviewed: bool
    canonical_isolation_reviewed: bool
    one_shot_scope_reviewed: bool

    def __post_init__(self) -> None:
        reviewers = tuple(dict.fromkeys(str(item).strip() for item in self.reviewer_ids))
        if not reviewers or any(not item for item in reviewers):
            raise ValueError("origin_evidence_execution_request_reviewer_missing")
        object.__setattr__(self, "reviewer_ids", reviewers)
        _parse_canonical_utc(
            self.reviewed_at,
            "origin_evidence_execution_request_reviewed_at_invalid",
        )
        for field in (
            "preflight_reviewed",
            "bundle_identity_reviewed",
            "destination_reviewed",
            "duplicate_prevention_reviewed",
            "append_only_reviewed",
            "canonical_isolation_reviewed",
            "one_shot_scope_reviewed",
        ):
            if type(getattr(self, field)) is not bool:
                raise ValueError(
                    f"origin_evidence_execution_request_review_flag_invalid:{field}"
                )

    @property
    def complete(self) -> bool:
        return all((
            self.preflight_reviewed,
            self.bundle_identity_reviewed,
            self.destination_reviewed,
            self.duplicate_prevention_reviewed,
            self.append_only_reviewed,
            self.canonical_isolation_reviewed,
            self.one_shot_scope_reviewed,
        ))

    def to_dict(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "reviewer_ids": self.reviewer_ids,
            "reviewed_at": self.reviewed_at,
            "preflight_reviewed": self.preflight_reviewed,
            "bundle_identity_reviewed": self.bundle_identity_reviewed,
            "destination_reviewed": self.destination_reviewed,
            "duplicate_prevention_reviewed": self.duplicate_prevention_reviewed,
            "append_only_reviewed": self.append_only_reviewed,
            "canonical_isolation_reviewed": self.canonical_isolation_reviewed,
            "one_shot_scope_reviewed": self.one_shot_scope_reviewed,
            "review_complete": self.complete,
        })


def build_origin_evidence_execution_request(
    *,
    preflight_artifact: Mapping[str, Any],
    review: OriginEvidenceExecutionReview,
    requested_at: str,
) -> Mapping[str, Any]:
    if not isinstance(preflight_artifact, Mapping):
        raise ValueError("origin_evidence_execution_request_preflight_type_invalid")
    if preflight_artifact.get("schema_version") != MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_PREFLIGHT_VERSION:
        raise ValueError("origin_evidence_execution_request_preflight_schema_mismatch")
    if preflight_artifact.get("artifact_kind") != "future_origin_evidence_single_batch_writer_preflight":
        raise ValueError("origin_evidence_execution_request_preflight_kind_mismatch")
    if not isinstance(review, OriginEvidenceExecutionReview):
        raise ValueError("origin_evidence_execution_request_review_type_invalid")
    requested = _parse_canonical_utc(
        requested_at,
        "origin_evidence_execution_request_requested_at_invalid",
    )
    reviewed = _parse_canonical_utc(
        review.reviewed_at,
        "origin_evidence_execution_request_reviewed_at_invalid",
    )
    if reviewed > requested:
        raise ValueError("origin_evidence_execution_request_review_after_request")

    required_true = (
        "single_origin_batch",
        "preflight_only",
        "approval_present",
        "preflight_ready",
    )
    for field in required_true:
        if preflight_artifact.get(field) is not True:
            raise ValueError(f"origin_evidence_execution_request_preflight_not_ready:{field}")
    required_false = (
        "write_allowed",
        "would_write",
        "writer_invoked",
        "write_execution_performed",
        "writes_dhot",
        "scheduler_enabled",
        "counts_as_real_shadow_evidence",
        "candidate_selection_performed",
        "live_parameter_apply_allowed",
        "auto_promotion_allowed",
        "canonical_replacement_allowed",
    )
    for field in required_false:
        if preflight_artifact.get(field) is not False:
            raise ValueError(f"origin_evidence_execution_request_unsafe_preflight_flag:{field}")
    if preflight_artifact.get("blockers") != ():
        raise ValueError("origin_evidence_execution_request_preflight_blockers_present")

    horizons = tuple(preflight_artifact.get("target_horizons_sec") or ())
    bundle_ids = tuple(str(item) for item in preflight_artifact.get("bundle_ids") or ())
    if horizons != FUTURE_MARKET_REGIME_HORIZONS_SEC:
        raise ValueError("origin_evidence_execution_request_horizons_invalid")
    if len(bundle_ids) != len(horizons) or len(set(bundle_ids)) != len(bundle_ids):
        raise ValueError("origin_evidence_execution_request_bundle_ids_invalid")

    plan = preflight_artifact.get("write_plan")
    nested = preflight_artifact.get("writer_preflight")
    if not isinstance(plan, Mapping) or not isinstance(nested, Mapping):
        raise ValueError("origin_evidence_execution_request_nested_preflight_missing")
    if nested.get("preflight_only") is not True or nested.get("write_allowed") is not True:
        raise ValueError("origin_evidence_execution_request_nested_preflight_not_approved")
    if nested.get("would_write") is not False:
        raise ValueError("origin_evidence_execution_request_nested_preflight_would_write_invalid")
    plan_bundle_ids = tuple(str(item) for item in plan.get("bundle_ids") or ())
    if (
        len(plan_bundle_ids) != len(bundle_ids)
        or len(set(plan_bundle_ids)) != len(plan_bundle_ids)
        or set(plan_bundle_ids) != set(bundle_ids)
    ):
        raise ValueError("origin_evidence_execution_request_plan_bundle_identity_mismatch")
    if int(plan.get("row_count") or 0) != len(bundle_ids):
        raise ValueError("origin_evidence_execution_request_plan_row_count_mismatch")
    if nested.get("dedupe_key") != plan.get("dedupe_key"):
        raise ValueError("origin_evidence_execution_request_dedupe_key_mismatch")
    if nested.get("row_count") != plan.get("row_count"):
        raise ValueError("origin_evidence_execution_request_nested_row_count_mismatch")

    approval_requested_at = str(preflight_artifact.get("approval_requested_at") or "").strip()
    approval_expires_at = str(preflight_artifact.get("approval_expires_at") or "").strip()
    preflight_executed_at = str(preflight_artifact.get("preflight_executed_at") or "").strip()
    approval_requested = _parse_canonical_utc(
        approval_requested_at,
        "origin_evidence_execution_request_approval_requested_at_invalid",
    )
    approval_expires = _parse_canonical_utc(
        approval_expires_at,
        "origin_evidence_execution_request_approval_expires_at_invalid",
    )
    preflight_executed = _parse_canonical_utc(
        preflight_executed_at,
        "origin_evidence_execution_request_preflight_executed_at_invalid",
    )
    if approval_expires <= approval_requested:
        raise ValueError("origin_evidence_execution_request_approval_window_invalid")
    if preflight_executed < approval_requested or preflight_executed >= approval_expires:
        raise ValueError("origin_evidence_execution_request_preflight_outside_approval_window")
    if requested < approval_requested or requested >= approval_expires:
        raise PermissionError("origin_evidence_execution_request_approval_not_active")
    if reviewed < preflight_executed:
        raise ValueError("origin_evidence_execution_request_review_before_preflight")
    if requested < preflight_executed:
        raise ValueError("origin_evidence_execution_request_before_preflight")

    approval_id = str(nested.get("approval_id") or "").strip()
    artifact_relpath = str(nested.get("artifact_relpath") or "").strip()
    dedupe_key = str(plan.get("dedupe_key") or "").strip()
    writer_id = str(plan.get("writer_id") or "").strip()
    writer_contract_version = str(plan.get("writer_contract_version") or "").strip()
    writer_contract_schema_version = str(
        preflight_artifact.get("writer_contract_schema_version") or ""
    ).strip()
    if (
        not approval_id
        or not artifact_relpath
        or not dedupe_key
        or not writer_id
        or not writer_contract_version
        or not writer_contract_schema_version
    ):
        raise ValueError("origin_evidence_execution_request_identity_missing")

    identity = {
        "prediction_origin": str(preflight_artifact["prediction_origin"]),
        "feature_snapshot_ref": str(preflight_artifact["feature_snapshot_ref"]),
        "shadow_candidate_id": str(preflight_artifact["shadow_candidate_id"]),
        "origin_feature_parameter_set_id": str(
            preflight_artifact["origin_feature_parameter_set_id"]
        ),
        "target_horizons_sec": horizons,
        "bundle_ids": bundle_ids,
        "write_plan_bundle_ids": plan_bundle_ids,
        "forecast_parameter_set_ids": tuple(
            preflight_artifact.get("forecast_parameter_set_ids") or ()
        ),
        "dedupe_key": dedupe_key,
        "artifact_relpath": artifact_relpath,
        "writer_id": writer_id,
        "writer_contract_version": writer_contract_version,
        "writer_contract_schema_version": writer_contract_schema_version,
        "approval_id": approval_id,
        "approval_requested_at": approval_requested_at,
        "approval_expires_at": approval_expires_at,
        "preflight_executed_at": preflight_executed_at,
        "requested_at": requested_at,
        "reviewer_ids": review.reviewer_ids,
        "reviewed_at": review.reviewed_at,
        "preflight_reviewed": review.preflight_reviewed,
        "bundle_identity_reviewed": review.bundle_identity_reviewed,
        "destination_reviewed": review.destination_reviewed,
        "duplicate_prevention_reviewed": review.duplicate_prevention_reviewed,
        "append_only_reviewed": review.append_only_reviewed,
        "canonical_isolation_reviewed": review.canonical_isolation_reviewed,
        "one_shot_scope_reviewed": review.one_shot_scope_reviewed,
        "review_complete": review.complete,
        "request_ready_for_separate_execution": review.complete,
        "blockers": () if review.complete else ("human_review_incomplete",),
        "one_shot_execution_requested": review.complete,
    }
    request_hash = _canonical_hash(identity)
    blockers = identity["blockers"]

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_one_shot_execution_request",
        "request_id": f"origin-evidence-execution-request:{request_hash}",
        "request_hash": request_hash,
        "requested_at": requested_at,
        "prediction_origin": identity["prediction_origin"],
        "feature_snapshot_ref": identity["feature_snapshot_ref"],
        "shadow_candidate_id": identity["shadow_candidate_id"],
        "origin_feature_parameter_set_id": identity["origin_feature_parameter_set_id"],
        "forecast_parameter_set_ids": tuple(
            preflight_artifact.get("forecast_parameter_set_ids") or ()
        ),
        "target_horizons_sec": horizons,
        "bundle_ids": bundle_ids,
        "write_plan_bundle_ids": plan_bundle_ids,
        "dedupe_key": dedupe_key,
        "artifact_relpath": artifact_relpath,
        "writer_id": writer_id,
        "writer_contract_version": writer_contract_version,
        "writer_contract_schema_version": writer_contract_schema_version,
        "approval_id": approval_id,
        "approval_requested_at": approval_requested_at,
        "approval_expires_at": approval_expires_at,
        "preflight_executed_at": preflight_executed_at,
        "review": review.to_dict(),
        "request_ready_for_separate_execution": review.complete,
        "blockers": blockers,
        "one_shot_execution_requested": review.complete,
        "execution_authorized_by_this_artifact": False,
        "enabled_acknowledgement_present": False,
        "once_acknowledgement_present": False,
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
