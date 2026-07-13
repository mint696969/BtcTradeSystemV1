# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_api_explainer.py
# desc: Verifies API health explainer content and collapsed presentation.

from __future__ import annotations

from pathlib import Path

TARGET = Path(__file__).resolve().parents[5] / "src/btcts/apps/operator_ui/components/health_chart_panels.py"


def test_api_chart_explanation_is_collapsed_into_one_line_expander() -> None:
    text = TARGET.read_text(encoding="utf-8-sig")

    marker = 'with st.expander("説明" if lang == "ja" else "Details", expanded=False):'
    assert marker in text

    expander_pos = text.index(marker)
    api_caption_pos = text.index('st.caption(get_text(lang, "health_chart_api_caption"))')
    unfinished_pos = text.index('st.caption(get_text(lang, "health_chart_unfinished_bucket_caption"))')

    assert expander_pos < api_caption_pos < unfinished_pos
    assert 'st.line_chart(api_chart_df, height=190, width="stretch")' in text


def test_api_and_ws_chart_explanations_use_collapsed_expanders() -> None:
    text = TARGET.read_text(encoding="utf-8-sig")

    marker = 'with st.expander("説明" if lang == "ja" else "Details", expanded=False):'
    assert text.count(marker) == 2

    api_start = text.index("def render_api_chart_panel(")
    ws_start = text.index("def render_ws_chart_panel(")
    layer3_start = text.index("def render_layer3_chart_panel(")

    api_block = text[api_start:ws_start]
    ws_block = text[ws_start:layer3_start]
    layer3_block = text[layer3_start:]

    assert marker in api_block
    assert marker in ws_block
    assert marker not in layer3_block
    assert 'st.caption(get_text(lang, "health_chart_ws_caption"))' in ws_block
    assert 'st.caption(get_text(lang, "health_chart_layer3_caption"))' in layer3_block
