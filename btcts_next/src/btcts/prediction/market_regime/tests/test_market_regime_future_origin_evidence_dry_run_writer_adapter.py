# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_dry_run_writer_adapter.py
# desc: MR-F6.20 tests for public writer preflight exercise without write-function import or filesystem mutation.

from __future__ import annotations

from types import MappingProxyType

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_forecast_contract import (
    FUTURE_MARKET_REGIME_HORIZONS_SEC,
)
from btcts.prediction.market_regime.future_mandatory_baseline_origin_evidence import (
    MarketRegimeOriginEvidence,
    build_market_regime_origin_evidence_bundle,
)
from btcts.prediction.market_regime.future_origin_evidence_dry_run_writer_adapter import (
    invoke_origin_evidence_writer_preflight_dry_run,
)
from btcts.prediction.market_regime.future_origin_evidence_execution_boundary import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION,
)
from btcts.prediction.market_regime.future_origin_evidence_execution_plan import (
    build_origin_evidence_dry_run_execution_plan,
)
from btcts.prediction.market_regime.future_origin_evidence_execution_request import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION,
)
from btcts.prediction.market_regime.future_origin_evidence_writer import (
    MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
    build_origin_evidence_approval,
    build_origin_evidence_write_plan,
)

REQUEST_HASH = "a" * 64


def _bundles() -> tuple[MappingProxyType, ...]:
    result = []
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        trace = f"trace:{horizon}"
        result.append(
            build_market_regime_origin_evidence_bundle(
                MarketRegimeOriginEvidence(
                    prediction_origin="2026-07-14T00:00:00Z",
                    prediction_origin_epoch_sec=1000.0,
                    source_timestamp="2026-07-13T23:59:59Z",
                    source_timestamp_epoch_sec=999.0,
                    target_horizon_sec=horizon,
                    trace_id=trace,
                    model_id="model.v1",
                    logic_version="logic.v1",
                    parameter_set_id=f"params.{horizon}.v1",
                    target_definition_version=(
                        f"market_regime_target.{horizon}s.v1"
                    ),
                    feature_snapshot_ref=f"snapshot:{trace}",
                    current_state=MarketRegimeCode.RANGE,
                    previous_state=MarketRegimeCode.RANGE,
                    regime_scores={MarketRegimeCode.RANGE: 1.0},
                    recent_return=0.0,
                    fast_ma=100.0,
                    slow_ma=100.0,
                    realized_volatility=0.02,
                    low_volatility_threshold=0.01,
                    high_volatility_threshold=0.03,
                    current_forecast_label_selection=MarketRegimeCode.RANGE,
                )
            )
        )
    return tuple(result)


def _writer_plan(bundles=None):
    values = bundles or _bundles()
    return build_origin_evidence_write_plan(
        generated_at="2026-07-14T00:00:00Z",
        writer_id="mr-f6-origin-writer",
        writer_contract_version="writer.v1",
        bundles=values,
        maximum_batch_rows=7,
    )


def _approval():
    return build_origin_evidence_approval(
        approval_id="approval:mr-f6.20:fixture",
        operator_ids=("operator:fixture",),
        requested_at="2026-07-14T00:00:00Z",
        expires_at="2026-07-15T00:00:00Z",
        approved_writer_id="mr-f6-origin-writer",
        approved_writer_contract_version="writer.v1",
    )


