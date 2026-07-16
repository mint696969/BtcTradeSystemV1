# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_write_execution.py
# desc: MR-F9.19H limited once-only execution envelope tests; writes are repository-tmp-only.

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from btcts.prediction.market_regime.runtime_horizon_persistence_plan import (
    EXPECTED_HORIZONS,
    build_runtime_horizon_persistence_plan,
)
from btcts.prediction.market_regime.runtime_horizon_write_approval import (
    build_runtime_horizon_write_approval_token,
)
from btcts.prediction.market_regime.runtime_horizon_write_execution import (
    classify_execution_output_root,
    execute_runtime_horizon_write_with_approval_once,
)
from btcts.prediction.market_regime.runtime_horizon_write_readiness import (
    build_runtime_horizon_write_readiness_report,
)


def _token(output_root) -> dict:
    return {
        "destination_root": str(output_root.resolve()),
        "run_id": "run-test",
        "prediction_origin": "2026-07-16T18:00:00Z",
        "operator_id": "mint",
        "approval_token_sha256": "a" * 64,
        "enabled_acknowledged": True,
        "once_acknowledged": True,
    }


def _readiness(output_root) -> dict:
    return {
        "destination_root": str(output_root.resolve()),
        "ready": True,
    }


def _plan() -> dict:
    return {"schema_version": "plan:test", "run_id": "run-test"}


def _write_result(*, duplicate: bool = False) -> dict:
    return {
        "written": not duplicate,
        "duplicate": duplicate,
        "written_count": 0 if duplicate else 9,
        "duplicate_count": 9 if duplicate else 0,
        "written_paths": () if duplicate else ("horizon=0.json", "manifest.json"),
        "duplicate_paths": ("horizon=0.json", "manifest.json") if duplicate else (),
        "manifest_relpath": "manifest.json",
        "manifest_written_last": True,
        "latest_pointer_created": False,
        "writer_registered": False,
        "producer_loop_enabled": False,
        "scheduler_enabled": False,
        "websocket_opened": False,
        "order_submission_allowed": False,
    }


def _real_inputs(output_root):
    origin = "2026-07-16T18:00:00Z"
    horizons = [
        {
            "horizon_sec": horizon,
            "trace_id": f"trace:{horizon}",
            "prediction_origin": origin,
            "source_timestamp": "2026-07-16T17:59:00Z",
            "source_currentness_verified": True,
            "source_freshness_state": "LIVE",
        }
        for horizon in EXPECTED_HORIZONS
    ]
    artifact = {
        "prediction_origin": origin,
        "horizon_count": 8,
        "horizons": horizons,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "safety": {
            "writes_dhot": False,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "websocket_opened": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_submission_allowed": False,
            "canonical_replacement": False,
        },
    }
    plan = build_runtime_horizon_persistence_plan(artifact=artifact)
    preflight = {
        "hot_root": str(output_root.resolve()),
        "runtime_horizon_artifact": artifact,
        "runtime_horizon_artifact_built": True,
        "runtime_horizon_artifact_persisted": False,
        "runtime_horizon_persistence_plan": plan,
        "runtime_horizon_persistence_plan_built": True,
        "runtime_horizon_writer_registered": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
    }
    readiness = build_runtime_horizon_write_readiness_report(
        preflight=preflight,
        destination_root=output_root,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    token = build_runtime_horizon_write_approval_token(
        readiness=readiness,
        plan=plan,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    return readiness, plan, token


def test_output_root_is_restricted_to_repository_tmp(tmp_path) -> None:
    repo = tmp_path / "repo"
    allowed = repo / "tmp" / "mr_f9_19h"
    assert classify_execution_output_root(allowed, repository_root=repo) == "repo_tmp"
    with pytest.raises(ValueError, match="output_root_not_repo_tmp"):
        classify_execution_output_root(repo / "outside", repository_root=repo)


def test_acknowledgements_are_required_before_validation_or_writer(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "out"
    with patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.validate_runtime_horizon_write_approval_token"
    ) as validate, patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.persist_runtime_horizon_plan_once"
    ) as writer:
        with pytest.raises(PermissionError, match="enabled_ack_required"):
            execute_runtime_horizon_write_with_approval_once(
                output_root=output,
                token=_token(output),
                readiness=_readiness(output),
                plan=_plan(),
                repository_root=repo,
            )
        with pytest.raises(PermissionError, match="once_ack_required"):
            execute_runtime_horizon_write_with_approval_once(
                output_root=output,
                token=_token(output),
                readiness=_readiness(output),
                plan=_plan(),
                enabled=True,
                repository_root=repo,
            )
        validate.assert_not_called()
        writer.assert_not_called()


def test_exact_token_is_validated_before_writer_and_result_is_safe(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "out"
    token = _token(output)
    readiness = _readiness(output)
    plan = _plan()
    events = Mock()

    with patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.validate_runtime_horizon_write_approval_token",
        side_effect=lambda **kwargs: events("validate", kwargs),
    ) as validate, patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.persist_runtime_horizon_plan_once",
        side_effect=lambda *args, **kwargs: (events("write", (args, kwargs)), _write_result())[1],
    ) as writer:
        result = execute_runtime_horizon_write_with_approval_once(
            output_root=output,
            token=token,
            readiness=readiness,
            plan=plan,
            enabled=True,
            once=True,
            repository_root=repo,
        )

    validate.assert_called_once_with(token=token, readiness=readiness, plan=plan)
    writer.assert_called_once_with(output.resolve(), plan=plan, enabled=True, once=True)
    assert events.call_args_list[0].args[0] == "validate"
    assert events.call_args_list[1].args[0] == "write"
    assert result["approval_validated_before_writer"] is True
    assert result["write_result"]["written_count"] == 9
    assert result["writes_dhot"] is False
    assert result["writer_registered"] is False
    assert result["latest_pointer_created"] is False
    assert result["producer_loop_enabled"] is False
    assert result["websocket_opened"] is False
    assert result["order_submission_allowed"] is False


def test_validation_failure_prevents_writer_invocation(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "out"
    with patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.validate_runtime_horizon_write_approval_token",
        side_effect=ValueError("runtime_horizon_write_approval_token_mismatch"),
    ), patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.persist_runtime_horizon_plan_once"
    ) as writer:
        with pytest.raises(ValueError, match="token_mismatch"):
            execute_runtime_horizon_write_with_approval_once(
                output_root=output,
                token=_token(output),
                readiness=_readiness(output),
                plan=_plan(),
                enabled=True,
                once=True,
                repository_root=repo,
            )
        writer.assert_not_called()


def test_destination_root_mismatch_prevents_writer_after_validation(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "out"
    other = repo / "tmp" / "other"
    token = _token(other)
    readiness = _readiness(output)
    with patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.validate_runtime_horizon_write_approval_token"
    ), patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.persist_runtime_horizon_plan_once"
    ) as writer:
        with pytest.raises(ValueError, match="destination_root_mismatch"):
            execute_runtime_horizon_write_with_approval_once(
                output_root=output,
                token=token,
                readiness=readiness,
                plan=_plan(),
                enabled=True,
                once=True,
                repository_root=repo,
            )
        writer.assert_not_called()


def test_duplicate_result_is_returned_without_runtime_activation(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "out"
    with patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.validate_runtime_horizon_write_approval_token"
    ), patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.persist_runtime_horizon_plan_once",
        return_value=_write_result(duplicate=True),
    ) as writer:
        result = execute_runtime_horizon_write_with_approval_once(
            output_root=output,
            token=_token(output),
            readiness=_readiness(output),
            plan=_plan(),
            enabled=True,
            once=True,
            repository_root=repo,
        )
    writer.assert_called_once()
    assert result["write_result"]["duplicate"] is True
    assert result["write_result"]["duplicate_count"] == 9
    assert result["writer_registered"] is False


def test_writer_conflict_propagates_and_safety_result_is_enforced(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "out"
    with patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.validate_runtime_horizon_write_approval_token"
    ), patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.persist_runtime_horizon_plan_once",
        side_effect=RuntimeError("runtime_horizon_persistence_existing_conflict:path"),
    ) as writer:
        with pytest.raises(RuntimeError, match="existing_conflict"):
            execute_runtime_horizon_write_with_approval_once(
                output_root=output,
                token=_token(output),
                readiness=_readiness(output),
                plan=_plan(),
                enabled=True,
                once=True,
                repository_root=repo,
            )
        writer.assert_called_once()

    unsafe = _write_result()
    unsafe["producer_loop_enabled"] = True
    with patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.validate_runtime_horizon_write_approval_token"
    ), patch(
        "btcts.prediction.market_regime.runtime_horizon_write_execution.persist_runtime_horizon_plan_once",
        return_value=unsafe,
    ) as writer:
        with pytest.raises(ValueError, match="result_safety_invalid:producer_loop_enabled"):
            execute_runtime_horizon_write_with_approval_once(
                output_root=output,
                token=_token(output),
                readiness=_readiness(output),
                plan=_plan(),
                enabled=True,
                once=True,
                repository_root=repo,
            )
        writer.assert_called_once()


def test_real_writer_integration_writes_duplicates_and_fails_closed_on_conflict(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "real-writer"
    readiness, plan, token = _real_inputs(output)

    first = execute_runtime_horizon_write_with_approval_once(
        output_root=output,
        token=token,
        readiness=readiness,
        plan=plan,
        enabled=True,
        once=True,
        repository_root=repo,
    )
    assert first["write_result"]["written"] is True
    assert first["write_result"]["written_count"] == 9
    assert first["write_result"]["duplicate_count"] == 0
    assert first["write_result"]["manifest_written_last"] is True

    second = execute_runtime_horizon_write_with_approval_once(
        output_root=output,
        token=token,
        readiness=readiness,
        plan=plan,
        enabled=True,
        once=True,
        repository_root=repo,
    )
    assert second["write_result"]["written"] is False
    assert second["write_result"]["duplicate"] is True
    assert second["write_result"]["written_count"] == 0
    assert second["write_result"]["duplicate_count"] == 9

    conflict_path = output / plan["horizon_artifacts"][0]["artifact_relpath"]
    conflict_path.write_text("conflict\n", encoding="utf-8", newline="\n")
    with pytest.raises(RuntimeError, match="existing_conflict"):
        execute_runtime_horizon_write_with_approval_once(
            output_root=output,
            token=token,
            readiness=readiness,
            plan=plan,
            enabled=True,
            once=True,
            repository_root=repo,
        )
