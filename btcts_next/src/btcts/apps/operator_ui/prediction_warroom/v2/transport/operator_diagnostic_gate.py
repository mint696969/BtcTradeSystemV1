# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_diagnostic_gate.py
# desc: WarRoom v2 visible read-only diagnostic gate from operator-review observation. Pure gate only; no UI, sockets, IO, DOM patch execution, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_OPERATOR_DIAGNOSTIC_GATE_VERSION = "prediction_warroom.v2.transport.operator_diagnostic_gate.ps_q31p.v1"


def build_warroom_v2_operator_review_diagnostic_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "diagnostic_gate_version": WARROOM_V2_OPERATOR_DIAGNOSTIC_GATE_VERSION,
        "gate_kind": "warroom_v2_operator_review_diagnostic_gate_contract",
        "input_packet_kind": "warroom_v2_operator_review_observation_packet",
        "output_packet_kind": "warroom_v2_operator_review_diagnostic_gate_packet",
        "visible_diagnostic_default_enabled": False,
        "visible_diagnostic_requested_default": False,
        "operator_read_only_ack_default": False,
        "visible_diagnostic_allowed_default": False,
        "future_visible_diagnostic_read_only": True,
        "gate_packet_only": True,
        "gate_renders_ui": False,
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


def _gate_status(*, requested: bool, read_only_ack: bool) -> str:
    if not requested:
        return "diagnostic_gate_hidden_default"
    if not read_only_ack:
        return "diagnostic_gate_blocked_read_only_ack_required"
    return "diagnostic_gate_ready_visible_read_only_no_render_here"


def _review_packet(observation_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packet = dict(observation_packet or {})
    return dict(packet.get("operator_review_packet") or {})


def build_warroom_v2_operator_review_diagnostic_gate_packet(
    observation_packet: Mapping[str, Any] | None = None,
    *,
    visible_diagnostic_requested: bool = False,
    operator_read_only_ack: bool = False,
) -> dict[str, Any]:
    packet = dict(observation_packet or {})
    review = _review_packet(packet)
    requested = bool(visible_diagnostic_requested)
    ack = bool(operator_read_only_ack)
    status = _gate_status(requested=requested, read_only_ack=ack)
    allowed = status == "diagnostic_gate_ready_visible_read_only_no_render_here"
    rows: list[dict[str, Any]] = []
    if allowed:
        rows.append(
            {
                "gate_row_id": "operator-review-summary",
                "operator_review_status": str(packet.get("operator_review_status") or review.get("operator_review_status") or ""),
                "review_row_count": int(packet.get("review_row_count") or review.get("review_row_count") or 0),
                "gate_row_action": "diagnostic_inspect_read_only",
                "read_only": True,
                "row_executes_patch": False,
                "row_renders_ui": False,
                "patch_execution_allowed": False,
                "streamlit_render_allowed": False,
                "warroom_page_ui_switch": False,
            }
        )
    return {
        "ok": True,
        "diagnostic_gate_version": WARROOM_V2_OPERATOR_DIAGNOSTIC_GATE_VERSION,
        "packet_kind": "warroom_v2_operator_review_diagnostic_gate_packet",
        "diagnostic_gate_status": status,
        "visible_diagnostic_requested": requested,
        "operator_read_only_ack": ack,
        "visible_diagnostic_allowed": allowed,
        "future_visible_diagnostic_read_only": True,
        "operator_review_status": str(packet.get("operator_review_status") or review.get("operator_review_status") or ""),
        "review_row_count": int(packet.get("review_row_count") or review.get("review_row_count") or 0),
        "gate_row_count": len(rows),
        "gate_rows": rows,
        "gate_packet_only": True,
        "gate_renders_ui": False,
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
