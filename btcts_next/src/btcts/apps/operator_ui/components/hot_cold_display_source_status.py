# path: ./btcts_next/src/btcts/apps/operator_ui/components/hot_cold_display_source_status.py
# desc: Hot/Cold dashboard display source read-only status model. No payload loader/rendering/file reader/copy/delete.

from __future__ import annotations

from btcts.apps.operator_ui.components.hot_cold_display_sources import (
    hot_cold_display_source_catalog_summary,
    load_hot_cold_display_source_catalog,
)

HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT = {
    "status_type": "hot_cold_dashboard_display_source_status",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "not_dataset_reader": True,
    "not_payload_loader": True,
    "not_simulation_connector": True,
    "not_training_connector": True,
    "not_copy_executor": True,
    "not_delete_executor": True,
    "not_archive_gc_enablement": True,
}


def _find_source(source_key: str) -> dict:
    for item in load_hot_cold_display_source_catalog():
        if item.get("source_key") == source_key:
            return dict(item)
    return {}


def _readiness_detail_rows(readiness_flags: dict) -> tuple[dict, ...]:
    ordered = (
        ("catalog_present", "catalog", "ready", "catalog metadata is registered"),
        ("schema_version_known", "schema", "ready", "schema version is known"),
        ("logical_identity_known", "identity", "ready", "logical identity is known"),
        ("payload_loader_opened", "payload_loader", "not_opened", "payload loader remains unopened"),
        ("dataset_reader_opened", "dataset_reader", "not_opened", "dataset reader remains unopened"),
        ("dashboard_rendering_opened", "dashboard_rendering", "not_opened", "dashboard rendering remains unopened"),
        ("simulation_connector_opened", "simulation_connector", "not_opened", "simulation connector remains unopened"),
        ("training_connector_opened", "training_connector", "not_opened", "training connector remains unopened"),
        ("copy_executor_opened", "copy_executor", "not_opened", "copy executor remains unopened"),
        ("delete_executor_opened", "delete_executor", "not_opened", "delete executor remains unopened"),
        ("archive_gc_enablement_opened", "archive_gc_enablement", "not_opened", "archive GC enablement remains unopened"),
    )
    rows: list[dict] = []
    for flag_key, boundary, expected_state, note in ordered:
        value = bool(readiness_flags.get(flag_key))
        if expected_state == "ready":
            actual_state = "ready" if value else "missing"
        else:
            actual_state = "opened" if value else "not_opened"
        rows.append(
            {
                "flag_key": flag_key,
                "boundary": boundary,
                "expected_state": expected_state,
                "actual_state": actual_state,
                "ok": actual_state == expected_state,
                "note": note,
            }
        )
    return tuple(rows)


def _unopened_boundary_statuses(readiness_flags: dict) -> dict:
    boundary_keys = {
        "payload_loader": "payload_loader_opened",
        "dataset_reader": "dataset_reader_opened",
        "dashboard_rendering": "dashboard_rendering_opened",
        "simulation_connector": "simulation_connector_opened",
        "training_connector": "training_connector_opened",
        "copy_executor": "copy_executor_opened",
        "delete_executor": "delete_executor_opened",
        "archive_gc_enablement": "archive_gc_enablement_opened",
    }
    return {
        boundary: ("opened" if bool(readiness_flags.get(flag_key)) else "not_opened")
        for boundary, flag_key in boundary_keys.items()
    }


def hot_cold_duplicate_safe_dataset_view_source_status() -> dict:
    """Return catalog/status metadata only; does not load dataset payloads or render UI."""
    source_key = "hot_cold_duplicate_safe_dataset_view_model"
    source = _find_source(source_key)
    catalog_summary = hot_cold_display_source_catalog_summary()
    catalog_present = bool(source)
    readiness_flags = {
        "catalog_present": catalog_present,
        "schema_version_known": source.get("schema_version") == "hot_cold_duplicate_safe_dataset_view_v1",
        "logical_identity_known": source.get("logical_identity") == "exchange:symbol:rel_file",
        "payload_loader_opened": False,
        "dashboard_rendering_opened": False,
        "dataset_reader_opened": False,
        "simulation_connector_opened": False,
        "training_connector_opened": False,
        "copy_executor_opened": False,
        "delete_executor_opened": False,
        "archive_gc_enablement_opened": False,
    }
    status_label = "catalog_ready_payload_not_opened" if all(
        value is True for key, value in readiness_flags.items() if key in ("catalog_present", "schema_version_known", "logical_identity_known")
    ) else "catalog_review"
    readiness_detail_rows = _readiness_detail_rows(readiness_flags)
    unopened_boundary_statuses = _unopened_boundary_statuses(readiness_flags)
    next_opening_gate = {
        "gate_type": "explicit_entry_criteria_required",
        "payload_loader_allowed": False,
        "dataset_reader_allowed": False,
        "dashboard_rendering_allowed": False,
        "copy_delete_gc_allowed": False,
        "app_py_wiring_allowed": False,
        "reason": "status model is metadata-only and must not open payload/reader/rendering/executor boundaries",
    }
    return {
        **HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT,
        "source_key": source_key,
        "source_type": str(source.get("source_type") or "unknown"),
        "source_origin": str(source.get("source_origin") or "unknown"),
        "schema_version": str(source.get("schema_version") or "unknown"),
        "logical_identity": str(source.get("logical_identity") or "unknown"),
        "consumer_scope": tuple(str(scope) for scope in (source.get("consumer_scope") or ()) if scope),
        "catalog_type": catalog_summary.get("catalog_type"),
        "catalog_source_count": int(catalog_summary.get("source_count") or 0),
        "catalog_present": catalog_present,
        "payload_loader_status": "not_opened",
        "dashboard_rendering_status": "not_opened",
        "dataset_reader_status": "not_opened",
        "simulation_connector_status": "not_opened",
        "training_connector_status": "not_opened",
        "copy_delete_gc_status": "not_opened",
        "unopened_boundary_statuses": unopened_boundary_statuses,
        "readiness_flags": readiness_flags,
        "readiness_detail_rows": readiness_detail_rows,
        "next_opening_gate": next_opening_gate,
        "metadata_detail_status": "ready_for_dashboard_hub_display_source_overview",
        "status_label": status_label,
        "compact_line": (
            "hot_cold_source_status="
            f"source:{source_key};"
            f"status:{status_label};"
            "payload:not_opened;reader:not_opened;rendering:not_opened"
        ),
    }
