# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/renderer.py
# desc: Streamlit renderer adapter for WarRoom interactive chart. Render-only with safe fallback result.

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from .candle_records import build_interactive_candle_records
from .constants import INTERACTIVE_CHART_COMPONENT_VERSION, recommended_visible_candle_count
from .html_builder import build_interactive_chart_html, component_height


def render_interactive_candle_chart(
    candle_frame: pd.DataFrame,
    *,
    mode: str,
    chart_context: Mapping[str, Any] | None,
    st_api: Any,
) -> dict[str, Any]:
    candles = build_interactive_candle_records(candle_frame)
    if not candles:
        return {"ok": False, "interactive_chart_rendered": False, "reason": "no_candles", "read_only": True}
    try:
        from streamlit.components.v1 import html as st_html

        html_doc = build_interactive_chart_html(
            candles=candles,
            mode=mode,
            chart_context=chart_context,
            visible_candle_count=recommended_visible_candle_count(mode),
        )
        st_html(html_doc, height=component_height(len(candles)), scrolling=False)
        return {
            "ok": True,
            "interactive_chart_rendered": True,
            "interactive_chart_component_version": INTERACTIVE_CHART_COMPONENT_VERSION,
            "interactive_chart_library": "tradingview_lightweight_charts_standalone",
            "selection_copy_ready": True,
            "clipboard_fallback_preview_ready": True,
            "overlay_layers_ready": True,
            "prediction_overlay_layers_ready": True,
            "single_candle_selection_ready": True,
            "range_selection_ready": True,
            "visible_candle_count": recommended_visible_candle_count(mode),
            "future_blank_space_ready": True,
            "read_only": True,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        }
    except Exception as exc:  # noqa: BLE001
        if hasattr(st_api, "caption"):
            st_api.caption(f"interactive chart fallback: {exc!r}")
        return {"ok": False, "interactive_chart_rendered": False, "reason": repr(exc), "read_only": True}
