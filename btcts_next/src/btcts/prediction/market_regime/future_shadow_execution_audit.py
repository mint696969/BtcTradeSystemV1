# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_execution_audit.py
# desc: Pure MR-F5.13 D-hot shadow execution readiness and post-write evidence audit contract. No reads or writes.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Tuple

EXPECTED_ROW_SCHEMA = "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1"
EXPECTED_WRITER_VERSION = "prediction.market_regime.future_shadow_writer.mr_f5_12.v1"
EXPECTED_BOUNDARY_VERSION = "prediction.market_regime.future_shadow_execution_boundary.mr_f5_10.v1"
EXPECTED_DRY_RUN_VERSION = "prediction.market_regime.future_shadow_writer_dry_run.mr_f5_11.v1"
MARKET_REGIME_FUTURE_SHADOW_EXECUTION_AUDIT_VERSION = "prediction.market_regime.future_shadow_execution_audit.mr_f5_13.v1"


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


def _refs(values: Tuple[str, ...], error: str) -> Tuple[str, ...]:
    normalized = tuple(dict.fromkeys(str(item).strip() for item in values))
    if not normalized or any(not item for item in normalized):
        raise ValueError(error)
    return normalized


@dataclass(frozen=True)
class FutureShadowSourceAudit:
    inspected_at: str
    source_role: str
    source_artifact_refs: Tuple[str, ...]
    discovered_row_count: int
    canonical_row_count: int
    legacy_row_count: int
    exact_schema_row_count: int
    trace_identity_verified_count: int
    outcome_identity_verified_count: int
    lookahead_violation_count: int

    def __post_init__(self) -> None:
        _parse_canonical_utc(self.inspected_at, "future_shadow_execution_audit_inspected_at_invalid")
        if self.source_role != "hot_data_root":
            raise ValueError("future_shadow_execution_audit_source_role_invalid")
        object.__setattr__(self, "source_artifact_refs", _refs(
            self.source_artifact_refs, "future_shadow_execution_audit_source_refs_missing"
        ))
        values = (
            self.discovered_row_count, self.canonical_row_count, self.legacy_row_count,
            self.exact_schema_row_count, self.trace_identity_verified_count,
            self.outcome_identity_verified_count, self.lookahead_violation_count,
        )
        for value in values:
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("future_shadow_execution_audit_count_invalid")
        categorized = (
            self.canonical_row_count + self.legacy_row_count + self.exact_schema_row_count
        )
        if categorized > self.discovered_row_count:
            raise ValueError("future_shadow_execution_audit_source_count_mismatch")
        if self.trace_identity_verified_count > self.exact_schema_row_count:
            raise ValueError("future_shadow_execution_audit_trace_count_mismatch")
        if self.outcome_identity_verified_count > self.trace_identity_verified_count:
            raise ValueError("future_shadow_execution_audit_outcome_count_mismatch")


@dataclass(frozen=True)
class FutureShadowExecutionApprovalArtifact:
    approval_id: str
    operator_ids: Tuple[str, ...]
    approved_at: str
    expires_at: str
    boundary_schema_version: str
    dry_run_schema_version: str
    writer_version: str
    source_role: str
    destination_role: str
    approved_artifact_refs: Tuple[str, ...]
    retention_policy_ref: str
    rollback_plan_ref: str
    limited_batch_scope_ref: str
    preflight_artifact_ref: str
    operator_explicit_write_ack: bool

    def __post_init__(self) -> None:
        for name in (
            "approval_id", "boundary_schema_version", "dry_run_schema_version", "writer_version",
            "source_role", "destination_role", "retention_policy_ref", "rollback_plan_ref",
            "limited_batch_scope_ref", "preflight_artifact_ref",
        ):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"future_shadow_execution_approval_identity_missing:{name}")
        object.__setattr__(self, "operator_ids", _refs(
            self.operator_ids, "future_shadow_execution_approval_operator_missing"
        ))
        object.__setattr__(self, "approved_artifact_refs", _refs(
            self.approved_artifact_refs, "future_shadow_execution_approval_refs_missing"
        ))
        approved = _parse_canonical_utc(self.approved_at, "future_shadow_execution_approval_approved_at_invalid")
        expires = _parse_canonical_utc(self.expires_at, "future_shadow_execution_approval_expires_at_invalid")
        if expires <= approved:
            raise ValueError("future_shadow_execution_approval_window_invalid")
        if type(self.operator_explicit_write_ack) is not bool:
            raise ValueError("future_shadow_execution_approval_ack_invalid")


