# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_execution_plan.py
# desc: MR-F6.19 tests for deterministic dry-run execution planning without writer invocation.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_origin_evidence_execution_boundary import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION,
)
from btcts.prediction.market_regime.future_origin_evidence_execution_plan import (
    build_origin_evidence_dry_run_execution_plan,
)
from btcts.prediction.market_regime.future_origin_evidence_execution_request import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION,
)

REQUEST_HASH = "a" * 64
BUNDLE_IDS = tuple(f"bundle-{index}" for index in range(7))
WRITE_PLAN_BUNDLE_IDS = tuple(reversed(BUNDLE_IDS))


def _request() -> dict[str, object]:
    return {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION,
        "artifact_kind": "future_origin_evidence_one_shot_execution_request",
        "request_id": f"origin-evidence-execution-request:{REQUEST_HASH}",
        "request_hash": REQUEST_HASH,
        "writer_id": "mr-f6-origin-writer",
        "writer_contract_version": "writer.v1",
        "writer_contract_schema_version": "writer-schema.v1",
        "approval_id": "approval:fixture",
        "approval_expires_at": "2026-07-15T00:00:00Z",
        "artifact_relpath": "prediction/market_regime/future_origin_evidence/date=2026-07-14/batch-dedupe.json",
        "dedupe_key": "dedupe",
        "target_horizons_sec": FUTURE_MARKET_REGIME_HORIZONS_SEC,
        "bundle_ids": BUNDLE_IDS,
        "write_plan_bundle_ids": WRITE_PLAN_BUNDLE_IDS,
        "forecast_parameter_set_ids": ("forecast-parameters.v1",),
    }


def _boundary() -> dict[str, object]:
    return {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION,
        "artifact_kind": "future_origin_evidence_one_shot_execution_boundary",
        "request_id": f"origin-evidence-execution-request:{REQUEST_HASH}",
        "request_hash": REQUEST_HASH,
        "expected_request_hash": REQUEST_HASH,
        "writer_id": "mr-f6-origin-writer",
        "writer_contract_version": "writer.v1",
        "evaluated_at": "2026-07-14T01:15:00Z",
        "approval_id": "approval:fixture",
        "approval_requested_at": "2026-07-14T00:00:00Z",
        "approval_expires_at": "2026-07-15T00:00:00Z",
        "artifact_relpath": "prediction/market_regime/future_origin_evidence/date=2026-07-14/batch-dedupe.json",
        "dedupe_key": "dedupe",
        "bundle_ids": BUNDLE_IDS,
        "enabled_acknowledgement_present": True,
        "once_acknowledgement_present": True,
        "destination_artifact_exists": False,
        "destination_artifact_matches_request": False,
        "authorization_ready_for_separate_writer_call": True,
        "blockers": (),
        "decision": "separate_writer_call_may_be_considered",
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
    }


def _plan(**overrides: object):
    values = dict(
        execution_request=_request(),
        execution_boundary=_boundary(),
        planned_at="2026-07-14T01:20:00Z",
        expected_request_hash=REQUEST_HASH,
        expected_writer_id="mr-f6-origin-writer",
        expected_writer_contract_version="writer.v1",
    )
    values.update(overrides)
    return build_origin_evidence_dry_run_execution_plan(**values)


def test_ready_boundary_builds_deterministic_immutable_plan() -> None:
    first = _plan()
    second = _plan()
    assert first["execution_plan_id"] == second["execution_plan_id"]
    assert first["execution_plan_hash"] == second["execution_plan_hash"]
    assert first["execution_plan_ready"] is True
    assert first["dry_run_only"] is True
    assert first["bundle_ids"] == BUNDLE_IDS
    assert first["write_plan_bundle_ids"] == WRITE_PLAN_BUNDLE_IDS
    with pytest.raises(TypeError):
        first["execution_plan_ready"] = False


def test_plan_never_authorizes_or_invokes_writer() -> None:
    result = _plan()
    assert result["execution_authorized_by_this_artifact"] is False
    assert result["writer_imported"] is False
    assert result["writer_invoked"] is False
    assert result["execution_performed"] is False
    assert result["writes_dhot"] is False
    assert result["scheduler_enabled"] is False


def test_planned_at_must_follow_boundary_and_precede_expiry() -> None:
    with pytest.raises(ValueError, match="before_boundary"):
        _plan(planned_at="2026-07-14T01:14:59Z")
    with pytest.raises(PermissionError, match="approval_expired"):
        _plan(planned_at="2026-07-15T00:00:00Z")


def test_boundary_must_be_ready_and_conflict_free() -> None:
    boundary = _boundary()
    boundary["authorization_ready_for_separate_writer_call"] = False
    with pytest.raises(ValueError, match="boundary_not_ready"):
        _plan(execution_boundary=boundary)

    boundary = _boundary()
    boundary["destination_artifact_exists"] = True
    with pytest.raises(ValueError, match="destination_not_absent"):
        _plan(execution_boundary=boundary)


def test_request_boundary_and_external_identity_must_match() -> None:
    with pytest.raises(PermissionError, match="external_request_hash_mismatch"):
        _plan(expected_request_hash="b" * 64)

    boundary = _boundary()
    boundary["request_hash"] = "b" * 64
    with pytest.raises(ValueError, match="boundary_request_hash_mismatch"):
        _plan(execution_boundary=boundary)

    with pytest.raises(PermissionError, match="writer_scope_mismatch"):
        _plan(expected_writer_id="other")


def test_bundle_and_destination_identity_are_revalidated() -> None:
    boundary = _boundary()
    boundary["bundle_ids"] = tuple(reversed(BUNDLE_IDS))
    with pytest.raises(ValueError, match="bundle_identity_invalid"):
        _plan(execution_boundary=boundary)

    boundary = _boundary()
    boundary["dedupe_key"] = "other"
    with pytest.raises(ValueError, match="boundary_identity_mismatch:dedupe_key"):
        _plan(execution_boundary=boundary)


def test_plan_hash_changes_when_execution_time_changes() -> None:
    first = _plan(planned_at="2026-07-14T01:20:00Z")
    second = _plan(planned_at="2026-07-14T01:21:00Z")
    assert first["execution_plan_hash"] != second["execution_plan_hash"]


def test_module_exposes_no_writer_or_runtime_surface() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_execution_plan as module
    assert not hasattr(module, "write_origin_evidence_once")
    assert not hasattr(module, "preflight_origin_evidence_write")
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
