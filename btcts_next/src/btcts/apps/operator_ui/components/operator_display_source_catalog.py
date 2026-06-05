# path: ./btcts_next/src/btcts/apps/operator_ui/components/operator_display_source_catalog.py
# desc: Operator dashboard hub 用の read-only display source catalog facade。

from __future__ import annotations

from typing import Iterable

from btcts.apps.operator_ui.components.ai_operator_display_sources import (
    load_operator_display_source_catalog as load_ai_operator_display_source_catalog,
)

OPERATOR_DASHBOARD_HUB_CONTRACT = {
    "catalog_type": "operator_dashboard_display_source_catalog",
    "dashboard_role": "hub",
    "current_tab_layout_is_temporary": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "read_only_contract": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
}


def _with_origin(items: Iterable[dict], origin: str) -> tuple[dict, ...]:
    out: list[dict] = []
    for item in items:
        normalized = dict(item)
        normalized.setdefault("source_origin", origin)
        normalized.setdefault("read_only_contract", True)
        normalized.setdefault("widget_reusable", True)
        normalized.setdefault("layout_decision_free", True)
        normalized.setdefault("not_runtime_wiring", True)
        normalized.setdefault("not_ui_rendering", True)
        out.append(normalized)
    return tuple(out)


def load_operator_dashboard_display_source_catalog() -> dict:
    sources = _with_origin(
        load_ai_operator_display_source_catalog(),
        "ai_operator_display_sources",
    )
    return {
        **OPERATOR_DASHBOARD_HUB_CONTRACT,
        "sources": sources,
        "source_count": len(sources),
        "source_keys": tuple(item.get("source_key") for item in sources),
    }


def select_display_sources_for_consumer(consumer: str, catalog: dict | None = None) -> tuple[dict, ...]:
    payload = catalog or load_operator_dashboard_display_source_catalog()
    sources = payload.get("sources") or ()
    selected: list[dict] = []
    for item in sources:
        if not isinstance(item, dict):
            continue
        scopes = item.get("consumer_scope") or ()
        if consumer in scopes or "future_widget" in scopes:
            selected.append(dict(item))
    return tuple(selected)
