# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ac_filesystem_exists_check_rows.py
# desc: PS-Q18AC pure-data presenter rows for latest_prediction_summary_widget filesystem existence check result. No Streamlit import and no file access.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ac_filesystem_exists_check import (
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ac_filesystem_exists_check_packet,
)

Q18AC_EXISTENCE_RESULT_ROW_ITEMS = (
    "filesystem_exists_check_state",
    "source_artifact_exists_checked",
    "source_artifact_exists_result_available",
    "source_artifact_exists_result_state",
    "selected_candidate_generated_at",
    "selected_candidate_source_artifact_ref",
    "selected_candidate_market_uid",
    "path_shape_preview",
    "schema_validation",
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
        "existence_result_item": item,
        "value": _clean(value),
        "state": "observed" if _clean(value) else "not_supplied",
        "operator_note": note,
    }
    row.update({key: True for key in TRUE_BOUNDARIES})
    row.update({key: False for key in FALSE_BOUNDARIES})
    return row


def build_latest_prediction_summary_widget_q18ac_filesystem_exists_check_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        _row("filesystem_exists_check_state", data.get("filesystem_exists_check_state"), "Existence check was executed; this is not schema validation or source read."),
        _row("source_artifact_exists_checked", data.get("source_artifact_exists_checked"), "The explicit path preview was checked with filesystem exists only."),
        _row("source_artifact_exists_result_available", data.get("source_artifact_exists_result_available"), "A true/false existence result is available."),
        _row("source_artifact_exists_result_state", data.get("source_artifact_exists_result_state"), "Result may be exists or missing; both are valid observations."),
        _row("selected_candidate_generated_at", data.get("selected_candidate_generated_at"), "Candidate timestamp carried forward."),
        _row("selected_candidate_source_artifact_ref", data.get("selected_candidate_source_artifact_ref"), "Artifact ref remains informational."),
        _row("selected_candidate_market_uid", data.get("selected_candidate_market_uid"), "Market uid carried forward."),
        _row("path_shape_preview", data.get("path_shape_preview"), "Path remains explicit and bounded to one candidate."),
        _row("schema_validation", "false", "Schema validation remains deferred."),
        _row("actual_source_read", "false", "No bytes or text are read from the file."),
        _row("real_widget_render", "false", "The real latest_prediction_summary_widget is not rendered."),
        _row("deferred_runtime_boundary", "schema=false; actual_read=false; render=false; refresh=false; writes=false", "Runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_q18ac_filesystem_exists_check_result_packet(
    *,
    supplied_q18ab_safe_display_mount_packet: Mapping[str, Any] | Any | None = None,
    execute_filesystem_exists_check: bool = False,
    explicit_ack: str = "",
) -> dict[str, Any]:
    packet = build_latest_prediction_summary_widget_q18ac_filesystem_exists_check_packet(
        supplied_q18ab_safe_display_mount_packet=supplied_q18ab_safe_display_mount_packet,
        execute_filesystem_exists_check=execute_filesystem_exists_check,
        explicit_ack=explicit_ack,
    )
    rows = build_latest_prediction_summary_widget_q18ac_filesystem_exists_check_rows(packet) if packet.get("source_artifact_exists_result_available") is True else []
    failures: list[str] = list(packet.get("validation_failures") or [])
    if packet.get("source_artifact_exists_result_available") is True and len(rows) != len(Q18AC_EXISTENCE_RESULT_ROW_ITEMS):
        failures.append("q18ac_filesystem_exists_check_row_count_mismatch")
    result = dict(packet)
    result.update({
        "ok": packet.get("ok") is True and not [item for item in failures if item.startswith("q18ab_") or item == "path_shape_preview_missing"],
        "filesystem_exists_check_row_count": len(rows),
        "filesystem_exists_check_rows": rows,
        "filesystem_exists_check_validation_failures": failures,
    })
    return result
