# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/renderer_plan.py
# desc: WarRoom v2 renderer plan from display-update readiness. Pure plan only; no UI, sockets, IO, DOM patch execution, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Mapping

from .topic_policy import build_warroom_v2_topic_policy

WARROOM_V2_RENDERER_PLAN_VERSION = "prediction_warroom.v2.transport.renderer_plan.ps_q31k.v1"


def build_warroom_v2_renderer_plan_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "renderer_plan_version": WARROOM_V2_RENDERER_PLAN_VERSION,
        "plan_kind": "warroom_v2_display_update_renderer_plan_contract",
        "input_packet_kind": "warroom_v2_display_update_readiness_packet",
        "patch_unit": "widget_dom_region",
        "renderer_executes_patch": False,
        "warroom_page_ui_switch": False,
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


def _plan_status(readiness_status: str) -> str:
    status = str(readiness_status or "")
    if status == "display_events_ready_for_widget_dom_region":
        return "renderer_plan_ready_no_ui_switch"
    if status == "blocked_local_loop_not_ready":
        return "renderer_plan_blocked"
    return "renderer_plan_idle_shadow_ready"


def _surface_topics(readiness_packet: Mapping[str, Any] | None = None) -> list[tuple[str, str]]:
    packet = dict(readiness_packet or {})
    surface_summary = dict(packet.get("surface_summary") or {})
    pairs: list[tuple[str, str]] = []
    for surface, row in surface_summary.items():
        for topic in dict(row or {}).get("topics") or []:
            pairs.append((str(surface), str(topic)))
    if pairs:
        return pairs
    return [("unknown", str(topic)) for topic in packet.get("observed_topics") or []]


def build_warroom_v2_renderer_plan_from_readiness(readiness_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packet = dict(readiness_packet or {})
    readiness_status = str(packet.get("readiness_status") or "")
    status = _plan_status(readiness_status)
    ready = status == "renderer_plan_ready_no_ui_switch"
    entries: list[dict[str, Any]] = []
    if ready:
        for surface, topic in _surface_topics(packet):
            policy = build_warroom_v2_topic_policy(topic)
            entries.append(
                {
                    "topic": topic,
                    "surface": str(policy.get("surface") or surface),
                    "patch_unit": "widget_dom_region",
                    "plan_action": "prepare_widget_dom_region_patch",
                    "patch_execution_allowed": False,
                    "streamlit_render_allowed": False,
                    "priority": int(policy.get("priority") or 0),
                    "cadence_hint_ms": int(policy.get("cadence_hint_ms") or 0),
                }
            )
    return {
        "ok": True,
        "renderer_plan_version": WARROOM_V2_RENDERER_PLAN_VERSION,
        "packet_kind": "warroom_v2_renderer_plan_packet",
        "renderer_plan_status": status,
        "readiness_status": readiness_status,
        "display_update_events_ready": bool(packet.get("display_update_events_ready", False)),
        "plan_entry_count": len(entries),
        "plan_entries": entries,
        "surfaces": sorted({entry["surface"] for entry in entries}),
        "observed_topics": [entry["topic"] for entry in entries],
        "patch_unit": "widget_dom_region",
        "renderer_executes_patch": False,
        "patch_execution_allowed": False,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
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
