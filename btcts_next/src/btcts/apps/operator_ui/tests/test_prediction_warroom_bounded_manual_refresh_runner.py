# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_bounded_manual_refresh_runner.py
# desc: Verify PS-Q16D bounded manual refresh runner gates actual export and status writes behind explicit operator flags.

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_bounded_manual_refresh_runner import (  # noqa: E402
    PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
    build_prediction_warroom_bounded_manual_refresh_runner,
)


def _fake_export_success(**kwargs: Any) -> dict[str, Any]:
    root = Path(str(kwargs["hot_latest_root_hint"]))
    target = root / "prediction" / "latest_prediction_system_result.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('{"ok": true}\n', encoding="utf-8")
    return {
        "runner_state": "latest_payload_actual_export_runner_exported",
        "target_file_written": True,
        "target_artifact_path": str(target),
        "target_file_size_bytes": target.stat().st_size,
        "prediction_run_id": "prediction_system.ps_q16d.test:BTC_JPY:bitFlyer:2026-06-22T10:00:00Z",
        "generated_at": "2026-06-22T10:00:00Z",
        "exported_at": "2026-06-22T10:00:01Z",
        "blocked_reasons": [],
        "warning_reasons": ["test_warning_visible"],
        "warroom_page_mutation_allowed": False,
        "warroom_panel_mutation_allowed": False,
        "ui_triggered_runner_execution": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "authorization_grant_requested": False,
        "autotrade_trigger_enabled": False,
    }


def test_default_manual_refresh_is_blocked_and_does_not_invoke_export() -> None:
    called = {"value": False}

    def _should_not_call(**_: Any) -> dict[str, Any]:
        called["value"] = True
        raise AssertionError("export runner should not be called")

    packet = build_prediction_warroom_bounded_manual_refresh_runner(actual_export_runner=_should_not_call).to_dict()
    assert packet["runner_version"] == PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION
    assert packet["actual_export_runner_invoked"] is False
    assert called["value"] is False
    assert packet["latest_prediction_artifact_written"] is False
    assert packet["status_artifact_written"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["scheduled_loop_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["parameter_apply_allowed"] is False
    assert packet["parameter_staging_write_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert "operator_acknowledgement_required" in packet["blocked_reasons"]
    assert "execute_manual_refresh_false" in packet["blocked_reasons"]


def test_explicit_bounded_manual_refresh_invokes_export_and_writes_status(tmp_path: Path) -> None:
    packet = build_prediction_warroom_bounded_manual_refresh_runner(
        hot_latest_root_hint=str(tmp_path),
        operator_acknowledged=True,
        execute_manual_refresh=True,
        allow_actual_read=True,
        allow_prediction_build=True,
        allow_export_preflight=True,
        allow_latest_payload_export=True,
        allow_runtime_artifact_write=True,
        allow_status_artifact_write=True,
        execute_status_artifact_write=True,
        allow_guard_test_root=True,
        actual_export_runner=_fake_export_success,
    ).to_dict()
    assert packet["runner_state"] == "bounded_manual_refresh_exported_status_written"
    assert packet["actual_export_runner_invoked"] is True
    assert packet["latest_prediction_artifact_written"] is True
    assert packet["status_artifact_written"] is True
    assert packet["scheduler_enabled"] is False
    assert packet["scheduled_loop_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["ready_for_scheduler_enablement"] is False
    status_path = Path(packet["status_artifact_path"])
    data = json.loads(status_path.read_text(encoding="utf-8"))
    assert data["producer_version"] == PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION
    assert data["producer_enabled"] is False
    assert data["scheduler_enabled"] is False
    assert data["runtime_artifact_write_enabled"] is True
    assert data["last_success_generated_at"] == "2026-06-22T10:00:00Z"
    assert data["last_prediction_run_id"] == "prediction_system.ps_q16d.test:BTC_JPY:bitFlyer:2026-06-22T10:00:00Z"
    assert data["last_target_file_size_bytes"] == packet["latest_prediction_artifact_size_bytes"]
    assert data["disable_rollback_state"] == "manual_refresh_only_disable_by_not_running; scheduler_not_registered"


def test_forbidden_ui_scheduler_and_approval_requests_block_without_export(tmp_path: Path) -> None:
    called = {"value": False}

    def _should_not_call(**_: Any) -> dict[str, Any]:
        called["value"] = True
        return {}

    packet = build_prediction_warroom_bounded_manual_refresh_runner(
        hot_latest_root_hint=str(tmp_path),
        operator_acknowledged=True,
        execute_manual_refresh=True,
        allow_actual_read=True,
        allow_prediction_build=True,
        allow_export_preflight=True,
        allow_latest_payload_export=True,
        allow_runtime_artifact_write=True,
        allow_status_artifact_write=True,
        execute_status_artifact_write=True,
        allow_guard_test_root=True,
        actual_export_runner=_should_not_call,
        request_scheduler_enable=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert called["value"] is False
    assert packet["actual_export_runner_invoked"] is False
    assert packet["latest_prediction_artifact_written"] is False
    assert packet["status_artifact_written"] is True
    assert packet["runner_state"] == "bounded_manual_refresh_blocked_status_written"
    assert set(packet["blocked_reasons"]) >= {
        "scheduler_enable_not_allowed_in_ps_q16d",
        "warroom_ui_trigger_not_allowed_in_ps_q16d",
        "parameter_apply_not_allowed_in_ps_q16d",
        "parameter_staging_write_not_allowed_in_ps_q16d",
        "approval_ledger_autotrade_broker_not_allowed_in_ps_q16d",
    }


if __name__ == "__main__":
    test_default_manual_refresh_is_blocked_and_does_not_invoke_export()
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp_dir:
        test_explicit_bounded_manual_refresh_invokes_export_and_writes_status(Path(temp_dir))
    with TemporaryDirectory() as temp_dir:
        test_forbidden_ui_scheduler_and_approval_requests_block_without_export(Path(temp_dir))
    print(json.dumps({"ok": True}, ensure_ascii=False))
