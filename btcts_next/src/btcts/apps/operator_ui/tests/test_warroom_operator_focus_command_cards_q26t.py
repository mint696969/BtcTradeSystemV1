# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_operator_focus_command_cards_q26t.py
# desc: PS-Q26T tests for WarRoom operator focus command cards. Visual-only; no runtime writes or execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import (  # noqa: E402
    WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION,
    build_warroom_operator_focus_nav_packet,
    warroom_operator_focus_card_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q26t_command_cards_are_three_primary_reading_cards() -> None:
    cards = warroom_operator_focus_card_rows()
    assert len(cards) == 3
    assert [card["順"] for card in cards] == ["①", "②", "③"]
    assert [card["card_id"] for card in cards] == ["current_state", "prediction_read", "operator_alert"]
    assert cards[0]["見出し"] == "現在状態"
    assert cards[1]["見出し"] == "予測表示"
    assert cards[2]["見出し"] == "alert / operator"
    assert "古い・注意" in cards[0]["合図"]
    assert "時刻が変わった時だけ" in cards[1]["合図"]


def test_q26t_packet_marks_command_cards_visual_only_and_page_untouched() -> None:
    packet = build_warroom_operator_focus_nav_packet()
    assert packet["focus_command_cards_version"] == WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION
    assert packet["command_cards_visible"] is True
    assert packet["card_row_count"] == 3
    assert packet["improves_first_screen_glanceability"] is True
    assert packet["visual_route_strip_visible"] is True
    assert packet["visual_only_change"] is True
    assert packet["warroom_page_changed"] is False
    assert packet["warroom_page_slimming_main_goal"] is False
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False

    panel_text = PANEL.read_text(encoding="utf-8-sig")
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "warroom_operator_focus_card_rows" in panel_text
    assert "command_cards_visible" in panel_text
    assert "WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION" in panel_text
    assert "st.columns" in panel_text
    assert "WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_VERSION" not in page_text
