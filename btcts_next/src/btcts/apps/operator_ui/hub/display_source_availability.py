# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_availability.py
# desc: Dashboard hub display source availability/status read model. No rendering/layout/runtime wiring.

from __future__ import annotations

from btcts.apps.operator_ui.hub.display_source_overview import (
    dashboard_hub_display_source_overview,
)
from btcts.apps.operator_ui.hub.display_source_registry import (
    load_dashboard_hub_display_source_registry,
)

DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT = {
    "availability_type": "dashboard_hub_display_source_availability",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
}


def _page_keys_for_source(entries: tuple[dict, ...], source_key: str) -> tuple[str, ...]:
    page_keys: list[str] = []
    for entry in entries:
        if source_key not in tuple(str(key) for key in (entry.get("source_keys") or ()) if key):
            continue
        page_key = str(entry.get("page_key") or "unknown")
        page_keys.append(page_key)
    return tuple(page_keys)


def _catalog_sources(registry: dict) -> tuple[dict, ...]:
    catalog = registry.get("source_catalog") or {}
    sources = catalog.get("sources") or ()
    return tuple(dict(item) for item in sources if isinstance(item, dict))


def _source_status(item: dict, entries: tuple[dict, ...]) -> dict:
    source_key = str(item.get("source_key") or "unknown")
    page_keys = _page_keys_for_source(entries, source_key)
    consumer_scope = tuple(str(scope) for scope in (item.get("consumer_scope") or ()) if scope)
    return {
        "source_key": source_key,
        "source_type": str(item.get("source_type") or "unknown"),
        "source_origin": str(item.get("source_origin") or "unknown"),
        "consumer_scope": consumer_scope,
        "page_keys": page_keys,
        "page_count": len(page_keys),
        "catalog_present": True,
        "referenced_by_page": bool(page_keys),
        "available_for_future_widget": "future_widget" in consumer_scope,
        "read_only_contract": item.get("read_only_contract") is True,
        "widget_reusable": item.get("widget_reusable") is True,
        "layout_decision_free": item.get("layout_decision_free") is True,
        "not_runtime_wiring": item.get("not_runtime_wiring") is True,
        "not_ui_rendering": item.get("not_ui_rendering") is True,
        "status": "referenced" if page_keys else "catalog_only",
    }


def dashboard_hub_display_source_availability(
    registry: dict | None = None,
    overview: dict | None = None,
) -> dict:
    payload = registry or load_dashboard_hub_display_source_registry()
    entries = tuple(entry for entry in (payload.get("page_entries") or ()) if isinstance(entry, dict))
    overview_payload = overview or dashboard_hub_display_source_overview(payload)
    catalog_sources = _catalog_sources(payload)
    catalog_keys = tuple(str(item.get("source_key") or "unknown") for item in catalog_sources)
    referenced_keys = tuple(str(key) for key in (overview_payload.get("source_keys") or ()) if key)
    missing_references = tuple(sorted(set(referenced_keys) - set(catalog_keys)))
    statuses = tuple(_source_status(item, entries) for item in catalog_sources)
    future_widget_source_keys = tuple(
        status["source_key"] for status in statuses if status["available_for_future_widget"]
    )
    compact_parts = tuple(
        f"{status['source_key']}:{status['status']}:{','.join(status['page_keys']) or 'none'}"
        for status in statuses
    )
    return {
        **DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT,
        "registry_type": payload.get("registry_type"),
        "overview_type": overview_payload.get("overview_type"),
        "source_count": len(statuses),
        "referenced_source_count": sum(1 for status in statuses if status["referenced_by_page"]),
        "future_widget_source_keys": future_widget_source_keys,
        "missing_references": missing_references,
        "source_statuses": statuses,
        "compact_line": "dashboard_hub_source_availability=" + ";".join(compact_parts),
    }
