# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_presenter.py
# desc: Verify dashboard hub display source presenter is render-free and does not wire app.py/Streamlit/layout.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hub.display_source_presenter import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_PRESENTER_CONTRACT,
    dashboard_hub_display_source_presenter,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_PRESENTER_CONTRACT["presenter_type"] == "dashboard_hub_display_source_presenter"
    assert DASHBOARD_HUB_SOURCE_PRESENTER_CONTRACT["render_free"] is True
    assert DASHBOARD_HUB_SOURCE_PRESENTER_CONTRACT["not_ui_rendering"] is True
    assert DASHBOARD_HUB_SOURCE_PRESENTER_CONTRACT["not_app_py_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_PRESENTER_CONTRACT["layout_decision_free"] is True

    blocked = dashboard_hub_display_source_presenter({
        "entry_type": "dashboard_hub_display_source_ui_entry_criteria",
        "ui_entry_ready": False,
        "diagnostic_level": "guardrail_failure",
        "page_count": 2,
        "source_count": 2,
        "blocked_reasons": ("guardrail_failures_must_be_empty",),
        "allowed_initial_surface": "none",
        "guardrail_failures": ("layout_decision_free",),
        "missing_references": (),
        "empty_page_keys": (),
        "orphan_source_keys": (),
        "next_required_step": "fix_diagnostics_before_ui_entry",
    })
    assert blocked["status_label"] == "blocked"
    assert blocked["ui_entry_ready"] is False
    assert blocked["blocked_reasons"] == ("guardrail_failures_must_be_empty",)
    assert blocked["summary_rows"][0] == {"label": "status", "value": "blocked"}
    assert {"label": "next_required_step", "value": "fix_diagnostics_before_ui_entry"} in blocked["detail_rows"]

    ready = dashboard_hub_display_source_presenter({
        "entry_type": "dashboard_hub_display_source_ui_entry_criteria",
        "ui_entry_ready": True,
        "diagnostic_level": "healthy",
        "page_count": 7,
        "source_count": 5,
        "blocked_reasons": (),
        "allowed_initial_surface": "diagnostics_read_only_panel",
        "guardrail_failures": (),
        "missing_references": (),
        "empty_page_keys": (),
        "orphan_source_keys": (),
        "next_required_step": "manual_streamlit_smoke_passed_health_page_panel_visible",
        "hot_cold_status": {
            "status_label": "catalog_ready_payload_not_opened",
            "metadata_detail_status": "ready_for_dashboard_hub_display_source_overview",
            "unopened_boundary_statuses": {
                "payload_loader": "not_opened",
                "dataset_reader": "not_opened",
                "dashboard_rendering": "not_opened",
                "copy_executor": "not_opened",
            },
            "next_opening_gate": {"gate_type": "explicit_entry_criteria_required"},
        },
    })
    assert ready["status_label"] == "ready"
    assert ready["ui_entry_ready"] is True
    assert ready["summary_rows"][5] == {"label": "allowed_initial_surface", "value": "diagnostics_read_only_panel"}
    assert ready["hot_cold_status_label"] == "catalog_ready_payload_not_opened"
    assert ready["hot_cold_metadata_detail_status"] == "ready_for_dashboard_hub_display_source_overview"
    assert ready["hot_cold_detail_rows"] == (
        {"label": "hot_cold_status", "value": "catalog_ready_payload_not_opened"},
        {"label": "hot_cold_metadata", "value": "ready_for_dashboard_hub_display_source_overview"},
        {"label": "hot_cold_payload_loader", "value": "not_opened"},
        {"label": "hot_cold_dataset_reader", "value": "not_opened"},
        {"label": "hot_cold_dashboard_rendering", "value": "not_opened"},
        {"label": "hot_cold_copy_executor", "value": "not_opened"},
        {"label": "hot_cold_next_gate", "value": "explicit_entry_criteria_required"},
    )
    assert ready["detail_rows"][-7:] == ready["hot_cold_detail_rows"]
    assert ready["compact_line"].startswith("dashboard_hub_source_presenter=")

    real_presenter = dashboard_hub_display_source_presenter()
    assert real_presenter["entry_type"] == "dashboard_hub_display_source_ui_entry_criteria"
    assert real_presenter["title"] == "Dashboard hub display source diagnostics"
    assert real_presenter["read_only_contract"] is True
    assert real_presenter["widget_reusable"] is True
    assert real_presenter["layout_decision_free"] is True
    assert real_presenter["not_runtime_wiring"] is True
    assert real_presenter["not_ui_rendering"] is True
    assert real_presenter["not_app_py_wiring"] is True
    assert real_presenter["render_free"] is True
    assert len(real_presenter["hot_cold_detail_rows"]) == 7
    assert real_presenter["hot_cold_status_label"] == "catalog_ready_payload_not_opened"
    assert real_presenter["hot_cold_metadata_detail_status"] == "ready_for_dashboard_hub_display_source_overview"
    assert real_presenter["hot_cold_detail_rows"][2] == {"label": "hot_cold_payload_loader", "value": "not_opened"}
    assert real_presenter["hot_cold_detail_rows"][3] == {"label": "hot_cold_dataset_reader", "value": "not_opened"}
    assert real_presenter["hot_cold_detail_rows"][4] == {"label": "hot_cold_dashboard_rendering", "value": "not_opened"}
    assert real_presenter["hot_cold_detail_rows"][6] == {
        "label": "hot_cold_next_gate",
        "value": "metadata_only_ui_entry_no_payload_reader_rendering_or_executor_opened",
    }

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
