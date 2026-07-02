# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_horizon_matrix_contract_q29f.py
# desc: PS-Q29F guards for WarRoom v2 item-by-horizon card matrix contract.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2 import (  # noqa: E402
    WARROOM_V2_CARD_AXIS_POLICY_VERSION,
    WARROOM_V2_HORIZON_LABELS,
    build_warroom_v2_card_axis_policy,
    build_warroom_v2_placeholder_read_models_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
PREDICTION_CARDS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/prediction_cards.py"
DETAIL_OVERLAY = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/card_detail_overlay_html.py"
PLACEHOLDERS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/placeholder_read_models.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29F_WARROOM_V2_HORIZON_MATRIX_CONTRACT_2026-07-02.md"

EXPECTED_HORIZONS = ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]


def test_q29f_axis_policy_matches_q26w_q27e_card_specs() -> None:
    packet = build_warroom_v2_card_axis_policy()
    assert packet["card_axis_policy_version"] == WARROOM_V2_CARD_AXIS_POLICY_VERSION
    assert list(WARROOM_V2_HORIZON_LABELS) == EXPECTED_HORIZONS
    assert packet["layout_shape"] == "item_rows_by_horizon_columns"
    assert packet["row_axis"] == "prediction_item"
    assert packet["column_axis"] == "horizon"
    assert packet["card_row_layout"] == "horizontal_time_axis_cards"
    assert packet["card_shape"] == "horizontal_rectangle"
    assert packet["cards_do_not_shrink"] is True
    assert packet["horizontal_scroll_required"] is True
    assert packet["card_body_three_lines"] is True
    assert packet["freshness_badge"] == "top_right_badge_only"
    assert packet["border_meaning"] == "evidence_quality"
    assert packet["detail_disclosure_mode"] in {"card_overlay", "row_level_overlay_panel"}


def test_q29f_prediction_read_models_have_horizon_cards_per_item_row() -> None:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T06:00:00Z")
    cards = [model for model in packet["read_models"] if model["payload"].get("zone") == "prediction_cards"]
    assert len(cards) >= 8
    for model in cards:
        payload = model["payload"]
        assert payload["row_axis"] == "prediction_item"
        assert payload["column_axis"] == "horizon"
        assert payload["horizon_labels"] == EXPECTED_HORIZONS
        assert payload["horizon_card_count"] == 8
        assert payload["card_row_layout"] == "horizontal_time_axis_cards"
        assert payload["cards_do_not_shrink"] is True
        assert payload["horizontal_scroll_required"] is True
        assert payload["card_shape"] == "horizontal_rectangle"
        assert [card["horizon"] for card in payload["horizon_cards"]] == EXPECTED_HORIZONS
        assert all(len(card["card_body_lines"]) == 3 for card in payload["horizon_cards"])
        assert all(card["runtime_connected"] is False for card in payload["horizon_cards"])
        assert all(card["push_connected"] is False for card in payload["horizon_cards"])


def test_q29f_prediction_renderer_uses_item_rows_and_horizon_columns() -> None:
    text = PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert "horizon_cards" in text
    # Q29G may render the Q29F matrix contract through HTML/CSS instead of
    # Streamlit columns. Q29F's durable guard is item rows by horizon columns.
    assert "warroom_v2_prediction_matrix_html" in text
    assert "wv2-strip" in text
    assert "wv2-card" in text
    overlay_text = DETAIL_OVERLAY.read_text(encoding="utf-8-sig")
    assert "warroom_v2_detail_button_html" in text
    assert "warroom_v2_detail_overlay_panel_html" in text
    assert "build_warroom_v2_card_detail_balloon_packet" in overlay_text
    assert "st.columns(max(1, len(horizon_cards)))" not in text


def test_q29f_no_route_legacy_or_runtime_ownership_changed() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    placeholder_text = PLACEHOLDERS.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", "WarRoom v2", warroom_v2_page)' in app_text
    assert "card_axis_policy" not in legacy_text
    assert "prediction_warroom.v2" not in legacy_text
    for token in (
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
    ):
        assert token not in placeholder_text


def test_q29f_doc_records_horizon_matrix_contract() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "horizontal axis = horizons" in text
    assert "vertical axis = prediction items" in text
    assert "card_shape=horizontal_rectangle" in text
    assert "card_body_three_lines=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_changing_legacy_warroom=true" in text
