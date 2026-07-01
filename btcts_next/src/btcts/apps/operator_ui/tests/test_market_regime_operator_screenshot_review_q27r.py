# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_operator_screenshot_review_q27r.py
# desc: PS-Q27R guard for WarRoom market-regime operator screenshot review checklist. Documentation-only.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27R_WARROOM_OPERATOR_SCREENSHOT_REVIEW_2026-07-02.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


def test_q27r_review_doc_exists_and_is_documentation_only() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "ps_q27r_warroom_operator_screenshot_review=true" in text
    assert "production_code_changed=false" in text
    assert "production_ui_code_changed=false" in text
    assert "runtime_code_changed=false" in text
    assert "warroom_page_changed=false" in text
    assert "operator_screenshot_required=true" in text


def test_q27r_review_doc_preserves_q26w_q27e_card_invariants() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "card_row_layout=horizontal_time_axis_cards",
        "card_width_px=208",
        "cards_do_not_shrink=true",
        "card_body_three_lines=true",
        "freshness_encoded_by_badge_only=true",
        "border_meaning=evidence_quality",
        "confidence_meaning=classification_certainty_not_win_rate",
        "detail_disclosure_mode=card_overlay",
        "no_vertical_layout_shift_on_detail_open=true",
    ):
        assert marker in text


def test_q27r_review_doc_has_off_and_on_checklists() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "## OFF screenshot checklist" in text
    assert "checkbox_default_off=true" in text
    assert "no_d_hot_read=true" in text
    assert "## ON screenshot checklist" in text
    assert "operator_checkbox_on=true" in text
    assert "real_preview_cards_visible=true" in text
    assert "would_send_to_broker=false" in text


def test_q27r_review_doc_records_allowed_improvement_candidates_not_changes() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "Improvement candidates allowed after screenshot review" in text
    assert "ON時のcaption" in text
    assert "confidence line" in text
    assert "detail overlay内" in text
    assert "They must be implemented in later explicit slices" in text


def test_q27r_no_production_ui_files_changed_by_review_slice() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert "preview_enabled=True" not in page_text
    assert "warroom_market_regime_card_preview_enabled_q27p" in page_text
    assert "build_warroom_market_regime_card_preview_switch_packet" in panel_text
    for text in (page_text, panel_text):
        for token in (
            "send_to_broker(",
            "append_ledger(",
            "ledger.append(",
            "write_runtime_artifact(",
            "write_status_artifact(",
            "write_prediction_artifact(",
        ):
            assert token not in text
