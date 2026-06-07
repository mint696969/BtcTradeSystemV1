# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_ui_entry_criteria.py
# desc: Entry criteria for opening dashboard hub display source UI consumption. No rendering/layout/runtime wiring.

from __future__ import annotations

from btcts.apps.operator_ui.hub.display_source_diagnostics import (
    dashboard_hub_display_source_diagnostics,
)

DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT = {
    "entry_type": "dashboard_hub_display_source_ui_entry_criteria",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "not_app_py_wiring": True,
}

REQUIRED_DIAGNOSTIC_LEVELS = ("healthy", "coverage_gap", "review")


def _hot_cold_entry_summary(diagnostics: dict) -> dict:
    summary = diagnostics.get("hot_cold_summary") if isinstance(diagnostics.get("hot_cold_summary"), dict) else {}
    return {
        "source_key": summary.get("source_key") or "hot_cold_duplicate_safe_dataset_view_model",
        "status_label": diagnostics.get("hot_cold_status_label") or summary.get("status_label") or "unknown",
        "metadata_detail_status": diagnostics.get("hot_cold_metadata_detail_status") or summary.get("metadata_detail_status") or "unknown",
        "payload_loader_status": str(summary.get("payload_loader_status") or "unknown"),
        "dataset_reader_status": str(summary.get("dataset_reader_status") or "unknown"),
        "dashboard_rendering_status": str(summary.get("dashboard_rendering_status") or "unknown"),
        "entry_note": "metadata_only_ui_entry_no_payload_reader_rendering_or_executor_opened",
    }


def dashboard_hub_display_source_ui_entry_criteria(diagnostics: dict | None = None) -> dict:
    payload = diagnostics or dashboard_hub_display_source_diagnostics()
    guardrail_failures = tuple(str(item) for item in (payload.get("guardrail_failures") or ()) if item)
    missing_references = tuple(str(item) for item in (payload.get("missing_references") or ()) if item)
    diagnostic_level = str(payload.get("diagnostic_level") or "unknown")
    app_py_wiring_allowed = False
    streamlit_rendering_allowed = False
    layout_decision_allowed = False
    reasons: list[str] = []
    if guardrail_failures:
        reasons.append("guardrail_failures_must_be_empty")
    if missing_references:
        reasons.append("missing_references_must_be_empty")
    if diagnostic_level not in REQUIRED_DIAGNOSTIC_LEVELS:
        reasons.append("diagnostic_level_must_be_entry_safe")
    ui_entry_ready = not reasons
    hot_cold_summary = _hot_cold_entry_summary(payload)
    return {
        **DASHBOARD_HUB_SOURCE_UI_ENTRY_CRITERIA_CONTRACT,
        "diagnostics_type": payload.get("diagnostics_type"),
        "diagnostic_level": diagnostic_level,
        "ui_entry_ready": ui_entry_ready,
        "blocked_reasons": tuple(reasons),
        "guardrail_failures": guardrail_failures,
        "missing_references": missing_references,
        "empty_page_keys": tuple(payload.get("empty_page_keys") or ()),
        "orphan_source_keys": tuple(payload.get("orphan_source_keys") or ()),
        "page_count": int(payload.get("page_count") or 0),
        "source_count": int(payload.get("source_count") or 0),
        "allowed_initial_surface": "diagnostics_read_only_panel" if ui_entry_ready else "none",
        "app_py_wiring_allowed": app_py_wiring_allowed,
        "streamlit_rendering_allowed": streamlit_rendering_allowed,
        "layout_decision_allowed": layout_decision_allowed,
        "presenter_entry_policy": "create_separate_render_free_presenter_entry",
        "hot_cold_summary": hot_cold_summary,
        "hot_cold_status_label": hot_cold_summary.get("status_label"),
        "hot_cold_metadata_detail_status": hot_cold_summary.get("metadata_detail_status"),
        "next_required_step": (
            "manual_streamlit_smoke_passed_health_page_panel_visible" if ui_entry_ready else "fix_diagnostics_before_ui_entry"
        ),
        "compact_line": (
            "dashboard_hub_source_ui_entry="
            f"ready:{ui_entry_ready};"
            f"level:{diagnostic_level};"
            f"blocked:{','.join(reasons) or 'none'};"
            f"hot_cold_status:{hot_cold_summary.get('status_label')}"
        ),
    }
