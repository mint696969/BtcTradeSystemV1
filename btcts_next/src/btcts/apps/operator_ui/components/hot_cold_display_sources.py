# path: ./btcts_next/src/btcts/apps/operator_ui/components/hot_cold_display_sources.py
# desc: Hot/Cold operational display source catalog entries. Catalog-only; no dataset reader/rendering/copy/delete.

from __future__ import annotations

HOT_COLD_DISPLAY_SOURCE_CATALOG = (
    {
        "source_key": "hot_cold_duplicate_safe_dataset_view_model",
        "source_type": "hot_cold_duplicate_safe_dataset_view_read_only_model",
        "consumer_scope": ("dashboard", "health_tab", "research", "future_widget"),
        "source_origin": "hot_cold_display_sources",
        "schema_version": "hot_cold_duplicate_safe_dataset_view_v1",
        "logical_identity": "exchange:symbol:rel_file",
        "read_only_contract": True,
        "widget_reusable": True,
        "layout_decision_free": True,
        "not_runtime_wiring": True,
        "not_ui_rendering": True,
        "not_dataset_reader": True,
        "not_simulation_connector": True,
        "not_training_connector": True,
        "not_copy_executor": True,
        "not_delete_executor": True,
        "not_archive_gc_enablement": True,
    },
)

HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT = {
    "catalog_type": "hot_cold_display_source_catalog",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "not_dataset_reader": True,
    "not_simulation_connector": True,
    "not_training_connector": True,
    "not_copy_executor": True,
    "not_delete_executor": True,
    "not_archive_gc_enablement": True,
}


def load_hot_cold_display_source_catalog() -> tuple[dict, ...]:
    """Return catalog entries only; does not load dataset view payloads or render UI."""
    return tuple(dict(item) for item in HOT_COLD_DISPLAY_SOURCE_CATALOG)


def hot_cold_display_source_catalog_summary() -> dict:
    sources = load_hot_cold_display_source_catalog()
    return {
        **HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT,
        "source_count": len(sources),
        "source_keys": tuple(str(item.get("source_key")) for item in sources),
        "compact_line": "hot_cold_display_sources=" + ",".join(str(item.get("source_key")) for item in sources),
    }
