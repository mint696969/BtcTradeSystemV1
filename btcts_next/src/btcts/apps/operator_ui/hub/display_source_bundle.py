# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_bundle.py
# desc: Dashboard hub display source read-only bundle facade. No rendering/layout/runtime wiring.

from __future__ import annotations

from btcts.apps.operator_ui.hub.display_source_availability import (
    dashboard_hub_display_source_availability,
)
from btcts.apps.operator_ui.hub.display_source_coverage import (
    dashboard_hub_display_source_coverage,
)
from btcts.apps.operator_ui.hub.display_source_matrix import (
    dashboard_hub_display_source_matrix,
)
from btcts.apps.operator_ui.hub.display_source_overview import (
    dashboard_hub_display_source_overview,
)
from btcts.apps.operator_ui.hub.display_source_registry import (
    load_dashboard_hub_display_source_registry,
)

DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT = {
    "bundle_type": "dashboard_hub_display_source_bundle",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
}


def _hot_cold_bundle_summary(overview: dict) -> dict:
    status = overview.get("hot_cold_status") if isinstance(overview.get("hot_cold_status"), dict) else {}
    unopened = overview.get("hot_cold_unopened_boundary_statuses")
    if not isinstance(unopened, dict):
        unopened = status.get("unopened_boundary_statuses") if isinstance(status.get("unopened_boundary_statuses"), dict) else {}
    return {
        "source_key": status.get("source_key") or "hot_cold_duplicate_safe_dataset_view_model",
        "status_label": overview.get("hot_cold_status_label") or status.get("status_label") or "unknown",
        "metadata_detail_status": overview.get("hot_cold_metadata_detail_status") or status.get("metadata_detail_status") or "unknown",
        "payload_loader_status": str(unopened.get("payload_loader") or "unknown"),
        "dataset_reader_status": str(unopened.get("dataset_reader") or "unknown"),
        "dashboard_rendering_status": str(unopened.get("dashboard_rendering") or "unknown"),
        "copy_executor_status": str(unopened.get("copy_executor") or "unknown"),
        "delete_executor_status": str(unopened.get("delete_executor") or "unknown"),
        "archive_gc_enablement_status": str(unopened.get("archive_gc_enablement") or "unknown"),
        "readiness_detail_row_count": int(status.get("readiness_detail_row_count") or 0),
        "compact_line": (
            "hot_cold_bundle_summary="
            f"status:{overview.get('hot_cold_status_label') or status.get('status_label') or 'unknown'};"
            f"metadata:{overview.get('hot_cold_metadata_detail_status') or status.get('metadata_detail_status') or 'unknown'};"
            f"payload:{unopened.get('payload_loader') or 'unknown'};"
            f"reader:{unopened.get('dataset_reader') or 'unknown'};"
            f"rendering:{unopened.get('dashboard_rendering') or 'unknown'}"
        ),
    }


def dashboard_hub_display_source_bundle() -> dict:
    registry = load_dashboard_hub_display_source_registry()
    overview = dashboard_hub_display_source_overview(registry)
    availability = dashboard_hub_display_source_availability(registry, overview)
    matrix = dashboard_hub_display_source_matrix(registry, availability)
    coverage = dashboard_hub_display_source_coverage(matrix)
    page_keys = tuple(str(key) for key in (matrix.get("page_keys") or ()) if key)
    source_keys = tuple(str(key) for key in (matrix.get("source_keys") or ()) if key)
    hot_cold_summary = _hot_cold_bundle_summary(overview)
    guardrail_flags = {
        "registry_read_only": registry.get("read_only_contract") is True,
        "overview_read_only": overview.get("read_only_contract") is True,
        "availability_read_only": availability.get("read_only_contract") is True,
        "matrix_read_only": matrix.get("read_only_contract") is True,
        "coverage_read_only": coverage.get("read_only_contract") is True,
        "layout_decision_free": all(
            payload.get("layout_decision_free") is True
            for payload in (registry, overview, availability, matrix, coverage)
        ),
        "not_runtime_wiring": all(
            payload.get("not_runtime_wiring") is True
            for payload in (registry, overview, availability, matrix, coverage)
        ),
        "not_ui_rendering": all(
            payload.get("not_ui_rendering") is True
            for payload in (registry, overview, availability, matrix, coverage)
        ),
    }
    return {
        **DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT,
        "registry": registry,
        "overview": overview,
        "availability": availability,
        "matrix": matrix,
        "coverage": coverage,
        "page_count": len(page_keys),
        "source_count": len(source_keys),
        "page_keys": page_keys,
        "source_keys": source_keys,
        "coverage_ok": coverage.get("coverage_ok") is True,
        "missing_references": tuple(coverage.get("missing_references") or ()),
        "empty_page_keys": tuple(coverage.get("empty_page_keys") or ()),
        "orphan_source_keys": tuple(coverage.get("orphan_source_keys") or ()),
        "guardrail_flags": guardrail_flags,
        "hot_cold_summary": hot_cold_summary,
        "hot_cold_status_label": hot_cold_summary.get("status_label"),
        "hot_cold_metadata_detail_status": hot_cold_summary.get("metadata_detail_status"),
        "compact_line": (
            "dashboard_hub_source_bundle="
            f"pages:{len(page_keys)};sources:{len(source_keys)};"
            f"coverage_ok:{coverage.get('coverage_ok') is True};"
            f"missing:{','.join(tuple(coverage.get('missing_references') or ())) or 'none'};"
            f"{hot_cold_summary.get('compact_line') or ''}"
        ),
    }
