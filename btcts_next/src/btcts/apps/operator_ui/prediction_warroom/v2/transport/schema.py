# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/schema.py
# desc: WarRoom v2 transport message schema helpers. Pure validation/normalization only; no sockets, IO, Streamlit, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_TRANSPORT_SCHEMA_VERSION = "prediction_warroom.v2.transport.schema.ps_q31c.v1"
WARROOM_V2_MESSAGE_TYPE = "warroom_v2_widget_update"
WARROOM_V2_PAYLOAD_KIND = "widget_update_event_envelope"
WARROOM_V2_PATCH_UNIT = "widget_dom_region"


def build_warroom_v2_transport_schema_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "schema_version": WARROOM_V2_TRANSPORT_SCHEMA_VERSION,
        "schema_kind": "warroom_v2_display_update_message_schema",
        "message_type": WARROOM_V2_MESSAGE_TYPE,
        "payload_kind": WARROOM_V2_PAYLOAD_KIND,
        "patch_unit": WARROOM_V2_PATCH_UNIT,
        "q30g_payload_compatible": True,
        "q31b_simulator_compatible": True,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "transport_enabled": False,
        "transport_enabled_default": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
        "classifier_invoked": False,
    }


def normalize_warroom_v2_transport_message(message: Mapping[str, Any] | None = None) -> dict[str, Any]:
    raw = dict(message or {})
    normalized = {
        "schema_version": WARROOM_V2_TRANSPORT_SCHEMA_VERSION,
        "message_type": str(raw.get("message_type") or WARROOM_V2_MESSAGE_TYPE),
        "payload_kind": str(raw.get("payload_kind") or WARROOM_V2_PAYLOAD_KIND),
        "topic": str(raw.get("topic") or ""),
        "widget_id": str(raw.get("widget_id") or ""),
        "sequence": int(raw.get("sequence") or 0),
        "generated_at": str(raw.get("generated_at") or ""),
        "ui_patch_unit": str(raw.get("ui_patch_unit") or raw.get("would_patch_unit") or WARROOM_V2_PATCH_UNIT),
        "broad_page_reload_required": bool(raw.get("broad_page_reload_required", False)),
        "envelope": dict(raw.get("envelope") or {}),
        "json_payload": str(raw.get("json_payload") or ""),
        "read_only": True,
        "display_only": True,
        "transport_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }
    return normalized


def validate_warroom_v2_transport_message(message: Mapping[str, Any] | None = None) -> dict[str, Any]:
    normalized = normalize_warroom_v2_transport_message(message)
    errors: list[str] = []
    if normalized["message_type"] != WARROOM_V2_MESSAGE_TYPE:
        errors.append("message_type")
    if normalized["payload_kind"] != WARROOM_V2_PAYLOAD_KIND:
        errors.append("payload_kind")
    if not normalized["topic"]:
        errors.append("topic")
    if not normalized["widget_id"]:
        errors.append("widget_id")
    if normalized["ui_patch_unit"] != WARROOM_V2_PATCH_UNIT:
        errors.append("ui_patch_unit")
    if normalized["broad_page_reload_required"] is not False:
        errors.append("broad_page_reload_required")
    return {"ok": not errors, "schema_version": WARROOM_V2_TRANSPORT_SCHEMA_VERSION, "errors": errors, "message": normalized}
