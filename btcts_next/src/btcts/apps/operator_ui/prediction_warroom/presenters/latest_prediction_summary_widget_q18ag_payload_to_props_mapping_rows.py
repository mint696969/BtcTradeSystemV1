# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ag_payload_to_props_mapping_rows.py
# desc: PS-Q18AG presenter rows for payload-to-widget props mapping preflight. No Streamlit import and no file access.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.mapping.latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight import (
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight_packet,
)

Q18AG_PAYLOAD_TO_PROPS_MAPPING_ROW_ITEMS = (
    "mapping_preflight_state",
    "path_shape_preview",
    "mapped_generated_at",
    "record_count",
    "mapped_first_record_family",
    "mapped_first_record_horizon_sec",
    "mapped_first_record_primary_label",
    "mapped_first_record_score",
    "props_candidate_key_count",
    "component_runtime_binding",
    "real_widget_render",
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
    row = {"mapping_item": item, "value": _clean(value), "state": "observed" if _clean(value) else "not_supplied", "operator_note": note}
    row.update({key: True for key in TRUE_BOUNDARIES})
    row.update({key: False for key in FALSE_BOUNDARIES})
    return row


def build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        _row("mapping_preflight_state", data.get("mapping_preflight_state"), "Props candidate mapping state."),
        _row("path_shape_preview", data.get("path_shape_preview"), "Single refreshed candidate path."),
        _row("mapped_generated_at", data.get("mapped_generated_at"), "Mapped from forecast_batch.generated_at."),
        _row("record_count", data.get("record_count"), "Mapped forecast_batch.records count."),
        _row("mapped_first_record_family", data.get("mapped_first_record_family"), "First record family for operator summary."),
        _row("mapped_first_record_horizon_sec", data.get("mapped_first_record_horizon_sec"), "First record horizon seconds."),
        _row("mapped_first_record_primary_label", data.get("mapped_first_record_primary_label"), "First record primary label."),
        _row("mapped_first_record_score", data.get("mapped_first_record_score"), "First record score."),
        _row("props_candidate_key_count", data.get("props_candidate_key_count"), "Props candidate is contract-complete."),
        _row("component_runtime_binding", "false", "Props are not bound to a component runtime."),
        _row("real_widget_render", "false", "The real latest_prediction_summary_widget is not rendered."),
        _row("deferred_runtime_boundary", "render=false; refresh=false; writes=false; autotrade=false; broker=false", "Runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_result_packet(
    *,
    supplied_q18af_schema_probe_packet: Mapping[str, Any] | Any | None = None,
    execute_mapping_preflight: bool = False,
    explicit_ack: str = "",
    max_mapping_bytes: int = 5_000_000,
) -> dict[str, Any]:
    packet = build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight_packet(
        supplied_q18af_schema_probe_packet=supplied_q18af_schema_probe_packet,
        execute_mapping_preflight=execute_mapping_preflight,
        explicit_ack=explicit_ack,
        max_mapping_bytes=max_mapping_bytes,
    )
    rows = build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_rows(packet) if packet.get("ok") is True else []
    failures: list[str] = list(packet.get("validation_failures") or [])
    if packet.get("ok") is True and len(rows) != len(Q18AG_PAYLOAD_TO_PROPS_MAPPING_ROW_ITEMS):
        failures.append("q18ag_payload_to_props_mapping_row_count_mismatch")
    result = dict(packet)
    result.update({"ok": packet.get("ok") is True and not failures, "payload_to_props_mapping_row_count": len(rows), "payload_to_props_mapping_rows": rows, "payload_to_props_mapping_validation_failures": failures})
    return result
