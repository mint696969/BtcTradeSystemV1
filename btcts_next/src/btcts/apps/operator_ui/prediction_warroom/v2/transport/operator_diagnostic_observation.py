# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_diagnostic_observation.py
# desc: WarRoom v2 hidden operator diagnostic panel observation helpers. Pure packet only; no visible UI, sockets, IO, DOM patch execution, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .operator_diagnostic_gate import build_warroom_v2_operator_review_diagnostic_gate_packet
from .operator_diagnostic_panel import build_warroom_v2_operator_review_diagnostic_panel_packet
from .operator_review_observation import build_warroom_v2_operator_review_observation_packet

WARROOM_V2_OPERATOR_DIAGNOSTIC_OBSERVATION_VERSION = "prediction_warroom.v2.transport.operator_diagnostic_observation.ps_q31r.v1"
WARROOM_V2_OPERATOR_DIAGNOSTIC_OBSERVATION_STATE_KEY = "warroom_v2_operator_diagnostic_observation_q31r"


def build_warroom_v2_operator_diagnostic_observation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "observation_version": WARROOM_V2_OPERATOR_DIAGNOSTIC_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_OPERATOR_DIAGNOSTIC_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_operator_diagnostic_observation_packet",
        "input_pipeline": ["q31o_operator_review_observation", "q31p_diagnostic_gate", "q31q_diagnostic_panel_adapter"],
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


def build_warroom_v2_operator_diagnostic_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str | None = None,
    visible_diagnostic_requested: bool = False,
    operator_read_only_ack: bool = False,
    received_at: str = "streamlit-operator-diagnostic-observation",
) -> dict[str, Any]:
    review_observation = build_warroom_v2_operator_review_observation_packet(
        fragment_summary=fragment_summary,
        messages=messages or [],
        consumer_state=consumer_state,
        evidence=evidence,
        operator_approval_token=operator_approval_token,
        received_at=received_at,
    )
    diagnostic_gate = build_warroom_v2_operator_review_diagnostic_gate_packet(
        review_observation,
        visible_diagnostic_requested=visible_diagnostic_requested,
        operator_read_only_ack=operator_read_only_ack,
    )
    diagnostic_panel = build_warroom_v2_operator_review_diagnostic_panel_packet(diagnostic_gate)
    return {
        "ok": True,
        "observation_version": WARROOM_V2_OPERATOR_DIAGNOSTIC_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_OPERATOR_DIAGNOSTIC_OBSERVATION_STATE_KEY,
        "packet_kind": "warroom_v2_operator_diagnostic_observation_packet",
        "fragment_summary": dict(review_observation.get("fragment_summary") or {}),
        "operator_review_observation": review_observation,
        "diagnostic_gate_packet": diagnostic_gate,
        "diagnostic_panel_packet": diagnostic_panel,
        "default_streamlit_message_count": len(list(messages or [])),
        "diagnostic_gate_status": str(diagnostic_gate.get("diagnostic_gate_status") or ""),
        "diagnostic_panel_status": str(diagnostic_panel.get("diagnostic_panel_status") or ""),
        "panel_row_count": int(diagnostic_panel.get("panel_row_count") or 0),
        "visible_diagnostic_requested": bool(visible_diagnostic_requested),
        "operator_read_only_ack": bool(operator_read_only_ack),
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
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
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
