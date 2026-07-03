# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_visible_panel_plan.py
# desc: WarRoom v2 default-off operator-visible panel plan. Pure packet only; WebSocket-first premise, no UI, no sockets, no order send.

from __future__ import annotations

from typing import Any, Mapping

from .bidirectional_order_boundary import build_warroom_v2_bidirectional_order_boundary_contract

WARROOM_V2_OPERATOR_VISIBLE_PANEL_PLAN_VERSION = "prediction_warroom.v2.transport.operator_visible_panel_plan.ps_q31t.v1"


def build_warroom_v2_operator_visible_panel_plan_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "plan_version": WARROOM_V2_OPERATOR_VISIBLE_PANEL_PLAN_VERSION,
        "plan_kind": "warroom_v2_operator_visible_panel_plan_contract",
        "input_observation_kind": "warroom_v2_operator_diagnostic_observation_packet",
        "input_boundary_kind": "warroom_v2_bidirectional_websocket_order_intent_boundary",
        "output_packet_kind": "warroom_v2_operator_visible_panel_plan_packet",
        "websocket_first_future_transport": True,
        "bidirectional_websocket_premise": True,
        "read_model_push_plane": "server_to_warroom_ui",
        "command_intent_plane": "warroom_ui_or_autotrade_to_order_intent_gateway",
        "no_polling_fallback_introduced": True,
        "no_browser_timer_reload_introduced": True,
        "operator_visible_panel_default_enabled": False,
        "operator_visible_panel_requested_default": False,
        "operator_read_only_ack_default": False,
        "operator_visible_panel_allowed_default": False,
        "plan_packet_only": True,
        "plan_mounts_into_warroom": False,
        "plan_renders_ui": False,
        "plan_visible_now": False,
        "panel_read_only": True,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "websocket_enabled": False,
        "socket_opened": False,
        "external_message_send_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def _plan_status(*, requested: bool, read_only_ack: bool, diagnostic_ready: bool) -> str:
    if not requested:
        return "operator_visible_panel_plan_hidden_default"
    if not read_only_ack:
        return "operator_visible_panel_plan_blocked_read_only_ack_required"
    if not diagnostic_ready:
        return "operator_visible_panel_plan_blocked_diagnostic_not_ready"
    return "operator_visible_panel_plan_ready_default_off_no_mount"


def _diagnostic_panel(observation_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    packet = dict(observation_packet or {})
    return dict(packet.get("diagnostic_panel_packet") or {})


def build_warroom_v2_operator_visible_panel_plan_packet(
    observation_packet: Mapping[str, Any] | None = None,
    boundary_packet: Mapping[str, Any] | None = None,
    *,
    operator_visible_panel_requested: bool = False,
    operator_read_only_ack: bool = False,
) -> dict[str, Any]:
    observation = dict(observation_packet or {})
    diagnostic_panel = _diagnostic_panel(observation)
    boundary = dict(boundary_packet or build_warroom_v2_bidirectional_order_boundary_contract())
    requested = bool(operator_visible_panel_requested)
    ack = bool(operator_read_only_ack)
    diagnostic_ready = str(observation.get("diagnostic_panel_status") or diagnostic_panel.get("diagnostic_panel_status") or "") == "diagnostic_panel_ready_read_only_disabled_by_default"
    status = _plan_status(requested=requested, read_only_ack=ack, diagnostic_ready=diagnostic_ready)
    allowed = status == "operator_visible_panel_plan_ready_default_off_no_mount"
    plan_rows: list[dict[str, Any]] = []
    if allowed:
        plan_rows.append(
            {
                "plan_row_id": "operator-visible-diagnostic-panel",
                "plan_row_action": "prepare_read_only_panel_mount_plan",
                "source_diagnostic_panel_status": str(diagnostic_panel.get("diagnostic_panel_status") or ""),
                "source_panel_row_count": int(diagnostic_panel.get("panel_row_count") or 0),
                "websocket_first_future_transport": True,
                "read_model_push_plane": str(boundary.get("read_model_push_plane") or "server_to_warroom_ui"),
                "panel_row_read_only": True,
                "plan_row_mounts_ui": False,
                "plan_row_renders_ui": False,
                "plan_row_executes_patch": False,
                "order_intent_submitted": False,
                "would_send_to_broker": False,
            }
        )
    return {
        "ok": True,
        "plan_version": WARROOM_V2_OPERATOR_VISIBLE_PANEL_PLAN_VERSION,
        "packet_kind": "warroom_v2_operator_visible_panel_plan_packet",
        "operator_visible_panel_plan_status": status,
        "operator_visible_panel_requested": requested,
        "operator_read_only_ack": ack,
        "operator_visible_panel_allowed": allowed,
        "diagnostic_ready": diagnostic_ready,
        "diagnostic_panel_status": str(observation.get("diagnostic_panel_status") or diagnostic_panel.get("diagnostic_panel_status") or ""),
        "panel_row_count": int(observation.get("panel_row_count") or diagnostic_panel.get("panel_row_count") or 0),
        "plan_row_count": len(plan_rows),
        "plan_rows": plan_rows,
        "websocket_first_future_transport": True,
        "bidirectional_websocket_premise": True,
        "read_model_push_plane": str(boundary.get("read_model_push_plane") or "server_to_warroom_ui"),
        "command_intent_plane": str(boundary.get("command_intent_plane") or "warroom_ui_or_autotrade_to_order_intent_gateway"),
        "no_polling_fallback_introduced": True,
        "no_browser_timer_reload_introduced": True,
        "plan_packet_only": True,
        "plan_mounts_into_warroom": False,
        "plan_renders_ui": False,
        "plan_visible_now": False,
        "panel_read_only": True,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "websocket_enabled": False,
        "socket_opened": False,
        "external_message_send_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }
