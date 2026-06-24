# path: ./tools/test_phase4a_prediction_system_ps_q18al_intermediate_goal_close.py
# desc: Unit tests for PS-Q18AL intermediate-goal close packet facts.

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


def test_ps_q18al_intermediate_goal_is_reached_and_execution_boundaries_stay_closed() -> None:
    q18aj = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    q18ak = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        now_utc="2026-06-24T13:20:00Z",
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    assert q18aj["ok"] is True
    assert q18aj["auto_refresh_enabled"] is True
    assert q18aj["fragment_slot_refresh_path_enabled"] is True
    assert q18aj["partial_update_enabled"] is True
    assert q18aj["broad_page_reload_disabled"] is True
    assert q18ak["ok"] is True
    assert q18ak["auto_refresh_enabled"] is True
    assert q18ak["freshness_monitor_enabled"] is True
    assert q18ak["error_fallback_visible"] is True
    assert q18ak["freshness_state"] == "stale"
    assert "source_generated_at_stale" in q18ak["safe_fallback_reason_codes"]
    for packet in (q18aj, q18ak):
        assert packet["real_prediction_widget_render_invoked"] is False
        assert packet["streamlit_real_widget_render_invoked"] is False
        assert packet["runtime_artifact_write_allowed"] is False
        assert packet["status_artifact_write_allowed"] is False
        assert packet["parameter_apply_allowed"] is False
        assert packet["ledger_append_allowed"] is False
        assert packet["autotrade_trigger_allowed"] is False
        assert packet["broker_private_api_allowed"] is False
