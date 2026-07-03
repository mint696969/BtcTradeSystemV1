# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/shadow_integration.py
# desc: WarRoom v2 Streamlit shadow integration packet helpers. Pure comparison only; no visible UI, sockets, IO, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .replay import build_warroom_v2_reconnect_request
from .simulator import build_warroom_v2_disabled_transport_simulation_frame
from .topic_policy import build_warroom_v2_topic_policy_contract

WARROOM_V2_STREAMLIT_SHADOW_INTEGRATION_VERSION = "prediction_warroom.v2.transport.shadow_integration.ps_q31e.v1"
WARROOM_V2_STREAMLIT_SHADOW_STATE_KEY = "warroom_v2_transport_shadow_integration_q31e"


def build_warroom_v2_streamlit_shadow_integration_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "shadow_integration_version": WARROOM_V2_STREAMLIT_SHADOW_INTEGRATION_VERSION,
        "state_key": WARROOM_V2_STREAMLIT_SHADOW_STATE_KEY,
        "integration_kind": "streamlit_hidden_session_state_shadow_packet",
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "visible_ui_decoration_added": False,
        "fragment_refresh_replaced": False,
        "transport_enabled": False,
        "transport_enabled_default": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
    }


def _fragment_shadow_summary(fragment_summary: Mapping[str, Any] | None = None) -> dict[str, Any]:
    summary = dict(fragment_summary or {})
    return {
        "fragment_widget_count": int(summary.get("fragment_widget_count") or 0),
        "fragment_interval_sec": int(summary.get("fragment_interval_sec") or 0),
        "page_reload_interval_sec": int(summary.get("page_reload_interval_sec") or 0),
        "hybrid_refresh": bool(summary.get("hybrid_refresh", False)),
        "page_fragment_enabled": bool(summary.get("page_fragment_enabled", False)),
        "prediction_fragment_enabled": bool(summary.get("prediction_fragment_enabled", False)),
        "fragment_refresh_replaced": False,
    }


def build_warroom_v2_streamlit_shadow_integration_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    subscribed_topics: Iterable[str] | None = None,
    frame_id: str = "streamlit-shadow",
) -> dict[str, Any]:
    fragment_packet = _fragment_shadow_summary(fragment_summary)
    shadow_frame = build_warroom_v2_disabled_transport_simulation_frame(messages=messages, frame_id=frame_id)
    topic_policy = build_warroom_v2_topic_policy_contract()
    reconnect_request = build_warroom_v2_reconnect_request(consumer_state=consumer_state, subscribed_topics=subscribed_topics)
    return {
        "ok": True,
        "shadow_integration_version": WARROOM_V2_STREAMLIT_SHADOW_INTEGRATION_VERSION,
        "state_key": WARROOM_V2_STREAMLIT_SHADOW_STATE_KEY,
        "packet_kind": "warroom_v2_streamlit_shadow_integration_packet",
        "fragment_summary": fragment_packet,
        "disabled_shadow_frame": shadow_frame,
        "topic_policy_contract": topic_policy,
        "reconnect_request": reconnect_request,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "visible_ui_decoration_added": False,
        "fragment_refresh_replaced": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
        "transport_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
    }
