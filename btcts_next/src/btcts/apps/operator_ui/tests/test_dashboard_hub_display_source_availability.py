# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_availability.py
# desc: Verify dashboard hub display source availability stays read-only, reusable, and layout-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_availability import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT,
    dashboard_hub_display_source_availability,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT["availability_type"] == "dashboard_hub_display_source_availability"
    assert DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT["dashboard_role"] == "hub"
    assert DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT["read_only_contract"] is True
    assert DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT["widget_reusable"] is True
    assert DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT["layout_decision_free"] is True
    assert DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_AVAILABILITY_CONTRACT["not_ui_rendering"] is True

    registry = {
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
        "source_catalog": {
            "sources": (
                {
                    "source_key": "summary_widget",
                    "source_type": "market_summary_widget_model",
                    "source_origin": "ai_operator_display_sources",
                    "consumer_scope": ("collector_tab", "future_widget"),
                    "read_only_contract": True,
                    "widget_reusable": True,
                    "layout_decision_free": True,
                    "not_runtime_wiring": True,
                    "not_ui_rendering": True,
                },
                {
                    "source_key": "prediction_widget",
                    "source_type": "prediction_summary_widget_model",
                    "source_origin": "ai_operator_display_sources",
                    "consumer_scope": ("prediction_tab", "future_widget"),
                    "read_only_contract": True,
                    "widget_reusable": True,
                    "layout_decision_free": True,
                    "not_runtime_wiring": True,
                    "not_ui_rendering": True,
                },
            ),
        },
    }
    overview = {
        "overview_type": "dashboard_hub_display_source_overview",
        "source_keys": ("summary_widget", "review_hint_display"),
    }

    availability = dashboard_hub_display_source_availability(registry, overview)
    assert availability["availability_type"] == "dashboard_hub_display_source_availability"
    assert availability["registry_type"] == "dashboard_hub_display_source_registry"
    assert availability["overview_type"] == "dashboard_hub_display_source_overview"
    assert availability["source_count"] == 2
    assert availability["referenced_source_count"] == 1
    assert availability["future_widget_source_keys"] == ("summary_widget", "prediction_widget")
    assert availability["missing_references"] == ("review_hint_display",)
    assert availability["compact_line"].startswith("dashboard_hub_source_availability=")

    statuses = {item["source_key"]: item for item in availability["source_statuses"]}
    assert statuses["summary_widget"]["status"] == "referenced"
    assert statuses["summary_widget"]["page_keys"] == ("collector", "research")
    assert statuses["summary_widget"]["page_count"] == 2
    assert statuses["summary_widget"]["referenced_by_page"] is True
    assert statuses["summary_widget"]["available_for_future_widget"] is True
    assert statuses["prediction_widget"]["status"] == "catalog_only"
    assert statuses["prediction_widget"]["page_keys"] == ()
    assert statuses["prediction_widget"]["referenced_by_page"] is False
    assert all(item["catalog_present"] is True for item in availability["source_statuses"])
    assert all(item["read_only_contract"] is True for item in availability["source_statuses"])
    assert all(item["widget_reusable"] is True for item in availability["source_statuses"])
    assert all(item["layout_decision_free"] is True for item in availability["source_statuses"])
    assert all(item["not_runtime_wiring"] is True for item in availability["source_statuses"])
    assert all(item["not_ui_rendering"] is True for item in availability["source_statuses"])

    real_availability = dashboard_hub_display_source_availability()
    assert real_availability["source_count"] >= 5
    assert "summary_widget" in {item["source_key"] for item in real_availability["source_statuses"]}
    assert "review_hint_display" in real_availability["future_widget_source_keys"]
    assert real_availability["missing_references"] == ()
    assert real_availability["read_only_contract"] is True
    assert real_availability["widget_reusable"] is True
    assert real_availability["layout_decision_free"] is True
    assert real_availability["not_runtime_wiring"] is True
    assert real_availability["not_ui_rendering"] is True

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
