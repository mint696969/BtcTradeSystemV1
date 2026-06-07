# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_dashboard_display_source_status.py
# desc: Verify Hot/Cold display source status is metadata-only and keeps payload/rendering/reader unopened.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.hot_cold_display_source_status import (  # noqa: E402
    HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT,
    hot_cold_duplicate_safe_dataset_view_source_status,
)


def main() -> int:
    assert HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT["status_type"] == "hot_cold_dashboard_display_source_status"
    assert HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT["read_only_contract"] is True
    assert HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT["not_payload_loader"] is True
    assert HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT["not_dataset_reader"] is True
    assert HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT["not_ui_rendering"] is True
    assert HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT["not_copy_executor"] is True
    assert HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT["not_delete_executor"] is True
    assert HOT_COLD_DISPLAY_SOURCE_STATUS_CONTRACT["not_archive_gc_enablement"] is True

    status = hot_cold_duplicate_safe_dataset_view_source_status()
    assert status["status_type"] == "hot_cold_dashboard_display_source_status"
    assert status["source_key"] == "hot_cold_duplicate_safe_dataset_view_model"
    assert status["source_type"] == "hot_cold_duplicate_safe_dataset_view_read_only_model"
    assert status["source_origin"] == "hot_cold_display_sources"
    assert status["schema_version"] == "hot_cold_duplicate_safe_dataset_view_v1"
    assert status["logical_identity"] == "exchange:symbol:rel_file"
    assert status["catalog_type"] == "hot_cold_display_source_catalog"
    assert status["catalog_source_count"] == 1
    assert status["catalog_present"] is True
    assert status["payload_loader_status"] == "not_opened"
    assert status["dashboard_rendering_status"] == "not_opened"
    assert status["dataset_reader_status"] == "not_opened"
    assert status["simulation_connector_status"] == "not_opened"
    assert status["training_connector_status"] == "not_opened"
    assert status["copy_delete_gc_status"] == "not_opened"
    assert status["metadata_detail_status"] == "ready_for_dashboard_hub_display_source_overview"
    assert status["status_label"] == "catalog_ready_payload_not_opened"
    assert status["compact_line"].startswith("hot_cold_source_status=")

    unopened = status["unopened_boundary_statuses"]
    assert unopened["payload_loader"] == "not_opened"
    assert unopened["dataset_reader"] == "not_opened"
    assert unopened["dashboard_rendering"] == "not_opened"
    assert unopened["copy_executor"] == "not_opened"
    assert unopened["delete_executor"] == "not_opened"
    assert unopened["archive_gc_enablement"] == "not_opened"

    detail_rows = status["readiness_detail_rows"]
    assert len(detail_rows) == 11
    assert all(row["ok"] is True for row in detail_rows)
    assert {row["boundary"] for row in detail_rows} >= {
        "catalog",
        "schema",
        "identity",
        "payload_loader",
        "dataset_reader",
        "dashboard_rendering",
        "copy_executor",
        "delete_executor",
        "archive_gc_enablement",
    }

    gate = status["next_opening_gate"]
    assert gate["gate_type"] == "explicit_entry_criteria_required"
    assert gate["payload_loader_allowed"] is False
    assert gate["dataset_reader_allowed"] is False
    assert gate["dashboard_rendering_allowed"] is False
    assert gate["copy_delete_gc_allowed"] is False
    assert gate["app_py_wiring_allowed"] is False

    flags = status["readiness_flags"]
    assert flags["catalog_present"] is True
    assert flags["schema_version_known"] is True
    assert flags["logical_identity_known"] is True
    assert flags["payload_loader_opened"] is False
    assert flags["dashboard_rendering_opened"] is False
    assert flags["dataset_reader_opened"] is False
    assert flags["simulation_connector_opened"] is False
    assert flags["training_connector_opened"] is False
    assert flags["copy_executor_opened"] is False
    assert flags["delete_executor_opened"] is False
    assert flags["archive_gc_enablement_opened"] is False

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
