# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_writer.py
# desc: MR-F5.12 isolated disabled-by-default future-shadow writer tests.

from __future__ import annotations

import json
from pathlib import Path

import pytest

from btcts.prediction.market_regime.future_shadow_execution_boundary import (
    FutureShadowExecutionMode,
    FutureShadowOperatorApproval,
    FutureShadowWriterDesign,
    build_market_regime_future_shadow_execution_boundary,
)
from btcts.prediction.market_regime.future_shadow_writer_dry_run import (
    FutureShadowDryRunArtifactIdentity,
    FutureShadowDryRunBatch,
    FutureShadowDryRunPolicy,
    build_market_regime_future_shadow_writer_dry_run,
    deterministic_shadow_row_hash,
)
from btcts.prediction.market_regime.tools.write_future_shadow import (
    preflight_market_regime_future_shadow_write,
    write_market_regime_future_shadow_once,
)


def _rows() -> tuple[dict, ...]:
    return tuple({
        "schema_version": "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_evaluation_row",
        "trace_id": trace,
        "target_horizon_sec": 300,
        "model_id": "model.v1",
        "logic_version": "logic.v1",
        "parameter_set_id": "params.v1",
        "feature_snapshot_ref": f"snapshot:{trace}",
        "outcome_status": "CORRECT",
    } for trace in ("t1", "t2"))


def _plan(rows: tuple[dict, ...] | None = None):
    values = rows or _rows()
    batch = FutureShadowDryRunBatch(
        generated_at="2026-07-12T12:00:00Z",
        writer_id="market-regime-shadow-writer",
        writer_contract_version="writer.v1",
        trace_ids=tuple(row["trace_id"] for row in values),
        row_payload_hashes=tuple(deterministic_shadow_row_hash(row) for row in values),
        artifact_identity=FutureShadowDryRunArtifactIdentity(
            artifact_family="prediction/market_regime",
            artifact_kind="future_shadow_evidence",
            schema_version="prediction.market_regime.future_shadow_outcome.mr_f5_6.v1",
            source_role="hot_data_root",
            destination_role="hot_data_root",
            namespace="prediction/market_regime/future_shadow",
            partition_key="2026-07-12",
        ),
        policy=FutureShadowDryRunPolicy(
            disabled_by_default=True,
            scheduler_registration_allowed=False,
            canonical_path_overlap_allowed=False,
            append_only_required=True,
            atomic_temp_then_replace_required=True,
            duplicate_prevention_required=True,
            retention_policy_ref="docs/retention/mr-f5.12.md",
            rollback_plan_ref="docs/rollback/mr-f5.12.md",
            maximum_batch_rows=100,
        ),
    )
    return build_market_regime_future_shadow_writer_dry_run(batch=batch)


def _boundary():
    design = FutureShadowWriterDesign(
        writer_id="market-regime-shadow-writer",
        writer_contract_version="writer.v1",
        source_role="hot_data_root",
        destination_role="hot_data_root",
        artifact_family="prediction/market_regime",
        artifact_kind="future_shadow_evidence",
        retention_policy_ref="docs/retention/mr-f5.12.md",
        rollback_plan_ref="docs/rollback/mr-f5.12.md",
        dry_run_evidence_refs=("artifact:dry-run",),
        duplicate_prevention_verified=True,
        atomic_write_verified=True,
        append_only_verified=True,
        canonical_isolation_verified=True,
    )
    approval = FutureShadowOperatorApproval(
        approval_id="approval:mr-f5.12:test",
        operator_ids=("operator:test",),
        requested_at="2026-07-12T00:00:00Z",
        expires_at="2026-07-13T00:00:00Z",
        approved_writer_id="market-regime-shadow-writer",
        approved_writer_contract_version="writer.v1",
        approved_artifact_family="prediction/market_regime",
        approved_artifact_kind="future_shadow_evidence",
        approved_source_role="hot_data_root",
        approved_destination_role="hot_data_root",
        approval_artifact_refs=("docs/approval/mr-f5.12-test.md",),
        dry_run_reviewed=True,
        retention_reviewed=True,
        rollback_reviewed=True,
        canonical_isolation_reviewed=True,
        limited_shadow_scope_reviewed=True,
    )
    return build_market_regime_future_shadow_execution_boundary(
        mode=FutureShadowExecutionMode.APPROVED_SHADOW_WRITE,
        writer_design=design,
        operator_approval=approval,
        evaluated_at="2026-07-12T12:00:00Z",
    )


def test_preflight_validates_without_writing(tmp_path: Path) -> None:
    result = preflight_market_regime_future_shadow_write(
        dry_run_plan=_plan(), approved_boundary=_boundary(), rows=_rows(), executed_at="2026-07-12T12:00:00Z"
    )
    assert result["would_write"] is False
    assert result["write_allowed"] is True
    assert not list(tmp_path.rglob("*"))


