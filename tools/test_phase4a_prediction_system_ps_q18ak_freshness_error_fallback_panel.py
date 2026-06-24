# path: ./tools/test_phase4a_prediction_system_ps_q18ak_freshness_error_fallback_panel.py
# desc: Unit tests for PS-Q18AK freshness/error fallback panel.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (  # noqa: E402
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet,
)


def _assert_safe_boundaries(packet: dict) -> None:
    for key in FALSE_BOUNDARIES:
        assert packet[key] is False, key
    for key in ("real_prediction_widget_render_invoked", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "parameter_apply_allowed", "ledger_append_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
        assert packet[key] is False, key


def test_ps_q18ak_reports_fresh_source_when_timestamp_is_recent() -> None:
    packet = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        now_utc="2026-06-22T13:35:00Z",
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    assert packet["ok"] is True
    assert packet["freshness_state"] == "fresh"
    assert packet["source_age_sec"] == 22
    assert packet["safe_fallback_reason_codes"] == ["source_freshness_ok"]
    assert packet["auto_refresh_enabled"] is True
    assert packet["fragment_slot_refresh_path_enabled"] is True
    assert packet["freshness_monitor_enabled"] is True
    assert packet["error_fallback_visible"] is True
    _assert_safe_boundaries(packet)


def test_ps_q18ak_reports_stale_source_without_enabling_execution() -> None:
    packet = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        now_utc="2026-06-24T13:15:00Z",
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    assert packet["ok"] is True
    assert packet["freshness_state"] == "stale"
    assert packet["source_age_sec"] > 3600
    assert "source_generated_at_stale" in packet["safe_fallback_reason_codes"]
    assert packet["stale_source_warning_visible"] is True
    assert packet["auto_refresh_enabled"] is True
    assert packet["broad_page_reload_disabled"] is True
    _assert_safe_boundaries(packet)


def test_ps_q18ak_blocks_when_auto_refresh_source_is_unavailable() -> None:
    supplied = {"ok": False, "auto_refresh_enabled": False, "component_source_generated_at": ""}
    packet = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        supplied_q18aj_bounded_auto_refresh_packet=supplied,
        now_utc="2026-06-24T13:15:00Z",
    )
    assert packet["ok"] is False
    assert packet["freshness_state"] == "unknown"
    assert "auto_refresh_source_packet_not_ok" in packet["safe_fallback_reason_codes"]
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
