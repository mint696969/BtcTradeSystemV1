# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_prediction_widgets_always_visible.py
# desc: Structural guard that existing WarRoom scenario guidance and prediction cards are always-visible compact sections.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
CARDS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py"
GUIDANCE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/inference_guidance_view.py"


def test_prediction_widgets_are_restored_as_always_visible_sections() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")

    assert 'render_compact_section_label(st, index=3, title="Inference scenario guidance", note="予測シナリオ: 観測ベース / 読み取り専用 / prediction実行なし")' in page
    assert 'render_compact_section_label(st, index=4, title="Prediction cards", note="予測カード: context-only / 読み取り専用 / broker操作なし")' in page
    assert 'with st.expander("3. Inference scenario guidance' not in page
    assert 'with st.expander("4. Prediction cards' not in page

    guidance_label_pos = page.index('render_compact_section_label(st, index=3')
    guidance_render_pos = page.index('render_inference_guidance(snapshot["guidance_packet"], st)', guidance_label_pos)
    cards_label_pos = page.index('render_compact_section_label(st, index=4')
    cards_render_pos = page.index('render_rt_prediction_cards(snapshot["display_packets"]["cards"], st)', cards_label_pos)
    chart_pos = page.index('render_compact_section_label(st, index=5')
    assert guidance_label_pos < guidance_render_pos < cards_label_pos < cards_render_pos < chart_pos


def test_prediction_card_renderer_reuses_original_market_regime_shell_and_safe_boundary() -> None:
    cards = CARDS.read_text(encoding="utf-8-sig")
    guidance = GUIDANCE.read_text(encoding="utf-8-sig")

    assert "def render_rt_prediction_cards" in cards
    assert "render_warroom_market_regime_card_shell" in cards
    assert "WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION" in cards
    assert "RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT" in cards
    assert "FUTURE_PREDICTION_CARD_ROWS" in cards
    assert "prediction_cards_scope=market_regime_first" in cards
    assert "original_warroom_market_regime_shell=true" in cards
    assert "prediction_invoked=false" in cards
    assert "classifier_invoked=false" in cards
    assert "broker_action_allowed=false" in cards
    assert "st_api.columns(len(cards))" not in cards
    assert 'column.metric("state"' not in cards

    assert "def render_inference_guidance" in guidance
    assert "observational_scenario_only" in guidance
    assert "prediction_invoked" in guidance
    assert "broker_send_enabled" in guidance
