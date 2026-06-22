# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_status_panel.py
# desc: Verify PS-Q16C producer status panel loader is read-only and observes the PS-Q16B status artifact without invoking runner/scheduler/export.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_runner import (  # noqa: E402
    build_prediction_warroom_non_ui_scheduled_producer_runner,
)
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_status_panel import (  # noqa: E402
    PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_STATUS_PANEL_VERSION,
    build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet,
)


def test_default_status_panel_is_read_blocked_without_explicit_allow() -> None:
    packet = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet().to_dict()
    assert packet["panel_version"] == PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_STATUS_PANEL_VERSION
    assert packet["allow_actual_read_requested"] is False
    assert packet["actual_file_read_attempted"] is False
    assert packet["payload_decode_succeeded"] is False
    assert "allow_actual_read_false" in packet["blocked_reasons"]
    assert packet["read_only"] is True
    assert packet["producer_runner_invoked"] is False
    assert packet["scheduler_enabled_by_this_panel"] is False
    assert packet["would_write_status_artifact"] is False
    assert packet["would_write_latest_prediction_artifact"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False


def test_status_panel_loads_status_artifact_read_only(tmp_path: Path) -> None:
    writer = build_prediction_warroom_non_ui_scheduled_producer_runner(
        hot_latest_root_hint=str(tmp_path),
        operator_acknowledged=True,
        allow_status_artifact_write=True,
        execute_status_artifact_write=True,
        allow_guard_test_root=True,
    ).to_dict()
    assert writer["status_artifact_written"] is True
    packet = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet(
        hot_latest_root_hint=str(tmp_path),
        allow_actual_read=True,
        allow_guard_test_root=True,
    ).to_dict()
    assert packet["panel_state"] == "producer_status_panel_loaded"
    assert packet["actual_file_read_succeeded"] is True
    assert packet["payload_decode_succeeded"] is True
    assert packet["producer_runner_invoked"] is False
    assert packet["would_write_status_artifact"] is False
    assert packet["would_write_latest_prediction_artifact"] is False
    payload = packet["payload"]
    assert payload["producer_enabled"] is False
    assert payload["scheduler_enabled"] is False
    assert payload["runtime_artifact_write_enabled"] is False
    assert payload["disable_rollback_state"] == "disabled_by_default_no_scheduler_no_latest_prediction_write"
    assert packet["status_rows"]
    assert packet["safety_rows"]
    assert packet["warning_rows"]


def test_status_panel_reports_missing_status_without_force_ready(tmp_path: Path) -> None:
    packet = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet(
        hot_latest_root_hint=str(tmp_path),
        allow_actual_read=True,
        allow_guard_test_root=True,
    ).to_dict()
    assert packet["panel_state"] == "producer_status_panel_missing"
    assert packet["path_exists"] is False
    assert packet["payload_decode_succeeded"] is False
    assert "producer_status_artifact_missing" in packet["warning_reasons"]
    assert packet["producer_runner_invoked"] is False
    assert packet["scheduler_enabled_by_this_panel"] is False
    assert packet["would_write_status_artifact"] is False


if __name__ == "__main__":
    test_default_status_panel_is_read_blocked_without_explicit_allow()
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp_dir:
        test_status_panel_loads_status_artifact_read_only(Path(temp_dir))
    with TemporaryDirectory() as temp_dir:
        test_status_panel_reports_missing_status_without_force_ready(Path(temp_dir))
    print(json.dumps({"ok": True}, ensure_ascii=False))
