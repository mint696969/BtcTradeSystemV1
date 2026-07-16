# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_dhot_write_once.py
# desc: MR-F9.19J fresh-package exact-authorization one-shot tool tests.

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once import (
    _default_authorization_reader,
    execute_runtime_horizon_dhot_write_once,
    main,
)

NOW = "2026-07-16T18:00:00Z"


def _preflight() -> dict:
    return {
        "generated_at": NOW,
        "shadow_candidate_id": "candidate:test",
        "runtime_horizon_persistence_plan_built": True,
        "runtime_horizon_writer_registered": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "runtime_horizon_persistence_plan": {"schema_version": "plan:test"},
    }


def _readiness(root) -> dict:
    return {
        "ready": True,
        "blockers": (),
        "destination_root": str(root.resolve()),
        "run_id": "run:test",
        "prediction_origin": NOW,
        "operator_id": "mint",
    }


def _token(root) -> dict:
    return {
        "destination_root": str(root.resolve()),
        "run_id": "run:test",
        "prediction_origin": NOW,
        "operator_id": "mint",
        "approval_token_sha256": "a" * 64,
        "readiness_sha256": "b" * 64,
    }


def _package(root) -> dict:
    order = tuple([f"horizon={index}.json" for index in range(8)] + ["manifest.json"])
    text = (
        "AUTHORIZE MR-F9 ONE-SHOT D-HOT WRITE run_id=run:test "
        f"approval_token_sha256={'a' * 64} operator_id=mint paths=9"
    )
    return {
        "destination_root": str(root.resolve()),
        "run_id": "run:test",
        "prediction_origin": NOW,
        "approval_token_sha256": "a" * 64,
        "authorization_package_sha256": "c" * 64,
        "expires_at": "2026-07-16T18:05:00Z",
        "expected_authorization_text_sha256": "d" * 64,
        "expected_authorization_text": text,
        "write_order": order,
    }


def _write_result() -> dict:
    order = tuple([f"horizon={index}.json" for index in range(8)] + ["manifest.json"])
    return {
        "written": True,
        "duplicate": False,
        "written_count": 9,
        "duplicate_count": 0,
        "written_paths": order,
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


def _execute(tmp_path, *, supplied_text=None, writer_result=None):
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    package = _package(destination)
    reader = Mock(return_value=package["expected_authorization_text"] if supplied_text is None else supplied_text)
    writer = Mock(return_value=_write_result() if writer_result is None else writer_result)
    with patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_shadow_runtime_preflight_once",
        return_value=_preflight(),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_readiness_report",
        return_value=_readiness(destination),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_approval_token",
        return_value=_token(destination),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_authorization_package",
        return_value=package,
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.validate_runtime_horizon_write_authorization_package"
    ) as validator, patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.persist_runtime_horizon_plan_once",
        writer,
    ):
        result = execute_runtime_horizon_dhot_write_once(
            source_root=source,
            destination_root=destination,
            shadow_candidate_id="candidate:test",
            operator_id="mint",
            enabled=True,
            once=True,
            authorization_reader=reader,
            now_provider=Mock(side_effect=[NOW, NOW, NOW]),
        )
    return result, reader, validator, writer, destination


def test_default_authorization_reader_displays_bound_context(monkeypatch, capsys, tmp_path) -> None:
    package = _package(tmp_path / "destination")
    expected = package["expected_authorization_text"]
    monkeypatch.setattr("builtins.input", lambda prompt: expected)

    assert _default_authorization_reader(expected, package) == expected
    output = capsys.readouterr().out
    assert package["destination_root"] in output
    assert package["run_id"] in output
    assert package["prediction_origin"] in output
    assert package["expires_at"] in output
    assert package["authorization_package_sha256"] in output
    assert expected in output


def test_requires_enabled_and_once_before_preflight(tmp_path) -> None:
    with patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_shadow_runtime_preflight_once"
    ) as preflight:
        with pytest.raises(PermissionError, match="enabled_ack_required"):
            execute_runtime_horizon_dhot_write_once(
                source_root=tmp_path / "source",
                destination_root=tmp_path / "destination",
                    shadow_candidate_id="candidate:test",
                operator_id="mint",
            )
        with pytest.raises(PermissionError, match="once_ack_required"):
            execute_runtime_horizon_dhot_write_once(
                source_root=tmp_path / "source",
                destination_root=tmp_path / "destination",
                    shadow_candidate_id="candidate:test",
                operator_id="mint",
                enabled=True,
            )
        preflight.assert_not_called()


