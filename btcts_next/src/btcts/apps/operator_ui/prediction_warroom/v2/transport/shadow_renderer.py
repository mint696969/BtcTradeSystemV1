# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/shadow_renderer.py
# desc: WarRoom v2 shadow renderer adapter from renderer plan. Pure packet only; no UI, sockets, IO, DOM patch execution, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_SHADOW_RENDERER_ADAPTER_VERSION = "prediction_warroom.v2.transport.shadow_renderer.ps_q31l.v1"


def build_warroom_v2_shadow_renderer_adapter_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "shadow_renderer_version": WARROOM_V2_SHADOW_RENDERER_ADAPTER_VERSION,
        "adapter_kind": "warroom_v2_shadow_renderer_adapter_contract",
        "input_packet_kind": "warroom_v2_renderer_plan_packet",
        "output_packet_kind": "warroom_v2_shadow_renderer_adapter_packet",
        "patch_unit": "widget_dom_region",
        "shadow_renderer_only": True,
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


def _adapter_status(renderer_plan_status: str) -> str:
    status = str(renderer_plan_status or "")
    if status == "renderer_plan_ready_no_ui_switch":
        return "shadow_renderer_ready_no_ui_switch"
    if status == "renderer_plan_blocked":
        return "shadow_renderer_blocked"
    return "shadow_renderer_idle"


def _candidate_id(surface: str, topic: str) -> str:
    return "shadow::" + str(surface).replace(".", "_") + "::" + str(topic).replace(".", "_")


def build_warroom_v2_shadow_renderer_adapter_packet(renderer_plan: Mapping[str, Any] | None = None) -> dict[str, Any]:
    plan = dict(renderer_plan or {})
    status = _adapter_status(str(plan.get("renderer_plan_status") or ""))
    ready = status == "shadow_renderer_ready_no_ui_switch"
    candidates: list[dict[str, Any]] = []
    if ready:
        for entry in plan.get("plan_entries") or []:
            row = dict(entry or {})
            topic = str(row.get("topic") or "")
            surface = str(row.get("surface") or "unknown")
            candidates.append(
                {
                    "candidate_id": _candidate_id(surface, topic),
                    "topic": topic,
                    "surface": surface,
                    "patch_unit": str(row.get("patch_unit") or "widget_dom_region"),
                    "candidate_action": "shadow_prepare_widget_dom_region_patch",
                    "source_plan_action": str(row.get("plan_action") or ""),
                    "priority": int(row.get("priority") or 0),
                    "cadence_hint_ms": int(row.get("cadence_hint_ms") or 0),
                    "candidate_executes_patch": False,
                    "patch_execution_allowed": False,
                    "streamlit_render_allowed": False,
                    "warroom_page_ui_switch": False,
                }
            )
    return {
        "ok": True,
        "shadow_renderer_version": WARROOM_V2_SHADOW_RENDERER_ADAPTER_VERSION,
        "packet_kind": "warroom_v2_shadow_renderer_adapter_packet",
        "shadow_renderer_status": status,
        "renderer_plan_status": str(plan.get("renderer_plan_status") or ""),
        "candidate_count": len(candidates),
        "shadow_candidates": candidates,
        "observed_topics": [candidate["topic"] for candidate in candidates],
        "surfaces": sorted({candidate["surface"] for candidate in candidates}),
        "patch_unit": "widget_dom_region",
        "shadow_renderer_only": True,
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
