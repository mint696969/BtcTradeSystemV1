# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_continuity_single_legend.py
# desc: Verifies the Health continuity grid renders one shared legend.

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[5] / "src/btcts/apps/operator_ui"
CONTINUITY = ROOT / "components/health_continuity.py"
TOP_PANELS = ROOT / "components/health_top_panels.py"


def test_continuity_legend_can_be_suppressed_per_group() -> None:
    text = CONTINUITY.read_text(encoding="utf-8-sig")

    assert 'def render_continuity_legend(*, range_key: str = "1h", lang: str = "ja") -> None:' in text
    assert "show_legend: bool = True" in text
    assert "if show_legend:" in text


def test_continuity_explanation_is_rendered_once_after_all_three_rows() -> None:
    text = TOP_PANELS.read_text(encoding="utf-8-sig")

    assert text.count("show_legend=False") == 2
    legend_call = "render_continuity_legend(range_key=range_key, lang=lang)"
    assert text.count(legend_call) == 1
    assert text.count("API REST / WS Board / WS Executions") == 1
    assert 'st.caption(get_text(lang, "health_continuity_caption_api"))' not in text
    assert 'st.caption(get_text(lang, "health_continuity_caption_ws"))' not in text

    api_pos = text.index("api_continuity_rail,")
    ws_pos = text.index("ws_continuity_rail,")
    legend_pos = text.index(legend_call)
    assert api_pos < ws_pos < legend_pos
