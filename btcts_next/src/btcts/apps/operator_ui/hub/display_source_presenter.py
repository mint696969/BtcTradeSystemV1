# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_presenter.py
# desc: Render-free presenter model for dashboard hub display source diagnostics. No Streamlit/app.py/layout/runtime wiring.

from __future__ import annotations

from btcts.apps.operator_ui.hub.display_source_ui_entry_criteria import (
    dashboard_hub_display_source_ui_entry_criteria,
)

DASHBOARD_HUB_SOURCE_PRESENTER_CONTRACT = {
    "presenter_type": "dashboard_hub_display_source_presenter",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "not_app_py_wiring": True,
    "render_free": True,
}


def _status_label(entry: dict) -> str:
    if entry.get("ui_entry_ready") is True:
        return "ready"
    return "blocked"


def dashboard_hub_display_source_presenter(entry: dict | None = None) -> dict:
    payload = entry or dashboard_hub_display_source_ui_entry_criteria()
    blocked_reasons = tuple(str(item) for item in (payload.get("blocked_reasons") or ()) if item)
    summary_rows = (
        {"label": "status", "value": _status_label(payload)},
        {"label": "diagnostic_level", "value": str(payload.get("diagnostic_level") or "unknown")},
        {"label": "pages", "value": str(int(payload.get("page_count") or 0))},
        {"label": "sources", "value": str(int(payload.get("source_count") or 0))},
        {"label": "blocked_reasons", "value": ",".join(blocked_reasons) or "none"},
        {"label": "allowed_initial_surface", "value": str(payload.get("allowed_initial_surface") or "none")},
    )
    detail_rows = (
        {"label": "guardrail_failures", "value": ",".join(tuple(payload.get("guardrail_failures") or ())) or "none"},
        {"label": "missing_references", "value": ",".join(tuple(payload.get("missing_references") or ())) or "none"},
        {"label": "empty_page_keys", "value": ",".join(tuple(payload.get("empty_page_keys") or ())) or "none"},
        {"label": "orphan_source_keys", "value": ",".join(tuple(payload.get("orphan_source_keys") or ())) or "none"},
        {"label": "next_required_step", "value": str(payload.get("next_required_step") or "unknown")},
    )
    return {
        **DASHBOARD_HUB_SOURCE_PRESENTER_CONTRACT,
        "entry_type": payload.get("entry_type"),
        "ui_entry_ready": payload.get("ui_entry_ready") is True,
        "status_label": _status_label(payload),
        "title": "Dashboard hub display source diagnostics",
        "subtitle": "Read-only source readiness for future dashboard panels",
        "summary_rows": summary_rows,
        "detail_rows": detail_rows,
        "blocked_reasons": blocked_reasons,
        "compact_line": "dashboard_hub_source_presenter=" + ";".join(
            f"{row['label']}:{row['value']}" for row in summary_rows
        ),
    }
