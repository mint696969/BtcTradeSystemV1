# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport_ownership.py
# desc: WarRoom v2 transport ownership contracts for future natural widget updates. No Streamlit, socket, runtime, or execution behavior.

from __future__ import annotations

from typing import Any, Mapping

from .safety import warroom_v2_safety_flags
from .topics import WARROOM_V2_WIDGET_TOPICS

WARROOM_V2_TRANSPORT_OWNERSHIP_VERSION = "prediction_warroom.v2.transport_ownership.ps_q30c.v1"
WARROOM_V2_TRANSPORT_ENVELOPE_VERSION = "prediction_warroom.v2.transport_event_envelope.ps_q30c.v1"


def build_warroom_v2_transport_ownership_contract() -> dict[str, Any]:
    packet: dict[str, Any] = {
        "ok": True,
        "transport_ownership_version": WARROOM_V2_TRANSPORT_OWNERSHIP_VERSION,
        "transport_owner": "external_read_model_event_bridge",
        "ui_role": "read_model_event_consumer_only",
        "page_owns_transport_source": False,
        "widget_owns_transport_source": False,
        "widget_owns_artifact_scanning": False,
        "widget_owns_classifier_invocation": False,
        "widget_owns_cache_invalidation": False,
        "event_unit": "widget_topic",
        "patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "natural_update_goal": True,
        "transport_implemented_now": False,
        "future_websocket_compatible": True,
        "future_sse_compatible": True,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "page_reload_enabled": False,
        "browser_timer_reload_enabled": False,
        "topics": list(WARROOM_V2_WIDGET_TOPICS),
        "primary_natural_update_topics": ["warroom.market.snapshot", "warroom.chart.review"],
    }
    packet.update(warroom_v2_safety_flags())
    return packet


def build_warroom_v2_transport_subscription_contract(*, widget_id: str, topic: str) -> dict[str, Any]:
    return {
        "ok": True,
        "transport_ownership_version": WARROOM_V2_TRANSPORT_OWNERSHIP_VERSION,
        "widget_id": str(widget_id),
        "topic": str(topic),
        "topic_known": str(topic) in WARROOM_V2_WIDGET_TOPICS,
        "subscription_kind": "future_read_model_event_stream",
        "ui_consumer_only": True,
        "event_unit": "widget_topic",
        "patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "transport_implemented_now": False,
        "future_websocket_compatible": True,
        "future_sse_compatible": True,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
    }


def build_warroom_v2_transport_event_envelope(*, widget_update_event: Mapping[str, Any], channel: str = "future_stream") -> dict[str, Any]:
    event = dict(widget_update_event)
    topic = str(event.get("topic") or "")
    read_model = dict(event.get("read_model") or {})
    return {
        "ok": True,
        "transport_event_envelope_version": WARROOM_V2_TRANSPORT_ENVELOPE_VERSION,
        "channel": str(channel),
        "topic": topic,
        "widget_id": str(read_model.get("widget_id") or ""),
        "sequence": int(event.get("sequence") or 0),
        "changed": bool(event.get("changed")),
        "payload_kind": "widget_update_event",
        "event": event,
        "ui_patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "event_source_replaceable": True,
        "transport_implemented_now": False,
        "future_websocket_compatible": True,
        "future_sse_compatible": True,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
    }
