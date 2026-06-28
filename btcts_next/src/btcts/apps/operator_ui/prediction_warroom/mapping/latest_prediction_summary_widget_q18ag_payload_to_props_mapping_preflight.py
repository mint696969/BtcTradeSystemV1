# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/mapping/latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight.py
# desc: PS-Q18AG retired payload-to-props mapping preflight for legacy latest_prediction_summary_widget. Kept no-render/no-refresh/no-write after PS-Q23J manifest-first display default.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets._shared import REQUIRED_COMPONENT_PROPS
from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import (
    MOUNT_SLOT_ID,
    MOUNT_ZONE_ID,
    SOURCE_PACKET_ID,
    WIDGET_FAMILY_ID,
    build_latest_prediction_summary_widget_props,
)
from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18af_schema_probe import (
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK,
    build_latest_prediction_summary_widget_q18af_schema_probe_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ag_payload_to_props_mapping_preflight.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK = "PS_Q18AG_MAP_BOUNDED_PAYLOAD_TO_WIDGET_PROPS_CANDIDATE_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_KIND = "bounded_payload_to_widget_props_mapping_preflight"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_STATE = "props_candidate_ready_render_refresh_writes_disabled"
DEFAULT_MAX_MAPPING_BYTES = 5_000_000

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "payload_to_widget_props_mapping_preflight_only",
    "q18af_schema_probe_consumed",
    "source_artifact_schema_valid",
    "mapping_payload_file_size_checked",
    "mapping_payload_read_invoked",
    "mapping_payload_json_decode_invoked",
    "mapping_payload_json_decode_succeeded",
    "forecast_batch_records_consumed",
    "props_candidate_built",
    "props_contract_complete",
    "path_shape_preview_string_only",
    "source_candidate_count_fixed_to_one",
)

