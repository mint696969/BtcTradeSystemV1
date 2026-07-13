# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_graph_first_layout.py
# desc: Verifies graph-first ordering of Health page sections.

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HEALTH_PAGE = ROOT / "src/btcts/apps/operator_ui/views/health_page.py"
CHART_PANELS = ROOT / "src/btcts/apps/operator_ui/components/health_chart_panels.py"
TOP_PANELS = ROOT / "src/btcts/apps/operator_ui/components/health_top_panels.py"


def test_health_primary_visualizations_are_grouped_before_detail_panels() -> None:
    text = HEALTH_PAGE.read_text(encoding="utf-8-sig")

    api_pos = text.index('health_widget_slot("api_chart_panel")')
    ws_pos = text.index('health_widget_slot("ws_chart_panel")')
    layer3_pos = text.index('health_widget_slot("layer3_chart_panel")')
    continuity_pos = text.index('render_body=_render_continuity_section')
    safety_pos = text.index('health_widget_slot("hot_cold_retention_safety_panel")')
    evidence_pos = text.index('health_widget_slot("evidence_presentation_panel")')
    source_pos = text.index('health_widget_slot("dashboard_hub_source_panel")')
    current_pos = text.index('health_widget_slot("current_state_section")')

    assert api_pos < ws_pos < continuity_pos < layer3_pos
    assert layer3_pos < safety_pos < evidence_pos < source_pos < current_pos


def test_health_graphs_and_summary_cards_use_compact_heights() -> None:
    charts = CHART_PANELS.read_text(encoding="utf-8-sig")
    top = TOP_PANELS.read_text(encoding="utf-8-sig")

    assert 'st.line_chart(api_chart_df, height=190, width="stretch")' in charts
    assert 'st.line_chart(ws_chart_df, height=180, width="stretch")' in charts
    assert "height:88px" in top
    assert "-webkit-line-clamp:2" in top
    assert "overflow:hidden" in top
