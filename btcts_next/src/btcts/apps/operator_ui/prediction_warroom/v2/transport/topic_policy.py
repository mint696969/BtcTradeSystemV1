# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/topic_policy.py
# desc: WarRoom v2 transport topic cadence/freshness policy. Pure policy only; no UI, sockets, prediction inference, IO, or execution.

from __future__ import annotations

from typing import Any

from ..topics import WARROOM_V2_WIDGET_TOPICS

WARROOM_V2_TOPIC_POLICY_VERSION = "prediction_warroom.v2.transport.topic_policy.ps_q31c.v1"

TOP_INFORMATION_TOPICS: tuple[str, ...] = (
    "warroom.current_state",
    "warroom.alerts",
    "warroom.safety",
    "warroom.market.snapshot",
)
PREDICTION_DISPLAY_TOPICS: tuple[str, ...] = tuple(topic for topic in WARROOM_V2_WIDGET_TOPICS if topic.startswith("warroom.prediction."))
BOTTOM_CHART_TOPICS: tuple[str, ...] = ("warroom.chart.review",)

_POLICY_BY_TOPIC: dict[str, dict[str, Any]] = {
    "warroom.current_state": {"surface": "top_information", "update_class": "high_priority_when_changed", "priority": 90, "cadence_hint_ms": 1000, "stale_policy": "show_stale_or_missing_explicitly"},
    "warroom.alerts": {"surface": "top_information", "update_class": "high_priority_when_changed", "priority": 95, "cadence_hint_ms": 1000, "stale_policy": "never_hide_alert_staleness"},
    "warroom.safety": {"surface": "top_information", "update_class": "high_priority_when_changed", "priority": 100, "cadence_hint_ms": 1000, "stale_policy": "never_hide_safety_staleness"},
    "warroom.market.snapshot": {"surface": "top_information", "update_class": "fastest_safe", "priority": 100, "cadence_hint_ms": 750, "stale_policy": "show_latest_with_freshness"},
    "warroom.chart.review": {"surface": "bottom_chart", "update_class": "medium_or_operator_opt_in", "priority": 60, "cadence_hint_ms": 3000, "stale_policy": "avoid_noisy_redraw_but_preserve_freshness"},
}
for _topic in PREDICTION_DISPLAY_TOPICS:
    _POLICY_BY_TOPIC[_topic] = {"surface": "prediction_display", "update_class": "evidence_change_or_moderate_frequency", "priority": 50, "cadence_hint_ms": 5000, "stale_policy": "preserve_last_display_payload_with_generated_at"}
_POLICY_BY_TOPIC["warroom.prediction.scenario_ja"] = {"surface": "prediction_display", "update_class": "evidence_change_or_moderate_frequency", "priority": 55, "cadence_hint_ms": 5000, "stale_policy": "preserve_last_scenario_text_with_generated_at"}


def is_warroom_v2_display_topic(topic: str) -> bool:
    return str(topic) in set(WARROOM_V2_WIDGET_TOPICS)


def build_warroom_v2_topic_policy(topic: str) -> dict[str, Any]:
    name = str(topic)
    base = dict(_POLICY_BY_TOPIC.get(name) or {})
    if not base:
        return {"ok": False, "topic_policy_version": WARROOM_V2_TOPIC_POLICY_VERSION, "topic": name, "known_display_topic": False}
    return {
        "ok": True,
        "topic_policy_version": WARROOM_V2_TOPIC_POLICY_VERSION,
        "topic": name,
        "known_display_topic": True,
        "patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
        "transport_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        **base,
    }


def list_warroom_v2_topic_policies() -> list[dict[str, Any]]:
    return [build_warroom_v2_topic_policy(topic) for topic in WARROOM_V2_WIDGET_TOPICS]


def build_warroom_v2_topic_policy_contract() -> dict[str, Any]:
    policies = list_warroom_v2_topic_policies()
    return {
        "ok": True,
        "topic_policy_version": WARROOM_V2_TOPIC_POLICY_VERSION,
        "policy_scope": "whole_warroom_display",
        "topic_count": len(policies),
        "topics": [policy["topic"] for policy in policies],
        "surfaces": sorted({str(policy["surface"]) for policy in policies}),
        "top_information_topics": list(TOP_INFORMATION_TOPICS),
        "prediction_display_topics": list(PREDICTION_DISPLAY_TOPICS),
        "bottom_chart_topics": list(BOTTOM_CHART_TOPICS),
        "prediction_cards_display_update_target": True,
        "prediction_generation_out_of_scope": True,
        "prediction_inference_out_of_scope": True,
        "transport_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "policies": policies,
    }
