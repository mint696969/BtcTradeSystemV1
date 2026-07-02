# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/layout_policy.py
# desc: WarRoom v2 operator-first layout policy. Contract-only; legacy WarRoom remains untouched.

from __future__ import annotations

from typing import Any

from .safety import warroom_v2_safety_flags

WARROOM_V2_LAYOUT_POLICY_VERSION = "prediction_warroom.v2.layout_policy.ps_q29a.v1"


def build_warroom_v2_layout_policy() -> dict[str, Any]:
    widgets = [
        {"widget_id": "current_state_mini_bar", "topic": "warroom.current_state", "zone": "top", "order": 10, "default_visible": True},
        {"widget_id": "safety_mini_bar", "topic": "warroom.safety", "zone": "top", "order": 20, "default_visible": True},
        {"widget_id": "alert_summary", "topic": "warroom.alerts", "zone": "top", "order": 30, "default_visible": True},
        {"widget_id": "prediction_card_market_regime", "topic": "warroom.prediction.market_regime", "zone": "prediction_cards", "order": 100, "default_visible": True},
        {"widget_id": "prediction_card_trend_bias", "topic": "warroom.prediction.trend_bias", "zone": "prediction_cards", "order": 110, "default_visible": True},
        {"widget_id": "prediction_card_reversal_zone", "topic": "warroom.prediction.reversal_zone", "zone": "prediction_cards", "order": 120, "default_visible": True},
        {"widget_id": "prediction_card_volatility_risk", "topic": "warroom.prediction.volatility_risk", "zone": "prediction_cards", "order": 130, "default_visible": True},
        {"widget_id": "prediction_card_liquidity", "topic": "warroom.prediction.liquidity_execution_quality", "zone": "prediction_cards", "order": 140, "default_visible": True},
        {"widget_id": "prediction_card_breakout_false_break", "topic": "warroom.prediction.breakout_false_break", "zone": "prediction_cards", "order": 150, "default_visible": True},
        {"widget_id": "prediction_card_cross_venue", "topic": "warroom.prediction.cross_venue_confirmation", "zone": "prediction_cards", "order": 160, "default_visible": True},
        {"widget_id": "prediction_card_human_technical", "topic": "warroom.prediction.human_technical_structure", "zone": "prediction_cards", "order": 170, "default_visible": True},
        {"widget_id": "prediction_scenario_ja", "topic": "warroom.prediction.scenario_ja", "zone": "scenario", "order": 300, "default_visible": True},
    ]
    packet: dict[str, Any] = {
        "ok": True,
        "layout_policy_version": WARROOM_V2_LAYOUT_POLICY_VERSION,
        "warroom_v2_layout_shell_only": True,
        "warroom_legacy_retained_as_reference": True,
        "warroom_legacy_route_removed": False,
        "warroom_v2_page_added": False,
        "widget_count": len(widgets),
        "widgets": widgets,
        "zones": ["top", "prediction_cards", "scenario", "debug_collapsed"],
        "prediction_cards_zone": "prediction_cards",
        "scenario_zone_after_cards": True,
        "debug_default_collapsed": True,
        "page_owns_artifact_scanning": False,
        "page_owns_cache_invalidation": False,
        "page_owns_classifier_invocation": False,
        "page_owns_transport_source": False,
        "widget_update_unit": "topic",
        "broad_page_reload_target": False,
        "future_websocket_compatible": True,
        "future_sse_compatible": True,
    }
    packet.update(warroom_v2_safety_flags())
    return packet
