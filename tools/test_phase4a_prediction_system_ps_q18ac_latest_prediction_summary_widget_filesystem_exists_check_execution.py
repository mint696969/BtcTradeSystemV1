# path: ./tools/test_phase4a_prediction_system_ps_q18ac_latest_prediction_summary_widget_filesystem_exists_check_execution.py
# desc: Unit tests for PS-Q18AC latest_prediction_summary_widget bounded filesystem existence check execution.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ac_filesystem_exists_check import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_ACK,
    TRUE_BOUNDARIES,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ac_filesystem_exists_check_rows import (  # noqa: E402
    build_latest_prediction_summary_widget_q18ac_filesystem_exists_check_result_packet,
)


def _assert_boundaries(packet: dict) -> None:
    for key in TRUE_BOUNDARIES:
        assert packet[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18ac_executes_exists_check_without_reading_or_schema() -> None:
    packet = build_latest_prediction_summary_widget_q18ac_filesystem_exists_check_result_packet(
        execute_filesystem_exists_check=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_ACK,
    )
    assert packet["ok"] is True
    assert packet["filesystem_exists_check_executed"] is True
    assert packet["source_artifact_exists_checked"] is True
    assert packet["source_artifact_exists_result_available"] is True
    assert packet["source_artifact_exists_result_state"] in {"exists", "missing"}
    assert isinstance(packet["source_artifact_exists_result"], bool)
    assert packet["filesystem_exists_check_row_count"] == 12
    assert packet["source_artifact_schema_checked"] is False
    assert packet["actual_source_read_invoked"] is False
    assert packet["payload_reparse_allowed"] is False
    assert packet["real_prediction_widget_rendering_allowed"] is False
    assert packet["refresh_invocation_allowed"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    _assert_boundaries(packet)


def test_ps_q18ac_without_ack_is_blocked_and_has_no_result() -> None:
    packet = build_latest_prediction_summary_widget_q18ac_filesystem_exists_check_result_packet(
        execute_filesystem_exists_check=True,
        explicit_ack="",
    )
    assert packet["ok"] is False
    assert packet["filesystem_exists_check_execution_allowed"] is False
    assert packet["filesystem_exists_check_executed"] is False
    assert packet["source_artifact_exists_result_available"] is False
    assert packet["filesystem_exists_check_row_count"] == 0
    assert "explicit_ack_missing_or_mismatch" in packet["filesystem_exists_check_validation_failures"]
    assert packet["actual_source_read_invoked"] is False
    assert packet["source_artifact_schema_checked"] is False
