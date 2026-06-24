# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18af_schema_probe_rows.py
# desc: PS-Q18AF presenter rows for bounded schema probe result. No Streamlit import and no file access.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18af_schema_probe import (
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18af_schema_probe_packet,
)

Q18AF_SCHEMA_PROBE_ROW_ITEMS = (
    "schema_probe_state",
    "path_shape_preview",
    "observed_file_size_bytes",
    "top_level_key_count",
    "record_count",
    "first_record_key_count",
    "schema_probe_json_decode_succeeded",
    "source_artifact_schema_valid",
    "selected_candidate_market_uid",
    "actual_source_read",
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
    row = {"schema_probe_item": item, "value": _clean(value), "state": "observed" if _clean(value) else "not_supplied", "operator_note": note}
    row.update({key: True for key in TRUE_BOUNDARIES})
    row.update({key: False for key in FALSE_BOUNDARIES})
    return row


def build_latest_prediction_summary_widget_q18af_schema_probe_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        _row("schema_probe_state", data.get("schema_probe_state"), "Bounded JSON schema probe state."),
        _row("path_shape_preview", data.get("path_shape_preview"), "Single refreshed candidate path."),
        _row("observed_file_size_bytes", data.get("observed_file_size_bytes"), "File size observed before bounded read."),
        _row("top_level_key_count", data.get("top_level_key_count"), "Top-level JSON object key count."),
        _row("record_count", data.get("record_count"), "Records list count from payload shape."),
        _row("first_record_key_count", data.get("first_record_key_count"), "First record key count."),
        _row("schema_probe_json_decode_succeeded", data.get("schema_probe_json_decode_succeeded"), "JSON decode succeeded under the byte cap."),
        _row("source_artifact_schema_valid", data.get("source_artifact_schema_valid"), "Minimal schema shape is valid."),
        _row("selected_candidate_market_uid", data.get("selected_candidate_market_uid"), "Market uid remains deferred until mapping."),
        _row("actual_source_read", "false", "No payload-to-widget actual source handoff is performed."),
        _row("real_widget_render", "false", "The real latest_prediction_summary_widget is not rendered."),
        _row("deferred_runtime_boundary", "mapping=false; render=false; refresh=false; writes=false", "Runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_q18af_schema_probe_result_packet(
    *,
    supplied_q18ae_candidate_resolver_refresh_packet: Mapping[str, Any] | Any | None = None,
    execute_schema_probe: bool = False,
    explicit_ack: str = "",
    max_schema_probe_bytes: int = 5_000_000,
) -> dict[str, Any]:
    packet = build_latest_prediction_summary_widget_q18af_schema_probe_packet(
        supplied_q18ae_candidate_resolver_refresh_packet=supplied_q18ae_candidate_resolver_refresh_packet,
        execute_schema_probe=execute_schema_probe,
        explicit_ack=explicit_ack,
        max_schema_probe_bytes=max_schema_probe_bytes,
    )
    rows = build_latest_prediction_summary_widget_q18af_schema_probe_rows(packet) if packet.get("source_artifact_schema_valid") is True else []
    failures: list[str] = list(packet.get("validation_failures") or [])
    if packet.get("source_artifact_schema_valid") is True and len(rows) != len(Q18AF_SCHEMA_PROBE_ROW_ITEMS):
        failures.append("q18af_schema_probe_row_count_mismatch")
    result = dict(packet)
    result.update({"ok": packet.get("ok") is True and not failures, "schema_probe_row_count": len(rows), "schema_probe_rows": rows, "schema_probe_validation_failures": failures})
    return result
