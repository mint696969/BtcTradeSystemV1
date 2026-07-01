# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_focus_section_renderer_q26q.py
# desc: PS-Q26Q tests for WarRoom focus section renderer wrapper. Layout-only; no runtime writes or execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_sections import (  # noqa: E402
    WARROOM_FOCUS_SECTION_RENDERER_VERSION,
    build_warroom_focus_section_renderer_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
SECTION_RENDERER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_sections.py"


def test_q26q_focus_section_renderer_packet_is_safe_and_policy_backed() -> None:
    packet = build_warroom_focus_section_renderer_packet()
    assert packet["focus_section_renderer_version"] == WARROOM_FOCUS_SECTION_RENDERER_VERSION
    assert packet["uses_externalized_layout_policy_module"] is True
    assert packet["section_renderer_externalized"] is True
    assert packet["warroom_page_change_boundary"] == "import_and_focus_section_renderer_calls_only"
    assert packet["section_count"] == 8
    assert packet["operator_focus_nav_expanded_default"] is True
    assert packet["market_regime_card_sample_expanded_default"] is True
    assert packet["quick_status_detail_folded_default"] is True
    assert packet["market_evidence_detail_folded_default"] is True
    assert packet["operator_support_detail_folded_default"] is True
    assert packet["keeps_existing_panels_available"] is True
    assert packet["layout_only_change"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False


def test_q26q_warroom_page_uses_focus_section_renderer_not_direct_policy_lookup() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    renderer_text = SECTION_RENDERER.read_text(encoding="utf-8-sig")
    assert "from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_sections import" in page_text
    assert "render_warroom_focus_section" in page_text
    assert "warroom_focus_section_expanded" not in page_text
    assert "warroom_focus_section_label" not in page_text
    for section_id in (
        "operator_focus_nav",
        "market_regime_card_sample",
        "prediction_quick_status_detail",
        "live_nowcast",
        "latest_prediction_read_model",
        "header_alert_operator",
        "market_evidence_detail",
        "operator_support_detail",
    ):
        assert f'render_warroom_focus_section("{section_id}")' in page_text
    assert "live_shell.render_folded_section" in renderer_text
    assert "warroom_focus_section_label" in renderer_text
    assert "warroom_focus_section_expanded" in renderer_text
