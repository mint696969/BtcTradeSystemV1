# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/topics.py
# desc: WarRoom v2 push-ready widget topic catalog. Contract-only; no transport implementation.

from __future__ import annotations

from typing import Any

from .safety import warroom_v2_safety_flags

WARROOM_V2_TOPIC_CATALOG_VERSION = "prediction_warroom.v2.topic_catalog.ps_q30c.v1"

WARROOM_V2_WIDGET_TOPICS: tuple[str, ...] = (
    "warroom.current_state",
    "warroom.alerts",
    "warroom.safety",
    "warroom.market.snapshot",
    "warroom.chart.review",
    "warroom.prediction.market_regime",
    "warroom.prediction.trend_bias",
    "warroom.prediction.reversal_zone",
    "warroom.prediction.volatility_risk",
    "warroom.prediction.liquidity_execution_quality",
    "warroom.prediction.breakout_false_break",
    "warroom.prediction.cross_venue_confirmation",
    "warroom.prediction.human_technical_structure",
    "warroom.prediction.scenario_ja",
)

_TOPIC_ROLES: dict[str, str] = {
    "warroom.current_state": "current_state_mini_bar",
    "warroom.alerts": "operator_alert_summary",
    "warroom.safety": "safety_boundary_summary",
    "warroom.market.snapshot": "market_snapshot_strip",
    "warroom.chart.review": "chart_review_panel",
    "warroom.prediction.market_regime": "prediction_card",
    "warroom.prediction.trend_bias": "prediction_card",
    "warroom.prediction.reversal_zone": "prediction_card",
    "warroom.prediction.volatility_risk": "prediction_card",
    "warroom.prediction.liquidity_execution_quality": "prediction_card",
    "warroom.prediction.breakout_false_break": "prediction_card",
    "warroom.prediction.cross_venue_confirmation": "prediction_card",
    "warroom.prediction.human_technical_structure": "prediction_card",
    "warroom.prediction.scenario_ja": "scenario_text_ja",
}


def build_warroom_v2_widget_topic_catalog() -> dict[str, Any]:
    rows = [{"topic": topic, "role": _TOPIC_ROLES[topic], "widget_update_unit": True, "push_transport_required_now": False, "future_websocket_compatible": True, "future_sse_compatible": True, "page_reload_required": False} for topic in WARROOM_V2_WIDGET_TOPICS]
    packet: dict[str, Any] = {"ok": True, "topic_catalog_version": WARROOM_V2_TOPIC_CATALOG_VERSION, "topic_count": len(rows), "topics": [row["topic"] for row in rows], "rows": rows, "contract_only": True, "warroom_legacy_retained": True, "warroom_v2_page_added": False, "transport_implemented": False, "websocket_enabled": False, "sse_enabled": False, "broad_page_reload_target": False}
    packet.update(warroom_v2_safety_flags())
    return packet
