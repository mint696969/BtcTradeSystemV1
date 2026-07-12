# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_execution_boundary.py
# desc: Pure MR-F5.10 shadow-evidence execution boundary and operator-approval checklist. No runtime reads or writes.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Tuple

MARKET_REGIME_FUTURE_SHADOW_EXECUTION_BOUNDARY_VERSION = "prediction.market_regime.future_shadow_execution_boundary.mr_f5_10.v1"


class FutureShadowExecutionMode(str, Enum):
    DISCOVERY_ONLY = "discovery_only"
    DESIGN_REVIEW = "design_review"
    APPROVED_SHADOW_WRITE = "approved_shadow_write"


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


def _non_empty_tuple(values: Tuple[str, ...], error: str) -> Tuple[str, ...]:
    normalized = tuple(dict.fromkeys(str(item).strip() for item in values))
    if not normalized or any(not item for item in normalized):
        raise ValueError(error)
    return normalized


@dataclass(frozen=True)
class FutureShadowWriterDesign:
    writer_id: str
    writer_contract_version: str
    source_role: str
    destination_role: str
    artifact_family: str
    artifact_kind: str
    retention_policy_ref: str
    rollback_plan_ref: str
    dry_run_evidence_refs: Tuple[str, ...]
    duplicate_prevention_verified: bool
    atomic_write_verified: bool
    append_only_verified: bool
    canonical_isolation_verified: bool

    def __post_init__(self) -> None:
        for name in (
            "writer_id", "writer_contract_version", "source_role", "destination_role",
            "artifact_family", "artifact_kind", "retention_policy_ref", "rollback_plan_ref",
        ):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"future_shadow_execution_identity_missing:{name}")
        if self.source_role != "hot_data_root" or self.destination_role != "hot_data_root":
            raise ValueError("future_shadow_execution_data_role_invalid")
        if self.artifact_family != "prediction/market_regime" or self.artifact_kind != "future_shadow_evidence":
            raise ValueError("future_shadow_execution_artifact_identity_invalid")
        object.__setattr__(self, "dry_run_evidence_refs", _non_empty_tuple(
            self.dry_run_evidence_refs, "future_shadow_execution_dry_run_evidence_missing"
        ))
        for name in (
            "duplicate_prevention_verified", "atomic_write_verified", "append_only_verified",
            "canonical_isolation_verified",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"future_shadow_execution_design_boolean_invalid:{name}")


@dataclass(frozen=True)
class FutureShadowOperatorApproval:
    approval_id: str
    operator_ids: Tuple[str, ...]
    requested_at: str
    expires_at: str
    approved_writer_id: str
    approved_writer_contract_version: str
    approved_artifact_family: str
    approved_artifact_kind: str
    approved_source_role: str
    approved_destination_role: str
    approval_artifact_refs: Tuple[str, ...]
    dry_run_reviewed: bool
    retention_reviewed: bool
    rollback_reviewed: bool
    canonical_isolation_reviewed: bool
    limited_shadow_scope_reviewed: bool

    def __post_init__(self) -> None:
        for name in (
            "approval_id", "approved_writer_id", "approved_writer_contract_version",
            "approved_artifact_family", "approved_artifact_kind",
            "approved_source_role", "approved_destination_role",
        ):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"future_shadow_execution_approval_identity_missing:{name}")
        object.__setattr__(self, "operator_ids", _non_empty_tuple(
            self.operator_ids, "future_shadow_execution_operator_missing"
        ))
        object.__setattr__(self, "approval_artifact_refs", _non_empty_tuple(
            self.approval_artifact_refs, "future_shadow_execution_approval_ref_missing"
        ))
        requested = _parse_canonical_utc(self.requested_at, "future_shadow_execution_requested_at_invalid")
        expires = _parse_canonical_utc(self.expires_at, "future_shadow_execution_expires_at_invalid")
        if expires <= requested:
            raise ValueError("future_shadow_execution_approval_window_invalid")
        for name in (
            "dry_run_reviewed", "retention_reviewed", "rollback_reviewed",
            "canonical_isolation_reviewed", "limited_shadow_scope_reviewed",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"future_shadow_execution_approval_boolean_invalid:{name}")


