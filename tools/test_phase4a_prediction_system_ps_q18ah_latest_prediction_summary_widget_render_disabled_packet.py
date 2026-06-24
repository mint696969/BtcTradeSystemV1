# path: ./tools/test_phase4a_prediction_system_ps_q18ah_latest_prediction_summary_widget_render_disabled_packet.py
# desc: Unit tests for PS-Q18AH latest_prediction_summary_widget render-disabled packet builder validation.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.mapping.latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK,
    TRUE_BOUNDARIES,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ah_render_disabled_packet_rows import (  # noqa: E402
    build_latest_prediction_summary_widget_q18ah_render_disabled_packet_result_packet,
)


def _assert_boundaries(packet: dict) -> None:
    for key in TRUE_BOUNDARIES:
        assert packet[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18ah_validates_render_disabled_packet_builder_without_real_rendering() -> None:
    packet = build_latest_prediction_summary_widget_q18ah_render_disabled_packet_result_packet(
        execute_packet_builder_validation=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK,
    )
    assert packet["ok"] is True
    assert packet["render_disabled_packet_builder_invoked"] is True
    assert packet["component_skeleton_packet_built"] is True
    assert packet["component_packet_valid"] is True
    assert packet["component_packet_render_disabled"] is True
    assert packet["component_packet_state"] == "read_only_component_skeleton_render_disabled"
    assert packet["mapped_values_visible_in_component_packet"] is True
    assert packet["mapped_record_count"] == 110
    assert packet["render_disabled_packet_row_count"] == 12
    assert packet["streamlit_render_invoked"] is False
    assert packet["real_prediction_widget_rendering_allowed"] is False
    assert packet["real_prediction_widget_render_invoked"] is False
    assert packet["refresh_invocation_allowed"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["actual_source_read_invoked"] is False
    _assert_boundaries(packet)


def test_ps_q18ah_without_ack_is_blocked_and_does_not_build_packet() -> None:
    packet = build_latest_prediction_summary_widget_q18ah_render_disabled_packet_result_packet(
        execute_packet_builder_validation=True,
        explicit_ack="",
    )
    assert packet["ok"] is False
    assert packet["render_disabled_packet_builder_invoked"] is False
    assert packet["component_skeleton_packet_built"] is False
    assert packet["component_packet"] == {}
    assert packet["render_disabled_packet_row_count"] == 0
    assert "explicit_ack_missing_or_mismatch" in packet["render_disabled_packet_validation_failures"]
    assert packet["streamlit_render_invoked"] is False
    assert packet["real_prediction_widget_rendering_allowed"] is False
