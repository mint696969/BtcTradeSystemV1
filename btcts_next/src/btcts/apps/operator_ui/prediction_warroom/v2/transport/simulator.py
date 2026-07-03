# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/simulator.py
# desc: Disabled in-process WarRoom v2 transport simulator. Pure shadow-frame helpers only; no sockets, Streamlit, IO, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from ..disabled_transport_adapter import build_warroom_v2_disabled_transport_outbox
from ..topics import WARROOM_V2_WIDGET_TOPICS

WARROOM_V2_DISABLED_TRANSPORT_SIMULATOR_VERSION = "prediction_warroom.v2.transport.simulator.ps_q31b.v1"

WARROOM_V2_DISPLAY_TARGET_TOPICS: tuple[str, ...] = WARROOM_V2_WIDGET_TOPICS

_TARGET_WIDGET_IDS: dict[str, str] = {
    "warroom.current_state": "current_state_mini_bar",
    "warroom.alerts": "operator_alert_summary",
    "warroom.safety": "safety_boundary_summary",
    "warroom.market.snapshot": "market_snapshot_strip",
    "warroom.chart.review": "chart_review_panel",
    "warroom.prediction.market_regime": "prediction_card.market_regime",
    "warroom.prediction.trend_bias": "prediction_card.trend_bias",
    "warroom.prediction.reversal_zone": "prediction_card.reversal_zone",
    "warroom.prediction.volatility_risk": "prediction_card.volatility_risk",
    "warroom.prediction.liquidity_execution_quality": "prediction_card.liquidity_execution_quality",
    "warroom.prediction.breakout_false_break": "prediction_card.breakout_false_break",
    "warroom.prediction.cross_venue_confirmation": "prediction_card.cross_venue_confirmation",
    "warroom.prediction.human_technical_structure": "prediction_card.human_technical_structure",
    "warroom.prediction.scenario_ja": "scenario_text_ja",
}


def _as_message(item: Mapping[str, Any]) -> dict[str, Any]:
    message = dict(item)
    message["topic"] = str(message.get("topic") or "")
    message["widget_id"] = str(message.get("widget_id") or _TARGET_WIDGET_IDS.get(message["topic"], ""))
    message["sequence"] = int(message.get("sequence") or 0)
    message["ui_patch_unit"] = str(message.get("ui_patch_unit") or "widget_dom_region")
    message["broad_page_reload_required"] = bool(message.get("broad_page_reload_required", False))
    return message


def build_warroom_v2_disabled_transport_simulator_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "simulator_version": WARROOM_V2_DISABLED_TRANSPORT_SIMULATOR_VERSION,
        "simulator_kind": "disabled_in_process_transport_shadow_frame_builder",
        "target_goal": "seamless_whole_warroom_display_updates",
        "target_topics": list(WARROOM_V2_DISPLAY_TARGET_TOPICS),
        "target_widget_ids": [_TARGET_WIDGET_IDS[topic] for topic in WARROOM_V2_DISPLAY_TARGET_TOPICS],
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "input_kind": "q30g_outbound_message_payloads_or_local_event_queue_state",
        "output_kind": "disabled_transport_simulation_frame",
        "patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "transport_enabled": False,
        "transport_enabled_default": False,
        "simulator_sends_messages": False,
        "simulator_opens_socket": False,
        "simulator_starts_server": False,
        "simulator_starts_client": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
        "classifier_invoked": False,
    }


def filter_warroom_v2_display_target_messages(messages: Iterable[Mapping[str, Any]] | None = None) -> list[dict[str, Any]]:
    allowed = set(WARROOM_V2_DISPLAY_TARGET_TOPICS)
    return [_as_message(item) for item in messages or [] if str(dict(item).get("topic") or "") in allowed]


def build_warroom_v2_disabled_transport_simulation_frame(*, messages: Iterable[Mapping[str, Any]] | None = None, frame_id: str = "", max_messages: int = 32) -> dict[str, Any]:
    bounded = max(1, int(max_messages or 32))
    target_messages = filter_warroom_v2_display_target_messages(messages)[-bounded:]
    return {
        "ok": True,
        "simulator_version": WARROOM_V2_DISABLED_TRANSPORT_SIMULATOR_VERSION,
        "frame_kind": "disabled_in_process_transport_shadow_frame",
        "frame_id": str(frame_id),
        "max_messages": bounded,
        "message_count": len(target_messages),
        "messages": target_messages,
        "topics": [message["topic"] for message in target_messages],
        "widget_ids": [message["widget_id"] for message in target_messages],
        "would_patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "transport_enabled": False,
        "simulator_sends_messages": False,
        "simulator_opens_socket": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_disabled_transport_simulation_from_queue(*, queue_state: Mapping[str, Any] | None = None, frame_id: str = "", max_messages: int = 32) -> dict[str, Any]:
    outbox = build_warroom_v2_disabled_transport_outbox(queue_state=queue_state, transport_kind="disabled_in_process_simulator", max_messages=max_messages)
    frame = build_warroom_v2_disabled_transport_simulation_frame(messages=outbox.get("messages") or [], frame_id=frame_id, max_messages=max_messages)
    frame["source_outbox_kind"] = outbox.get("adapter_kind")
    frame["source_message_count"] = outbox.get("message_count", 0)
    return frame
