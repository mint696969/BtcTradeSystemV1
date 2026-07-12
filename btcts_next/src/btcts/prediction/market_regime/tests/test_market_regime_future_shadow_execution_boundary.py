# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_execution_boundary.py
# desc: MR-F5.10 shadow-evidence execution boundary and operator-approval checklist tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_shadow_execution_boundary import (
    FutureShadowExecutionMode,
    FutureShadowOperatorApproval,
    FutureShadowWriterDesign,
    build_market_regime_future_shadow_execution_boundary,
)


def _design(**overrides) -> FutureShadowWriterDesign:
    values = {
        "writer_id": "market-regime-shadow-writer",
        "writer_contract_version": "writer.v1",
        "source_role": "hot_data_root",
        "destination_role": "hot_data_root",
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_evidence",
        "retention_policy_ref": "docs/retention/mr-f5.md",
        "rollback_plan_ref": "docs/rollback/mr-f5.md",
        "dry_run_evidence_refs": ("artifact:dry-run-1",),
        "duplicate_prevention_verified": True,
        "atomic_write_verified": True,
        "append_only_verified": True,
        "canonical_isolation_verified": True,
    }
    values.update(overrides)
    return FutureShadowWriterDesign(**values)


def _approval(**overrides) -> FutureShadowOperatorApproval:
    values = {
        "approval_id": "approval:mr-f5.10:001",
        "operator_ids": ("operator:mint",),
        "requested_at": "2026-07-12T00:00:00Z",
        "expires_at": "2026-07-13T00:00:00Z",
        "approved_writer_id": "market-regime-shadow-writer",
        "approved_writer_contract_version": "writer.v1",
        "approved_artifact_family": "prediction/market_regime",
        "approved_artifact_kind": "future_shadow_evidence",
        "approved_source_role": "hot_data_root",
        "approved_destination_role": "hot_data_root",
        "approval_artifact_refs": ("docs/approval/mr-f5.10.md",),
        "dry_run_reviewed": True,
        "retention_reviewed": True,
        "rollback_reviewed": True,
        "canonical_isolation_reviewed": True,
        "limited_shadow_scope_reviewed": True,
    }
    values.update(overrides)
    return FutureShadowOperatorApproval(**values)


def test_discovery_only_never_allows_write() -> None:
    boundary = build_market_regime_future_shadow_execution_boundary(
        mode=FutureShadowExecutionMode.DISCOVERY_ONLY,
        writer_design=None,
        operator_approval=None,
        evaluated_at="2026-07-12T12:00:00Z",
    )
    assert boundary["write_allowed"] is False
    assert boundary["execution_performed"] is False
    assert "write_mode_not_requested" in boundary["blockers"]


def test_complete_design_and_approval_only_satisfy_boundary_without_execution() -> None:
    boundary = build_market_regime_future_shadow_execution_boundary(
        mode=FutureShadowExecutionMode.APPROVED_SHADOW_WRITE,
        writer_design=_design(),
        operator_approval=_approval(),
        evaluated_at="2026-07-12T12:00:00Z",
    )
    assert boundary["write_allowed"] is True
    assert boundary["decision"] == "approved_shadow_write_boundary_satisfied"
    assert boundary["execution_performed"] is False
    assert boundary["safety"]["writer_invoked"] is False
    assert boundary["safety"]["writes_dhot"] is False


def test_expired_or_not_yet_valid_approval_blocks_write() -> None:
    expired = build_market_regime_future_shadow_execution_boundary(
        mode=FutureShadowExecutionMode.APPROVED_SHADOW_WRITE,
        writer_design=_design(),
        operator_approval=_approval(),
        evaluated_at="2026-07-13T00:00:00Z",
    )
    assert expired["write_allowed"] is False
    assert "operator_approval_expired" in expired["blockers"]
    future = build_market_regime_future_shadow_execution_boundary(
        mode=FutureShadowExecutionMode.APPROVED_SHADOW_WRITE,
        writer_design=_design(),
        operator_approval=_approval(),
        evaluated_at="2026-07-11T23:59:59Z",
    )
    assert "operator_approval_not_yet_valid" in future["blockers"]


def test_scope_mismatch_blocks_write() -> None:
    boundary = build_market_regime_future_shadow_execution_boundary(
        mode=FutureShadowExecutionMode.APPROVED_SHADOW_WRITE,
        writer_design=_design(),
        operator_approval=_approval(approved_writer_contract_version="writer.v2"),
        evaluated_at="2026-07-12T12:00:00Z",
    )
    assert boundary["write_allowed"] is False
    assert "operator_approval_scope_mismatch:writer_contract_version" in boundary["blockers"]


def test_incomplete_design_or_review_blocks_write() -> None:
    boundary = build_market_regime_future_shadow_execution_boundary(
        mode=FutureShadowExecutionMode.APPROVED_SHADOW_WRITE,
        writer_design=_design(atomic_write_verified=False),
        operator_approval=_approval(rollback_reviewed=False),
        evaluated_at="2026-07-12T12:00:00Z",
    )
    assert "writer_design_incomplete:atomic_write_verified" in boundary["blockers"]
    assert "operator_approval_incomplete:rollback_reviewed" in boundary["blockers"]
    assert boundary["write_allowed"] is False


def test_invalid_approval_window_and_boolean_fail_closed() -> None:
    with pytest.raises(ValueError, match="future_shadow_execution_approval_window_invalid"):
        _approval(expires_at="2026-07-12T00:00:00Z")
    with pytest.raises(ValueError, match="future_shadow_execution_design_boolean_invalid:atomic_write_verified"):
        _design(atomic_write_verified=1)


def test_physical_or_cold_data_roles_are_rejected() -> None:
    with pytest.raises(ValueError, match="future_shadow_execution_data_role_invalid"):
        _design(source_role="cold_data_root")
    with pytest.raises(ValueError, match="future_shadow_execution_data_role_invalid"):
        _design(destination_role="D:/btc_ts_hot")


def test_public_boundary_is_immutable() -> None:
    boundary = build_market_regime_future_shadow_execution_boundary(
        mode=FutureShadowExecutionMode.DESIGN_REVIEW,
        writer_design=_design(),
        operator_approval=None,
        evaluated_at="2026-07-12T12:00:00Z",
    )
    with pytest.raises(TypeError): boundary["write_allowed"] = True
    with pytest.raises(TypeError): boundary["safety"]["writes_dhot"] = True
