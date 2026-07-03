# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_review_observation.py
# desc: WarRoom v2 hidden operator-review observation helpers. Pure packet only; no visible UI, sockets, IO, DOM patch execution, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .operator_review import build_warroom_v2_operator_shadow_renderer_review_packet
from .shadow_renderer_observation import build_warroom_v2_shadow_renderer_observation_packet

WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_VERSION = "prediction_warroom.v2.transport.operator_review_observation.ps_q31o.v1"
WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY = "warroom_v2_operator_review_observation_q31o"


def build_warroom_v2_operator_review_observation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "observation_version": WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_operator_review_observation_packet",
        "input_pipeline": ["q31m_shadow_renderer_observation", "q31n_operator_review_packet"],
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


def build_warroom_v2_operator_review_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str | None = None,
    received_at: str = "streamlit-operator-review-observation",
) -> dict[str, Any]:
    shadow_observation = build_warroom_v2_shadow_renderer_observation_packet(
        fragment_summary=fragment_summary,
        messages=messages or [],
        consumer_state=consumer_state,
        evidence=evidence,
        operator_approval_token=operator_approval_token,
        received_at=received_at,
    )
    operator_review = build_warroom_v2_operator_shadow_renderer_review_packet(shadow_observation)
    return {
        "ok": True,
        "observation_version": WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY,
        "packet_kind": "warroom_v2_operator_review_observation_packet",
        "fragment_summary": dict(shadow_observation.get("fragment_summary") or {}),
        "shadow_renderer_observation": shadow_observation,
        "operator_review_packet": operator_review,
        "default_streamlit_message_count": len(list(messages or [])),
        "operator_review_status": str(operator_review.get("operator_review_status") or ""),
        "review_row_count": int(operator_review.get("review_row_count") or 0),
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
