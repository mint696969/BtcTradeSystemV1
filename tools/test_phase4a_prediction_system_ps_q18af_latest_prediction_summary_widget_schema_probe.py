# path: ./tools/test_phase4a_prediction_system_ps_q18af_latest_prediction_summary_widget_schema_probe.py
# desc: Unit tests for PS-Q18AF bounded JSON schema probe.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18af_schema_probe import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK,
    TRUE_BOUNDARIES,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18af_schema_probe_rows import (  # noqa: E402
    build_latest_prediction_summary_widget_q18af_schema_probe_result_packet,
)


def _assert_boundaries(packet: dict) -> None:
    for key in TRUE_BOUNDARIES:
        assert packet[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18af_schema_probe_validates_refreshed_artifact_shape() -> None:
    packet = build_latest_prediction_summary_widget_q18af_schema_probe_result_packet(
        execute_schema_probe=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK,
    )
    assert packet["ok"] is True
    assert packet["schema_probe_file_read_invoked"] is True
    assert packet["schema_probe_json_decode_succeeded"] is True
    assert packet["source_artifact_schema_checked"] is True
    assert packet["source_artifact_schema_valid"] is True
    assert packet["record_count"] > 0
    assert packet["schema_probe_row_count"] == 12
    assert packet["actual_source_read_invoked"] is False
    assert packet["payload_to_widget_mapping_invoked"] is False
    assert packet["real_prediction_widget_rendering_allowed"] is False
    assert packet["refresh_invocation_allowed"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    _assert_boundaries(packet)


def test_ps_q18af_without_ack_is_blocked_and_does_not_read() -> None:
    packet = build_latest_prediction_summary_widget_q18af_schema_probe_result_packet(
        execute_schema_probe=True,
        explicit_ack="",
    )
    assert packet["ok"] is False
    assert packet["schema_probe_allowed"] is False
    assert packet["schema_probe_file_read_invoked"] is False
    assert packet["schema_probe_json_decode_invoked"] is False
    assert packet["source_artifact_schema_checked"] is False
    assert packet["schema_probe_row_count"] == 0
    assert "explicit_ack_missing_or_mismatch" in packet["schema_probe_validation_failures"]
    assert packet["actual_source_read_invoked"] is False
