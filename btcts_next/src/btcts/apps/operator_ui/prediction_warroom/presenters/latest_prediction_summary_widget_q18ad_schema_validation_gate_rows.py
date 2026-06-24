# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ad_schema_validation_gate_rows.py
# desc: PS-Q18AD presenter rows for latest_prediction_summary_widget schema validation gate blocked by missing source. No Streamlit import and no file access.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ad_schema_validation_gate import (
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ad_schema_validation_gate_packet,
)

Q18AD_SCHEMA_VALIDATION_GATE_ROW_ITEMS = (
    "schema_validation_gate_state",
    "source_artifact_exists_result_state",
    "schema_validation_block_reason",
    "source_artifact_schema_result_state",
    "selected_candidate_generated_at",
    "selected_candidate_source_artifact_ref",
    "selected_candidate_market_uid",
    "path_shape_preview",
    "filesystem_recheck",
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
    row = {
        "schema_gate_item": item,
        "value": _clean(value),
        "state": "observed" if _clean(value) else "not_supplied",
        "operator_note": note,
    }
    row.update({key: True for key in TRUE_BOUNDARIES})
    row.update({key: False for key in FALSE_BOUNDARIES})
    return row


def build_latest_prediction_summary_widget_q18ad_schema_validation_gate_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        _row("schema_validation_gate_state", data.get("schema_validation_gate_state"), "Schema validation gate is closed because the source artifact is missing."),
        _row("source_artifact_exists_result_state", data.get("source_artifact_exists_result_state"), "PS-Q18AC observed the source as missing."),
        _row("schema_validation_block_reason", data.get("schema_validation_block_reason"), "Schema validation cannot proceed without a present payload source."),
        _row("source_artifact_schema_result_state", data.get("source_artifact_schema_result_state"), "Schema result is blocked, not valid or invalid."),
        _row("selected_candidate_generated_at", data.get("selected_candidate_generated_at"), "Candidate timestamp carried forward."),
        _row("selected_candidate_source_artifact_ref", data.get("selected_candidate_source_artifact_ref"), "Artifact ref remains informational."),
        _row("selected_candidate_market_uid", data.get("selected_candidate_market_uid"), "Market uid carried forward."),
        _row("path_shape_preview", data.get("path_shape_preview"), "Path remains a string preview from prior slices."),
        _row("filesystem_recheck", "false", "This slice does not re-run filesystem checks."),
        _row("actual_source_read", "false", "No bytes or text are read from the file."),
        _row("real_widget_render", "false", "The real latest_prediction_summary_widget is not rendered."),
        _row("deferred_runtime_boundary", "schema_checked=false; actual_read=false; render=false; refresh=false; writes=false", "Runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_q18ad_schema_validation_gate_result_packet(
    *,
    supplied_q18ac_filesystem_exists_result_packet: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    packet = build_latest_prediction_summary_widget_q18ad_schema_validation_gate_packet(
        supplied_q18ac_filesystem_exists_result_packet=supplied_q18ac_filesystem_exists_result_packet,
    )
    rows = build_latest_prediction_summary_widget_q18ad_schema_validation_gate_rows(packet) if packet.get("ok") is True else []
    failures: list[str] = list(packet.get("validation_failures") or [])
    if packet.get("ok") is True and len(rows) != len(Q18AD_SCHEMA_VALIDATION_GATE_ROW_ITEMS):
        failures.append("q18ad_schema_validation_gate_row_count_mismatch")
    result = dict(packet)
    result.update({
        "ok": packet.get("ok") is True and not failures,
        "schema_validation_gate_row_count": len(rows),
        "schema_validation_gate_rows": rows,
        "schema_validation_gate_validation_failures": failures,
    })
    return result
