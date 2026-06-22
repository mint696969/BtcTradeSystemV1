# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_runner.py
# desc: Verify PS-Q16B disabled-by-default non-UI producer runner scaffold and status artifact writer boundaries.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    REQUIRED_STATUS_FIELDS,
)
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_runner import (  # noqa: E402
    PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION,
    build_prediction_warroom_non_ui_scheduled_producer_runner,
)


def test_default_runner_is_disabled_and_does_not_write() -> None:
    packet = build_prediction_warroom_non_ui_scheduled_producer_runner().to_dict()
    assert packet["runner_version"] == PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION
    assert packet["producer_enabled"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["runtime_artifact_write_enabled"] is False
    assert packet["latest_prediction_artifact_write_enabled"] is False
    assert packet["status_artifact_written"] is False
    assert packet["actual_export_runner_invoked"] is False
    assert packet["prediction_build_requested"] is False
    assert packet["latest_prediction_artifact_written"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["parameter_apply_allowed"] is False
    assert packet["parameter_staging_write_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["ready_for_scheduler_enablement"] is False
    assert packet["ready_for_latest_prediction_artifact_write_automation"] is False
    assert "status_artifact_write_not_executed" in packet["warning_reasons"]
    for field in REQUIRED_STATUS_FIELDS:
        assert field in packet["status_payload"]


def test_status_artifact_writer_is_explicit_and_guard_root_bounded(tmp_path: Path) -> None:
    packet = build_prediction_warroom_non_ui_scheduled_producer_runner(
        hot_latest_root_hint=str(tmp_path),
        operator_acknowledged=True,
        allow_status_artifact_write=True,
        execute_status_artifact_write=True,
        allow_guard_test_root=True,
    ).to_dict()
    assert packet["runner_state"] == "producer_disabled_status_written"
    assert packet["status_artifact_written"] is True
    assert packet["status_artifact_size_bytes"] and packet["status_artifact_size_bytes"] > 0
    assert packet["status_artifact_path"].endswith(PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH.replace("/", "\\")) or packet[
        "status_artifact_path"
    ].endswith(PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH)
    status_path = Path(packet["status_artifact_path"])
    data = json.loads(status_path.read_text(encoding="utf-8"))
    assert data["producer_version"] == PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION
    assert data["producer_enabled"] is False
    assert data["scheduler_enabled"] is False
    assert data["runtime_artifact_write_enabled"] is False
    assert data["disable_rollback_state"] == "disabled_by_default_no_scheduler_no_latest_prediction_write"
    assert data["latest_prediction_artifact_relative_path"] == "prediction/latest_prediction_system_result.json"
    assert data["status_artifact_relative_path"] == PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    assert all(field in data for field in REQUIRED_STATUS_FIELDS)


def test_forbidden_enablement_requests_are_blocked(tmp_path: Path) -> None:
    packet = build_prediction_warroom_non_ui_scheduled_producer_runner(
        hot_latest_root_hint=str(tmp_path),
        operator_acknowledged=True,
        allow_status_artifact_write=True,
        execute_status_artifact_write=True,
        allow_guard_test_root=True,
        request_enable_producer=True,
        request_scheduler_enable=True,
        request_latest_prediction_artifact_write=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["runner_state"] == "producer_disabled_status_blocked"
    assert packet["status_artifact_written"] is False
    assert packet["ready_for_scheduler_enablement"] is False
    assert packet["ready_for_latest_prediction_artifact_write_automation"] is False
    assert set(packet["blocked_reasons"]) >= {
        "producer_enable_not_allowed_in_ps_q16b",
        "scheduler_enable_not_allowed_in_ps_q16b",
        "latest_prediction_artifact_write_not_allowed_in_ps_q16b",
        "warroom_ui_trigger_not_allowed_in_ps_q16b",
        "parameter_apply_not_allowed_in_ps_q16b",
        "parameter_staging_write_not_allowed_in_ps_q16b",
        "approval_ledger_autotrade_broker_not_allowed_in_ps_q16b",
    }


if __name__ == "__main__":
    test_default_runner_is_disabled_and_does_not_write()
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp_dir:
        test_status_artifact_writer_is_explicit_and_guard_root_bounded(Path(temp_dir))
    with TemporaryDirectory() as temp_dir:
        test_forbidden_enablement_requests_are_blocked(Path(temp_dir))
    print("ok")