def test_writer_is_disabled_and_once_acknowledgement_is_required(tmp_path: Path) -> None:
    with pytest.raises(PermissionError, match="future_shadow_writer_disabled_by_default"):
        write_market_regime_future_shadow_once(
            tmp_path, dry_run_plan=_plan(), approved_boundary=_boundary(), rows=_rows(), executed_at="2026-07-12T12:00:00Z"
        )
    with pytest.raises(PermissionError, match="future_shadow_writer_once_ack_required"):
        write_market_regime_future_shadow_once(
            tmp_path, dry_run_plan=_plan(), approved_boundary=_boundary(), rows=_rows(), executed_at="2026-07-12T12:00:00Z", enabled=True
        )


def test_writer_creates_one_isolated_immutable_batch(tmp_path: Path) -> None:
    result = write_market_regime_future_shadow_once(
        tmp_path, dry_run_plan=_plan(), approved_boundary=_boundary(), rows=_rows(), executed_at="2026-07-12T12:00:00Z", enabled=True, once=True
    )
    assert result["written"] is True
    assert result["counts_as_real_shadow_evidence"] is False
    path = tmp_path / result["artifact_relpath"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["append_only"] is True
    assert payload["canonical_isolated"] is True
    assert payload["rows"][0]["trace_id"] == "t1"
    assert "latest" not in result["artifact_relpath"]


def test_same_batch_is_idempotent_duplicate(tmp_path: Path) -> None:
    first = write_market_regime_future_shadow_once(
        tmp_path, dry_run_plan=_plan(), approved_boundary=_boundary(), rows=_rows(), executed_at="2026-07-12T12:00:00Z", enabled=True, once=True
    )
    second = write_market_regime_future_shadow_once(
        tmp_path, dry_run_plan=_plan(), approved_boundary=_boundary(), rows=tuple(reversed(_rows())), executed_at="2026-07-12T12:00:00Z", enabled=True, once=True
    )
    assert first["written"] is True
    assert second["written"] is False
    assert second["duplicate"] is True


def test_existing_conflicting_artifact_fails_closed(tmp_path: Path) -> None:
    plan = _plan()
    first = write_market_regime_future_shadow_once(
        tmp_path, dry_run_plan=plan, approved_boundary=_boundary(), rows=_rows(), executed_at="2026-07-12T12:00:00Z", enabled=True, once=True
    )
    path = tmp_path / first["artifact_relpath"]
    path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="future_shadow_writer_existing_artifact_conflict"):
        write_market_regime_future_shadow_once(
            tmp_path, dry_run_plan=plan, approved_boundary=_boundary(), rows=_rows(), executed_at="2026-07-12T12:00:00Z", enabled=True, once=True
        )


def test_unapproved_boundary_and_payload_mismatch_fail_closed(tmp_path: Path) -> None:
    boundary = dict(_boundary())
    boundary["write_allowed"] = False
    with pytest.raises(PermissionError, match="future_shadow_writer_boundary_not_approved"):
        preflight_market_regime_future_shadow_write(
            dry_run_plan=_plan(), approved_boundary=boundary, rows=_rows(), executed_at="2026-07-12T12:00:00Z"
        )
    changed = [dict(row) for row in _rows()]
    changed[0]["outcome_status"] = "INCORRECT"
    with pytest.raises(ValueError, match="future_shadow_writer_payload_hash_mismatch"):
        preflight_market_regime_future_shadow_write(
            dry_run_plan=_plan(), approved_boundary=_boundary(), rows=changed, executed_at="2026-07-12T12:00:00Z"
        )


def test_expired_approval_and_tampered_dedupe_fail_closed() -> None:
    with pytest.raises(PermissionError, match="future_shadow_writer_approval_expired"):
        preflight_market_regime_future_shadow_write(
            dry_run_plan=_plan(), approved_boundary=_boundary(), rows=_rows(),
            executed_at="2026-07-13T00:00:00Z",
        )
    plan = dict(_plan())
    plan["dedupe_key"] = "0" * 64
    with pytest.raises(ValueError, match="future_shadow_writer_dedupe_key_mismatch"):
        preflight_market_regime_future_shadow_write(
            dry_run_plan=plan, approved_boundary=_boundary(), rows=_rows(),
            executed_at="2026-07-12T12:00:00Z",
        )


def test_tampered_boundary_and_partition_fail_closed() -> None:
    boundary = dict(_boundary())
    boundary["schema_version"] = "wrong"
    with pytest.raises(ValueError, match="future_shadow_writer_boundary_schema_invalid"):
        preflight_market_regime_future_shadow_write(
            dry_run_plan=_plan(), approved_boundary=boundary, rows=_rows(),
            executed_at="2026-07-12T12:00:00Z",
        )
    plan = dict(_plan())
    plan["partition_key"] = "2026-07-13"
    with pytest.raises(ValueError, match="future_shadow_writer_partition_generated_at_mismatch"):
        preflight_market_regime_future_shadow_write(
            dry_run_plan=plan, approved_boundary=_boundary(), rows=_rows(),
            executed_at="2026-07-12T12:00:00Z",
        )


def test_no_scheduler_cli_or_canonical_latest_surface() -> None:
    import btcts.prediction.market_regime.tools.write_future_shadow as module

    assert not hasattr(module, "main")
    assert not hasattr(module, "_build_parser")
    assert not hasattr(module, "register")
