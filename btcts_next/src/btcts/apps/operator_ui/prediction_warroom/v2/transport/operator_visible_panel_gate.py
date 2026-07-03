# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_visible_panel_gate.py
# desc: WarRoom v2 default-off read-only visible panel gate. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_VERSION = "prediction_warroom.v2.transport.operator_visible_panel_gate.ps_q31v.v1"


def build_warroom_v2_operator_visible_panel_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "gate_version": WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_VERSION,
        "gate_kind": "warroom_v2_operator_visible_panel_gate_contract",
        "input_packet_kind": "warroom_v2_operator_visible_panel_observation_packet",
        "output_packet_kind": "warroom_v2_operator_visible_panel_gate_packet",
        "websocket_first_future_transport": True,
        "bidirectional_websocket_premise": True,
        "no_polling_fallback_introduced": True,
        "no_browser_timer_reload_introduced": True,
        "visible_panel_gate_default_enabled": False,
        "visible_panel_gate_requested_default": False,
        "operator_read_only_ack_default": False,
        "visible_panel_gate_allowed_default": False,
        "gate_packet_only": True,
        "gate_mounts_into_warroom": False,
        "gate_renders_ui": False,
        "gate_visible_now": False,
        "panel_read_only": True,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "websocket_enabled": False,
        "socket_opened": False,
        "external_message_send_enabled": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "runtime_connected": False,
        "push_connected": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def _gate_status(*, requested: bool, read_only_ack: bool, plan_allowed: bool) -> str:
    if not requested:
        return "visible_panel_gate_hidden_default"
    if not read_only_ack:
        return "visible_panel_gate_blocked_read_only_ack_required"
    if not plan_allowed:
        return "visible_panel_gate_blocked_plan_not_allowed"
    return "visible_panel_gate_ready_read_only_no_mount"


def _visible_plan(observation_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packet = dict(observation_packet or {})
    return dict(packet.get("operator_visible_panel_plan_packet") or {})


def build_warroom_v2_operator_visible_panel_gate_packet(
    observation_packet: Mapping[str, Any] | None = None,
    *,
    visible_panel_gate_requested: bool = False,
    operator_read_only_ack: bool = False,
) -> dict[str, Any]:
    observation = dict(observation_packet or {})
    visible_plan = _visible_plan(observation)
    requested = bool(visible_panel_gate_requested)
    ack = bool(operator_read_only_ack)
    plan_allowed = bool(observation.get("operator_visible_panel_allowed", visible_plan.get("operator_visible_panel_allowed", False)))
    status = _gate_status(requested=requested, read_only_ack=ack, plan_allowed=plan_allowed)
    allowed = status == "visible_panel_gate_ready_read_only_no_mount"
    rows: list[dict[str, Any]] = []
    if allowed:
        for row in visible_plan.get("plan_rows") or []:
            source = dict(row or {})
            rows.append(
                {
                    "gate_row_id": str(source.get("plan_row_id") or "operator-visible-diagnostic-panel"),
                    "gate_row_action": "allow_read_only_panel_gate_no_mount",
                    "source_plan_row_action": str(source.get("plan_row_action") or ""),
                    "source_plan_row_mounts_ui": bool(source.get("plan_row_mounts_ui", False)),
                    "source_plan_row_renders_ui": bool(source.get("plan_row_renders_ui", False)),
                    "gate_row_read_only": True,
                    "gate_row_mounts_ui": False,
                    "gate_row_renders_ui": False,
                    "gate_row_executes_patch": False,
                    "streamlit_render_allowed": False,
                    "warroom_page_ui_switch": False,
                    "order_intent_submitted": False,
                    "would_send_to_broker": False,
                }
            )
    return {
        "ok": True,
        "gate_version": WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_VERSION,
        "packet_kind": "warroom_v2_operator_visible_panel_gate_packet",
        "visible_panel_gate_status": status,
        "visible_panel_gate_requested": requested,
        "operator_read_only_ack": ack,
        "visible_panel_gate_allowed": allowed,
        "source_operator_visible_panel_allowed": plan_allowed,
        "source_operator_visible_panel_plan_status": str(observation.get("operator_visible_panel_plan_status") or visible_plan.get("operator_visible_panel_plan_status") or ""),
        "gate_row_count": len(rows),
        "gate_rows": rows,
        "websocket_first_future_transport": True,
        "bidirectional_websocket_premise": True,
        "no_polling_fallback_introduced": True,
        "no_browser_timer_reload_introduced": True,
        "gate_packet_only": True,
        "gate_mounts_into_warroom": False,
        "gate_renders_ui": False,
        "gate_visible_now": False,
        "panel_read_only": True,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "websocket_enabled": False,
        "socket_opened": False,
        "external_message_send_enabled": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "runtime_connected": False,
        "push_connected": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }
