# path: ./tools/test_phase4a_prediction_system_ps_q18ad_latest_prediction_summary_widget_schema_validation_gate.py
# desc: Unit tests for PS-Q18AD latest_prediction_summary_widget schema validation gate blocked by missing source.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ad_schema_validation_gate import (  # noqa: E402
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ad_schema_validation_gate_rows import (  # noqa: E402
    build_latest_prediction_summary_widget_q18ad_schema_validation_gate_result_packet,
)


def _assert_boundaries(packet: dict) -> None:
    for key in TRUE_BOUNDARIES:
        assert packet[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18ad_blocks_schema_validation_for_missing_source_without_reading() -> None:
    packet = build_latest_prediction_summary_widget_q18ad_schema_validation_gate_result_packet()
    assert packet["ok"] is True
    assert packet["source_artifact_exists_result_state"] == "missing"
    assert packet["schema_validation_blocked"] is True
    assert packet["schema_validation_block_reason"] == "source_artifact_missing_after_filesystem_exists_check"
    assert packet["source_artifact_schema_result_state"] == "blocked_missing_source_artifact"
    assert packet["schema_validation_gate_row_count"] == 12
    assert packet["filesystem_exists_check_reexecuted"] is False
    assert packet["source_artifact_schema_check_allowed"] is False
    assert packet["source_artifact_schema_checked"] is False
    assert packet["source_artifact_schema_result_available"] is False
    assert packet["actual_source_read_invoked"] is False
    assert packet["payload_parse_allowed"] is False
    assert packet["real_prediction_widget_rendering_allowed"] is False
    assert packet["refresh_invocation_allowed"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    _assert_boundaries(packet)


def test_ps_q18ad_rejects_non_missing_source_result() -> None:
    packet = build_latest_prediction_summary_widget_q18ad_schema_validation_gate_result_packet(
        supplied_q18ac_filesystem_exists_result_packet={
            "ok": True,
            "source_artifact_exists_checked": True,
            "source_artifact_exists_result_available": True,
            "source_artifact_exists_result_state": "exists",
            "source_artifact_schema_checked": False,
            "actual_source_read_invoked": False,
            "path_shape_preview": "D:/btc_ts_hot/prediction_sources/BTC-USD/2026-06-22T00:00:00Z/latest_prediction.json",
            "source_candidate_count": 1,
        }
    )
    assert packet["ok"] is False
    assert packet["schema_validation_gate_row_count"] == 0
    assert any(str(item).startswith("source_artifact_exists_result_state_not_missing") for item in packet["schema_validation_gate_validation_failures"])
    assert packet["source_artifact_schema_checked"] is False
    assert packet["actual_source_read_invoked"] is False
