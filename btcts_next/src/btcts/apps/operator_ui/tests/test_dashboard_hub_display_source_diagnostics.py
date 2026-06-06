# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_diagnostics.py
# desc: Verify dashboard hub display source diagnostics stays read-only and layout-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_diagnostics import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT,
    dashboard_hub_display_source_diagnostics,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT["diagnostics_type"] == "dashboard_hub_display_source_diagnostics"
    assert DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT["dashboard_role"] == "hub"
    assert DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT["read_only_contract"] is True
    assert DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT["widget_reusable"] is True
    assert DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT["layout_decision_free"] is True
    assert DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT["not_ui_rendering"] is True

    failing_bundle = {
        "bundle_type": "dashboard_hub_display_source_bundle",
        "coverage_ok": False,
        "page_keys": ("collector", "logs"),
        "source_keys": ("summary_widget", "future_only"),
        "missing_references": ("ghost_source",),
        "empty_page_keys": ("logs",),
        "orphan_source_keys": ("future_only",),
        "guardrail_flags": {
            "registry_read_only": True,
            "overview_read_only": True,
            "availability_read_only": True,
            "matrix_read_only": True,
            "coverage_read_only": True,
            "layout_decision_free": False,
            "not_runtime_wiring": True,
            "not_ui_rendering": True,
        },
    }
    diagnostics = dashboard_hub_display_source_diagnostics(failing_bundle)
    assert diagnostics["diagnostics_type"] == "dashboard_hub_display_source_diagnostics"
    assert diagnostics["bundle_type"] == "dashboard_hub_display_source_bundle"
    assert diagnostics["diagnostic_level"] == "guardrail_failure"
    assert diagnostics["coverage_ok"] is False
    assert diagnostics["page_count"] == 2
    assert diagnostics["source_count"] == 2
    assert diagnostics["missing_references"] == ("ghost_source",)
    assert diagnostics["empty_page_keys"] == ("logs",)
    assert diagnostics["orphan_source_keys"] == ("future_only",)
    assert diagnostics["guardrail_failures"] == ("layout_decision_free",)
    assert diagnostics["compact_line"].startswith("dashboard_hub_source_diagnostics=")

    coverage_gap = dashboard_hub_display_source_diagnostics({
        **failing_bundle,
        "missing_references": (),
        "guardrail_flags": {key: True for key in failing_bundle["guardrail_flags"]},
    })
    assert coverage_gap["diagnostic_level"] == "coverage_gap"

    healthy = dashboard_hub_display_source_diagnostics()
    assert healthy["page_count"] >= 3
    assert healthy["source_count"] >= 5
    assert healthy["missing_references"] == ()
    assert healthy["guardrail_failures"] == ()
    assert healthy["diagnostic_level"] in ("healthy", "coverage_gap", "review")
    assert "summary_widget" in healthy["source_keys"]
    assert "review_hint_display" in healthy["source_keys"]
    assert healthy["read_only_contract"] is True
    assert healthy["widget_reusable"] is True
    assert healthy["layout_decision_free"] is True
    assert healthy["not_runtime_wiring"] is True
    assert healthy["not_ui_rendering"] is True

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
