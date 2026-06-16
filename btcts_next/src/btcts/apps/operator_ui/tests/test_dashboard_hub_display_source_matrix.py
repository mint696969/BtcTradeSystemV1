# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_matrix.py
# desc: Verify dashboard hub display source/page matrix stays read-only and layout-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_matrix import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT,
    dashboard_hub_display_source_matrix,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT["matrix_type"] == "dashboard_hub_display_source_matrix"
    assert DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT["dashboard_role"] == "hub"
    assert DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT["read_only_contract"] is True
    assert DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT["widget_reusable"] is True
    assert DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT["layout_decision_free"] is True
    assert DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_MATRIX_CONTRACT["not_ui_rendering"] is True

    registry = {
        "registry_type": "dashboard_hub_display_source_registry",
        "page_entries": (
            {
                "page_key": "collector",
                "consumer_scope": "collector_tab",
                "source_keys": ("summary_widget",),
                "source_count": 1,
                "read_only_contract": True,
                "widget_reusable": True,
                "layout_decision_free": True,
                "not_runtime_wiring": True,
                "not_ui_rendering": True,
            },
            {
                "page_key": "research",
                "consumer_scope": "future_widget",
                "source_keys": ("summary_widget", "review_hint_display"),
                "source_count": 2,
                "read_only_contract": True,
                "widget_reusable": True,
                "layout_decision_free": True,
                "not_runtime_wiring": True,
                "not_ui_rendering": True,
            },
        ),
    }
    availability = {
        "availability_type": "dashboard_hub_display_source_availability",
        "missing_references": (),
        "source_statuses": (
            {
                "source_key": "summary_widget",
                "source_type": "market_summary_widget_model",
                "source_origin": "ai_operator_display_sources",
                "page_keys": ("collector", "research"),
                "available_for_future_widget": True,
                "status": "referenced",
                "read_only_contract": True,
                "widget_reusable": True,
                "layout_decision_free": True,
                "not_runtime_wiring": True,
                "not_ui_rendering": True,
            },
            {
                "source_key": "review_hint_display",
                "source_type": "prediction_review_hint_display_context",
                "source_origin": "ai_operator_display_sources",
                "page_keys": ("research",),
                "available_for_future_widget": True,
                "status": "referenced",
                "read_only_contract": True,
                "widget_reusable": True,
                "layout_decision_free": True,
                "not_runtime_wiring": True,
                "not_ui_rendering": True,
            },
        ),
    }

    matrix = dashboard_hub_display_source_matrix(registry, availability)
    assert matrix["matrix_type"] == "dashboard_hub_display_source_matrix"
    assert matrix["registry_type"] == "dashboard_hub_display_source_registry"
    assert matrix["availability_type"] == "dashboard_hub_display_source_availability"
    assert matrix["page_count"] == 2
    assert matrix["source_count"] == 2
    assert matrix["page_keys"] == ("collector", "research")
    assert matrix["source_keys"] == ("summary_widget", "review_hint_display")
    assert matrix["missing_references"] == ()
    assert matrix["compact_line"].startswith("dashboard_hub_source_matrix=pages[")

    page_rows = {row["page_key"]: row for row in matrix["page_rows"]}
    assert page_rows["collector"]["source_presence"] == {
        "summary_widget": True,
        "review_hint_display": False,
    }
    assert page_rows["research"]["source_presence"] == {
        "summary_widget": True,
        "review_hint_display": True,
    }
    assert all(row["read_only_contract"] is True for row in matrix["page_rows"])
    assert all(row["widget_reusable"] is True for row in matrix["page_rows"])
    assert all(row["layout_decision_free"] is True for row in matrix["page_rows"])
    assert all(row["not_runtime_wiring"] is True for row in matrix["page_rows"])
    assert all(row["not_ui_rendering"] is True for row in matrix["page_rows"])

    source_rows = {row["source_key"]: row for row in matrix["source_rows"]}
    assert source_rows["summary_widget"]["page_presence"] == {
        "collector": True,
        "research": True,
    }
    assert source_rows["review_hint_display"]["page_presence"] == {
        "collector": False,
        "research": True,
    }
    assert source_rows["summary_widget"]["status"] == "referenced"
    assert source_rows["summary_widget"]["available_for_future_widget"] is True
    assert all(row["read_only_contract"] is True for row in matrix["source_rows"])
    assert all(row["widget_reusable"] is True for row in matrix["source_rows"])
    assert all(row["layout_decision_free"] is True for row in matrix["source_rows"])
    assert all(row["not_runtime_wiring"] is True for row in matrix["source_rows"])
    assert all(row["not_ui_rendering"] is True for row in matrix["source_rows"])

    real_matrix = dashboard_hub_display_source_matrix()
    assert real_matrix["page_count"] >= 3
    assert "collector" in real_matrix["page_keys"]
    assert "summary_widget" in real_matrix["source_keys"]
    assert "review_hint_display" in real_matrix["source_keys"]
    assert real_matrix["missing_references"] == ()
    assert real_matrix["read_only_contract"] is True
    assert real_matrix["widget_reusable"] is True
    assert real_matrix["layout_decision_free"] is True
    assert real_matrix["not_runtime_wiring"] is True
    assert real_matrix["not_ui_rendering"] is True

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
