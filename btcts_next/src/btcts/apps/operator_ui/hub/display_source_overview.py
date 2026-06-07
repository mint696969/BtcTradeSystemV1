# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_overview.py
# desc: Dashboard hub display source registry の read-only overview presenter。描画・layout 決定はしない。

from __future__ import annotations

from btcts.apps.operator_ui.components.hot_cold_display_source_status import (
    hot_cold_duplicate_safe_dataset_view_source_status,
)
from btcts.apps.operator_ui.hub.display_source_registry import (
    load_dashboard_hub_display_source_registry,
)

DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT = {
    "overview_type": "dashboard_hub_display_source_overview",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
}


def _hot_cold_overview_status() -> dict:
    status = hot_cold_duplicate_safe_dataset_view_source_status()
    return {
        "source_key": status.get("source_key"),
        "status_label": status.get("status_label"),
        "metadata_detail_status": status.get("metadata_detail_status"),
        "payload_loader_status": status.get("payload_loader_status"),
        "dataset_reader_status": status.get("dataset_reader_status"),
        "dashboard_rendering_status": status.get("dashboard_rendering_status"),
        "copy_delete_gc_status": status.get("copy_delete_gc_status"),
        "unopened_boundary_statuses": dict(status.get("unopened_boundary_statuses") or {}),
        "readiness_detail_row_count": len(status.get("readiness_detail_rows") or ()),
        "next_opening_gate": dict(status.get("next_opening_gate") or {}),
        "compact_line": (
            "hot_cold_overview_status="
            f"source:{status.get('source_key')};"
            f"status:{status.get('status_label')};"
            f"metadata:{status.get('metadata_detail_status')}"
        ),
    }


def _entry_line(entry: dict) -> str:
    page_key = str(entry.get("page_key") or "unknown")
    consumer_scope = str(entry.get("consumer_scope") or "unknown")
    source_keys = tuple(str(key) for key in (entry.get("source_keys") or ()) if key)
    source_count = int(entry.get("source_count") or len(source_keys))
    source_part = ",".join(source_keys) if source_keys else "none"
    return f"{page_key}:{consumer_scope}:{source_count}:{source_part}"


def dashboard_hub_display_source_overview(registry: dict | None = None) -> dict:
    payload = registry or load_dashboard_hub_display_source_registry()
    entries = tuple(entry for entry in (payload.get("page_entries") or ()) if isinstance(entry, dict))
    lines = tuple(_entry_line(entry) for entry in entries)
    page_keys = tuple(str(entry.get("page_key") or "unknown") for entry in entries)
    source_keys = tuple(
        sorted(
            {
                str(source_key)
                for entry in entries
                for source_key in (entry.get("source_keys") or ())
                if source_key
            }
        )
    )
    hot_cold_status = _hot_cold_overview_status()
    return {
        **DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT,
        "registry_type": payload.get("registry_type"),
        "page_count": len(entries),
        "page_keys": page_keys,
        "source_keys": source_keys,
        "overview_lines": lines,
        "hot_cold_status": hot_cold_status,
        "hot_cold_status_label": hot_cold_status.get("status_label"),
        "hot_cold_metadata_detail_status": hot_cold_status.get("metadata_detail_status"),
        "hot_cold_unopened_boundary_statuses": hot_cold_status.get("unopened_boundary_statuses"),
        "compact_line": "dashboard_hub_sources=" + ";".join(lines) + ";" + str(hot_cold_status.get("compact_line") or ""),
    }