def test_exact_authorization_is_validated_before_writer(tmp_path) -> None:
    result, reader, validator, writer, destination = _execute(tmp_path)
    expected = _package(destination)["expected_authorization_text"]
    reader.assert_called_once()
    assert reader.call_args.args[0] == expected
    assert validator.call_count == 2
    writer.assert_called_once_with(
        destination.resolve(),
        plan=_preflight()["runtime_horizon_persistence_plan"],
        enabled=True,
        once=True,
    )
    assert result["authorization_validated"] is True
    assert result["human_authorized"] is True
    assert result["writer_invoked"] is True
    assert result["write_result"]["written_count"] == 9
    assert result["latest_pointer_created"] is False
    assert result["scheduler_enabled"] is False
    assert result["producer_loop_enabled"] is False
    assert result["websocket_opened"] is False
    assert result["order_submission_allowed"] is False


def test_mismatched_or_empty_authorization_never_invokes_writer(tmp_path) -> None:
    for supplied in ("", "wrong", " AUTHORIZE"):
        with pytest.raises(PermissionError, match="authorization_text_mismatch"):
            _execute(tmp_path, supplied_text=supplied)


def test_expired_package_before_writer_never_invokes_writer(tmp_path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    package = _package(destination)
    writer = Mock()
    validator = Mock(side_effect=[None, PermissionError("runtime_horizon_write_authorization_expired")])
    with patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_shadow_runtime_preflight_once",
        return_value=_preflight(),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_readiness_report",
        return_value=_readiness(destination),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_approval_token",
        return_value=_token(destination),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_authorization_package",
        return_value=package,
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.validate_runtime_horizon_write_authorization_package",
        validator,
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.persist_runtime_horizon_plan_once",
        writer,
    ):
        with pytest.raises(PermissionError, match="expired"):
            execute_runtime_horizon_dhot_write_once(
                source_root=source,
                destination_root=destination,
                    shadow_candidate_id="candidate:test",
                operator_id="mint",
                enabled=True,
                once=True,
                authorization_reader=lambda expected, package: expected,
                now_provider=Mock(side_effect=[NOW, NOW, "2026-07-16T18:06:00Z"]),
            )
    writer.assert_not_called()


def test_readiness_or_preflight_safety_failure_never_invokes_writer(tmp_path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    unsafe = _preflight()
    unsafe["scheduler_enabled"] = True
    with patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_shadow_runtime_preflight_once",
        return_value=unsafe,
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.persist_runtime_horizon_plan_once"
    ) as writer:
        with pytest.raises(ValueError, match="preflight_safety_invalid:scheduler_enabled"):
            execute_runtime_horizon_dhot_write_once(
                source_root=source,
                destination_root=destination,
                    shadow_candidate_id="candidate:test",
                operator_id="mint",
                enabled=True,
                once=True,
            )
        writer.assert_not_called()

    blocked = _readiness(destination)
    blocked["ready"] = False
    blocked["blockers"] = ("destination_conflict",)
    with patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_shadow_runtime_preflight_once",
        return_value=_preflight(),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_readiness_report",
        return_value=blocked,
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.persist_runtime_horizon_plan_once"
    ) as writer:
        with pytest.raises(PermissionError, match="readiness_not_ready"):
            execute_runtime_horizon_dhot_write_once(
                source_root=source,
                destination_root=destination,
                    shadow_candidate_id="candidate:test",
                operator_id="mint",
                enabled=True,
                once=True,
            )
        writer.assert_not_called()


def test_mixed_written_and_duplicate_paths_are_accepted_in_package_order(tmp_path) -> None:
    order = _write_result()["written_paths"]
    mixed = _write_result()
    mixed["written"] = True
    mixed["duplicate"] = False
    mixed["written_paths"] = (order[1], order[3], order[5], order[7], order[8])
    mixed["duplicate_paths"] = (order[0], order[2], order[4], order[6])
    mixed["written_count"] = 5
    mixed["duplicate_count"] = 4
    mixed["manifest_written_last"] = True

    result, _, _, writer, _ = _execute(tmp_path, writer_result=mixed)
    writer.assert_called_once()
    assert result["write_result"]["written_count"] == 5
    assert result["write_result"]["duplicate_count"] == 4


