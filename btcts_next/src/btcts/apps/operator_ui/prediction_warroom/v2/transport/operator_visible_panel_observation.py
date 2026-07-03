# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_visible_panel_observation.py
# desc: WarRoom v2 hidden operator visible panel plan observation. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .bidirectional_order_boundary import build_warroom_v2_bidirectional_order_boundary_contract
from .operator_diagnostic_observation import build_warroom_v2_operator_diagnostic_observation_packet
from .operator_visible_panel_plan import build_warroom_v2_operator_visible_panel_plan_packet

WARROOM_V2_OPERATOR_VISIBLE_PANEL_OBSERVATION_VERSION = "prediction_warroom.v2.transport.operator_visible_panel_observation.ps_q31u.v1"
WARROOM_V2_OPERATOR_VISIBLE_PANEL_OBSERVATION_STATE_KEY = "warroom_v2_operator_visible_panel_observation_q31u"


def build_warroom_v2_operator_visible_panel_observation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "observation_version": WARROOM_V2_OPERATOR_VISIBLE_PANEL_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_OPERATOR_VISIBLE_PANEL_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_operator_visible_panel_plan_observation_packet",
        "input_pipeline": ["q31r_operator_diagnostic_observation", "q31s_bidirectional_order_boundary", "q31t_operator_visible_panel_plan"],
        "websocket_first_future_transport": True,
        "bidirectional_websocket_premise": True,
        "no_polling_fallback_introduced": True,
        "no_browser_timer_reload_introduced": True,
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
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_operator_visible_panel_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str | None = None,
    visible_diagnostic_requested: bool = False,
    diagnostic_read_only_ack: bool = False,
    operator_visible_panel_requested: bool = False,
    operator_read_only_ack: bool = False,
    received_at: str = "streamlit-operator-visible-panel-observation",
) -> dict[str, Any]:
    diagnostic_observation = build_warroom_v2_operator_diagnostic_observation_packet(
        fragment_summary=fragment_summary,
        messages=messages or [],
        consumer_state=consumer_state,
        evidence=evidence,
        operator_approval_token=operator_approval_token,
        visible_diagnostic_requested=visible_diagnostic_requested,
        operator_read_only_ack=diagnostic_read_only_ack,
        received_at=received_at,
    )
    boundary = build_warroom_v2_bidirectional_order_boundary_contract()
    visible_plan = build_warroom_v2_operator_visible_panel_plan_packet(
        diagnostic_observation,
        boundary,
        operator_visible_panel_requested=operator_visible_panel_requested,
        operator_read_only_ack=operator_read_only_ack,
    )
    return {
        "ok": True,
        "observation_version": WARROOM_V2_OPERATOR_VISIBLE_PANEL_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_OPERATOR_VISIBLE_PANEL_OBSERVATION_STATE_KEY,
        "packet_kind": "warroom_v2_operator_visible_panel_observation_packet",
        "fragment_summary": dict(diagnostic_observation.get("fragment_summary") or {}),
        "diagnostic_observation_packet": diagnostic_observation,
        "boundary_packet": boundary,
        "operator_visible_panel_plan_packet": visible_plan,
        "default_streamlit_message_count": len(list(messages or [])),
        "operator_visible_panel_plan_status": str(visible_plan.get("operator_visible_panel_plan_status") or ""),
        "operator_visible_panel_requested": bool(operator_visible_panel_requested),
        "operator_read_only_ack": bool(operator_read_only_ack),
        "operator_visible_panel_allowed": bool(visible_plan.get("operator_visible_panel_allowed", False)),
        "plan_row_count": int(visible_plan.get("plan_row_count") or 0),
        "websocket_first_future_transport": True,
        "bidirectional_websocket_premise": True,
        "no_polling_fallback_introduced": True,
        "no_browser_timer_reload_introduced": True,
        "plan_packet_only": True,
        "plan_mounts_into_warroom": False,
        "plan_renders_ui": False,
        "plan_visible_now": False,
        "panel_read_only": True,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
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
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }
