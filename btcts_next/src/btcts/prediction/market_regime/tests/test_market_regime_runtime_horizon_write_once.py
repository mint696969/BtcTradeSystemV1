# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_write_once.py
# desc: MR-F9.19E explicit once-only CLI boundary tests; output roots are repository tmp only.

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from btcts.prediction.market_regime.tools.runtime_horizon_write_once import (
    classify_output_root,
    execute_runtime_horizon_write_once,
    main,
)


def _preflight() -> dict:
    return {
        "generated_at": "2026-07-16T15:00:00Z",
        "shadow_candidate_id": "candidate:test",
        "runtime_horizon_persistence_plan_built": True,
        "runtime_horizon_writer_registered": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "runtime_horizon_persistence_plan": {"schema_version": "plan:test"},
    }


def _write_result() -> dict:
    return {
        "written": True,
        "duplicate": False,
        "written_count": 9,
        "duplicate_count": 0,
        "written_paths": ("horizon=0.json", "manifest.json"),
        "duplicate_paths": (),
        "manifest_relpath": "manifest.json",
        "manifest_written_last": True,
        "latest_pointer_created": False,
        "writer_registered": False,
        "producer_loop_enabled": False,
        "scheduler_enabled": False,
        "websocket_opened": False,
        "order_submission_allowed": False,
    }


def test_output_root_must_be_inside_repository_tmp(tmp_path) -> None:
    repo = tmp_path / "repo"
    allowed = repo / "tmp" / "mr_f9"
    assert classify_output_root(allowed, repository_root=repo) == "repo_tmp"
    with pytest.raises(ValueError, match="output_root_not_repo_tmp"):
        classify_output_root(repo / "outside", repository_root=repo)
    with pytest.raises(ValueError, match="output_root_not_repo_tmp"):
        classify_output_root(tmp_path / "d_hot", repository_root=repo)


def test_execute_requires_enabled_and_once_before_preflight(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "writer"
    with patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_write_once.build_shadow_runtime_preflight_once"
    ) as preflight:
        with pytest.raises(PermissionError, match="enabled_ack_required"):
            execute_runtime_horizon_write_once(
                hot_root=tmp_path / "hot",
                output_root=output,
                generated_at="2026-07-16T15:00:00Z",
                shadow_candidate_id="candidate:test",
                repository_root=repo,
            )
        with pytest.raises(PermissionError, match="once_ack_required"):
            execute_runtime_horizon_write_once(
                hot_root=tmp_path / "hot",
                output_root=output,
                generated_at="2026-07-16T15:00:00Z",
                shadow_candidate_id="candidate:test",
                enabled=True,
                repository_root=repo,
            )
        preflight.assert_not_called()


def test_execute_composes_preflight_plan_and_guarded_writer_once(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "writer"
    hot = tmp_path / "hot"
    preflight = _preflight()
    writer = Mock(return_value=_write_result())

    with patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_write_once.build_shadow_runtime_preflight_once",
        return_value=preflight,
    ) as preflight_builder, patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_write_once.persist_runtime_horizon_plan_once",
        writer,
    ):
        result = execute_runtime_horizon_write_once(
            hot_root=hot,
            output_root=output,
            generated_at="2026-07-16T15:00:00Z",
            shadow_candidate_id="candidate:test",
            enabled=True,
            once=True,
            repository_root=repo,
        )

    preflight_builder.assert_called_once_with(
        hot_root=hot,
        generated_at="2026-07-16T15:00:00Z",
        shadow_candidate_id="candidate:test",
    )
    writer.assert_called_once_with(
        output.resolve(),
        plan=preflight["runtime_horizon_persistence_plan"],
        enabled=True,
        once=True,
    )
    assert result["output_root_kind"] == "repo_tmp"
    assert result["write_result"]["written_count"] == 9
    assert result["write_result"]["manifest_written_last"] is True
    assert result["writes_dhot"] is False
    assert result["writer_registered"] is False
    assert result["latest_pointer_created"] is False
    assert result["scheduler_enabled"] is False
    assert result["producer_loop_enabled"] is False
    assert result["websocket_opened"] is False
    assert result["order_submission_allowed"] is False
    assert result["ui_inference_allowed"] is False
    assert result["ui_confidence_recalculation_allowed"] is False


def test_execute_rejects_preflight_runtime_activation_or_missing_plan(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "writer"
    cases = (
        ("runtime_horizon_persistence_plan_built", False, "plan_not_built"),
        ("runtime_horizon_writer_registered", True, "writer_registration_invalid"),
        ("writer_invoked", True, "preflight_writer_state_invalid"),
        ("writes_dhot", True, "preflight_dhot_state_invalid"),
    )
    for key, value, error in cases:
        preflight = _preflight()
        preflight[key] = value
        with patch(
            "btcts.prediction.market_regime.tools.runtime_horizon_write_once.build_shadow_runtime_preflight_once",
            return_value=preflight,
        ), patch(
            "btcts.prediction.market_regime.tools.runtime_horizon_write_once.persist_runtime_horizon_plan_once"
        ) as writer:
            with pytest.raises(ValueError, match=error):
                execute_runtime_horizon_write_once(
                    hot_root=tmp_path / "hot",
                    output_root=output,
                    generated_at="2026-07-16T15:00:00Z",
                    shadow_candidate_id="candidate:test",
                    enabled=True,
                    once=True,
                    repository_root=repo,
                )
            writer.assert_not_called()


def test_main_requires_enabled_and_once_flags() -> None:
    with pytest.raises(SystemExit) as exc:
        main([
            "--hot-root", "hot",
            "--output-root", "tmp/out",
            "--generated-at", "2026-07-16T15:00:00Z",
            "--shadow-candidate-id", "candidate:test",
        ])
    assert exc.value.code != 0


def test_execute_rejects_writer_runtime_activation_result(tmp_path) -> None:
    repo = tmp_path / "repo"
    output = repo / "tmp" / "writer"
    for key in (
        "latest_pointer_created",
        "writer_registered",
        "producer_loop_enabled",
        "scheduler_enabled",
        "websocket_opened",
        "order_submission_allowed",
    ):
        unsafe = _write_result()
        unsafe[key] = True
        with patch(
            "btcts.prediction.market_regime.tools.runtime_horizon_write_once.build_shadow_runtime_preflight_once",
            return_value=_preflight(),
        ), patch(
            "btcts.prediction.market_regime.tools.runtime_horizon_write_once.persist_runtime_horizon_plan_once",
            return_value=unsafe,
        ):
            with pytest.raises(ValueError, match=f"writer_result_safety_invalid:{key}"):
                execute_runtime_horizon_write_once(
                    hot_root=tmp_path / "hot",
                    output_root=output,
                    generated_at="2026-07-16T15:00:00Z",
                    shadow_candidate_id="candidate:test",
                    enabled=True,
                    once=True,
                    repository_root=repo,
                )


def test_main_requires_each_acknowledgement_flag() -> None:
    base = [
        "--hot-root", "hot",
        "--output-root", "tmp/out",
        "--generated-at", "2026-07-16T15:00:00Z",
        "--shadow-candidate-id", "candidate:test",
    ]
    for partial in (["--enabled"], ["--once"]):
        with pytest.raises(SystemExit) as exc:
            main(base + partial)
        assert exc.value.code != 0
