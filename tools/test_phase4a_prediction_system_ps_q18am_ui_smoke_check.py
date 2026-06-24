# path: ./tools/test_phase4a_prediction_system_ps_q18am_ui_smoke_check.py
# desc: Unit tests for PS-Q18AM UI smoke/manual visual check packet facts.

from __future__ import annotations

import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (  # noqa: E402
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (  # noqa: E402
    build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet,
)


def build_ps_q18am_ui_smoke_check_packet() -> dict:
    q18aj = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    q18ak = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        now_utc="2026-06-24T13:25:00Z",
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    manual_checklist = [
        "open_operator_ui",
        "open_warroom_tab",
        "confirm_latest_prediction_auto_refresh_panel_visible",
        "confirm_freshness_fallback_panel_visible",
        "confirm_poll_normal_5s_caption",
        "confirm_no_broad_page_reload_whiteout",
        "confirm_no_autotrade_broker_parameter_ledger_runtime_write",
    ]
    failures: list[str] = []
    if q18aj.get("auto_refresh_enabled") is not True:
        failures.append("auto_refresh_not_enabled")
    if q18aj.get("fragment_slot_refresh_path_enabled") is not True:
        failures.append("fragment_slot_refresh_path_not_enabled")
    if q18aj.get("broad_page_reload_disabled") is not True:
        failures.append("broad_page_reload_not_disabled")
    if q18ak.get("freshness_monitor_enabled") is not True:
        failures.append("freshness_monitor_not_enabled")
    if q18ak.get("error_fallback_visible") is not True:
        failures.append("error_fallback_not_visible")
    for packet_name, packet in (("q18aj", q18aj), ("q18ak", q18ak)):
        for key in (
            "real_prediction_widget_render_invoked",
            "streamlit_real_widget_render_invoked",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "parameter_apply_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
        ):
            if packet.get(key) is not False:
                failures.append(f"{packet_name}:{key}_not_false")
    return {
        "ok": not failures,
        "ps_q18am_ui_smoke_check_packet_version": "prediction_warroom.latest_prediction_summary_widget.q18am_ui_smoke_check.v1",
        "intermediate_goal_reached": q18aj.get("auto_refresh_enabled") is True,
        "manual_visual_check_required": True,
        "manual_checklist": manual_checklist,
        "manual_checklist_count": len(manual_checklist),
        "auto_refresh_enabled": q18aj.get("auto_refresh_enabled"),
        "fragment_slot_refresh_path_enabled": q18aj.get("fragment_slot_refresh_path_enabled"),
        "partial_update_enabled": q18aj.get("partial_update_enabled"),
        "broad_page_reload_disabled": q18aj.get("broad_page_reload_disabled"),
        "refresh_mode": q18aj.get("refresh_mode"),
        "refresh_interval_sec": q18aj.get("refresh_interval_sec"),
        "freshness_monitor_enabled": q18ak.get("freshness_monitor_enabled"),
        "error_fallback_visible": q18ak.get("error_fallback_visible"),
        "freshness_state": q18ak.get("freshness_state"),
        "safe_fallback_reason_codes": q18ak.get("safe_fallback_reason_codes"),
        "real_prediction_widget_render_invoked": False,
        "streamlit_real_widget_render_invoked": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "parameter_apply_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "failures": failures,
    }


def test_ps_q18am_ui_smoke_packet_keeps_intermediate_goal_and_safety_boundaries() -> None:
    packet = build_ps_q18am_ui_smoke_check_packet()
    assert packet["ok"] is True
    assert packet["intermediate_goal_reached"] is True
    assert packet["manual_visual_check_required"] is True
    assert packet["manual_checklist_count"] == 7
    assert packet["auto_refresh_enabled"] is True
    assert packet["fragment_slot_refresh_path_enabled"] is True
    assert packet["partial_update_enabled"] is True
    assert packet["broad_page_reload_disabled"] is True
    assert packet["refresh_mode"] == "poll_normal"
    assert packet["refresh_interval_sec"] == 5
    assert packet["freshness_monitor_enabled"] is True
    assert packet["error_fallback_visible"] is True
    assert packet["real_prediction_widget_render_invoked"] is False
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
