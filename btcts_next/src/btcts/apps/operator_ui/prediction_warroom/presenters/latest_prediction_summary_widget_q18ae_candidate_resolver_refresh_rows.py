# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_rows.py
# desc: PS-Q18AE presenter rows for latest_prediction_summary_widget candidate resolver refresh. No Streamlit import and no file access.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ae_candidate_resolver_refresh import (
    FALSE_BOUNDARIES,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_packet,
)

Q18AE_CANDIDATE_RESOLVER_REFRESH_ROW_ITEMS = (
    "candidate_resolver_refresh_state",
    "previous_candidate_exists_result_state",
    "previous_candidate_path_shape_preview",
    "refreshed_candidate_relative_path",
    "refreshed_candidate_exists_result_state",
    "refreshed_candidate_path_shape_preview",
    "selected_candidate_source_artifact_ref",
    "selected_candidate_market_uid",
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
        "candidate_resolver_item": item,
        "value": _clean(value),
        "state": "observed" if _clean(value) else "not_supplied",
        "operator_note": note,
    }
    row.update({key: True for key in TRUE_BOUNDARIES})
    row.update({key: False for key in FALSE_BOUNDARIES})
    return row


def build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        _row("candidate_resolver_refresh_state", data.get("candidate_resolver_refresh_state"), "Candidate resolver refresh selected the present latest prediction artifact."),
        _row("previous_candidate_exists_result_state", data.get("previous_candidate_exists_result_state"), "Previous candidate remains recorded as missing."),
        _row("previous_candidate_path_shape_preview", data.get("previous_candidate_path_shape_preview"), "Previous missing path is kept for traceability only."),
        _row("refreshed_candidate_relative_path", data.get("refreshed_candidate_relative_path"), "Refreshed candidate follows the non-UI scheduled producer contract path."),
        _row("refreshed_candidate_exists_result_state", data.get("refreshed_candidate_exists_result_state"), "Refreshed candidate presence is observed by exists only."),
        _row("refreshed_candidate_path_shape_preview", data.get("refreshed_candidate_path_shape_preview"), "Path remains a string preview for next schema validation slice."),
        _row("selected_candidate_source_artifact_ref", data.get("selected_candidate_source_artifact_ref"), "Artifact ref points at the hot latest prediction artifact."),
        _row("selected_candidate_market_uid", data.get("selected_candidate_market_uid"), "Market uid remains deferred until schema validation."),
        _row("schema_validation", "false", "Schema validation remains deferred to the next slice."),
        _row("actual_source_read", "false", "No bytes or text are read from the artifact."),
        _row("real_widget_render", "false", "The real latest_prediction_summary_widget is not rendered."),
        _row("deferred_runtime_boundary", "schema=false; actual_read=false; render=false; refresh=false; writes=false", "Runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_result_packet(
    *,
    supplied_q18ad_schema_validation_gate_packet: Mapping[str, Any] | Any | None = None,
    execute_refreshed_candidate_exists_check: bool = False,
    explicit_ack: str = "",
) -> dict[str, Any]:
    packet = build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_packet(
        supplied_q18ad_schema_validation_gate_packet=supplied_q18ad_schema_validation_gate_packet,
        execute_refreshed_candidate_exists_check=execute_refreshed_candidate_exists_check,
        explicit_ack=explicit_ack,
    )
    rows = build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_rows(packet) if packet.get("refreshed_candidate_present_observed") is True else []
    failures: list[str] = list(packet.get("validation_failures") or [])
    if packet.get("refreshed_candidate_present_observed") is True and len(rows) != len(Q18AE_CANDIDATE_RESOLVER_REFRESH_ROW_ITEMS):
        failures.append("q18ae_candidate_resolver_refresh_row_count_mismatch")
    result = dict(packet)
    result.update({
        "ok": packet.get("ok") is True and not failures,
        "candidate_resolver_refresh_row_count": len(rows),
        "candidate_resolver_refresh_rows": rows,
        "candidate_resolver_refresh_validation_failures": failures,
    })
    return result
