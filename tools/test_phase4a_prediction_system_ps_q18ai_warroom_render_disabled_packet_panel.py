# path: ./tools/test_phase4a_prediction_system_ps_q18ai_warroom_render_disabled_packet_panel.py
# desc: Unit tests for PS-Q18AI WarRoom render-disabled packet status/value panel mount.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel import (  # noqa: E402
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ai_warroom_panel_packet,
)


def _assert_boundaries(packet: dict) -> None:
    for key in TRUE_BOUNDARIES:
        assert packet[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18ai_builds_warroom_panel_packet_without_refresh_or_real_render() -> None:
    packet = build_latest_prediction_summary_widget_q18ai_warroom_panel_packet()
    assert packet["ok"] is True
    assert packet["warroom_display_mounted"] is True
    assert packet["component_packet_valid"] is True
    assert packet["component_packet_render_disabled"] is True
    assert packet["component_packet_state"] == "read_only_component_skeleton_render_disabled"
    assert packet["component_source_generated_at"] == "2026-06-22T13:34:38Z"
    assert packet["mapped_record_count"] == 110
    assert packet["display_row_count"] == 12
    assert packet["real_prediction_widget_render_invoked"] is False
    assert packet["streamlit_real_widget_render_invoked"] is False
    assert packet["refresh_invocation_allowed"] is False
    assert packet["auto_refresh_enabled"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    _assert_boundaries(packet)
