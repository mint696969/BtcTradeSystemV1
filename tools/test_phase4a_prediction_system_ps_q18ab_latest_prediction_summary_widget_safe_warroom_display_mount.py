# path: ./tools/test_phase4a_prediction_system_ps_q18ab_latest_prediction_summary_widget_safe_warroom_display_mount.py
# desc: Unit tests for PS-Q18AB latest_prediction_summary_widget safe WarRoom display mount panel packet.

from __future__ import annotations

import os
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ab_safe_display_mount_panel import (  # noqa: E402
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_STATE,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet,
    latest_prediction_summary_widget_q18ab_safe_display_mount_rows,
)


def test_ps_q18ab_safe_display_mount_packet_is_read_only_panel_mount_only() -> None:
    packet = build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet()
    assert packet["ok"] is True
    assert packet["safe_display_mount_panel_ack"] == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_ACK
    assert packet["safe_display_mount_panel_state"] == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_STATE
    assert packet["q18aa_mount_preflight_gate_ready"] is True
    assert packet["safe_display_mount_panel_row_count"] == 12
    assert packet["q18aa_mount_preflight_gate_row_count"] == 12
    assert packet["display_packet_row_count"] == 12
    assert packet["source_candidate_count"] == 1
    assert packet["warroom_display_mount_allowed"] is True
    assert packet["warroom_display_mounted"] is True
    assert packet["real_prediction_widget_rendering_allowed"] is False
    assert packet["render_latest_prediction_summary_widget_invoked"] is False
    assert packet["actual_source_read_invoked"] is False
    assert packet["refresh_invocation_allowed"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    for key in TRUE_BOUNDARIES:
        assert packet[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
    rows = latest_prediction_summary_widget_q18ab_safe_display_mount_rows(packet)
    assert len(rows) == 12
    assert all(row["real_widget_render"] == "false" for row in rows)
    assert all(row["actual_source_read"] == "false" for row in rows)


def test_ps_q18ab_blocks_bad_supplied_gate_packet() -> None:
    packet = build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet(
        supplied_q18aa_mount_preflight_gate_packet={"ok": False, "mount_preflight_gate_row_count": 0}
    )
    assert packet["ok"] is False
    assert "q18aa_mount_preflight_gate_not_ok" in packet["safe_display_mount_panel_failures"]
    assert packet["safe_display_mount_panel_row_count"] == 0
    assert packet["real_prediction_widget_rendering_allowed"] is False
    assert packet["actual_source_read_invoked"] is False


def main() -> int:
    test_ps_q18ab_safe_display_mount_packet_is_read_only_panel_mount_only()
    test_ps_q18ab_blocks_bad_supplied_gate_packet()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
