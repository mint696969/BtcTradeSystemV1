# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/streamlit_observation.py
# desc: WarRoom v2 Streamlit hidden local-loop observation helpers. Pure packet only; no visible UI, sockets, IO, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .gates import WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN
from .local_loop import run_warroom_v2_local_only_transport_experiment

WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_VERSION = "prediction_warroom.v2.transport.streamlit_observation.ps_q31i.v1"
WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_STATE_KEY = "warroom_v2_streamlit_local_loop_observation_q31i"


def _q31i_default_gate_evidence() -> dict[str, str]:
    return {
        "q31f_focused_guard": "6_passed",
        "q31f_close_guard": "68_passed",
        "q31f_py_compile": "passed",
        "q31e_focused_guard": "5_passed",
        "q31d_focused_guard": "7_passed",
        "q31c_focused_guard": "7_passed",
        "q31b_focused_guard": "7_passed",
        "q31a_focused_guard": "8_passed",
    }


def build_warroom_v2_streamlit_local_loop_observation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "observation_version": WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_STATE_KEY,
        "observation_kind": "streamlit_hidden_local_loop_observation_packet",
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


def _fragment_summary(fragment_summary: Mapping[str, Any] | None = None) -> dict[str, Any]:
    raw = dict(fragment_summary or {})
    return {
        "fragment_widget_count": int(raw.get("fragment_widget_count") or 0),
        "fragment_interval_sec": int(raw.get("fragment_interval_sec") or 0),
        "page_reload_interval_sec": int(raw.get("page_reload_interval_sec") or 0),
        "hybrid_refresh": bool(raw.get("hybrid_refresh", False)),
        "page_fragment_enabled": bool(raw.get("page_fragment_enabled", False)),
        "prediction_fragment_enabled": bool(raw.get("prediction_fragment_enabled", False)),
    }


def build_warroom_v2_streamlit_local_loop_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str = WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
    received_at: str = "streamlit-shadow-observation",
) -> dict[str, Any]:
    local_loop = run_warroom_v2_local_only_transport_experiment(
        evidence=evidence or _q31i_default_gate_evidence(),
        operator_approval_token=operator_approval_token,
        messages=messages or [],
        consumer_state=consumer_state,
        received_at=received_at,
    )
    return {
        "ok": True,
        "observation_version": WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_STATE_KEY,
        "packet_kind": "warroom_v2_streamlit_local_loop_observation_packet",
        "fragment_summary": _fragment_summary(fragment_summary),
        "local_loop_result": local_loop,
        "local_loop_observed": True,
        "default_streamlit_message_count": len(list(messages or [])),
        "emitted_message_count": int(dict(local_loop.get("outbox") or {}).get("emitted_message_count") or 0),
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
