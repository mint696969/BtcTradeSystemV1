# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_operator_focus_route_table_fold_q26v.py
# desc: PS-Q26V tests for WarRoom operator focus route table fold. Visual-only; no runtime writes or execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import (  # noqa: E402
    WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_VERSION,
    build_warroom_operator_focus_nav_packet,
    warroom_operator_focus_route_table_fold_label,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q26v_route_text_remains_visible_while_route_table_is_folded() -> None:
    packet = build_warroom_operator_focus_nav_packet()
    assert packet["focus_route_table_fold_version"] == WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_VERSION
    assert packet["visual_route_text_visible"] is True
    assert packet["visual_route_strip_visible"] is True
    assert packet["route_table_available"] is True
    assert packet["route_table_folded_default"] is True
    assert packet["route_table_label"] == warroom_operator_focus_route_table_fold_label()
    assert packet["route_row_count"] == 4
    assert packet["detail_table_folded_default"] is True
    assert packet["reduces_first_screen_table_density"] is True


def test_q26v_render_folds_route_table_and_does_not_touch_page() -> None:
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_VERSION" in panel_text
    assert "route_table_folded_default" in panel_text
    assert "with st.expander(str(packet[\"route_table_label\"]), expanded=False)" in panel_text
    assert "st.dataframe(packet[\"route_rows\"]" in panel_text
    assert "読む順の補足 / 4ステップ表" in panel_text
    assert "WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_VERSION" not in page_text

    packet = build_warroom_operator_focus_nav_packet()
    assert packet["command_cards_visible"] is True
    assert packet["warroom_page_changed"] is False
    assert packet["warroom_page_slimming_main_goal"] is False
    assert packet["visual_only_change"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False
