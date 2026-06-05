# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_overview.py
# desc: Dashboard hub display source registry の read-only overview presenter。描画・layout 決定はしない。

from __future__ import annotations

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
    return {
        **DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT,
        "registry_type": payload.get("registry_type"),
        "page_count": len(entries),
        "page_keys": page_keys,
        "source_keys": source_keys,
        "overview_lines": lines,
        "compact_line": "dashboard_hub_sources=" + ";".join(lines),
    }
