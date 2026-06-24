# path: ./tools/test_phase4a_prediction_system_ps_q18ap_ui_visibility_polish.py
# desc: Unit tests for PS-Q18AP UI visibility polish.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (  # noqa: E402
    FALSE_BOUNDARIES as Q18AJ_FALSE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
    latest_prediction_summary_widget_q18aj_searchable_plain_text,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (  # noqa: E402
    FALSE_BOUNDARIES as Q18AK_FALSE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet,
    latest_prediction_summary_widget_q18ak_searchable_plain_text,
)


def test_ps_q18ap_q18aj_searchable_refresh_heartbeat_tokens_are_visible() -> None:
    packet = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet()
    text = latest_prediction_summary_widget_q18aj_searchable_plain_text(packet)
    assert "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT" in text
    assert "auto_refresh_enabled=true" in text
    assert "refresh_mode=poll_normal" in text
    assert "refresh_interval_sec=5" in text
    assert "refresh_heartbeat_utc=" in text
    assert "broad_page_reload=false" in text
    assert "real_widget_render=false" in text
    assert "autotrade=false" in text
    assert "broker=false" in text
    for key in Q18AJ_FALSE_BOUNDARIES:
        assert packet[key] is False, key


def test_ps_q18ap_q18ak_searchable_freshness_tokens_are_visible() -> None:
    packet = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        now_utc="2026-06-24T04:57:45Z",
        fragment_supported=True,
        ui_auto_refresh=True,
    )
    text = latest_prediction_summary_widget_q18ak_searchable_plain_text(packet)
    assert "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS" in text
    assert "freshness_state=stale" in text
    assert "safe_fallback_reason_codes=source_generated_at_stale" in text
    assert "observed_now_utc=2026-06-24T04:57:45Z" in text
    assert "source_age_sec=" in text
    assert "auto_refresh_enabled=true" in text
    assert "broad_page_reload=false" in text
    assert "autotrade=false" in text
    assert "broker=false" in text
    for key in Q18AK_FALSE_BOUNDARIES:
        assert packet[key] is False, key
