# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_ui_entry_criteria.py
# desc: Verify dashboard hub display source UI entry criteria does not open rendering/layout/app.py wiring.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_ui_entry_criteria import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT,
    dashboard_hub_display_source_ui_entry_criteria,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT["entry_type"] == "dashboard_hub_display_source_ui_entry_criteria"
    assert DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT["dashboard_role"] == "hub"
    assert DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT["read_only_contract"] is True
    assert DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT["widget_reusable"] is True
    assert DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT["layout_decision_free"] is True
    assert DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT["not_ui_rendering"] is True
    assert DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT["not_app_py_wiring"] is True

    blocked = dashboard_hub_display_source_ui_entry_criteria(
        {
            "diagnostics_type": "dashboard_hub_display_source_diagnostics",
            "diagnostic_level": "guardrail_failure",
            "guardrail_failures": ("layout_decision_free",),
            "missing_references": ("ghost_source",),
            "empty_page_keys": ("logs",),
            "orphan_source_keys": ("future_only",),
            "page_count": 2,
            "source_count": 2,
        }
    )
    assert blocked["ui_entry_ready"] is False
    assert blocked["allowed_initial_surface"] == "none"
    assert blocked["app_py_wiring_allowed"] is False
    assert blocked["streamlit_rendering_allowed"] is False
    assert blocked["layout_decision_allowed"] is False
    assert blocked["next_required_step"] == "fix_diagnostics_before_ui_entry"
    assert blocked["blocked_reasons"] == (
        "guardrail_failures_must_be_empty",
        "missing_references_must_be_empty",
        "diagnostic_level_must_be_entry_safe",
    )

    ready = dashboard_hub_display_source_ui_entry_criteria(
        {
            "diagnostics_type": "dashboard_hub_display_source_diagnostics",
            "diagnostic_level": "healthy",
            "guardrail_failures": (),
            "missing_references": (),
            "empty_page_keys": (),
            "orphan_source_keys": (),
            "page_count": 7,
            "source_count": 5,
        }
    )
    assert ready["ui_entry_ready"] is True
    assert ready["allowed_initial_surface"] == "diagnostics_read_only_panel"
    assert ready["blocked_reasons"] == ()
    assert ready["next_required_step"] == "manual_streamlit_smoke_passed_health_page_panel_visible"
    assert ready["presenter_entry_policy"] == "create_separate_render_free_presenter_entry"
    assert ready["app_py_wiring_allowed"] is False
    assert ready["streamlit_rendering_allowed"] is False
    assert ready["layout_decision_allowed"] is False
    assert ready["compact_line"].startswith("dashboard_hub_source_ui_entry=")

    real_entry = dashboard_hub_display_source_ui_entry_criteria()
    assert real_entry["diagnostics_type"] == "dashboard_hub_display_source_diagnostics"
    assert real_entry["guardrail_failures"] == ()
    assert real_entry["missing_references"] == ()
    assert real_entry["page_count"] >= 3
    assert real_entry["source_count"] >= 5
    assert real_entry["read_only_contract"] is True
    assert real_entry["widget_reusable"] is True
    assert real_entry["layout_decision_free"] is True
    assert real_entry["not_runtime_wiring"] is True
    assert real_entry["not_ui_rendering"] is True
    assert real_entry["not_app_py_wiring"] is True
    assert real_entry["app_py_wiring_allowed"] is False
    assert real_entry["streamlit_rendering_allowed"] is False
    assert real_entry["layout_decision_allowed"] is False

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
