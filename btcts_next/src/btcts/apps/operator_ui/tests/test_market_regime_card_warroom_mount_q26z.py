# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_warroom_mount_q26z.py
# desc: PS-Q26Z tests for sample-only market regime card WarRoom mount. No live data connection.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_layout_policy import (  # noqa: E402
    build_warroom_focus_layout_policy_packet,
    warroom_focus_section_expanded,
    warroom_focus_section_label,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_sections import (  # noqa: E402
    build_warroom_focus_section_renderer_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (  # noqa: E402
    build_warroom_market_regime_card_renderer_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q26z_focus_policy_adds_expanded_market_regime_card_section() -> None:
    assert warroom_focus_section_label("market_regime_card_sample") == "地合いカード / sample preview"
    assert warroom_focus_section_expanded("market_regime_card_sample") is True
    packet = build_warroom_focus_layout_policy_packet()
    assert packet["section_count"] == 8
    assert packet["market_regime_card_sample_expanded_default"] is True
    rows = packet["rows"]
    ids = [row["section_id"] for row in rows]
    assert ids.index("operator_focus_nav") < ids.index("market_regime_card_sample") < ids.index("prediction_quick_status_detail")


def test_q26z_focus_section_renderer_exposes_market_regime_card_policy() -> None:
    packet = build_warroom_focus_section_renderer_packet()
    assert packet["section_count"] == 8
    assert packet["market_regime_card_sample_expanded_default"] is True
    assert packet["layout_only_change"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True


def test_q26z_warroom_page_mounts_sample_only_market_regime_cards_after_entry() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "render_warroom_market_regime_card_shell" in text
    assert 'render_warroom_focus_section("market_regime_card_sample")' in text
    assert text.index('render_warroom_focus_section("operator_focus_nav")') < text.index('render_warroom_focus_section("market_regime_card_sample")') < text.index('render_warroom_focus_section("prediction_quick_status_detail")')
    assert "load_execution_market_summary_status_payload" in text  # existing live state loader unchanged


def test_q26z_renderer_packet_remains_sample_only_after_mount() -> None:
    packet = build_warroom_market_regime_card_renderer_packet()
    assert packet["sample_data_only"] is True
    assert packet["live_data_connected"] is False
    assert packet["warroom_page_changed"] is False
    assert packet["warroom_page_mounted"] is False
    assert packet["streamlit_render_function_declared"] is True
    assert packet["streamlit_render_invoked_by_page"] is False
    assert packet["card_count"] == 8
    assert packet["horizons"][-1] == "24時間後"
    assert packet["cards_do_not_shrink"] is True
    assert packet["freshness_encoded_by_badge_only"] is True
    assert packet["border_meaning"] == "evidence_quality"
    for key in ("runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False
