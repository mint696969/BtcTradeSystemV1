# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_bundle.py
# desc: Verify dashboard hub display source bundle facade stays read-only and layout-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_bundle import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT,
    dashboard_hub_display_source_bundle,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT["bundle_type"] == "dashboard_hub_display_source_bundle"
    assert DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT["dashboard_role"] == "hub"
    assert DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT["read_only_contract"] is True
    assert DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT["widget_reusable"] is True
    assert DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT["layout_decision_free"] is True
    assert DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_BUNDLE_CONTRACT["not_ui_rendering"] is True

    bundle = dashboard_hub_display_source_bundle()
    assert bundle["bundle_type"] == "dashboard_hub_display_source_bundle"
    assert bundle["page_count"] >= 3
    assert bundle["source_count"] >= 5
    assert "collector" in bundle["page_keys"]
    assert "summary_widget" in bundle["source_keys"]
    assert "review_hint_display" in bundle["source_keys"]
    assert bundle["missing_references"] == ()
    assert bundle["compact_line"].startswith("dashboard_hub_source_bundle=")

    assert bundle["registry"]["registry_type"] == "dashboard_hub_display_source_registry"
    assert bundle["overview"]["overview_type"] == "dashboard_hub_display_source_overview"
    assert bundle["availability"]["availability_type"] == "dashboard_hub_display_source_availability"
    assert bundle["matrix"]["matrix_type"] == "dashboard_hub_display_source_matrix"
    assert bundle["coverage"]["coverage_type"] == "dashboard_hub_display_source_coverage"

    flags = bundle["guardrail_flags"]
    assert flags["registry_read_only"] is True
    assert flags["overview_read_only"] is True
    assert flags["availability_read_only"] is True
    assert flags["matrix_read_only"] is True
    assert flags["coverage_read_only"] is True
    assert flags["layout_decision_free"] is True
    assert flags["not_runtime_wiring"] is True
    assert flags["not_ui_rendering"] is True

    assert bundle["read_only_contract"] is True
    assert bundle["widget_reusable"] is True
    assert bundle["layout_decision_free"] is True
    assert bundle["not_runtime_wiring"] is True
    assert bundle["not_ui_rendering"] is True
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
