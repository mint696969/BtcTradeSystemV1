# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_overview.py
# desc: Verify dashboard hub display source overview is read-only, reusable, and layout-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_overview import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT,
    dashboard_hub_display_source_overview,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT["overview_type"] == "dashboard_hub_display_source_overview"
    assert DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT["dashboard_role"] == "hub"
    assert DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT["read_only_contract"] is True
    assert DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT["widget_reusable"] is True
    assert DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT["layout_decision_free"] is True
    assert DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_OVERVIEW_CONTRACT["not_ui_rendering"] is True

    overview = dashboard_hub_display_source_overview(
        {
            "registry_type": "dashboard_hub_display_source_registry",
            "page_entries": (
                {
                    "page_key": "collector",
                    "consumer_scope": "collector_tab",
                    "source_keys": ("summary_widget",),
                    "source_count": 1,
                },
                {
                    "page_key": "research",
                    "consumer_scope": "future_widget",
                    "source_keys": ("summary_widget", "review_hint_display"),
                    "source_count": 2,
                },
            ),
        }
    )
    assert overview["overview_type"] == "dashboard_hub_display_source_overview"
    assert overview["registry_type"] == "dashboard_hub_display_source_registry"
    assert overview["page_count"] == 2
    assert overview["page_keys"] == ("collector", "research")
    assert overview["source_keys"] == ("review_hint_display", "summary_widget")
    assert overview["overview_lines"] == (
        "collector:collector_tab:1:summary_widget",
        "research:future_widget:2:summary_widget,review_hint_display",
    )
    assert overview["hot_cold_status_label"] == "catalog_ready_payload_not_opened"
    assert overview["hot_cold_metadata_detail_status"] == "ready_for_dashboard_hub_display_source_overview"
    assert overview["hot_cold_status"]["readiness_detail_row_count"] == 11
    assert overview["hot_cold_unopened_boundary_statuses"]["payload_loader"] == "not_opened"
    assert overview["hot_cold_unopened_boundary_statuses"]["dataset_reader"] == "not_opened"
    assert overview["hot_cold_unopened_boundary_statuses"]["dashboard_rendering"] == "not_opened"
    assert overview["hot_cold_unopened_boundary_statuses"]["copy_executor"] == "not_opened"
    assert overview["hot_cold_status"]["next_opening_gate"]["gate_type"] == "explicit_entry_criteria_required"
    assert overview["compact_line"].startswith("dashboard_hub_sources=")
    assert "review_hint_display" in overview["compact_line"]
    assert "hot_cold_overview_status=" in overview["compact_line"]
    assert overview["read_only_contract"] is True
    assert overview["widget_reusable"] is True
    assert overview["layout_decision_free"] is True
    assert overview["not_runtime_wiring"] is True
    assert overview["not_ui_rendering"] is True

    real_overview = dashboard_hub_display_source_overview()
    assert real_overview["page_count"] >= 3
    assert "collector" in real_overview["page_keys"]
    assert "summary_widget" in real_overview["source_keys"]
    assert "review_hint_display" in real_overview["source_keys"]
    assert "hot_cold_duplicate_safe_dataset_view_model" in real_overview["source_keys"]
    assert real_overview["hot_cold_status_label"] == "catalog_ready_payload_not_opened"
    assert real_overview["hot_cold_metadata_detail_status"] == "ready_for_dashboard_hub_display_source_overview"
    assert real_overview["hot_cold_unopened_boundary_statuses"]["payload_loader"] == "not_opened"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
