# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_api_compact_metrics.py
# desc: Verifies compact API health metrics layout and ordering.

from __future__ import annotations

from pathlib import Path

TARGET = Path(__file__).resolve().parents[5] / "src/btcts/apps/operator_ui/components/health_chart_panels.py"


def _api_slice() -> str:
    text = TARGET.read_text(encoding="utf-8-sig")
    start = text.index("def render_api_chart_panel(")
    end = text.index("\ndef render_ws_chart_panel(", start)
    return text[start:end]


def test_short_api_metrics_are_compact_and_ordered_in_one_row() -> None:
    text = _api_slice()

    assert "a1, a2, a3, a4, a5, a6 = st.columns(6)" in text
    req_1m = text.index('get_text(lang, "health_metric_req_1m")')
    req_5m = text.index('get_text(lang, "health_metric_req_5m")')
    target = text.index('get_text(lang, "health_metric_target_ratio")')
    hard_cap = text.index('get_text(lang, "health_metric_hard_cap_ratio")')
    public_rest = text.index('get_text(lang, "health_metric_public_rest_1m")')
    private_rest = text.index('get_text(lang, "health_metric_private_rest_1m")')

    assert req_1m < req_5m < target < hard_cap < public_rest < private_rest


def test_duplicate_budget_overlay_row_is_not_rendered_in_api_panel() -> None:
    text = _api_slice()

    assert "o1.metric(" not in text
    assert "o2.metric(" not in text
    assert "o3.metric(" not in text
    assert "o4.metric(" not in text
    assert 'st.line_chart(api_chart_df, height=190, width="stretch")' in text
    assert "latest_overlay = dict(rate_overlay[-1]) if rate_overlay else {}" in text
