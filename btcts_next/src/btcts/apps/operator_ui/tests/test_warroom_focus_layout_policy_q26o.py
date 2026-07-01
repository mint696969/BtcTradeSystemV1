# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_focus_layout_policy_q26o.py
# desc: PS-Q26O tests for externalized WarRoom focus layout policy. Layout-only; no runtime writes or execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_layout_policy import (  # noqa: E402
    WARROOM_FOCUS_LAYOUT_POLICY_VERSION,
    build_warroom_focus_layout_policy_packet,
    warroom_focus_section_expanded,
    warroom_focus_section_label,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q26o_focus_layout_policy_folds_quick_status_detail_only() -> None:
    assert warroom_focus_section_label("operator_focus_nav") == "最初に見る場所 / WarRoom 入口"
    assert warroom_focus_section_label("prediction_quick_status_detail") == "予測最新ステータス / quick status"
    assert warroom_focus_section_expanded("operator_focus_nav") is True
    assert warroom_focus_section_expanded("prediction_quick_status_detail") is False
    assert warroom_focus_section_expanded("live_nowcast") is True
    assert warroom_focus_section_expanded("latest_prediction_read_model") is True

    packet = build_warroom_focus_layout_policy_packet()
    assert packet["focus_layout_policy_version"] == WARROOM_FOCUS_LAYOUT_POLICY_VERSION
    assert packet["externalized_layout_policy_module"] is True
    assert packet["warroom_page_change_boundary"] == "import_and_policy_lookup_only"
    assert packet["quick_status_detail_folded_default"] is True
    assert packet["keeps_existing_panels_available"] is True
    assert packet["layout_only_change"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False


def test_q26o_warroom_page_uses_external_policy_for_top_focus_sections() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_layout_policy import" in text
    assert "warroom_focus_section_label" in text
    assert "warroom_focus_section_expanded" in text
    assert 'render_folded_section("予測最新ステータス / quick status", expanded=True)' not in text
    assert 'warroom_focus_section_expanded("prediction_quick_status_detail")' in text
    assert 'warroom_focus_section_expanded("live_nowcast")' in text
    assert 'warroom_focus_section_expanded("latest_prediction_read_model")' in text