@dataclass(frozen=True)
class FutureShadowPostWriteAudit:
    audited_at: str
    artifact_ref: str
    artifact_schema_version: str
    writer_version: str
    row_count: int
    exact_schema_row_count: int
    trace_identity_verified_count: int
    outcome_identity_verified_count: int
    dedupe_key_verified: bool
    canonical_isolation_verified: bool
    append_only_verified: bool
    scheduler_disabled_verified: bool
    canonical_replacement_absent: bool

    def __post_init__(self) -> None:
        _parse_canonical_utc(self.audited_at, "future_shadow_post_write_audited_at_invalid")
        for name in ("artifact_ref", "artifact_schema_version", "writer_version"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"future_shadow_post_write_identity_missing:{name}")
        for value in (
            self.row_count, self.exact_schema_row_count,
            self.trace_identity_verified_count, self.outcome_identity_verified_count,
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("future_shadow_post_write_count_invalid")
        if not (
            self.outcome_identity_verified_count <= self.trace_identity_verified_count
            <= self.exact_schema_row_count <= self.row_count
        ):
            raise ValueError("future_shadow_post_write_count_mismatch")
        for name in (
            "dedupe_key_verified", "canonical_isolation_verified", "append_only_verified",
            "scheduler_disabled_verified", "canonical_replacement_absent",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"future_shadow_post_write_boolean_invalid:{name}")


def build_market_regime_future_shadow_execution_audit(
    *,
    source_audit: FutureShadowSourceAudit,
    approval: FutureShadowExecutionApprovalArtifact | None,
    post_write_audit: FutureShadowPostWriteAudit | None,
    evaluated_at: str,
) -> Mapping[str, Any]:
    evaluated = _parse_canonical_utc(evaluated_at, "future_shadow_execution_audit_evaluated_at_invalid")
    blockers: list[str] = []

    if source_audit.exact_schema_row_count <= 0:
        blockers.append("exact_future_shadow_rows_absent")
    if source_audit.trace_identity_verified_count != source_audit.exact_schema_row_count:
        blockers.append("trace_identity_not_fully_verified")
    if source_audit.outcome_identity_verified_count != source_audit.exact_schema_row_count:
        blockers.append("outcome_identity_not_fully_verified")
    if source_audit.lookahead_violation_count != 0:
        blockers.append("lookahead_violation_present")
    if (
        source_audit.exact_schema_row_count == 0
        and (source_audit.canonical_row_count or source_audit.legacy_row_count)
    ):
        blockers.append("legacy_or_canonical_rows_not_eligible_as_shadow_evidence")

    if approval is None:
        blockers.append("operator_execution_approval_absent")
    else:
        if approval.boundary_schema_version != EXPECTED_BOUNDARY_VERSION:
            blockers.append("approval_boundary_version_mismatch")
        if approval.dry_run_schema_version != EXPECTED_DRY_RUN_VERSION:
            blockers.append("approval_dry_run_version_mismatch")
        if approval.writer_version != EXPECTED_WRITER_VERSION:
            blockers.append("approval_writer_version_mismatch")
        if approval.source_role != "hot_data_root" or approval.destination_role != "hot_data_root":
            blockers.append("approval_data_role_mismatch")
        if approval.operator_explicit_write_ack is not True:
            blockers.append("operator_explicit_write_ack_absent")
        approved = _parse_canonical_utc(approval.approved_at, "future_shadow_execution_approval_approved_at_invalid")
        expires = _parse_canonical_utc(approval.expires_at, "future_shadow_execution_approval_expires_at_invalid")
        if evaluated < approved:
            blockers.append("operator_approval_not_yet_valid")
        if evaluated >= expires:
            blockers.append("operator_approval_expired")

    pre_write_ready = not blockers

    post_blockers: list[str] = []
    if post_write_audit is None:
        post_blockers.append("post_write_audit_absent")
    else:
        if post_write_audit.artifact_schema_version != EXPECTED_WRITER_VERSION:
            post_blockers.append("post_write_artifact_schema_mismatch")
        if post_write_audit.writer_version != EXPECTED_WRITER_VERSION:
            post_blockers.append("post_write_writer_version_mismatch")
        if post_write_audit.row_count <= 0:
            post_blockers.append("post_write_rows_absent")
        if post_write_audit.exact_schema_row_count != post_write_audit.row_count:
            post_blockers.append("post_write_schema_not_fully_verified")
        if post_write_audit.trace_identity_verified_count != post_write_audit.row_count:
            post_blockers.append("post_write_trace_not_fully_verified")
        if post_write_audit.outcome_identity_verified_count != post_write_audit.row_count:
            post_blockers.append("post_write_outcome_not_fully_verified")
        for name in (
            "dedupe_key_verified", "canonical_isolation_verified", "append_only_verified",
            "scheduler_disabled_verified", "canonical_replacement_absent",
        ):
            if getattr(post_write_audit, name) is not True:
                post_blockers.append(f"post_write_invariant_failed:{name}")

    evidence_accepted = pre_write_ready and not post_blockers
    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_EXECUTION_AUDIT_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_execution_audit",
        "evaluated_at": evaluated_at,
        "pre_write_ready": pre_write_ready,
        "write_approval_allowed": pre_write_ready,
        "post_write_audit_complete": not post_blockers,
        "real_shadow_evidence_accepted": evidence_accepted,
        "blockers": tuple(blockers),
        "post_write_blockers": tuple(post_blockers),
        "legacy_canonical_records_count_as_shadow_evidence": False,
        "safety": MappingProxyType({
            "read_only_audit": True,
            "writer_invoked": False,
            "writes_dhot": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "ui_change": False,
        }),
    })
