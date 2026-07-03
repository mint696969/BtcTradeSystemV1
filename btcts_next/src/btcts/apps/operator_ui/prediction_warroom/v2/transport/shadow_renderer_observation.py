# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/shadow_renderer_observation.py
# desc: WarRoom v2 hidden shadow renderer observation helpers. Pure packet only; no visible UI, sockets, IO, DOM patch execution, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .readiness import build_warroom_v2_display_update_readiness_packet
from .renderer_plan import build_warroom_v2_renderer_plan_from_readiness
from .shadow_renderer import build_warroom_v2_shadow_renderer_adapter_packet
from .streamlit_observation import build_warroom_v2_streamlit_local_loop_observation_packet

WARROOM_V2_SHADOW_RENDERER_OBSERVATION_VERSION = "prediction_warroom.v2.transport.shadow_renderer_observation.ps_q31m.v1"
WARROOM_V2_SHADOW_RENDERER_OBSERVATION_STATE_KEY = "warroom_v2_shadow_renderer_observation_q31m"


def build_warroom_v2_shadow_renderer_observation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "observation_version": WARROOM_V2_SHADOW_RENDERER_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_SHADOW_RENDERER_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_shadow_renderer_observation_packet",
        "input_pipeline": ["q31i_observation", "q31j_readiness", "q31k_renderer_plan", "q31l_shadow_adapter"],
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


def build_warroom_v2_shadow_renderer_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str | None = None,
    received_at: str = "streamlit-shadow-renderer-observation",
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "fragment_summary": fragment_summary,
        "messages": messages or [],
        "consumer_state": consumer_state,
        "evidence": evidence,
        "received_at": received_at,
    }
    if operator_approval_token is not None:
        kwargs["operator_approval_token"] = operator_approval_token
    observation = build_warroom_v2_streamlit_local_loop_observation_packet(**kwargs)
    readiness = build_warroom_v2_display_update_readiness_packet(observation)
    renderer_plan = build_warroom_v2_renderer_plan_from_readiness(readiness)
    shadow_adapter = build_warroom_v2_shadow_renderer_adapter_packet(renderer_plan)
    return {
        "ok": True,
        "observation_version": WARROOM_V2_SHADOW_RENDERER_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_SHADOW_RENDERER_OBSERVATION_STATE_KEY,
        "packet_kind": "warroom_v2_shadow_renderer_observation_packet",
        "fragment_summary": dict(observation.get("fragment_summary") or {}),
        "local_loop_observation": observation,
        "display_update_readiness": readiness,
        "renderer_plan": renderer_plan,
        "shadow_renderer_adapter": shadow_adapter,
        "default_streamlit_message_count": len(list(messages or [])),
        "shadow_candidate_count": int(shadow_adapter.get("candidate_count") or 0),
        "shadow_renderer_status": str(shadow_adapter.get("shadow_renderer_status") or ""),
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