def build_market_regime_future_shadow_execution_boundary(
    *,
    mode: FutureShadowExecutionMode,
    writer_design: FutureShadowWriterDesign | None,
    operator_approval: FutureShadowOperatorApproval | None,
    evaluated_at: str,
) -> Mapping[str, Any]:
    if not isinstance(mode, FutureShadowExecutionMode):
        raise ValueError("future_shadow_execution_mode_invalid")

    evaluated = _parse_canonical_utc(
        evaluated_at, "future_shadow_execution_evaluated_at_invalid"
    )

    blockers: list[str] = []
    if writer_design is None:
        blockers.append("writer_design_absent")
    else:
        for name in (
            "duplicate_prevention_verified", "atomic_write_verified", "append_only_verified",
            "canonical_isolation_verified",
        ):
            if getattr(writer_design, name) is not True:
                blockers.append(f"writer_design_incomplete:{name}")

    if operator_approval is None:
        blockers.append("operator_approval_absent")
    elif writer_design is not None:
        requested = _parse_canonical_utc(
            operator_approval.requested_at, "future_shadow_execution_requested_at_invalid"
        )
        expires = _parse_canonical_utc(
            operator_approval.expires_at, "future_shadow_execution_expires_at_invalid"
        )
        if evaluated < requested:
            blockers.append("operator_approval_not_yet_valid")
        if evaluated >= expires:
            blockers.append("operator_approval_expired")
        scope_pairs = (
            (operator_approval.approved_writer_id, writer_design.writer_id, "writer_id"),
            (operator_approval.approved_writer_contract_version, writer_design.writer_contract_version, "writer_contract_version"),
            (operator_approval.approved_artifact_family, writer_design.artifact_family, "artifact_family"),
            (operator_approval.approved_artifact_kind, writer_design.artifact_kind, "artifact_kind"),
            (operator_approval.approved_source_role, writer_design.source_role, "source_role"),
            (operator_approval.approved_destination_role, writer_design.destination_role, "destination_role"),
        )
        for approved, designed, name in scope_pairs:
            if approved != designed:
                blockers.append(f"operator_approval_scope_mismatch:{name}")
        for name in (
            "dry_run_reviewed", "retention_reviewed", "rollback_reviewed",
            "canonical_isolation_reviewed", "limited_shadow_scope_reviewed",
        ):
            if getattr(operator_approval, name) is not True:
                blockers.append(f"operator_approval_incomplete:{name}")

    write_requested = mode is FutureShadowExecutionMode.APPROVED_SHADOW_WRITE
    write_allowed = write_requested and not blockers
    if not write_requested:
        blockers.append("write_mode_not_requested")

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_EXECUTION_BOUNDARY_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_execution_boundary",
        "mode": mode.value,
        "writer_design_present": writer_design is not None,
        "operator_approval_present": operator_approval is not None,
        "write_requested": write_requested,
        "write_allowed": write_allowed,
        "blockers": tuple(blockers),
        "decision": "approved_shadow_write_boundary_satisfied" if write_allowed else "no_write",
        "execution_performed": False,
        "approval_id": operator_approval.approval_id if operator_approval else "",
        "approval_requested_at": operator_approval.requested_at if operator_approval else "",
        "approval_expires_at": operator_approval.expires_at if operator_approval else "",
        "evaluated_at": evaluated_at,
        "writer_id": writer_design.writer_id if writer_design else "",
        "writer_contract_version": writer_design.writer_contract_version if writer_design else "",
        "safety": MappingProxyType({
            "pure_boundary_check": True,
            "runtime_reader_invoked": False,
            "writer_invoked": False,
            "writes_dhot": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "ui_change": False,
            "human_gate_required": True,
        }),
    })
