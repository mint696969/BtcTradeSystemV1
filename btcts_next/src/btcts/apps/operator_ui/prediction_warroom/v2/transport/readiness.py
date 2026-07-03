# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/readiness.py
# desc: WarRoom v2 display-update readiness read-model from local-loop observation. Pure packet only; no UI, sockets, IO, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Mapping

from .topic_policy import build_warroom_v2_topic_policy, is_warroom_v2_display_topic

WARROOM_V2_DISPLAY_UPDATE_READINESS_VERSION = "prediction_warroom.v2.transport.readiness.ps_q31j.v1"


def build_warroom_v2_display_update_readiness_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "readiness_version": WARROOM_V2_DISPLAY_UPDATE_READINESS_VERSION,
        "readiness_kind": "warroom_v2_display_update_readiness_read_model",
        "input_packet_kind": "warroom_v2_streamlit_local_loop_observation_packet",
        "patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "visible_ui_decoration_added": False,
        "fragment_refresh_replaced": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }


def _surface_empty_summary() -> dict[str, dict[str, Any]]:
    return {
        "top_information": {"observed_message_count": 0, "topics": []},
        "prediction_display": {"observed_message_count": 0, "topics": []},
        "bottom_chart": {"observed_message_count": 0, "topics": []},
    }


def _outbox_messages(observation_packet: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    packet = dict(observation_packet or {})
    local_loop = dict(packet.get("local_loop_result") or {})
    outbox = dict(local_loop.get("outbox") or {})
    messages: list[dict[str, Any]] = []
    for item in outbox.get("outbox") or []:
        message = dict(item or {})
        topic = str(message.get("topic") or "")
        if is_warroom_v2_display_topic(topic):
            messages.append(message)
    return messages


def build_warroom_v2_display_update_readiness_packet(observation_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packet = dict(observation_packet or {})
    local_loop = dict(packet.get("local_loop_result") or {})
    session = dict(local_loop.get("session") or {})
    emitted_count = int(packet.get("emitted_message_count") or dict(local_loop.get("outbox") or {}).get("emitted_message_count") or 0)
    local_ready = bool(local_loop.get("local_loop_enabled_effective") or session.get("local_loop_enabled_effective"))
    messages = _outbox_messages(packet)
    if not local_ready:
        status = "blocked_local_loop_not_ready"
    elif not messages and emitted_count == 0:
        status = "shadow_ready_no_display_events"
    else:
        status = "display_events_ready_for_widget_dom_region"
    surfaces = _surface_empty_summary()
    for message in messages:
        topic = str(message.get("topic") or "")
        policy = build_warroom_v2_topic_policy(topic)
        surface = str(policy.get("surface") or "unknown")
        surfaces.setdefault(surface, {"observed_message_count": 0, "topics": []})
        surfaces[surface]["observed_message_count"] += 1
        surfaces[surface]["topics"].append(topic)
    ready = status == "display_events_ready_for_widget_dom_region"
    return {
        "ok": True,
        "readiness_version": WARROOM_V2_DISPLAY_UPDATE_READINESS_VERSION,
        "packet_kind": "warroom_v2_display_update_readiness_packet",
        "readiness_status": status,
        "display_update_events_ready": ready,
        "local_loop_ready": local_ready,
        "observed_message_count": len(messages),
        "emitted_message_count": emitted_count,
        "surface_summary": surfaces,
        "observed_topics": [str(message.get("topic") or "") for message in messages],
        "patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "visible_ui_decoration_added": False,
        "fragment_refresh_replaced": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }
