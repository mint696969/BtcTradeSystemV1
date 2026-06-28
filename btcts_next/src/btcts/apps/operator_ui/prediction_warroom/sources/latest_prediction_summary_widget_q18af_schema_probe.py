# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18af_schema_probe.py
# desc: PS-Q18AF retired schema probe for the legacy latest_prediction_summary_widget chain. Kept no-render/no-refresh/no-write after PS-Q23J manifest-first display default.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ae_candidate_resolver_refresh import (
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK,
    REFRESHED_CANDIDATE_PATH,
    build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18af_schema_probe.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK = "PS_Q18AF_RUN_BOUNDED_JSON_SCHEMA_PROBE_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_KIND = "retired_schema_probe_after_manifest_first_display_default"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_STATE = "schema_probe_succeeded_no_mapping_no_render_no_refresh"
DEFAULT_MAX_SCHEMA_PROBE_BYTES = 5_000_000

REQUIRED_TOP_LEVEL_KEYS = (
    "forecast_batch",
    "read_only",
    "non_executing",
    "broker_execution_requested",
    "command_ledger_append_requested",
    "approval_append_requested",
)
REQUIRED_FORECAST_BATCH_KEYS = (
    "generated_at",
    "records",
    "record_count",
    "read_only",
    "non_executing",
)
REQUIRED_RECORD_KEYS = (
    "family",
    "generated_at",
    "horizon_sec",
    "primary_label",
    "score",
    "usable",
    "read_only",
    "non_executing",
    "would_send_to_broker",
    "would_write_runtime_artifact",
)
TOP_LEVEL_FALSE_KEYS = (
    "broker_execution_requested",
    "command_ledger_append_requested",
    "approval_append_requested",
)
RECORD_FALSE_KEYS = (
    "would_send_to_broker",
    "would_write_runtime_artifact",
)

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "schema_probe_only",
    "q18ae_candidate_resolver_refresh_consumed",
    "refreshed_candidate_present_observed",
    "schema_probe_allowed",
    "schema_probe_file_size_checked",
    "schema_probe_file_read_invoked",
    "schema_probe_json_decode_invoked",
    "schema_probe_top_level_checked",
    "schema_probe_record_shape_checked",
    "source_artifact_schema_checked",
    "source_artifact_schema_result_available",
    "source_artifact_schema_valid",
    "path_shape_preview_string_only",
    "source_candidate_count_fixed_to_one",
)