FALSE_BOUNDARIES = (
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "component_props_binding_allowed",
    "component_props_bound_to_component",
    "component_runtime_binding_allowed",
    "real_prediction_widget_rendering_allowed",
    "render_latest_prediction_summary_widget_invoked",
    "streamlit_render_allowed",
    "streamlit_render_invoked",
    "warroom_page_mutation_allowed",
    "warroom_mount_patch_allowed",
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


def _first_mapping(items: Any) -> Mapping[str, Any]:
    if isinstance(items, list) and items:
        return _as_mapping(items[0])
    return {}


def _nested_mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    return _as_mapping(data.get(key))


def _market_uid_from_payload(payload: Mapping[str, Any]) -> str:
    for container_key in ("system_input", "run_identity", "inference_bundle", "forecast_batch"):
        container = _nested_mapping(payload, container_key)
        for key in ("market_uid", "symbol", "market", "instrument"):
            value = _clean(container.get(key))
            if value:
                return value
    return "unknown_until_widget_mapping_review"


def build_latest_prediction_summary_widget_q18ag_payload_to_props_mapping_preflight_packet(
    *,
    supplied_q18af_schema_probe_packet: Mapping[str, Any] | Any | None = None,
    execute_mapping_preflight: bool = False,
    explicit_ack: str = "",
    max_mapping_bytes: int = DEFAULT_MAX_MAPPING_BYTES,
) -> dict[str, Any]:
    schema = _as_mapping(supplied_q18af_schema_probe_packet)
    if not schema:
        schema = build_latest_prediction_summary_widget_q18af_schema_probe_packet(
            execute_schema_probe=True,
            explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AF_SCHEMA_PROBE_ACK,
        )
    failures: list[str] = []
    payload: Any | None = None
    path_preview = _clean(schema.get("path_shape_preview"))
    max_bytes = max(1, int(max_mapping_bytes or DEFAULT_MAX_MAPPING_BYTES))
    execution_allowed = bool(execute_mapping_preflight and explicit_ack == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK)
    observed_file_size_bytes: int | None = None
    file_size_checked = False
    payload_read_invoked = False
    json_decode_invoked = False
    json_decode_succeeded = False
    forecast_batch: Mapping[str, Any] = {}
    first_record: Mapping[str, Any] = {}
    record_count = 0
    generated_at = ""
    prediction_run_id = ""
    market_uid = ""
    props_candidate: dict[str, Any] = {}
    missing_required_component_props: list[str] = []
    exception_class = ""
    exception_message = ""

    if schema.get("ok") is not True:
        failures.append("q18af_schema_probe_not_ok")
    if schema.get("source_artifact_schema_valid") is not True:
        failures.append("q18af_schema_not_valid")
    if not path_preview:
        failures.append("path_shape_preview_missing")
    if not execute_mapping_preflight:
        failures.append("execute_mapping_preflight_false")
    if explicit_ack != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK:
        failures.append("explicit_ack_missing_or_mismatch")

    if execution_allowed and not any(item.startswith("q18af_") or item == "path_shape_preview_missing" for item in failures):
        try:
            path = Path(path_preview)
            observed_file_size_bytes = int(path.stat().st_size)
            file_size_checked = True
            if observed_file_size_bytes > max_bytes:
                failures.append("mapping_payload_file_exceeds_max_bytes")
            else:
                payload_read_invoked = True
                raw = path.read_bytes()
                json_decode_invoked = True
                payload = json.loads(raw.decode("utf-8"))
                json_decode_succeeded = True
                payload_data = _as_mapping(payload)
                if not payload_data:
                    failures.append("payload_not_mapping")
                else:
                    forecast_batch = _nested_mapping(payload_data, "forecast_batch")
                    if not forecast_batch:
                        failures.append("forecast_batch_missing_or_not_mapping")
                    records = forecast_batch.get("records")
                    if not isinstance(records, list) or not records:
                        failures.append("forecast_batch_records_missing_or_empty")
                    else:
                        record_count = len(records)
                        first_record = _first_mapping(records)
                    generated_at = _clean(forecast_batch.get("generated_at")) or _clean(payload_data.get("generated_at"))
                    prediction_run_id = _clean(_nested_mapping(payload_data, "run_identity").get("prediction_run_id")) or _clean(forecast_batch.get("batch_id"))
                    market_uid = _market_uid_from_payload(payload_data)
                    if not generated_at:
                        failures.append("generated_at_missing")
                    if not prediction_run_id:
                        failures.append("prediction_run_id_missing")
                    if not first_record:
                        failures.append("first_record_missing")
        except Exception as exc:  # noqa: BLE001 - bounded mapping diagnostic only
            exception_class = exc.__class__.__name__
            exception_message = str(exc)[:240]
            failures.append("payload_to_props_mapping_exception")

    if execution_allowed and not failures:
        first_family = _clean(first_record.get("family"))
        first_horizon_sec = _clean(first_record.get("horizon_sec"))
        first_primary_label = _clean(first_record.get("primary_label"))
        first_score = _clean(first_record.get("score"))
        first_confidence = _clean(first_record.get("confidence"))
        props_candidate = build_latest_prediction_summary_widget_props(
            {
                "widget_family_id": WIDGET_FAMILY_ID,
                "source_packet_id": SOURCE_PACKET_ID,
                "mount_zone_id": MOUNT_ZONE_ID,
                "mount_slot_id": MOUNT_SLOT_ID,
                "source_generated_at": generated_at,
                "source_artifact_ref": "hot://prediction/latest_manifest.json",
                "release_gate_state": "payload_to_widget_props_mapping_preflight_only_render_disabled",
                "fallback_reason_codes": ["ps_q18ag_props_candidate_ready_render_refresh_disabled"],
                "operator_summary_ja": f"latest_prediction_summary_widget props mapping preflight: generated_at={generated_at} / records={record_count} / first={first_family}:{first_horizon_sec}s:{first_primary_label} / score={first_score}。実 widget render / refresh / write はまだ行いません。",
                "read_only": True,
                "non_executing": True,
                "prediction_run_id": prediction_run_id,
                "generated_at": generated_at,
                "market_uid": market_uid,
                "record_count": record_count,
                "forecast_batch_generated_at": generated_at,
                "first_record_family": first_family,
                "first_record_horizon_sec": first_horizon_sec,
                "first_record_primary_label": first_primary_label,
                "first_record_score": first_score,
                "first_record_confidence": first_confidence,
                "payload_to_widget_props_mapping_preflight_only": True,
                "real_widget_rendering_deferred": True,
                "refresh_deferred": True,
            }
        )
        missing_required_component_props = [field for field in REQUIRED_COMPONENT_PROPS if field not in props_candidate]
        if missing_required_component_props:
            failures.extend(f"mapped_candidate_missing_required_component_prop:{field}" for field in missing_required_component_props)

    ok = bool(execution_allowed and payload_read_invoked and json_decode_succeeded and props_candidate and not failures)
    packet: dict[str, Any] = {
        "ok": ok,
        "mapping_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_VERSION,
        "mapping_preflight_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_ACK,
        "mapping_preflight_kind": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_KIND,
        "mapping_preflight_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AG_PAYLOAD_TO_PROPS_MAPPING_PREFLIGHT_STATE if ok else "props_candidate_blocked_or_not_mapped",
        "source_q18af_schema_probe_ready": schema.get("ok") is True,
        "source_artifact_schema_valid": schema.get("source_artifact_schema_valid") is True,
        "path_shape_preview": path_preview,
        "selected_candidate_source_artifact_ref": "hot://prediction/latest_manifest.json",
        "selected_candidate_market_uid": market_uid or "unknown_until_widget_mapping_review",
        "max_mapping_bytes": max_bytes,
        "observed_file_size_bytes": observed_file_size_bytes,
        "mapping_allowed": execution_allowed,
        "mapping_payload_file_size_checked": file_size_checked,
        "mapping_payload_read_invoked": payload_read_invoked,
        "mapping_payload_json_decode_invoked": json_decode_invoked,
        "mapping_payload_json_decode_succeeded": json_decode_succeeded,
        "forecast_batch_records_consumed": bool(record_count),
        "record_count": record_count,
        "mapped_generated_at": generated_at,
        "mapped_prediction_run_id": prediction_run_id,
        "mapped_market_uid": market_uid,
        "mapped_first_record_family": _clean(first_record.get("family")),
        "mapped_first_record_horizon_sec": _clean(first_record.get("horizon_sec")),
        "mapped_first_record_primary_label": _clean(first_record.get("primary_label")),
        "mapped_first_record_score": _clean(first_record.get("score")),
        "props_candidate": props_candidate,
        "props_candidate_key_count": len(props_candidate),
        "missing_required_component_props": missing_required_component_props,
        "validation_failures": failures,
        "exception_class": exception_class,
        "exception_message": exception_message,
        "recommended_next_slice": "render-disabled packet builder validation; keep real widget rendering, refresh, runtime writes, AutoTrade, broker, and parameter apply deferred unless explicitly approved.",
        "human_interpretation": "PS-Q18AG reads the single refreshed artifact under a byte cap and maps forecast_batch.records values into a latest_prediction_summary_widget props candidate. It does not bind props to a component runtime, render the real widget, refresh, write artifacts, stage/apply parameters, trigger AutoTrade, or call broker APIs.",
    }
    packet.update({key: ok for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["read_only"] = True
    packet["non_executing"] = True
    packet["display_only"] = True
    packet["payload_to_widget_props_mapping_preflight_only"] = True
    packet["q18af_schema_probe_consumed"] = schema.get("ok") is True
    packet["source_artifact_schema_valid"] = schema.get("source_artifact_schema_valid") is True
    packet["path_shape_preview_string_only"] = True
    packet["source_candidate_count_fixed_to_one"] = True
    return packet
