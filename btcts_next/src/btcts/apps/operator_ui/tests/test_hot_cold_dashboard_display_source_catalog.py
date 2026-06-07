# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_dashboard_display_source_catalog.py
# desc: Verify Hot/Cold display source catalog is registered for dashboard hub without reader/rendering/copy/delete.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.hot_cold_display_sources import (  # noqa: E402
    HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT,
    hot_cold_display_source_catalog_summary,
    load_hot_cold_display_source_catalog,
)
from btcts.apps.operator_ui.components.operator_display_source_catalog import (  # noqa: E402
    load_operator_dashboard_display_source_catalog,
    select_display_sources_for_consumer,
)
from btcts.apps.operator_ui.hub.display_source_registry import (  # noqa: E402
    display_source_keys_for_page,
    load_dashboard_hub_display_source_registry,
)


def main() -> int:
    assert HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT["catalog_type"] == "hot_cold_display_source_catalog"
    assert HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT["read_only_contract"] is True
    assert HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT["not_dataset_reader"] is True
    assert HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT["not_ui_rendering"] is True
    assert HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT["not_copy_executor"] is True
    assert HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT["not_delete_executor"] is True
    assert HOT_COLD_DISPLAY_SOURCE_CATALOG_CONTRACT["not_archive_gc_enablement"] is True

    sources = load_hot_cold_display_source_catalog()
    assert len(sources) == 1
    source = sources[0]
    assert source["source_key"] == "hot_cold_duplicate_safe_dataset_view_model"
    assert source["source_type"] == "hot_cold_duplicate_safe_dataset_view_read_only_model"
    assert source["source_origin"] == "hot_cold_display_sources"
    assert source["schema_version"] == "hot_cold_duplicate_safe_dataset_view_v1"
    assert source["logical_identity"] == "exchange:symbol:rel_file"
    assert source["read_only_contract"] is True
    assert source["widget_reusable"] is True
    assert source["layout_decision_free"] is True
    assert source["not_runtime_wiring"] is True
    assert source["not_ui_rendering"] is True
    assert source["not_dataset_reader"] is True
    assert source["not_simulation_connector"] is True
    assert source["not_training_connector"] is True
    assert source["not_copy_executor"] is True
    assert source["not_delete_executor"] is True
    assert source["not_archive_gc_enablement"] is True

    summary = hot_cold_display_source_catalog_summary()
    assert summary["source_count"] == 1
    assert summary["source_keys"] == ("hot_cold_duplicate_safe_dataset_view_model",)
    assert summary["compact_line"].startswith("hot_cold_display_sources=")

    dashboard_catalog = load_operator_dashboard_display_source_catalog()
    assert dashboard_catalog["catalog_type"] == "operator_dashboard_display_source_catalog"
    assert "hot_cold_duplicate_safe_dataset_view_model" in dashboard_catalog["source_keys"]
    assert dashboard_catalog["source_count"] >= 6

    health_sources = select_display_sources_for_consumer("health_tab", dashboard_catalog)
    health_keys = tuple(item["source_key"] for item in health_sources)
    assert "hot_cold_duplicate_safe_dataset_view_model" in health_keys

    registry = load_dashboard_hub_display_source_registry()
    health_registry_keys = display_source_keys_for_page("health", registry)
    assert "hot_cold_duplicate_safe_dataset_view_model" in health_registry_keys
    assert registry["read_only_contract"] is True

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