FALSE_BOUNDARIES = (
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "payload_to_widget_mapping_allowed",
    "payload_to_widget_mapping_invoked",
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


def _missing_keys(data: Mapping[str, Any], required: tuple[str, ...]) -> list[str]:
    return [key for key in required if key not in data]


def _false_key_failures(prefix: str, data: Mapping[str, Any], keys: tuple[str, ...]) -> list[str]:
    return [f"{prefix}_not_false:{key}" for key in keys if data.get(key) is not False]


def _safe_preview_keys(data: Mapping[str, Any]) -> list[str]:
    return [str(key) for key in list(data.keys())[:20]]


def build_latest_prediction_summary_widget_q18af_schema_probe_packet(
    *,
    supplied_q18ae_candidate_resolver_refresh_packet: Mapping[str, Any] | Any | None = None,
    execute_schema_probe: bool = False,
    explicit_ack: str = "",
    max_schema_probe_bytes: int = DEFAULT_MAX_SCHEMA_PROBE_BYTES,
) -> dict[str, Any]:
    source = _as_mapping(supplied_q18ae_candidate_resolver_refresh_packet)
    if not source:
        source = build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_packet(
            execute_refreshed_candidate_exists_check=True,
            explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK,
        )
    failures: list[str] = []
    warnings: list[str] = []
    payload: Any | None = None
    top_level_key_count = 0
    record_count = 0
    first_record_key_count = 0
    top_level_preview_keys: list[str] = []
    first_record_preview_keys: list[str] = []
    observed_file_size_bytes: int | None = None
    file_size_checked = False
    file_read_invoked = False
    json_decode_invoked = False
    json_decode_succeeded = False
    top_level_checked = False
    record_shape_checked = False
    schema_valid = False
    exception_class = ""
    exception_message = ""
    max_bytes = max(1, int(max_schema_probe_bytes or DEFAULT_MAX_SCHEMA_PROBE_BYTES))
    execution_allowed = bool(execute_schema_probe and explicit_ack == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK)
    path_preview = str(source.get("refreshed_candidate_path_shape_preview") or source.get("path_shape_preview") or REFRESHED_CANDIDATE_PATH)

    if source.get("ok") is not True:
        failures.append("q18ae_candidate_resolver_refresh_not_ok")
    if source.get("refreshed_candidate_present_observed") is not True:
        failures.append("refreshed_candidate_not_present")
    if path_preview != REFRESHED_CANDIDATE_PATH:
        failures.append("refreshed_candidate_path_mismatch")
    if not execute_schema_probe:
        failures.append("execute_schema_probe_false")
    if explicit_ack != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK:
        failures.append("explicit_ack_missing_or_mismatch")

    if execution_allowed and not any(item.startswith("q18ae_") or item.startswith("refreshed_candidate") for item in failures):
        try:
            path = Path(path_preview)
            observed_file_size_bytes = int(path.stat().st_size)
            file_size_checked = True
            if observed_file_size_bytes > max_bytes:
                failures.append("schema_probe_file_exceeds_max_bytes")
            else:
                file_read_invoked = True
                raw = path.read_bytes()
                json_decode_invoked = True
                payload = json.loads(raw.decode("utf-8"))
                json_decode_succeeded = True
                if not isinstance(payload, Mapping):
                    failures.append("payload_not_mapping")
                else:
                    top_level_checked = True
                    top_level_key_count = len(payload)
                    top_level_preview_keys = _safe_preview_keys(payload)
                    for key in _missing_keys(payload, REQUIRED_TOP_LEVEL_KEYS):
                        failures.append(f"missing_top_level_key:{key}")
                    failures.extend(_false_key_failures("top_level", payload, TOP_LEVEL_FALSE_KEYS))
                    if payload.get("read_only") is not True:
                        failures.append("top_level_read_only_not_true")
                    if payload.get("non_executing") is not True:
                        failures.append("top_level_non_executing_not_true")
                    forecast_batch = payload.get("forecast_batch")
                    if not isinstance(forecast_batch, Mapping):
                        failures.append("forecast_batch_not_mapping")
                        records = None
                    else:
                        for key in _missing_keys(forecast_batch, REQUIRED_FORECAST_BATCH_KEYS):
                            failures.append(f"missing_forecast_batch_key:{key}")
                        if forecast_batch.get("read_only") is not True:
                            failures.append("forecast_batch_read_only_not_true")
                        if forecast_batch.get("non_executing") is not True:
                            failures.append("forecast_batch_non_executing_not_true")
                        records = forecast_batch.get("records")
                    if not isinstance(records, list) or not records:
                        failures.append("forecast_batch_records_not_non_empty_list")
                    else:
                        record_count = len(records)
                        first = records[0]
                        if not isinstance(first, Mapping):
                            failures.append("first_record_not_mapping")
                        else:
                            record_shape_checked = True
                            first_record_key_count = len(first)
                            first_record_preview_keys = _safe_preview_keys(first)
                            for key in _missing_keys(first, REQUIRED_RECORD_KEYS):
                                failures.append(f"missing_record_key:{key}")
                            failures.extend(_false_key_failures("record", first, RECORD_FALSE_KEYS))
                            if first.get("read_only") is not True:
                                failures.append("record_read_only_not_true")
                            if first.get("non_executing") is not True:
                                failures.append("record_non_executing_not_true")
                            if not isinstance(first.get("horizon_sec"), int):
                                failures.append("record_horizon_sec_not_int")
                            if not isinstance(first.get("usable"), bool):
                                failures.append("record_usable_not_bool")
        except Exception as exc:  # noqa: BLE001 - bounded schema diagnostic only
            exception_class = exc.__class__.__name__
            exception_message = str(exc)[:240]
            failures.append("schema_probe_exception")

    schema_valid = bool(
        execution_allowed
        and file_size_checked
        and file_read_invoked
        and json_decode_invoked
        and json_decode_succeeded
        and top_level_checked
        and record_shape_checked
        and not failures
    )
    packet: dict[str, Any] = {
        "ok": schema_valid,
        "schema_probe_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_VERSION,
        "schema_probe_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK,
        "schema_probe_kind": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_KIND,
        "schema_probe_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_STATE if schema_valid else "schema_probe_blocked_or_invalid",
        "source_q18ae_candidate_resolver_refresh_ready": source.get("ok") is True,
        "refreshed_candidate_present_observed": source.get("refreshed_candidate_present_observed") is True,
        "path_shape_preview": path_preview,
        "selected_candidate_source_artifact_ref": "hot://prediction/latest_manifest.json",
        "selected_candidate_market_uid": "unknown_until_payload_mapping",
        "max_schema_probe_bytes": max_bytes,
        "observed_file_size_bytes": observed_file_size_bytes,
        "schema_probe_allowed": execution_allowed,
        "schema_probe_file_size_checked": file_size_checked,
        "schema_probe_file_read_invoked": file_read_invoked,
        "schema_probe_json_decode_invoked": json_decode_invoked,
        "schema_probe_json_decode_succeeded": json_decode_succeeded,
        "schema_probe_top_level_checked": top_level_checked,
        "schema_probe_record_shape_checked": record_shape_checked,
        "source_artifact_schema_checked": top_level_checked and record_shape_checked,
        "source_artifact_schema_result_available": top_level_checked and record_shape_checked,
        "source_artifact_schema_valid": schema_valid,
        "top_level_key_count": top_level_key_count,
        "record_count": record_count,
        "first_record_key_count": first_record_key_count,
        "top_level_preview_keys": top_level_preview_keys,
        "first_record_preview_keys": first_record_preview_keys,
        "required_top_level_keys": list(REQUIRED_TOP_LEVEL_KEYS),
        "required_forecast_batch_keys": list(REQUIRED_FORECAST_BATCH_KEYS),
        "required_record_keys": list(REQUIRED_RECORD_KEYS),
        "validation_failures": failures,
        "warning_reasons": warnings,
        "exception_class": exception_class,
        "exception_message": exception_message,
        "recommended_next_slice": "actual source read handoff or payload-to-widget props mapping preflight; keep real widget rendering, refresh, AutoTrade, broker, and parameter apply deferred unless explicitly approved.",
        "human_interpretation": "PS-Q18AF performs a bounded JSON schema probe against one refreshed present artifact. It reads only enough to decode the artifact under the max byte cap and validate shape; it does not perform payload-to-widget mapping, real widget rendering, refresh, writes, AutoTrade, or broker/private API behavior.",
    }
    packet.update({key: schema_valid for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["read_only"] = True
    packet["non_executing"] = True
    packet["display_only"] = True
    packet["schema_probe_only"] = True
    packet["q18ae_candidate_resolver_refresh_consumed"] = source.get("ok") is True
    packet["path_shape_preview_string_only"] = True
    packet["source_candidate_count_fixed_to_one"] = True
    return packet
