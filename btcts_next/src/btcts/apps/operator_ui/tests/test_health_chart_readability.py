# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_chart_readability.py
# desc: Verifies Health chart readability styling and spacing.

from __future__ import annotations

from pathlib import Path


TARGET = Path(__file__).resolve().parents[1] / "components" / "health_chart_panels.py"


def _source() -> str:
    return TARGET.read_text(encoding="utf-8-sig")


def test_api_chart_is_taller() -> None:
    text = _source()
    assert 'st.line_chart(api_chart_df, height=190, width="stretch")' in text
    assert 'st.line_chart(api_chart_df, height=160, width="stretch")' not in text


def test_ws_explanation_is_collapsed_into_single_expander() -> None:
    text = _source()
    ws_start = text.index("def render_ws_chart_panel(")
    ws_end = text.index("def _distribution_dict_text", ws_start)
    ws_block = text[ws_start:ws_end]

    assert 'with st.expander("説明" if lang == "ja" else "Details", expanded=False):' in ws_block
    assert 'st.caption(get_text(lang, "health_chart_ws_caption"))' in ws_block
    assert 'st.caption(get_text(lang, "health_chart_unfinished_bucket_caption"))' in ws_block


def test_health_chart_svg_text_is_darker() -> None:
    text = _source()
    assert '[data-testid="stVegaLiteChart"] svg text' in text
    assert 'fill: rgba(31, 41, 55, 0.96) !important;' in text
    assert text.count("_inject_health_chart_readability_styles(st)") >= 2

def test_health_chart_stack_spacing_is_compacted_locally() -> None:
    text = _source()
    assert '[class*="st-key-health"][class*="api_chart_panel"]' in text
    assert '[class*="st-key-health"][class*="ws_chart_panel"]' in text
    assert '[class*="st-key-health"][class*="layer3_chart_panel"]' in text
    assert 'margin-bottom: -0.45rem !important;' in text
    assert 'margin-top: -0.45rem !important;' in text
