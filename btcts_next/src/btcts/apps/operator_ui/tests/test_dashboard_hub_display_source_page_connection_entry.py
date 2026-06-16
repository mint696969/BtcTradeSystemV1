# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_page_connection_entry.py
# desc: Verify page connection entry criteria does not mutate app.py/page routing/layout/runtime.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_page_connection_entry import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT,
    dashboard_hub_display_source_page_connection_entry,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT["entry_type"] == "dashboard_hub_display_source_page_connection_entry"
    assert DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT["read_only_contract"] is True
    assert DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT["component_connection_planning"] is True
    assert DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT["not_app_py_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT["not_page_routing_mutation"] is True
    assert DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT["not_layout_decision"] is True
    assert DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT["not_broker_or_order_wiring"] is True

    entry = dashboard_hub_display_source_page_connection_entry()
    assert entry["page_connection_ready"] is True
    assert entry["selected_page_key"] == "health"
    assert entry["preferred_page_key"] == "health"
    assert "collector" in entry["connectable_page_keys"]
    assert "health" in entry["connectable_page_keys"]
    assert "research" in entry["connectable_page_keys"]
    assert entry["consumer_scope"] == "health_tab"
    assert entry["allowed_next_surface"] == "existing_view_component_call"
    assert entry["blocked_reasons"] == ()
    assert entry["app_py_wiring_allowed"] is False
    assert entry["page_routing_mutation_allowed"] is False
    assert entry["layout_decision_allowed"] is False
    assert entry["runtime_wiring_allowed"] is False
    assert entry["next_required_step"] == "create_guarded_existing_view_component_insertion_slice"
    assert entry["compact_line"].startswith("dashboard_hub_source_page_connection=")

    fallback = dashboard_hub_display_source_page_connection_entry(preferred_page="missing")
    assert fallback["page_connection_ready"] is True
    assert fallback["selected_page_key"] == "collector"
    assert fallback["consumer_scope"] == "collector_tab"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
