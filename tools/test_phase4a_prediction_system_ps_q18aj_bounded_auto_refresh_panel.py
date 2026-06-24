# path: ./tools/test_phase4a_prediction_system_ps_q18aj_bounded_auto_refresh_panel.py
# desc: Unit tests for PS-Q18AJ bounded WarRoom auto-refresh panel.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (  # noqa: E402
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
)


def _assert_boundaries(packet: dict) -> None:
    for key in TRUE_BOUNDARIES:
        assert packet[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18aj_enables_bounded_fragment_auto_refresh_without_trading_or_writes() -> None:
    packet = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    assert packet["ok"] is True
    assert packet["auto_refresh_enabled"] is True
    assert packet["fragment_refresh_enabled"] is True
    assert packet["fragment_slot_refresh_path_enabled"] is True
    assert packet["partial_update_enabled"] is True
    assert packet["broad_page_reload_disabled"] is True
    assert packet["refresh_mode"] == "poll_normal"
    assert packet["refresh_interval_sec"] == 5
    assert packet["display_row_count"] == 12
    assert packet["warroom_display_mounted"] is True
    assert packet["real_prediction_widget_render_invoked"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["status_artifact_write_allowed"] is False
    assert packet["parameter_apply_allowed"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    _assert_boundaries(packet)


def test_ps_q18aj_blocks_auto_refresh_when_fragment_is_not_supported() -> None:
    packet = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(
        fragment_supported=False,
        ui_auto_refresh=True,
    )
    assert packet["ok"] is False
    assert packet["auto_refresh_enabled"] is False
    assert packet["fragment_refresh_enabled"] is False
    assert packet["partial_update_enabled"] is False
    assert packet["broad_page_reload_disabled"] is True
    assert packet["real_prediction_widget_render_invoked"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
