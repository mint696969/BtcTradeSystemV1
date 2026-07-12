# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_execution_audit.py
# desc: MR-F5.13 execution readiness and post-write evidence audit tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_shadow_execution_audit import (
    EXPECTED_BOUNDARY_VERSION,
    EXPECTED_DRY_RUN_VERSION,
    EXPECTED_WRITER_VERSION,
    FutureShadowExecutionApprovalArtifact,
    FutureShadowPostWriteAudit,
    FutureShadowSourceAudit,
    build_market_regime_future_shadow_execution_audit,
)


def _source(**overrides) -> FutureShadowSourceAudit:
    values = {
        "inspected_at": "2026-07-12T12:00:00Z",
        "source_role": "hot_data_root",
        "source_artifact_refs": ("prediction/runs/example/forecast_records.jsonl",),
        "discovered_row_count": 2,
        "canonical_row_count": 0,
        "legacy_row_count": 0,
        "exact_schema_row_count": 2,
        "trace_identity_verified_count": 2,
        "outcome_identity_verified_count": 2,
        "lookahead_violation_count": 0,
    }
    values.update(overrides)
    return FutureShadowSourceAudit(**values)


def _approval(**overrides) -> FutureShadowExecutionApprovalArtifact:
    values = {
        "approval_id": "approval:mr-f5.13:test",
        "operator_ids": ("operator:test",),
        "approved_at": "2026-07-12T11:00:00Z",
        "expires_at": "2026-07-12T13:00:00Z",
        "boundary_schema_version": EXPECTED_BOUNDARY_VERSION,
        "dry_run_schema_version": EXPECTED_DRY_RUN_VERSION,
        "writer_version": EXPECTED_WRITER_VERSION,
        "source_role": "hot_data_root",
        "destination_role": "hot_data_root",
        "approved_artifact_refs": ("docs/approval/mr-f5.13.md",),
        "retention_policy_ref": "docs/retention/mr-f5.13.md",
        "rollback_plan_ref": "docs/rollback/mr-f5.13.md",
        "limited_batch_scope_ref": "scope:batch-1",
        "preflight_artifact_ref": "preflight:batch-1",
        "operator_explicit_write_ack": True,
    }
    values.update(overrides)
    return FutureShadowExecutionApprovalArtifact(**values)


def _post(**overrides) -> FutureShadowPostWriteAudit:
    values = {
        "audited_at": "2026-07-12T12:01:00Z",
        "artifact_ref": "prediction/market_regime/future_shadow/date=2026-07-12/batch-x.json",
        "artifact_schema_version": EXPECTED_WRITER_VERSION,
        "writer_version": EXPECTED_WRITER_VERSION,
        "row_count": 2,
        "exact_schema_row_count": 2,
        "trace_identity_verified_count": 2,
        "outcome_identity_verified_count": 2,
        "dedupe_key_verified": True,
        "canonical_isolation_verified": True,
        "append_only_verified": True,
        "scheduler_disabled_verified": True,
        "canonical_replacement_absent": True,
    }
    values.update(overrides)
    return FutureShadowPostWriteAudit(**values)


def test_exact_source_approval_and_post_write_audit_accept_evidence() -> None:
    result = build_market_regime_future_shadow_execution_audit(
        source_audit=_source(), approval=_approval(), post_write_audit=_post(),
        evaluated_at="2026-07-12T12:00:00Z",
    )
    assert result["pre_write_ready"] is True
    assert result["real_shadow_evidence_accepted"] is True


def test_current_legacy_rows_do_not_count_as_shadow_evidence() -> None:
    result = build_market_regime_future_shadow_execution_audit(
        source_audit=_source(
            discovered_row_count=2, canonical_row_count=1, legacy_row_count=1,
            exact_schema_row_count=0, trace_identity_verified_count=0,
            outcome_identity_verified_count=0,
        ),
        approval=None, post_write_audit=None, evaluated_at="2026-07-12T12:00:00Z",
    )
    assert result["pre_write_ready"] is False
    assert "exact_future_shadow_rows_absent" in result["blockers"]
    assert "legacy_or_canonical_rows_not_eligible_as_shadow_evidence" in result["blockers"]


def test_mixed_source_counts_only_exact_rows_as_eligible() -> None:
    result = build_market_regime_future_shadow_execution_audit(
        source_audit=_source(
            discovered_row_count=4, canonical_row_count=1, legacy_row_count=1,
            exact_schema_row_count=2, trace_identity_verified_count=2,
            outcome_identity_verified_count=2,
        ),
        approval=_approval(), post_write_audit=_post(),
        evaluated_at="2026-07-12T12:00:00Z",
    )
    assert result["pre_write_ready"] is True
    assert "legacy_or_canonical_rows_not_eligible_as_shadow_evidence" not in result["blockers"]
    assert result["real_shadow_evidence_accepted"] is True


def test_partial_identity_verification_blocks_execution() -> None:
    result = build_market_regime_future_shadow_execution_audit(
        source_audit=_source(trace_identity_verified_count=1, outcome_identity_verified_count=1),
        approval=_approval(), post_write_audit=None, evaluated_at="2026-07-12T12:00:00Z",
    )
    assert "trace_identity_not_fully_verified" in result["blockers"]
    assert "outcome_identity_not_fully_verified" in result["blockers"]


def test_expired_or_unacknowledged_approval_blocks_execution() -> None:
    expired = build_market_regime_future_shadow_execution_audit(
        source_audit=_source(), approval=_approval(), post_write_audit=None,
        evaluated_at="2026-07-12T13:00:00Z",
    )
    assert "operator_approval_expired" in expired["blockers"]
    unacked = build_market_regime_future_shadow_execution_audit(
        source_audit=_source(), approval=_approval(operator_explicit_write_ack=False),
        post_write_audit=None, evaluated_at="2026-07-12T12:00:00Z",
    )
    assert "operator_explicit_write_ack_absent" in unacked["blockers"]


def test_post_write_invariant_failure_rejects_evidence() -> None:
    result = build_market_regime_future_shadow_execution_audit(
        source_audit=_source(), approval=_approval(),
        post_write_audit=_post(canonical_isolation_verified=False),
        evaluated_at="2026-07-12T12:00:00Z",
    )
    assert result["pre_write_ready"] is True
    assert result["real_shadow_evidence_accepted"] is False
    assert "post_write_invariant_failed:canonical_isolation_verified" in result["post_write_blockers"]


def test_invalid_counts_and_windows_fail_closed() -> None:
    with pytest.raises(ValueError, match="future_shadow_execution_audit_trace_count_mismatch"):
        _source(exact_schema_row_count=1, trace_identity_verified_count=2)
    with pytest.raises(ValueError, match="future_shadow_execution_approval_window_invalid"):
        _approval(expires_at="2026-07-12T11:00:00Z")


def test_public_audit_is_immutable_and_never_writes() -> None:
    result = build_market_regime_future_shadow_execution_audit(
        source_audit=_source(), approval=None, post_write_audit=None,
        evaluated_at="2026-07-12T12:00:00Z",
    )
    assert result["safety"]["writes_dhot"] is False
    with pytest.raises(TypeError): result["write_approval_allowed"] = True
    with pytest.raises(TypeError): result["safety"]["writes_dhot"] = True
