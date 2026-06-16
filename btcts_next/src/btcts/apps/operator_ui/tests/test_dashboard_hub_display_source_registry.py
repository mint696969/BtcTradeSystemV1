# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_registry.py
# desc: Verify dashboard hub display source registry stays read-only and layout-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_registry import (  # noqa: E402
    DASHBOARD_HUB_PAGE_KEYS,
    DASHBOARD_HUB_REGISTRY_CONTRACT,
    PAGE_TO_CONSUMER_SCOPE,
    display_source_keys_for_page,
    load_dashboard_hub_display_source_registry,
)


def main() -> int:
    assert DASHBOARD_HUB_PAGE_KEYS == (
        "collector",
        "warroom",
        "health",
        "logs",
        "config",
        "research",
        "replay",
    )
    assert PAGE_TO_CONSUMER_SCOPE["collector"] == "collector_tab"
    assert PAGE_TO_CONSUMER_SCOPE["warroom"] == "warroom_tab"
    assert PAGE_TO_CONSUMER_SCOPE["health"] == "health_tab"
    assert DASHBOARD_HUB_REGISTRY_CONTRACT["dashboard_role"] == "hub"
    assert DASHBOARD_HUB_REGISTRY_CONTRACT["read_only_contract"] is True
    assert DASHBOARD_HUB_REGISTRY_CONTRACT["widget_reusable"] is True
    assert DASHBOARD_HUB_REGISTRY_CONTRACT["layout_decision_free"] is True
    assert DASHBOARD_HUB_REGISTRY_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_REGISTRY_CONTRACT["not_ui_rendering"] is True

    registry = load_dashboard_hub_display_source_registry()
    assert registry["registry_type"] == "dashboard_hub_display_source_registry"
    assert registry["dashboard_role"] == "hub"
    assert registry["catalog_type"] == "operator_dashboard_display_source_catalog"
    assert registry["page_keys"] == DASHBOARD_HUB_PAGE_KEYS
    assert len(registry["page_entries"]) == len(DASHBOARD_HUB_PAGE_KEYS)
    assert all(entry["read_only_contract"] is True for entry in registry["page_entries"])
    assert all(entry["widget_reusable"] is True for entry in registry["page_entries"])
    assert all(entry["layout_decision_free"] is True for entry in registry["page_entries"])
    assert all(entry["not_runtime_wiring"] is True for entry in registry["page_entries"])
    assert all(entry["not_ui_rendering"] is True for entry in registry["page_entries"])

    collector_keys = display_source_keys_for_page("collector", registry)
    warroom_keys = display_source_keys_for_page("warroom", registry)
    health_keys = display_source_keys_for_page("health", registry)
    research_keys = display_source_keys_for_page("research", registry)

    assert "summary_widget" in collector_keys
    assert "summary_widget" in warroom_keys
    assert "summary_widget" in health_keys
    assert research_keys
    assert "review_hint_display" in research_keys
    assert display_source_keys_for_page("unknown", registry) == ()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
