# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_operator_focus_nav_q26n.py
# desc: PS-Q26N tests for WarRoom operator-first focus navigation. Layout-only; no runtime writes or execution.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import (  # noqa: E402
    WARROOM_OPERATOR_FOCUS_NAV_VERSION,
    build_warroom_operator_focus_nav_packet,
    warroom_operator_focus_nav_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py"


def test_q26n_focus_nav_rows_are_operator_first_and_safe() -> None:
    rows = warroom_operator_focus_nav_rows()
    assert len(rows) == 5
    assert rows[0]["見る場所"] == "現在状態 nowcast / board・freshness"
    assert rows[1]["見る場所"] == "リアルタイム予測表示 / read model"
    joined = json.dumps(rows, ensure_ascii=False)
    assert "まず" in joined or "優先" in joined
    assert "generated_at" in joined
    assert "最初に見る場所" not in joined  # section label belongs to render body, not row data

    packet = build_warroom_operator_focus_nav_packet()
    assert packet["focus_nav_version"] == WARROOM_OPERATOR_FOCUS_NAV_VERSION
    assert packet["operator_first_navigation_visible"] is True
    assert packet["top_expanded_default"] is True
    assert packet["reduces_first_screen_ambiguity"] is True
    assert packet["keeps_existing_panels_available"] is True
    assert packet["layout_only_change"] is True
    assert packet["externalized_panel_module"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False


def test_q26n_render_body_places_focus_nav_before_guide_with_external_panel() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert "from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import" in page_text
    assert "render_warroom_operator_focus_nav" in page_text
    assert "def warroom_operator_focus_nav_rows()" not in page_text
    assert "def build_warroom_operator_focus_nav_packet()" not in page_text
    assert "def render_warroom_operator_focus_nav()" in panel_text
    header_index = page_text.index('live_shell.render_compact_page_header(get_text(lang, "warroom_title"))')
    literal_nav = 'live_shell.render_folded_section("最初に見る場所 / WarRoom 入口", expanded=True)'
    policy_nav = 'live_shell.render_folded_section(warroom_focus_section_label("operator_focus_nav"), expanded=warroom_focus_section_expanded("operator_focus_nav"))'
    renderer_nav = 'render_warroom_focus_section("operator_focus_nav")'
    assert literal_nav in page_text or policy_nav in page_text or renderer_nav in page_text
    nav_index = page_text.index(renderer_nav if renderer_nav in page_text else (policy_nav if policy_nav in page_text else literal_nav))
    guide_index = page_text.index('live_shell.render_folded_section(get_text(lang, "ui_label_guide"), expanded=False)')
    assert header_index < nav_index < guide_index
