# path: ./tools/test_phase4a_prediction_system_ps_q18ae_latest_prediction_summary_widget_candidate_resolver_refresh.py
# desc: Unit tests for PS-Q18AE latest_prediction_summary_widget candidate resolver refresh to present latest artifact.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ae_candidate_resolver_refresh import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK,
    REFRESHED_CANDIDATE_PATH,
    TRUE_BOUNDARIES,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_rows import (  # noqa: E402
    build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_result_packet,
)


def _assert_boundaries(packet: dict) -> None:
    for key in TRUE_BOUNDARIES:
        assert packet[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18ae_refreshes_candidate_to_present_latest_artifact_without_reading() -> None:
    packet = build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_result_packet(
        execute_refreshed_candidate_exists_check=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK,
    )
    assert packet["ok"] is True
    assert packet["previous_candidate_exists_result_state"] == "missing"
    assert packet["refreshed_candidate_path_shape_preview"] == REFRESHED_CANDIDATE_PATH
    assert packet["refreshed_candidate_relative_path"] == "prediction/latest_prediction_system_result.json"
    assert packet["refreshed_candidate_exists_checked"] is True
    assert packet["refreshed_candidate_exists_result_available"] is True
    assert packet["refreshed_candidate_exists_result_state"] == "present"
    assert packet["refreshed_candidate_present_observed"] is True
    assert packet["candidate_resolver_refresh_row_count"] == 12
    assert packet["source_artifact_schema_checked"] is False
    assert packet["actual_source_read_invoked"] is False
    assert packet["payload_parse_allowed"] is False
    assert packet["real_prediction_widget_rendering_allowed"] is False
    assert packet["refresh_invocation_allowed"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    _assert_boundaries(packet)


def test_ps_q18ae_without_ack_is_blocked_and_does_not_check() -> None:
    packet = build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_result_packet(
        execute_refreshed_candidate_exists_check=True,
        explicit_ack="",
    )
    assert packet["ok"] is False
    assert packet["refreshed_candidate_exists_check_allowed"] is False
    assert packet["refreshed_candidate_exists_checked"] is False
    assert packet["refreshed_candidate_exists_result_available"] is False
    assert packet["candidate_resolver_refresh_row_count"] == 0
    assert "explicit_ack_missing_or_mismatch" in packet["candidate_resolver_refresh_validation_failures"]
    assert packet["actual_source_read_invoked"] is False
    assert packet["source_artifact_schema_checked"] is False
