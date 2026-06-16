# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_registry.py
# desc: Dashboard hub 用 display source registry。描画・layout 決定をしない read-only catalog adapter。

from __future__ import annotations

from btcts.apps.operator_ui.components.operator_display_source_catalog import (
    load_operator_dashboard_display_source_catalog,
    select_display_sources_for_consumer,
)

DASHBOARD_HUB_PAGE_KEYS = (
    "collector",
    "warroom",
    "health",
    "logs",
    "config",
    "research",
    "replay",
)

PAGE_TO_CONSUMER_SCOPE = {
    "collector": "collector_tab",
    "warroom": "warroom_tab",
    "health": "health_tab",
    "logs": "future_widget",
    "config": "future_widget",
    "research": "future_widget",
    "replay": "future_widget",
}

DASHBOARD_HUB_REGISTRY_CONTRACT = {
    "registry_type": "dashboard_hub_display_source_registry",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
}


def load_dashboard_hub_display_source_registry() -> dict:
    catalog = load_operator_dashboard_display_source_catalog()
    page_entries: list[dict] = []
    for page_key in DASHBOARD_HUB_PAGE_KEYS:
        consumer_scope = PAGE_TO_CONSUMER_SCOPE.get(page_key, "future_widget")
        sources = select_display_sources_for_consumer(consumer_scope, catalog)
        page_entries.append(
            {
                "page_key": page_key,
                "consumer_scope": consumer_scope,
                "source_keys": tuple(item.get("source_key") for item in sources),
                "source_count": len(sources),
                "read_only_contract": True,
                "widget_reusable": True,
                "layout_decision_free": True,
                "not_runtime_wiring": True,
                "not_ui_rendering": True,
            }
        )
    return {
        **DASHBOARD_HUB_REGISTRY_CONTRACT,
        "catalog_type": catalog.get("catalog_type"),
        "page_keys": DASHBOARD_HUB_PAGE_KEYS,
        "page_entries": tuple(page_entries),
        "source_catalog": catalog,
    }


def display_source_keys_for_page(page_key: str, registry: dict | None = None) -> tuple[str, ...]:
    payload = registry or load_dashboard_hub_display_source_registry()
    for entry in payload.get("page_entries") or ():
        if isinstance(entry, dict) and entry.get("page_key") == page_key:
            return tuple(str(key) for key in (entry.get("source_keys") or ()) if key)
    return ()
