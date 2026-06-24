# path: ./tools/test_phase4a_prediction_system_ps_q18ag_latest_prediction_summary_widget_payload_to_props_mapping.py
# desc: Unit tests for PS-Q18AG payload-to-widget props mapping preflight.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.components.prediction_widgets._shared import REQUIRED_COMPONENT_PROPS  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.mapping.latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK,
    TRUE_BOUNDARIES,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ag_payload_to_props_mapping_rows import (  # noqa: E402
    build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_result_packet,
)


def _assert_boundaries(packet: dict) -> None:
    for key in TRUE_BOUNDARIES:
        assert packet[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18ag_maps_payload_to_props_candidate_without_rendering() -> None:
    packet = build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_result_packet(
        execute_mapping_preflight=True,
        explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK,
    )
    assert packet["ok"] is True
    assert packet["mapping_payload_read_invoked"] is True
    assert packet["mapping_payload_json_decode_succeeded"] is True
    assert packet["forecast_batch_records_consumed"] is True
    assert packet["record_count"] == 110
    assert packet["props_contract_complete"] is True
    assert packet["payload_to_props_mapping_row_count"] == 12
    candidate = packet["props_candidate"]
    for field in REQUIRED_COMPONENT_PROPS:
        assert field in candidate, field
    assert candidate["source_generated_at"] == packet["mapped_generated_at"]
    assert candidate["source_artifact_ref"] == "hot://prediction/latest_prediction_system_result.json"
    assert packet["component_props_bound_to_component"] is False
    assert packet["real_prediction_widget_rendering_allowed"] is False
    assert packet["render_latest_prediction_summary_widget_invoked"] is False
    assert packet["refresh_invocation_allowed"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["actual_source_read_invoked"] is False
    _assert_boundaries(packet)


def test_ps_q18ag_without_ack_is_blocked_and_does_not_read() -> None:
    packet = build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_result_packet(
        execute_mapping_preflight=True,
        explicit_ack="",
    )
    assert packet["ok"] is False
    assert packet["mapping_allowed"] is False
    assert packet["mapping_payload_read_invoked"] is False
    assert packet["mapping_payload_json_decode_invoked"] is False
    assert packet["props_candidate"] == {}
    assert packet["payload_to_props_mapping_row_count"] == 0
    assert "explicit_ack_missing_or_mismatch" in packet["payload_to_props_mapping_validation_failures"]
    assert packet["actual_source_read_invoked"] is False
    assert packet["real_prediction_widget_rendering_allowed"] is False
