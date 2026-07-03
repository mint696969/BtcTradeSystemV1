# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_diagnostic_panel.py
# desc: WarRoom v2 disabled-by-default read-only diagnostic panel adapter. Pure packet only; no UI, sockets, IO, DOM patch execution, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_OPERATOR_DIAGNOSTIC_PANEL_VERSION = "prediction_warroom.v2.transport.operator_diagnostic_panel.ps_q31q.v1"


def build_warroom_v2_operator_review_diagnostic_panel_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "diagnostic_panel_version": WARROOM_V2_OPERATOR_DIAGNOSTIC_PANEL_VERSION,
        "panel_kind": "warroom_v2_operator_review_diagnostic_panel_adapter_contract",
        "input_packet_kind": "warroom_v2_operator_review_diagnostic_gate_packet",
        "output_packet_kind": "warroom_v2_operator_review_diagnostic_panel_adapter_packet",
        "visible_panel_default_enabled": False,
        "panel_requested_default": False,
        "panel_allowed_default": False,
        "panel_adapter_only": True,
        "panel_mounts_into_warroom": False,
        "panel_renders_ui": False,
        "panel_visible_now": False,
        "panel_read_only": True,
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


def _panel_status(gate_status: str) -> str:
    status = str(gate_status or "")
    if status == "diagnostic_gate_ready_visible_read_only_no_render_here":
        return "diagnostic_panel_ready_read_only_disabled_by_default"
    if status == "diagnostic_gate_blocked_read_only_ack_required":
        return "diagnostic_panel_blocked_read_only_ack_required"
    return "diagnostic_panel_disabled_hidden_default"


def build_warroom_v2_operator_review_diagnostic_panel_packet(gate_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    gate = dict(gate_packet or {})
    status = _panel_status(str(gate.get("diagnostic_gate_status") or ""))
    ready = status == "diagnostic_panel_ready_read_only_disabled_by_default"
    rows: list[dict[str, Any]] = []
    if ready:
        for row in gate.get("gate_rows") or []:
            source = dict(row or {})
            rows.append(
                {
                    "panel_row_id": str(source.get("gate_row_id") or "operator-review-summary"),
                    "operator_review_status": str(source.get("operator_review_status") or gate.get("operator_review_status") or ""),
                    "review_row_count": int(source.get("review_row_count") or gate.get("review_row_count") or 0),
                    "panel_row_action": "present_read_only_diagnostic_row",
                    "source_gate_row_action": str(source.get("gate_row_action") or ""),
                    "panel_row_read_only": True,
                    "panel_row_renders_ui": False,
                    "panel_row_executes_patch": False,
                    "patch_execution_allowed": False,
                    "streamlit_render_allowed": False,
                    "warroom_page_ui_switch": False,
                }
            )
    return {
        "ok": True,
        "diagnostic_panel_version": WARROOM_V2_OPERATOR_DIAGNOSTIC_PANEL_VERSION,
        "packet_kind": "warroom_v2_operator_review_diagnostic_panel_adapter_packet",
        "diagnostic_panel_status": status,
        "diagnostic_gate_status": str(gate.get("diagnostic_gate_status") or ""),
        "visible_diagnostic_allowed": bool(gate.get("visible_diagnostic_allowed", False)),
        "panel_row_count": len(rows),
        "panel_rows": rows,
        "operator_review_status": str(gate.get("operator_review_status") or ""),
        "review_row_count": int(gate.get("review_row_count") or 0),
        "panel_adapter_only": True,
        "panel_mounts_into_warroom": False,
        "panel_renders_ui": False,
        "panel_visible_now": False,
        "panel_read_only": True,
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
