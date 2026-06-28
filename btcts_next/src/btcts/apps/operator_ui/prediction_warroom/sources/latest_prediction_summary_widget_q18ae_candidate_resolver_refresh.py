# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/sources/latest_prediction_summary_widget_q18ae_candidate_resolver_refresh.py
# desc: PS-Q18AE retired legacy candidate resolver for latest_prediction_summary_widget. After PS-Q23J the WarRoom display default is manifest-first; this chain is kept no-read/no-render/no-write for compatibility only.

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.sources.latest_prediction_summary_widget_q18ad_schema_validation_gate import (
    build_latest_prediction_summary_widget_q18ad_schema_validation_gate_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ae_candidate_resolver_refresh.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK = "PS_Q18AE_REFRESH_CANDIDATE_TO_PRESENT_LATEST_PREDICTION_ARTIFACT_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_KIND = "retired_legacy_candidate_resolver_after_manifest_first_default"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_STATE = "legacy_q18_candidate_resolver_retired_after_manifest_first_default"
HOT_ROOT_HINT = "D:/btc_ts_hot"
REFRESHED_CANDIDATE_PATH = "D:/btc_ts_hot/prediction/latest_manifest.json"
REFRESHED_CANDIDATE_RELATIVE_PATH = "prediction/latest_manifest.json"
PREVIOUS_MISSING_PATH = "D:/btc_ts_hot/prediction_sources/BTC-USD/2026-06-22T00:00:00Z/latest_prediction.json"

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "candidate_resolver_refresh_only",
    "q18ad_schema_gate_consumed",
    "previous_missing_candidate_acknowledged",
    "refreshed_candidate_selected",
    "refreshed_candidate_relative_path_matches_contract",
    "refreshed_candidate_exists_check_allowed",
    "refreshed_candidate_exists_checked",
    "refreshed_candidate_exists_result_available",
    "refreshed_candidate_present_observed",
    "path_shape_preview_string_only",
    "source_candidate_count_fixed_to_one",
)

FALSE_BOUNDARIES = (
    "previous_missing_candidate_reused",
    "filesystem_directory_scan_allowed",
    "glob_discovery_allowed",
    "source_artifact_schema_check_allowed",
    "source_artifact_schema_checked",
    "source_artifact_schema_result_available",
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


def build_latest_prediction_summary_widget_q18ae_candidate_resolver_refresh_packet(
    *,
    supplied_q18ad_schema_validation_gate_packet: Mapping[str, Any] | Any | None = None,
    execute_refreshed_candidate_exists_check: bool = False,
    explicit_ack: str = "",
) -> dict[str, Any]:
    source = _as_mapping(supplied_q18ad_schema_validation_gate_packet)
    if not source:
        source = build_latest_prediction_summary_widget_q18ad_schema_validation_gate_packet()
    failures: list[str] = []
    exists_result: bool | None = None
    exists_checked = False
    execution_allowed = bool(execute_refreshed_candidate_exists_check and explicit_ack == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK)

    if source.get("ok") is not True:
        failures.append("q18ad_schema_validation_gate_not_ok")
    if source.get("schema_validation_blocked") is not True:
        failures.append("q18ad_schema_validation_not_blocked")
    if source.get("source_artifact_exists_result_state") != "missing":
        failures.append("q18ad_source_result_not_missing")
    if _clean(source.get("path_shape_preview")) != PREVIOUS_MISSING_PATH:
        failures.append("q18ad_previous_missing_path_mismatch")
    if not execute_refreshed_candidate_exists_check:
        failures.append("execute_refreshed_candidate_exists_check_false")
    if explicit_ack != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK:
        failures.append("explicit_ack_missing_or_mismatch")
    failures.append("legacy_q18_candidate_resolver_retired_after_manifest_first_default")

    # Retired after PS-Q23J: keep the compatibility packet no-read/no-exists-check.
    execution_allowed = False

    result_available = exists_checked and exists_result is not None
    ok = bool(execution_allowed and exists_checked and exists_result is True and result_available and not [item for item in failures if item != "execute_refreshed_candidate_exists_check_false" and item != "explicit_ack_missing_or_mismatch"])
    packet: dict[str, Any] = {
        "ok": ok,
        "candidate_resolver_refresh_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_VERSION,
        "candidate_resolver_refresh_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_ACK,
        "candidate_resolver_refresh_kind": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_KIND,
        "candidate_resolver_refresh_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AE_CANDIDATE_RESOLVER_REFRESH_STATE,
        "source_q18ad_schema_gate_ready": source.get("ok") is True,
        "previous_candidate_path_shape_preview": _clean(source.get("path_shape_preview")),
        "previous_candidate_exists_result_state": _clean(source.get("source_artifact_exists_result_state")),
        "refreshed_candidate_root_hint": HOT_ROOT_HINT,
        "refreshed_candidate_relative_path": REFRESHED_CANDIDATE_RELATIVE_PATH,
        "refreshed_candidate_path_shape_preview": REFRESHED_CANDIDATE_PATH,
        "path_shape_preview": REFRESHED_CANDIDATE_PATH,
        "selected_candidate_generated_at": "runtime_latest_artifact_mtime_or_payload_generated_at_deferred",
        "selected_candidate_source_artifact_ref": f"hot://{REFRESHED_CANDIDATE_RELATIVE_PATH}",
        "selected_candidate_market_uid": "unknown_until_schema_validation",
        "refreshed_candidate_exists_check_allowed": execution_allowed,
        "refreshed_candidate_exists_checked": exists_checked,
        "refreshed_candidate_exists_result_available": result_available,
        "refreshed_candidate_exists_result": bool(exists_result) if exists_result is not None else None,
        "refreshed_candidate_exists_result_state": "present" if exists_result is True else "missing" if exists_result is False and result_available else "not_checked",
        "legacy_q18_candidate_resolver_retired": True,
        "manifest_first_display_default_replacement": True,
        "source_candidate_count": 0,
        "validation_failures": failures,
        "recommended_next_slice": "Use the PS-Q23J WarRoom display default manifest-first read path; do not reactivate this Q18 legacy widget chain." ,
        "human_interpretation": "PS-Q18AE is retired after the PS-Q23J manifest-first WarRoom display default. It preserves a compatibility packet only and does not read, parse, validate schema, render, refresh, write, trigger AutoTrade, or call broker APIs.",
    }
    packet.update({key: True for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["refreshed_candidate_exists_check_allowed"] = execution_allowed
    packet["refreshed_candidate_exists_checked"] = exists_checked
    packet["refreshed_candidate_exists_result_available"] = result_available
    packet["refreshed_candidate_present_observed"] = exists_result is True
    packet["previous_missing_candidate_reused"] = False
    return packet
