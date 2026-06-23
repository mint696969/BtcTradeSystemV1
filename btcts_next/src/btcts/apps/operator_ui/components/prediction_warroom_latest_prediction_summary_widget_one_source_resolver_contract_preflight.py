# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_resolver_contract_preflight.py
# desc: PS-Q18P pure-data resolver contract preflight for latest_prediction_summary_widget one-source handoff. No source resolution, path materialization, exists/schema check, actual read, D-hot discovery, render, refresh, or writes.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import SOURCE_PACKET_ID, WIDGET_FAMILY_ID
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_handoff_design_checkpoint import LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_VERSION, ONE_SOURCE_HANDOFF_DESIGN_ACK

LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_VERSION = "prediction_warroom_latest_prediction_summary_widget_one_source_resolver_contract_preflight.ps_q18p.v1"
ONE_SOURCE_RESOLVER_CONTRACT_ACK = "PS_Q18P_DECLARE_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_ONLY"
RESOLVER_CONTRACT_ITEMS = (
    "contract_source_candidate_count",
    "resolver_widget_family_id",
    "resolver_source_packet_id",
    "resolver_candidate_generated_at",
    "resolver_candidate_source_artifact_ref",
    "resolver_candidate_market_uid",
    "resolver_input_ref_kind",
    "resolver_output_contract",
    "explicit_resolver_contract_ack",
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
    text = _clean(value)
    return {
        "resolver_contract_item": item,
        "value": text,
        "state": "declared" if text else "not_supplied",
        "operator_note": note,
        "read_only": True,
        "non_executing": True,
        "one_source_resolver_contract_preflight_only": True,
        "source_candidate_count_fixed_to_one": True,
        "resolver_contract_declared": True,
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
        "q18o_validation_invoked_by_mount": False,
        "q18n_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
    }


def build_latest_prediction_summary_widget_one_source_resolver_contract_preflight_rows(*, supplied_design_checkpoint_report: Mapping[str, Any] | Any | None = None) -> list[dict[str, Any]]:
    report = _as_mapping(supplied_design_checkpoint_report)
    return [
        _row("contract_source_candidate_count", "1", "Exactly one candidate is accepted by this resolver contract preflight."),
        _row("resolver_widget_family_id", WIDGET_FAMILY_ID, "Resolver contract is scoped to latest_prediction_summary_widget only."),
        _row("resolver_source_packet_id", SOURCE_PACKET_ID, "Resolver contract is scoped to latest_prediction_source_review_packet only."),
        _row("resolver_candidate_generated_at", report.get("selected_candidate_generated_at"), "Candidate generated_at copied from supplied PS-Q18O report only."),
        _row("resolver_candidate_source_artifact_ref", report.get("selected_candidate_source_artifact_ref"), "Candidate source artifact ref copied from supplied PS-Q18O report only; not resolved."),
        _row("resolver_candidate_market_uid", report.get("selected_candidate_market_uid"), "Candidate market uid copied from supplied PS-Q18O report only."),
        _row("resolver_input_ref_kind", "artifact_ref_string_only", "Resolver input kind is declared; no path materialization is allowed."),
        _row("resolver_output_contract", "would_output_candidate_path_later=false; would_output_payload_later=false", "Future resolver output shape is named, but no output is produced in this slice."),
        _row("explicit_resolver_contract_ack", ONE_SOURCE_RESOLVER_CONTRACT_ACK, "Design-only acknowledgement; not an approval for resolution or read."),
        _row("deferred_runtime_boundary", "resolver_invoked=false; path_materialized=false; exists_check=false; schema_check=false; actual_read=false", "All resolver/runtime behavior remains deferred."),
    ]


def build_latest_prediction_summary_widget_one_source_resolver_contract_preflight_packet(*, supplied_design_checkpoint_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    report = _as_mapping(supplied_design_checkpoint_report)
    rows = build_latest_prediction_summary_widget_one_source_resolver_contract_preflight_rows(supplied_design_checkpoint_report=report)
    failures: list[str] = []
    if len(rows) != 10:
        failures.append("resolver_contract_row_count_mismatch")
    for row in rows:
        item = str(row.get("resolver_contract_item") or "")
        if item not in RESOLVER_CONTRACT_ITEMS:
            failures.append(f"unexpected_resolver_contract_item:{item}")
        for key in ("read_only", "non_executing", "one_source_resolver_contract_preflight_only", "source_candidate_count_fixed_to_one", "resolver_contract_declared"):
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
            "q18o_validation_invoked_by_mount",
            "q18n_validation_invoked_by_mount",
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
    return {
        "ok": not failures,
        "resolver_contract_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_VERSION,
        "source_design_checkpoint_version": LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_VERSION,
        "source_design_ack": ONE_SOURCE_HANDOFF_DESIGN_ACK,
        "widget_family_id": WIDGET_FAMILY_ID,
        "source_packet_id": SOURCE_PACKET_ID,
        "one_source_resolver_contract_ack": ONE_SOURCE_RESOLVER_CONTRACT_ACK,
        "resolver_contract_state": "latest_prediction_summary_widget_one_source_resolver_contract_declared_no_resolution_read_or_render",
        "resolver_contract_row_count": len(rows),
        "resolver_contract_rows": rows,
        "validation_failures": failures,
        "supplied_design_checkpoint_report": supplied,
        "resolver_contract_candidate_ready": candidate_ready,
        "one_source_candidate_preserved": True,
        "source_candidate_count": 1,
        "resolver_input_ref_kind": "artifact_ref_string_only",
        "selected_candidate_generated_at": _clean(report.get("selected_candidate_generated_at")) if report else "",
        "selected_candidate_source_artifact_ref": _clean(report.get("selected_candidate_source_artifact_ref")) if report else "",
        "selected_candidate_market_uid": _clean(report.get("selected_candidate_market_uid")) if report else "",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_one_source_resolver_contract_preflight_only": True,
        "one_source_resolver_contract_preflight_ready": True,
        "resolver_contract_declared": True,
        "source_candidate_count_fixed_to_one": True,
        "explicit_resolver_contract_ack_matched": True,
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
