# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_detail_overlay_click_polish_q29m.py
# desc: PS-Q29M guards for WarRoom v2 detail overlay click polish.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.card_detail_overlay_html import (  # noqa: E402
    WARROOM_V2_CARD_DETAIL_OVERLAY_HTML_VERSION,
    build_warroom_v2_detail_overlay_renderer_packet,
    warroom_v2_detail_overlay_css,
    warroom_v2_detail_overlay_html,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.prediction_cards import warroom_v2_prediction_matrix_html  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_placeholder_read_models_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
PREDICTION_CARDS = RENDERER_DIR / "prediction_cards.py"
OVERLAY = RENDERER_DIR / "card_detail_overlay_html.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29M_WARROOM_V2_DETAIL_OVERLAY_CLICK_POLISH_2026-07-02.md"


def _first_prediction_card() -> dict:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T08:20:00Z")
    for model in packet["read_models"]:
        if model["payload"].get("zone") == "prediction_cards":
            return model
    raise AssertionError("prediction card not found")


def test_q29m_detail_overlay_packet_is_click_polish_display_only() -> None:
    packet = build_warroom_v2_detail_overlay_renderer_packet(_first_prediction_card())
    assert packet["detail_overlay_html_version"] == WARROOM_V2_CARD_DETAIL_OVERLAY_HTML_VERSION
    assert packet["detail_disclosure_mode"] == "row_level_overlay_panel"
    assert packet["summary_button_label"] == "詳細"
    assert packet["aria_labels_present"] is True
    assert packet["overlay_max_height_px"] == 260
    assert packet["close_button_required"] is True
    assert packet["card_width_constrained"] is False
    assert packet["display_only"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False


def test_q29m_overlay_html_has_accessible_click_detail_markup() -> None:
    html = warroom_v2_detail_overlay_html(_first_prediction_card())
    assert "class='wv2-row-detail-panel'" in html
    assert "class='wv2-detail-close'" in html
    assert "aria-label='詳細を閉じる'" in html
    assert "role='dialog'" in html
    assert "row-level overlay / display-only" in html


def test_q29m_prediction_matrix_uses_overlay_helper_css() -> None:
    pred_text = PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert "warroom_v2_detail_button_html(toggle_id)" in pred_text
    assert "warroom_v2_detail_overlay_css()" in pred_text
    assert "build_warroom_v2_card_detail_balloon_packet" not in pred_text
    assert "wv2-detail-overlay { position: absolute" not in pred_text
    matrix_html = warroom_v2_prediction_matrix_html([_first_prediction_card()])
    assert "wv2-detail-button" in matrix_html
    assert "max-height: 260px" in matrix_html
    assert "row-level overlay / display-only" in matrix_html


def test_q29m_renderer_files_stay_small_and_side_effect_free() -> None:
    forbidden = (
        "D:" + "\\",
        "E:" + "\\",
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "write_runtime_artifact(",
        "websocket.",
        "sse.",
    )
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text


def test_q29m_no_route_or_legacy_warroom_change() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", "WarRoom v2", warroom_v2_page)' in app_text
    assert "card_detail_overlay_html" not in legacy_text
    assert "prediction_warroom.v2" not in legacy_text


def test_q29m_doc_records_detail_overlay_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "detail_disclosure_mode=card_overlay" in text or "detail_disclosure_mode=row_level_overlay_panel" in text
    assert "aria_labels_present=true" in text
    assert "prediction_cards_line_budget_preserved=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_changing_legacy_warroom=true" in text
