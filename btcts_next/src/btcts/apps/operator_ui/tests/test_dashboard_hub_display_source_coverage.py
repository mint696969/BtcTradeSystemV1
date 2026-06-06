# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_coverage.py
# desc: Verify dashboard hub source coverage summary stays read-only and layout-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_coverage import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT,
    dashboard_hub_display_source_coverage,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT["coverage_type"] == "dashboard_hub_display_source_coverage"
    assert DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT["dashboard_role"] == "hub"
    assert DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT["read_only_contract"] is True
    assert DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT["widget_reusable"] is True
    assert DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT["layout_decision_free"] is True
    assert DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT["not_ui_rendering"] is True

    matrix = {
        "matrix_type": "dashboard_hub_display_source_matrix",
        "missing_references": ("ghost_source",),
        "page_rows": (
            {
                "page_key": "collector",
                "consumer_scope": "collector_tab",
                "source_count": 1,
            },
            {
                "page_key": "logs",
                "consumer_scope": "future_widget",
                "source_count": 0,
            },
        ),
        "source_rows": (
            {
                "source_key": "summary_widget",
                "page_count": 1,
                "available_for_future_widget": True,
                "status": "referenced",
            },
            {
                "source_key": "future_only",
                "page_count": 0,
                "available_for_future_widget": True,
                "status": "catalog_only",
            },
        ),
    }
    coverage = dashboard_hub_display_source_coverage(matrix)
    assert coverage["coverage_type"] == "dashboard_hub_display_source_coverage"
    assert coverage["matrix_type"] == "dashboard_hub_display_source_matrix"
    assert coverage["page_count"] == 2
    assert coverage["source_count"] == 2
    assert coverage["referenced_source_count"] == 1
    assert coverage["future_widget_source_count"] == 2
    assert coverage["empty_page_keys"] == ("logs",)
    assert coverage["orphan_source_keys"] == ("future_only",)
    assert coverage["missing_references"] == ("ghost_source",)
    assert coverage["future_widget_source_keys"] == ("summary_widget", "future_only")
    assert coverage["referenced_source_keys"] == ("summary_widget",)
    assert coverage["page_source_count_range"] == {"min": 0, "max": 1}
    assert coverage["source_page_count_range"] == {"min": 0, "max": 1}
    assert coverage["coverage_ok"] is False
    assert coverage["compact_line"].startswith("dashboard_hub_source_coverage=")

    real_coverage = dashboard_hub_display_source_coverage()
    assert real_coverage["page_count"] >= 3
    assert real_coverage["source_count"] >= 5
    assert real_coverage["referenced_source_count"] >= 1
    assert real_coverage["future_widget_source_count"] >= 1
    assert "summary_widget" in real_coverage["referenced_source_keys"]
    assert "review_hint_display" in real_coverage["future_widget_source_keys"]
    assert real_coverage["missing_references"] == ()
    assert real_coverage["read_only_contract"] is True
    assert real_coverage["widget_reusable"] is True
    assert real_coverage["layout_decision_free"] is True
    assert real_coverage["not_runtime_wiring"] is True
    assert real_coverage["not_ui_rendering"] is True

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
