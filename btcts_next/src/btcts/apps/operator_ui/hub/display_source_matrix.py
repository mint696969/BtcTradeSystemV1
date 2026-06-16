# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_matrix.py
# desc: Dashboard hub display source/page cross-reference matrix. No rendering/layout/runtime wiring.

from __future__ import annotations

from btcts.apps.operator_ui.hub.display_source_availability import (
    dashboard_hub_display_source_availability,
)
from btcts.apps.operator_ui.hub.display_source_registry import (
    load_dashboard_hub_display_source_registry,
)

DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT = {
    "matrix_type": "dashboard_hub_display_source_matrix",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
}


def _page_entries(registry: dict) -> tuple[dict, ...]:
    return tuple(entry for entry in (registry.get("page_entries") or ()) if isinstance(entry, dict))


def _source_statuses(availability: dict) -> tuple[dict, ...]:
    return tuple(item for item in (availability.get("source_statuses") or ()) if isinstance(item, dict))


def _page_matrix_rows(entries: tuple[dict, ...], source_keys: tuple[str, ...]) -> tuple[dict, ...]:
    rows: list[dict] = []
    for entry in entries:
        page_key = str(entry.get("page_key") or "unknown")
        consumer_scope = str(entry.get("consumer_scope") or "unknown")
        entry_source_keys = tuple(str(key) for key in (entry.get("source_keys") or ()) if key)
        source_presence = {source_key: source_key in entry_source_keys for source_key in source_keys}
        rows.append(
            {
                "page_key": page_key,
                "consumer_scope": consumer_scope,
                "source_keys": entry_source_keys,
                "source_count": len(entry_source_keys),
                "source_presence": source_presence,
                "read_only_contract": entry.get("read_only_contract") is True,
                "widget_reusable": entry.get("widget_reusable") is True,
                "layout_decision_free": entry.get("layout_decision_free") is True,
                "not_runtime_wiring": entry.get("not_runtime_wiring") is True,
                "not_ui_rendering": entry.get("not_ui_rendering") is True,
            }
        )
    return tuple(rows)


def _source_matrix_rows(statuses: tuple[dict, ...], page_keys: tuple[str, ...]) -> tuple[dict, ...]:
    rows: list[dict] = []
    for status in statuses:
        source_key = str(status.get("source_key") or "unknown")
        status_page_keys = tuple(str(key) for key in (status.get("page_keys") or ()) if key)
        page_presence = {page_key: page_key in status_page_keys for page_key in page_keys}
        rows.append(
            {
                "source_key": source_key,
                "source_type": str(status.get("source_type") or "unknown"),
                "source_origin": str(status.get("source_origin") or "unknown"),
                "page_keys": status_page_keys,
                "page_count": len(status_page_keys),
                "page_presence": page_presence,
                "available_for_future_widget": status.get("available_for_future_widget") is True,
                "status": str(status.get("status") or "unknown"),
                "read_only_contract": status.get("read_only_contract") is True,
                "widget_reusable": status.get("widget_reusable") is True,
                "layout_decision_free": status.get("layout_decision_free") is True,
                "not_runtime_wiring": status.get("not_runtime_wiring") is True,
                "not_ui_rendering": status.get("not_ui_rendering") is True,
            }
        )
    return tuple(rows)


def _compact_line(page_rows: tuple[dict, ...], source_rows: tuple[dict, ...]) -> str:
    page_parts = tuple(
        f"{row['page_key']}:{','.join(row['source_keys']) or 'none'}"
        for row in page_rows
    )
    source_parts = tuple(
        f"{row['source_key']}:{','.join(row['page_keys']) or 'none'}"
        for row in source_rows
    )
    return "dashboard_hub_source_matrix=pages[" + ";".join(page_parts) + "] sources[" + ";".join(source_parts) + "]"


def dashboard_hub_display_source_matrix(
    registry: dict | None = None,
    availability: dict | None = None,
) -> dict:
    registry_payload = registry or load_dashboard_hub_display_source_registry()
    availability_payload = availability or dashboard_hub_display_source_availability(registry_payload)
    entries = _page_entries(registry_payload)
    statuses = _source_statuses(availability_payload)
    page_keys = tuple(str(entry.get("page_key") or "unknown") for entry in entries)
    source_keys = tuple(str(status.get("source_key") or "unknown") for status in statuses)
    page_rows = _page_matrix_rows(entries, source_keys)
    source_rows = _source_matrix_rows(statuses, page_keys)
    return {
        **DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT,
        "registry_type": registry_payload.get("registry_type"),
        "availability_type": availability_payload.get("availability_type"),
        "page_count": len(page_rows),
        "source_count": len(source_rows),
        "page_keys": page_keys,
        "source_keys": source_keys,
        "page_rows": page_rows,
        "source_rows": source_rows,
        "missing_references": tuple(availability_payload.get("missing_references") or ()),
        "compact_line": _compact_line(page_rows, source_rows),
    }