def _execution_plan():
    bundles = _bundles()
    writer_plan = _writer_plan(bundles)
    bundle_ids = tuple(str(item["bundle_id"]) for item in bundles)
    relpath = (
        "prediction/market_regime/future_origin_evidence/"
        f"date={writer_plan['partition_key']}/"
        f"batch-{writer_plan['dedupe_key']}.json"
    )
    request = {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION,
        "artifact_kind": "future_origin_evidence_one_shot_execution_request",
        "request_id": f"origin-evidence-execution-request:{REQUEST_HASH}",
        "request_hash": REQUEST_HASH,
        "writer_id": "mr-f6-origin-writer",
        "writer_contract_version": "writer.v1",
        "writer_contract_schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
        "approval_id": "approval:mr-f6.20:fixture",
        "approval_requested_at": "2026-07-14T00:00:00Z",
        "approval_expires_at": "2026-07-15T00:00:00Z",
        "artifact_relpath": relpath,
        "dedupe_key": writer_plan["dedupe_key"],
        "target_horizons_sec": FUTURE_MARKET_REGIME_HORIZONS_SEC,
        "bundle_ids": bundle_ids,
        "write_plan_bundle_ids": writer_plan["bundle_ids"],
        "forecast_parameter_set_ids": tuple(
            str(item["parameter_set_id"]) for item in bundles
        ),
    }
    boundary = {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION,
        "artifact_kind": "future_origin_evidence_one_shot_execution_boundary",
        "request_id": request["request_id"],
        "request_hash": REQUEST_HASH,
        "expected_request_hash": REQUEST_HASH,
        "writer_id": "mr-f6-origin-writer",
        "writer_contract_version": "writer.v1",
        "evaluated_at": "2026-07-14T01:15:00Z",
        "approval_id": request["approval_id"],
        "approval_requested_at": request["approval_requested_at"],
        "approval_expires_at": request["approval_expires_at"],
        "artifact_relpath": relpath,
        "dedupe_key": writer_plan["dedupe_key"],
        "bundle_ids": bundle_ids,
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
    execution_plan = build_origin_evidence_dry_run_execution_plan(
        execution_request=request,
        execution_boundary=boundary,
        planned_at="2026-07-14T01:20:00Z",
        expected_request_hash=REQUEST_HASH,
        expected_writer_id="mr-f6-origin-writer",
        expected_writer_contract_version="writer.v1",
    )
    return execution_plan, writer_plan, _approval(), bundles


def _invoke(**overrides: object):
    execution_plan, writer_plan, approval, bundles = _execution_plan()
    values = dict(
        execution_plan=execution_plan,
        writer_plan=writer_plan,
        approval=approval,
        bundles=bundles,
        executed_at="2026-07-14T01:25:00Z",
        expected_execution_plan_hash=execution_plan["execution_plan_hash"],
        expected_writer_id="mr-f6-origin-writer",
        expected_writer_contract_version="writer.v1",
    )
    values.update(overrides)
    return invoke_origin_evidence_writer_preflight_dry_run(**values)


def test_public_writer_preflight_is_exercised_without_write() -> None:
    result = _invoke()
    assert result["dry_run_contract_exercised"] is True
    assert result["writer_preflight_invoked"] is True
    assert result["preflight_snapshot"]["preflight_only"] is True
    assert result["preflight_snapshot"]["write_allowed"] is True
    assert result["preflight_snapshot"]["would_write"] is False
    assert result["writer_write_function_imported"] is False
    assert result["writer_write_function_invoked"] is False
    assert result["writer_invoked"] is False
    assert result["execution_performed"] is False
    assert result["filesystem_write_performed"] is False
    assert result["writes_dhot"] is False


def test_adapter_result_is_deterministic_and_immutable() -> None:
    first = _invoke()
    second = _invoke()
    assert first["adapter_result_id"] == second["adapter_result_id"]
    assert first["adapter_result_hash"] == second["adapter_result_hash"]
    with pytest.raises(TypeError):
        first["writer_invoked"] = True
    with pytest.raises(TypeError):
        first["preflight_snapshot"]["would_write"] = True


def test_external_plan_hash_and_writer_scope_are_required() -> None:
    with pytest.raises(PermissionError, match="external_plan_hash_mismatch"):
        _invoke(expected_execution_plan_hash="b" * 64)
    with pytest.raises(PermissionError, match="writer_scope_mismatch"):
        _invoke(expected_writer_id="other")


def test_execution_time_must_follow_plan_and_precede_expiry() -> None:
    with pytest.raises(ValueError, match="before_execution_plan"):
        _invoke(executed_at="2026-07-14T01:19:59Z")
    with pytest.raises(PermissionError, match="approval_not_active"):
        _invoke(executed_at="2026-07-15T00:00:00Z")


def test_approval_identity_and_window_must_match_plan() -> None:
    bad = dict(_approval())
    bad["approval_id"] = "other"
    with pytest.raises(ValueError, match="approval_id_mismatch"):
        _invoke(approval=bad)

    bad = dict(_approval())
    bad["requested_at"] = "2026-07-13T23:59:00Z"
    with pytest.raises(ValueError, match="approval_requested_at_mismatch"):
        _invoke(approval=bad)


def test_writer_plan_and_bundle_identity_must_match_execution_plan() -> None:
    _, writer_plan, _, bundles = _execution_plan()
    bad_plan = dict(writer_plan)
    bad_plan["dedupe_key"] = "other"
    with pytest.raises(ValueError, match="dedupe_key_mismatch"):
        _invoke(writer_plan=bad_plan)

    with pytest.raises(ValueError, match="bundle_identity_mismatch"):
        _invoke(bundles=bundles[:-1])


def test_tampered_execution_plan_fails_hash_validation() -> None:
    execution_plan, _, _, _ = _execution_plan()
    tampered = dict(execution_plan)
    tampered["artifact_relpath"] = "other"
    with pytest.raises(ValueError, match="execution_plan_hash_mismatch"):
        _invoke(execution_plan=tampered)


def test_module_imports_preflight_but_not_write_function_or_runtime_surface() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_dry_run_writer_adapter as module

    assert hasattr(module, "preflight_origin_evidence_write")
    assert not hasattr(module, "write_origin_evidence_once")
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
