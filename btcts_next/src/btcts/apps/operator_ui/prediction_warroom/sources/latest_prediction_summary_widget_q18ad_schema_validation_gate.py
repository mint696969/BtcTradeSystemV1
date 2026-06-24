# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ad_schema_validation_gate.py
# desc: PS-Q18AD schema validation gate for latest_prediction_summary_widget after missing filesystem existence result. Pure-data gate only; no filesystem check, file read, payload parse, render, refresh, writes, AutoTrade, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ac_filesystem_exists_check import (
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_VERSION,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AD_SCHEMA_VALIDATION_GATE_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ad_schema_validation_gate.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AD_SCHEMA_VALIDATION_GATE_ACK = "PS_Q18AD_DECLARE_SCHEMA_VALIDATION_BLOCKED_BY_MISSING_SOURCE_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AD_SCHEMA_VALIDATION_GATE_KIND = "schema_validation_gate_after_filesystem_exists_result"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AD_SCHEMA_VALIDATION_GATE_STATE = "schema_validation_blocked_missing_source_no_read_no_parse"
EXPECTED_PATH_SHAPE_PREVIEW = "D:/btc_ts_hot/prediction_sources/BTC-USD/2026-06-22T00:00:00Z/latest_prediction.json"
EXPECTED_SELECTED = {
    "selected_candidate_generated_at": "2026-06-22T00:00:00Z",
    "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    "selected_candidate_market_uid": "BTC-USD",
}

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "schema_validation_gate_only",
    "q18ac_filesystem_exists_result_consumed",
    "q18ad_schema_validation_gate_declared",
    "source_artifact_exists_checked",
    "source_artifact_exists_result_available",
    "source_artifact_missing_observed",
    "schema_validation_blocked",
    "schema_validation_block_reason_recorded",
    "path_shape_preview_string_only",
    "source_candidate_count_fixed_to_one",
)

FALSE_BOUNDARIES = (
    "filesystem_exists_check_reexecuted",
    "source_artifact_schema_check_allowed",
    "source_artifact_schema_checked",
    "source_artifact_schema_result_available",
    "source_artifact_schema_valid",
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "payload_parse_allowed",
    "payload_reparse_allowed",
    "real_prediction_widget_rendering_allowed",
    "render_latest_prediction_summary_widget_invoked",
    "component_runtime_binding_allowed",
    "refresh_invocation_allowed",
    "scheduler_enabled",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_write_runtime_artifact",
    "would_send_to_broker",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def q18ac_observed_missing_filesystem_exists_packet() -> dict[str, Any]:
    packet = {
        "ok": True,
        "filesystem_exists_check_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_VERSION,
        "filesystem_exists_check_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_ACK,
        "filesystem_exists_check_executed": True,
        "source_artifact_exists_checked": True,
        "source_artifact_exists_result_available": True,
        "source_artifact_exists_result": False,
        "source_artifact_exists_result_state": "missing",
        "source_candidate_count": 1,
        "display_packet_row_count": 12,
        "path_shape_preview": EXPECTED_PATH_SHAPE_PREVIEW,
        **EXPECTED_SELECTED,
        "source_artifact_schema_checked": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }
    return packet


def build_latest_prediction_summary_widget_q18ad_schema_validation_gate_packet(
    *,
    supplied_q18ac_filesystem_exists_result_packet: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    source = _as_mapping(supplied_q18ac_filesystem_exists_result_packet)
    if not source:
        source = q18ac_observed_missing_filesystem_exists_packet()
    failures: list[str] = []
    exists_state = _clean(source.get("source_artifact_exists_result_state"))
    if source.get("ok") is not True:
        failures.append("q18ac_filesystem_exists_result_not_ok")
    if source.get("source_artifact_exists_checked") is not True:
        failures.append("source_artifact_exists_not_checked")
    if source.get("source_artifact_exists_result_available") is not True:
        failures.append("source_artifact_exists_result_not_available")
    if exists_state != "missing":
        failures.append(f"source_artifact_exists_result_state_not_missing:{exists_state or 'empty'}")
    if source.get("source_artifact_schema_checked") is not False:
        failures.append("q18ac_source_should_not_have_schema_checked")
    if source.get("actual_source_read_invoked") is not False:
        failures.append("q18ac_source_should_not_have_actual_read")
    if not _clean(source.get("path_shape_preview")):
        failures.append("path_shape_preview_missing")
    packet: dict[str, Any] = {
        "ok": not failures,
        "schema_validation_gate_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AD_SCHEMA_VALIDATION_GATE_VERSION,
        "schema_validation_gate_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AD_SCHEMA_VALIDATION_GATE_ACK,
        "schema_validation_gate_kind": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AD_SCHEMA_VALIDATION_GATE_KIND,
        "schema_validation_gate_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AD_SCHEMA_VALIDATION_GATE_STATE,
        "source_filesystem_exists_check_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AC_FILESYSTEM_EXISTS_CHECK_VERSION,
        "source_artifact_exists_checked": source.get("source_artifact_exists_checked") is True,
        "source_artifact_exists_result_available": source.get("source_artifact_exists_result_available") is True,
        "source_artifact_exists_result_state": exists_state,
        "source_artifact_exists_result": source.get("source_artifact_exists_result"),
        "source_candidate_count": int(source.get("source_candidate_count") or 0),
        "display_packet_row_count": int(source.get("display_packet_row_count") or 0),
        "selected_candidate_generated_at": _clean(source.get("selected_candidate_generated_at")),
        "selected_candidate_source_artifact_ref": _clean(source.get("selected_candidate_source_artifact_ref")),
        "selected_candidate_market_uid": _clean(source.get("selected_candidate_market_uid")),
        "path_shape_preview": _clean(source.get("path_shape_preview")),
        "schema_validation_block_reason": "source_artifact_missing_after_filesystem_exists_check",
        "source_artifact_schema_result_state": "blocked_missing_source_artifact",
        "validation_failures": failures,
        "recommended_next_slice": "actual source availability repair or candidate resolver refresh; do not run actual source read or real widget render until a present source is observed and approved.",
        "human_interpretation": "PS-Q18AD records that schema validation is blocked because PS-Q18AC observed the explicit candidate path as missing. It does not re-run filesystem checks, read files, parse payloads, validate schema, render widgets, refresh, write artifacts, stage/apply parameters, trigger AutoTrade, or call broker APIs.",
    }
    packet.update({key: True for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet
