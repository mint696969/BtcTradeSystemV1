# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ah_render_disabled_packet_rows.py
# desc: PS-Q18AH presenter rows for render-disabled packet builder validation. No Streamlit import and no file access.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.mapping.latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation import (
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation_packet,
)

Q18AH_RENDER_DISABLED_PACKET_ROW_ITEMS = (
    "validation_state",
    "component_packet_state",
    "component_source_generated_at",
    "mapped_record_count",
    "mapped_first_record_family",
    "mapped_first_record_horizon_sec",
    "mapped_first_record_primary_label",
    "mapped_first_record_score",
    "component_packet_valid",
    "streamlit_render",
    "refresh",
    "deferred_runtime_boundary",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _row(item: str, value: Any, note: str) -> dict[str, Any]:
    row = {"render_disabled_packet_item": item, "value": _clean(value), "state": "observed" if _clean(value) else "not_supplied", "operator_note": note}
    row.update({key: True for key in TRUE_BOUNDARIES})
    row.update({key: False for key in FALSE_BOUNDARIES})
    return row


def build_latest_prediction_summary_widget_q18ah_render_disabled_packet_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        _row("validation_state", data.get("validation_state"), "Render-disabled packet validation state."),
        _row("component_packet_state", data.get("component_packet_state"), "Skeleton component packet stays render-disabled."),
        _row("component_source_generated_at", data.get("component_source_generated_at"), "Mapped source timestamp is visible in the packet."),
        _row("mapped_record_count", data.get("mapped_record_count"), "Mapped record count."),
        _row("mapped_first_record_family", data.get("mapped_first_record_family"), "First mapped family."),
        _row("mapped_first_record_horizon_sec", data.get("mapped_first_record_horizon_sec"), "First mapped horizon."),
        _row("mapped_first_record_primary_label", data.get("mapped_first_record_primary_label"), "First mapped label."),
        _row("mapped_first_record_score", data.get("mapped_first_record_score"), "First mapped score."),
        _row("component_packet_valid", data.get("component_packet_valid"), "Component packet is valid while render-disabled."),
        _row("streamlit_render", "false", "No Streamlit render is invoked."),
        _row("refresh", "false", "No refresh loop is enabled in this slice."),
        _row("deferred_runtime_boundary", "real_render=false; refresh=false; writes=false; autotrade=false; broker=false", "Runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_q18ah_render_disabled_packet_result_packet(
    *,
    supplied_q18ag_payload_to_props_mapping_packet: Mapping[str, Any] | Any | None = None,
    execute_packet_builder_validation: bool = False,
    explicit_ack: str = "",
) -> dict[str, Any]:
    packet = build_latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation_packet(
        supplied_q18ag_payload_to_props_mapping_packet=supplied_q18ag_payload_to_props_mapping_packet,
        execute_packet_builder_validation=execute_packet_builder_validation,
        explicit_ack=explicit_ack,
    )
    rows = build_latest_prediction_summary_widget_q18ah_render_disabled_packet_rows(packet) if packet.get("ok") is True else []
    failures: list[str] = list(packet.get("validation_failures") or [])
    if packet.get("ok") is True and len(rows) != len(Q18AH_RENDER_DISABLED_PACKET_ROW_ITEMS):
        failures.append("q18ah_render_disabled_packet_row_count_mismatch")
    result = dict(packet)
    result.update({"ok": packet.get("ok") is True and not failures, "render_disabled_packet_row_count": len(rows), "render_disabled_packet_rows": rows, "render_disabled_packet_validation_failures": failures})
    return result
