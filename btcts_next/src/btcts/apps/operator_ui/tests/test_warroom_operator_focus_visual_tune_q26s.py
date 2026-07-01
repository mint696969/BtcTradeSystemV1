# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_operator_focus_visual_tune_q26s.py
# desc: PS-Q26S tests for WarRoom operator focus visual tune. Visual-only; no runtime writes or execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import (  # noqa: E402
    WARROOM_OPERATOR_FOCUS_VISUAL_TUNE_VERSION,
    build_warroom_operator_focus_nav_packet,
    warroom_operator_focus_route_rows,
    warroom_operator_focus_visual_route_text,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q26s_visual_route_strip_is_short_and_operator_first() -> None:
    route_rows = warroom_operator_focus_route_rows()
    assert len(route_rows) == 4
    assert [row["順"] for row in route_rows] == ["①", "②", "③", "④⑤"]
    assert route_rows[0]["見る"] == "現在状態"
    assert route_rows[1]["見る"] == "予測表示"
    assert route_rows[3]["初期"] == "必要時だけ開く"
    text = warroom_operator_focus_visual_route_text()
    assert "① 現在状態" in text
    assert "② 予測表示" in text
    assert "④⑤ 理由確認" in text


def test_q26s_packet_marks_visual_only_and_does_not_touch_page() -> None:
    packet = build_warroom_operator_focus_nav_packet()
    assert packet["focus_visual_tune_version"] == WARROOM_OPERATOR_FOCUS_VISUAL_TUNE_VERSION
    assert packet["visual_route_strip_visible"] is True
    assert packet["route_row_count"] == 4
    assert packet["improves_first_screen_scanability"] is True
    assert packet["visual_only_change"] is True
    assert packet["warroom_page_changed"] is False
    assert packet["layout_only_change"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False

    panel_text = PANEL.read_text(encoding="utf-8-sig")
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "warroom_operator_focus_route_rows" in panel_text
    assert "visual_route_strip_visible" in panel_text
    assert "WARROOM_OPERATOR_FOCUS_VISUAL_TUNE_VERSION" in panel_text
    assert "WARROOM_OPERATOR_FOCUS_VISUAL_TUNE_VERSION" not in page_text
