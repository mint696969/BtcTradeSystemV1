# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/constants.py
# desc: Constants for WarRoom v2 interactive chart. No Streamlit, IO, broker, or prediction behavior.

from __future__ import annotations

INTERACTIVE_CHART_COMPONENT_VERSION = "warroom_v2_interactive_chart.2026_07_07.v7_engine_polling"
LIGHTWEIGHT_CHARTS_CDN = "https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"


def recommended_visible_candle_count(mode: str) -> int:
    if mode == "日足":
        return 60
    if mode == "1時間足":
        return 96
    if mode == "1分足":
        return 120
    return 90


def timeframe_key(mode: str) -> str:
    return {"Live": "live", "1分足": "1m", "1時間足": "1h", "日足": "1d"}.get(str(mode), "live")
