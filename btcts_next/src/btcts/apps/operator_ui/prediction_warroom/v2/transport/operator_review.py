# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_review.py
# desc: WarRoom v2 operator-review packet from hidden shadow renderer observation. Pure read-model only; no UI, sockets, IO, DOM patch execution, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_OPERATOR_REVIEW_PACKET_VERSION = "prediction_warroom.v2.transport.operator_review.ps_q31n.v1"


def build_warroom_v2_operator_shadow_renderer_review_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "operator_review_version": WARROOM_V2_OPERATOR_REVIEW_PACKET_VERSION,
        "review_kind": "warroom_v2_operator_shadow_renderer_review_contract",
        "input_packet_kind": "warroom_v2_shadow_renderer_observation_packet",
        "output_packet_kind": "warroom_v2_operator_shadow_renderer_review_packet",
        "review_packet_only": True,
        "review_renders_ui": False,
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


def _review_status(shadow_renderer_status: str) -> str:
    status = str(shadow_renderer_status or "")
    if status == "shadow_renderer_ready_no_ui_switch":
        return "operator_review_ready_shadow_candidates"
    if status == "shadow_renderer_blocked":
        return "operator_review_blocked_shadow_renderer"
    return "operator_review_idle_shadow_no_candidates"


def _shadow_adapter(observation_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packet = dict(observation_packet or {})
    return dict(packet.get("shadow_renderer_adapter") or {})


def build_warroom_v2_operator_shadow_renderer_review_packet(observation_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packet = dict(observation_packet or {})
    adapter = _shadow_adapter(packet)
    status = _review_status(str(packet.get("shadow_renderer_status") or adapter.get("shadow_renderer_status") or ""))
    rows: list[dict[str, Any]] = []
    if status == "operator_review_ready_shadow_candidates":
        for candidate in adapter.get("shadow_candidates") or []:
            row = dict(candidate or {})
            rows.append(
                {
                    "review_row_id": str(row.get("candidate_id") or ""),
                    "topic": str(row.get("topic") or ""),
                    "surface": str(row.get("surface") or "unknown"),
                    "patch_unit": str(row.get("patch_unit") or "widget_dom_region"),
                    "review_row_action": "inspect_shadow_candidate",
                    "source_candidate_action": str(row.get("candidate_action") or ""),
                    "priority": int(row.get("priority") or 0),
                    "cadence_hint_ms": int(row.get("cadence_hint_ms") or 0),
                    "review_row_executes_patch": False,
                    "review_row_renders_ui": False,
                    "patch_execution_allowed": False,
                    "streamlit_render_allowed": False,
                    "warroom_page_ui_switch": False,
                }
            )
    return {
        "ok": True,
        "operator_review_version": WARROOM_V2_OPERATOR_REVIEW_PACKET_VERSION,
        "packet_kind": "warroom_v2_operator_shadow_renderer_review_packet",
        "operator_review_status": status,
        "shadow_renderer_status": str(packet.get("shadow_renderer_status") or adapter.get("shadow_renderer_status") or ""),
        "review_row_count": len(rows),
        "review_rows": rows,
        "observed_topics": [row["topic"] for row in rows],
        "surfaces": sorted({row["surface"] for row in rows}),
        "review_packet_only": True,
        "review_renders_ui": False,
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
