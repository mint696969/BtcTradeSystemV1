# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.py
# desc: PS-Q18Q pure-data dry-run path-shape preflight for latest_prediction_summary_widget one-source resolver contract. No resolver invocation, no source resolution, no path materialization, no exists/schema check, no actual read, no D-hot discovery, no render, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_resolver_contract_preflight import LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_VERSION, ONE_SOURCE_RESOLVER_CONTRACT_ACK

LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_VERSION = "prediction_warroom_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.ps_q18q.v1"
ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_ACK = "PS_Q18Q_DECLARE_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_ONLY"
PATH_SHAPE_KIND = "dry_run_artifact_ref_to_candidate_path_shape_string_only"
PATH_SHAPE_TEMPLATE = "D:/btc_ts_hot/prediction_sources/{market_uid}/{generated_at}/latest_prediction.json"
PATH_SHAPE_ITEMS = (
    "dry_run_source_candidate_count",
    "dry_run_widget_family_id",
    "dry_run_source_packet_id",
    "dry_run_candidate_generated_at",
    "dry_run_candidate_source_artifact_ref",
    "dry_run_candidate_market_uid",
    "resolver_input_ref_kind",
    "path_shape_kind",
    "path_shape_template",
    "path_shape_preview",
    "path_shape_segments_declared",
    "explicit_path_shape_ack",
    "deferred_runtime_boundary",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _preview_path_shape(*, market_uid: Any, generated_at: Any) -> str:
    market = _clean(market_uid) or "{market_uid}"
    generated = _clean(generated_at) or "{generated_at}"
    return PATH_SHAPE_TEMPLATE.format(market_uid=market, generated_at=generated)


def _row(item: str, value: Any, note: str) -> dict[str, Any]:
    text = _clean(value)
    return {
        "path_shape_item": item,
        "value": text,
        "state": "declared" if text else "not_supplied",
        "operator_note": note,
        "read_only": True,
        "non_executing": True,
        "one_source_resolver_dry_run_path_shape_preflight_only": True,
        "source_candidate_count_fixed_to_one": True,
        "path_shape_declared": True,
        "path_shape_preview_string_only": True,
        "source_artifact_resolver_invoked": False,
        "source_artifact_resolution_allowed": False,
        "source_artifact_resolved": False,
        "source_artifact_path_materialized": False,
        "source_artifact_exists_checked": False,
        "source_artifact_schema_checked": False,
        "actual_source_read_allowed": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "q18p_validation_invoked_by_mount": False,
        "q18o_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_rows(*, supplied_resolver_contract_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_resolver_contract_report)
    preview = _preview_path_shape(
        market_uid=report.get("selected_candidate_market_uid"),
        generated_at=report.get("selected_candidate_generated_at"),
    )
    return [
        _row("dry_run_source_candidate_count", "1", "Exactly one candidate is accepted by this dry-run path-shape preflight."),
        _row("dry_run_widget_family_id", WIDGET_FAMILY_ID, "Dry-run path shape is scoped to latest_prediction_summary_widget only."),
        _row("dry_run_source_packet_id", SOURCE_PACKET_ID, "Dry-run path shape is scoped to latest_prediction_source_review_packet only."),
        _row("dry_run_candidate_generated_at", report.get("selected_candidate_generated_at"), "Candidate generated_at copied from supplied PS-Q18P report only."),
        _row("dry_run_candidate_source_artifact_ref", report.get("selected_candidate_source_artifact_ref"), "Candidate source artifact ref copied from supplied PS-Q18P report only; not resolved."),
        _row("dry_run_candidate_market_uid", report.get("selected_candidate_market_uid"), "Candidate market uid copied from supplied PS-Q18P report only."),
        _row("resolver_input_ref_kind", report.get("resolver_input_ref_kind") or "artifact_ref_string_only", "Input ref kind is declared; no resolver is invoked."),
        _row("path_shape_kind", PATH_SHAPE_KIND, "Path-shape kind is a string-only dry-run declaration."),
        _row("path_shape_template", PATH_SHAPE_TEMPLATE, "Template is not materialized into a filesystem path in this slice."),
        _row("path_shape_preview", preview, "Preview is a string-only dry-run shape; no existence/schema/read check."),
        _row("path_shape_segments_declared", "root=D:/btc_ts_hot; namespace=prediction_sources; market_uid; generated_at; file=latest_prediction.json", "Segments are declared as text only."),
        _row("explicit_path_shape_ack", ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_ACK, "Design-only acknowledgement; not an approval for resolution, path materialization, or read."),
        _row("deferred_runtime_boundary", "resolver_invoked=false; path_materialized=false; exists_check=false; schema_check=false; actual_read=false", "All resolver/runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_packet(*, supplied_resolver_contract_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_resolver_contract_report)
    rows = build_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_rows(supplied_resolver_contract_report=report)
    failures: list[str] = []
    if len(rows) != 13:
        failures.append("path_shape_row_count_mismatch")
    for row in rows:
        item = str(row.get("path_shape_item") or "")
        if item not in PATH_SHAPE_ITEMS:
            failures.append(f"unexpected_path_shape_item:{item}")
        for key in ("read_only", "non_executing", "one_source_resolver_dry_run_path_shape_preflight_only", "source_candidate_count_fixed_to_one", "path_shape_declared", "path_shape_preview_string_only"):
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in (
            "source_artifact_resolver_invoked",
            "source_artifact_resolution_allowed",
            "source_artifact_resolved",
            "source_artifact_path_materialized",
            "source_artifact_exists_checked",
            "source_artifact_schema_checked",
            "actual_source_read_allowed",
            "actual_source_read_invoked",
            "payload_reparse_allowed",
            "source_discovery_allowed",
            "d_hot_directory_scan_allowed",
            "d_hot_actual_read_allowed",
            "q18p_validation_invoked_by_mount",
            "q18o_validation_invoked_by_mount",
            "component_packet_builder_invoked_by_mount",
            "streamlit_render_invoked",
            "real_prediction_widget_rendering_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row_false_boundary_not_false:{item}:{key}")
    supplied = bool(report)
    candidate_ready = supplied and all(
        _clean(report.get(key))
        for key in ("selected_candidate_generated_at", "selected_candidate_source_artifact_ref", "selected_candidate_market_uid")
    )
    path_shape_preview = _preview_path_shape(
        market_uid=report.get("selected_candidate_market_uid"),
        generated_at=report.get("selected_candidate_generated_at"),
    )
    return {
        "ok": not failures,
        "path_shape_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_VERSION,
        "source_resolver_contract_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_VERSION,
        "source_resolver_contract_ack": ONE_SOURCE_RESOLVER_CONTRACT_ACK,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "one_source_resolver_dry_run_path_shape_ack": ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_ACK,
        "path_shape_state": "latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_declared_no_resolution_path_materialization_read_or_render",
        "path_shape_row_count": len(rows),
        "path_shape_rows": rows,
        "validation_failures": failures,
        "supplied_resolver_contract_report": supplied,
        "path_shape_candidate_ready": candidate_ready,
        "one_source_candidate_preserved": True,
        "source_candidate_count": 1,
        "resolver_input_ref_kind": str(report.get("resolver_input_ref_kind") or "artifact_ref_string_only"),
        "path_shape_kind": PATH_SHAPE_KIND,
        "path_shape_template": PATH_SHAPE_TEMPLATE,
        "path_shape_preview": path_shape_preview,
        "path_shape_preview_string_only": True,
        "selected_candidate_generated_at": _clean(report.get("selected_candidate_generated_at")) if report else "",
        "selected_candidate_source_artifact_ref": _clean(report.get("selected_candidate_source_artifact_ref")) if report else "",
        "selected_candidate_market_uid": _clean(report.get("selected_candidate_market_uid")) if report else "",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_only": True,
        "one_source_resolver_dry_run_path_shape_preflight_ready": True,
        "path_shape_declared": True,
        "source_candidate_count_fixed_to_one": True,
        "explicit_path_shape_ack_matched": True,
        "warroom_page_mutation_allowed": False,
        "source_artifact_resolver_invoked": False,
        "source_artifact_resolution_allowed": False,
        "source_artifact_resolved": False,
        "source_artifact_path_materialized": False,
        "source_artifact_exists_checked": False,
        "source_artifact_schema_checked": False,
        "actual_source_read_allowed": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "q18p_validation_invoked_by_mount": False,
        "q18o_validation_invoked_by_mount": False,
        "q18n_validation_invoked_by_mount": False,
        "q18m_validation_invoked_by_mount": False,
        "q18j_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "component_packet_builder_allowed_by_mount": False,
        "component_runtime_binding_allowed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "confidence_increase_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
    }
