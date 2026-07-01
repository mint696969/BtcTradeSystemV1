# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_secondary_detail_folding_q26p.py
# desc: PS-Q26P tests for WarRoom secondary detail folding via externalized layout policy. Layout-only; no runtime writes or execution.

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

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q26p_secondary_detail_policy_folds_priority_4_and_5_sections() -> None:
    assert warroom_focus_section_expanded("operator_focus_nav") is True
    assert warroom_focus_section_expanded("live_nowcast") is True
    assert warroom_focus_section_expanded("latest_prediction_read_model") is True
    assert warroom_focus_section_expanded("header_alert_operator") is True
    assert warroom_focus_section_expanded("prediction_quick_status_detail") is False
    assert warroom_focus_section_expanded("market_evidence_detail") is False
    assert warroom_focus_section_expanded("operator_support_detail") is False
    assert warroom_focus_section_label("market_evidence_detail") == "市場証拠 / graph / active event"
    assert warroom_focus_section_label("operator_support_detail") == "operator support / timeline / evidence"

    packet = build_warroom_focus_layout_policy_packet()
    assert packet["secondary_detail_sections_folded_default"] is True
    assert packet["market_evidence_detail_folded_default"] is True
    assert packet["operator_support_detail_folded_default"] is True
    assert packet["header_alert_operator_expanded_default"] is True
    assert packet["keeps_existing_panels_available"] is True
    assert packet["layout_only_change"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False


def test_q26p_warroom_page_wraps_secondary_details_in_policy_sections() -> None:
    text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert 'warroom_focus_section_expanded("header_alert_operator")' in text
    assert 'warroom_focus_section_expanded("market_evidence_detail")' in text
    assert 'warroom_focus_section_expanded("operator_support_detail")' in text
    assert 'warroom_focus_section_label("market_evidence_detail")' in text
    assert 'warroom_focus_section_label("operator_support_detail")' in text
    assert text.index('warroom_focus_section_expanded("latest_prediction_read_model")') < text.index('warroom_focus_section_expanded("header_alert_operator")') < text.index('warroom_focus_section_expanded("market_evidence_detail")') < text.index('warroom_focus_section_expanded("operator_support_detail")')
