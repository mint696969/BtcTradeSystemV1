# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_placeholder_ui_signoff_q29o.py
# desc: PS-Q29O signoff guards for WarRoom v2 placeholder UI polish through Q29N.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2 import warroom_v2_models_by_zone  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.card_detail_overlay_html import (  # noqa: E402
    build_warroom_v2_detail_overlay_renderer_packet,
    warroom_v2_detail_overlay_html,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.debug_preview import build_warroom_v2_debug_preview_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.prediction_cards import (  # noqa: E402
    build_warroom_v2_prediction_matrix_renderer_packet,
    warroom_v2_prediction_matrix_html,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.top_bar import build_warroom_v2_top_bar_renderer_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2_shell_preview_panel import build_warroom_v2_shell_preview_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29O_WARROOM_V2_PLACEHOLDER_UI_SIGNOFF_2026-07-02.md"


def _packet_shell() -> tuple[dict, dict]:
    packet = build_warroom_v2_shell_preview_panel_packet()
    return packet, packet["shell_preview"]


def test_q29o_warroom_v2_placeholder_ui_contract_is_signoff_ready() -> None:
    packet, shell = _packet_shell()
    top = build_warroom_v2_top_bar_renderer_packet(warroom_v2_models_by_zone(shell, "top"))
    cards = build_warroom_v2_prediction_matrix_renderer_packet(warroom_v2_models_by_zone(shell, "prediction_cards"))
    debug = build_warroom_v2_debug_preview_packet(packet, shell)
    assert top["top_bar_placeholder_status_polish"] is True
    assert cards["streamlit_components_html_used"] is True
    assert cards["markdown_unsafe_html_used"] is False
    assert cards["component_scrolling_enabled"] is False
    assert cards["row_horizontal_scroll_preserved"] is True
    assert cards["detail_disclosure_mode"] == "row_level_overlay_panel"
    assert cards["detail_overlay_close_button_required"] is True
    assert debug["compact_debug_preview"] is True
    assert debug["expanded_by_default"] is False
    for part in (packet, top, cards, debug):
        assert part["runtime_connected"] is False
        assert part["push_connected"] is False
        assert part["would_send_to_broker"] is False


def test_q29o_prediction_matrix_html_is_renderable_without_raw_html_text_regression() -> None:
    _packet, shell = _packet_shell()
    models = warroom_v2_models_by_zone(shell, "prediction_cards")
    html = warroom_v2_prediction_matrix_html(models)
    assert "<div class='wv2-card" in html
    assert "\n    <div class='wv2-card" not in html
    assert "overflow-x: auto" in html
    assert "overflow-y: hidden" in html
    assert "wv2-detail-button" in html
    assert "wv2-row-detail-panel" in html
    assert "wv2-detail-close" in html
    assert "role='dialog'" in html
    assert "Debug / raw preview packet" not in html


def test_q29o_detail_overlay_and_debug_preview_are_display_only() -> None:
    packet, shell = _packet_shell()
    first_card = warroom_v2_models_by_zone(shell, "prediction_cards")[0]
    detail = build_warroom_v2_detail_overlay_renderer_packet(first_card)
    detail_html = warroom_v2_detail_overlay_html(first_card)
    debug = build_warroom_v2_debug_preview_packet(packet, shell)
    assert detail["summary_button_label"] == "詳細"
    assert detail["close_button_required"] is True
    assert detail["aria_labels_present"] is True
    assert detail["overlay_max_height_px"] == 260
    assert "row-level overlay / display-only" in detail_html
    assert debug["model_count"] >= 12
    assert debug["zones"]["top"] == 3
    assert debug["zones"]["prediction_cards"] >= 8
    assert debug["zones"]["scenario"] == 1
    assert detail["runtime_connected"] is False
    assert debug["runtime_connected"] is False


def test_q29o_route_is_separate_and_legacy_warroom_is_not_changed_to_v2() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", get_text(lang, "page_warroom"), warroom_v2_page)' in app_text
    assert 'LEGACY_PAGE_KEY_REDIRECTS = {' in app_text
    assert '"warroom": "warroom_v2"' in app_text
    assert "prediction_warroom.v2.push_widgets" in legacy_text
    assert "ensure_warroom_push_widget_live_observation_runtime" in legacy_text
    assert "apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state" in legacy_text
    assert "warroom_v2_page" not in legacy_text
    assert "build_warroom_v2_shell_preview_packet" not in legacy_text
    assert "classify_market_regime_feature_bundle(" not in legacy_text
    assert "send_to_broker(" not in legacy_text
    assert "autotrade_trigger_allowed = True" not in legacy_text
    assert "warroom_v2_shell_preview_panel" not in legacy_text
    assert "card_detail_overlay_html" not in legacy_text
    assert "debug_preview_renderer.ps_q29n" not in legacy_text


def test_q29o_renderer_files_remain_small_and_side_effect_free() -> None:
    forbidden = (
        "D:" + "\\",
        "E:" + "\\",
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
        "websocket.",
        "sse.",
    )
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29o_doc_records_placeholder_ui_signoff_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_placeholder_ui_signoff=true" in text
    assert "visual_verify_next=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_invoking_classifier=true" in text
    assert "not_enabling_websocket=true" in text
    assert "not_touching_autotrade_broker_ledger_mode_parameter=true" in text
    assert "not_changing_legacy_warroom=true" in text