def test_manifest_receipt_path_must_match_package_manifest(tmp_path) -> None:
    bad = _write_result()
    bad["manifest_relpath"] = "other-manifest.json"
    with pytest.raises(ValueError, match="manifest_receipt_path_mismatch"):
        _execute(tmp_path, writer_result=bad)


def test_writer_result_must_match_exact_nine_path_order(tmp_path) -> None:
    bad = _write_result()
    bad["written_paths"] = tuple(reversed(bad["written_paths"]))
    with pytest.raises(ValueError, match="written_path_order_mismatch"):
        _execute(tmp_path, writer_result=bad)

    order = _write_result()["written_paths"]
    bad = _write_result()
    bad["written_paths"] = order[4:]
    bad["duplicate_paths"] = tuple(reversed(order[:4]))
    bad["written_count"] = 5
    bad["duplicate_count"] = 4
    with pytest.raises(ValueError, match="duplicate_path_order_mismatch"):
        _execute(tmp_path, writer_result=bad)

    bad = _write_result()
    bad["manifest_written_last"] = False
    with pytest.raises(ValueError, match="manifest_not_written_last"):
        _execute(tmp_path, writer_result=bad)


def test_readiness_receives_destination_bound_copy_without_mutating_source_preflight(tmp_path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source_preflight = _preflight()
    source_preflight["hot_root"] = str(source.resolve())
    package = _package(destination)

    with patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_shadow_runtime_preflight_once",
        return_value=source_preflight,
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_readiness_report",
        return_value=_readiness(destination),
    ) as readiness_builder, patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_approval_token",
        return_value=_token(destination),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_authorization_package",
        return_value=package,
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.validate_runtime_horizon_write_authorization_package"
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.persist_runtime_horizon_plan_once",
        return_value=_write_result(),
    ):
        execute_runtime_horizon_dhot_write_once(
            source_root=source,
            destination_root=destination,
            shadow_candidate_id="candidate:test",
            operator_id="mint",
            enabled=True,
            once=True,
            authorization_reader=lambda expected, package: expected,
            now_provider=Mock(side_effect=[NOW, NOW, NOW]),
        )

    readiness_preflight = readiness_builder.call_args.kwargs["preflight"]
    assert readiness_preflight is not source_preflight
    assert readiness_preflight["hot_root"] == str(destination.resolve())
    assert source_preflight["hot_root"] == str(source.resolve())
    assert readiness_preflight["runtime_horizon_persistence_plan"] is source_preflight["runtime_horizon_persistence_plan"]


def test_preflight_generated_at_comes_from_now_provider(tmp_path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    package = _package(destination)
    now_provider = Mock(side_effect=[NOW, NOW, NOW])
    with patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_shadow_runtime_preflight_once",
        return_value=_preflight(),
    ) as preflight, patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_readiness_report",
        return_value=_readiness(destination),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_approval_token",
        return_value=_token(destination),
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.build_runtime_horizon_write_authorization_package",
        return_value=package,
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.validate_runtime_horizon_write_authorization_package"
    ), patch(
        "btcts.prediction.market_regime.tools.runtime_horizon_dhot_write_once.persist_runtime_horizon_plan_once",
        return_value=_write_result(),
    ):
        execute_runtime_horizon_dhot_write_once(
            source_root=source,
            destination_root=destination,
            shadow_candidate_id="candidate:test",
            operator_id="mint",
            enabled=True,
            once=True,
            authorization_reader=lambda expected, package: expected,
            now_provider=now_provider,
        )
    assert preflight.call_args.kwargs["generated_at"] == NOW
    assert now_provider.call_count == 3


def test_main_requires_each_acknowledgement_flag() -> None:
    base = [
        "--source-root", "source",
        "--destination-root", "destination",
        "--shadow-candidate-id", "candidate:test",
        "--operator-id", "mint",
    ]
    for partial in ([], ["--enabled"], ["--once"]):
        with pytest.raises(SystemExit) as exc:
            main(base + partial)
        assert exc.value.code != 0
