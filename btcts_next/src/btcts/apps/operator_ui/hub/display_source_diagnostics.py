# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_diagnostics.py
# desc: Dashboard hub display source read-only diagnostics. No rendering/layout/runtime wiring.

from __future__ import annotations

from btcts.apps.operator_ui.hub.display_source_bundle import (
    dashboard_hub_display_source_bundle,
)

DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT = {
    "diagnostics_type": "dashboard_hub_display_source_diagnostics",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
}


def _hot_cold_diagnostic_summary(bundle: dict) -> dict:
    summary = bundle.get("hot_cold_summary") if isinstance(bundle.get("hot_cold_summary"), dict) else {}
    return {
        "source_key": summary.get("source_key") or "hot_cold_duplicate_safe_dataset_view_model",
        "status_label": bundle.get("hot_cold_status_label") or summary.get("status_label") or "unknown",
        "metadata_detail_status": bundle.get("hot_cold_metadata_detail_status") or summary.get("metadata_detail_status") or "unknown",
        "payload_loader_status": str(summary.get("payload_loader_status") or "unknown"),
        "dataset_reader_status": str(summary.get("dataset_reader_status") or "unknown"),
        "dashboard_rendering_status": str(summary.get("dashboard_rendering_status") or "unknown"),
        "copy_executor_status": str(summary.get("copy_executor_status") or "unknown"),
        "diagnostic_note": "metadata_only_no_payload_reader_rendering_or_executor_opened",
    }


def _guardrail_failures(flags: dict) -> tuple[str, ...]:
    return tuple(str(key) for key, value in flags.items() if value is not True)


def _diagnostic_level(bundle: dict, guardrail_failures: tuple[str, ...]) -> str:
    if guardrail_failures:
        return "guardrail_failure"
    if tuple(bundle.get("missing_references") or ()):
        return "missing_references"
    if tuple(bundle.get("empty_page_keys") or ()) or tuple(bundle.get("orphan_source_keys") or ()):
        return "coverage_gap"
    if bundle.get("coverage_ok") is True:
        return "healthy"
    return "review"


def dashboard_hub_display_source_diagnostics(bundle: dict | None = None) -> dict:
    payload = bundle or dashboard_hub_display_source_bundle()
    flags = dict(payload.get("guardrail_flags") or {})
    failures = _guardrail_failures(flags)
    level = _diagnostic_level(payload, failures)
    missing_references = tuple(str(item) for item in (payload.get("missing_references") or ()) if item)
    empty_page_keys = tuple(str(item) for item in (payload.get("empty_page_keys") or ()) if item)
    orphan_source_keys = tuple(str(item) for item in (payload.get("orphan_source_keys") or ()) if item)
    page_keys = tuple(str(item) for item in (payload.get("page_keys") or ()) if item)
    source_keys = tuple(str(item) for item in (payload.get("source_keys") or ()) if item)
    hot_cold_summary = _hot_cold_diagnostic_summary(payload)
    summary_items = (
        f"level={level}",
        f"pages={len(page_keys)}",
        f"sources={len(source_keys)}",
        f"coverage_ok={payload.get('coverage_ok') is True}",
        f"missing={','.join(missing_references) or 'none'}",
        f"empty_pages={','.join(empty_page_keys) or 'none'}",
        f"orphan_sources={','.join(orphan_source_keys) or 'none'}",
        f"guardrail_failures={','.join(failures) or 'none'}",
        f"hot_cold_status={hot_cold_summary.get('status_label')}",
        f"hot_cold_metadata={hot_cold_summary.get('metadata_detail_status')}",
    )
    return {
        **DASHBOARD_HUB_SOURCE_DIAGNOSTICS_CONTRACT,
        "bundle_type": payload.get("bundle_type"),
        "diagnostic_level": level,
        "coverage_ok": payload.get("coverage_ok") is True,
        "page_count": len(page_keys),
        "source_count": len(source_keys),
        "page_keys": page_keys,
        "source_keys": source_keys,
        "missing_references": missing_references,
        "empty_page_keys": empty_page_keys,
        "orphan_source_keys": orphan_source_keys,
        "guardrail_failures": failures,
        "hot_cold_summary": hot_cold_summary,
        "hot_cold_status_label": hot_cold_summary.get("status_label"),
        "hot_cold_metadata_detail_status": hot_cold_summary.get("metadata_detail_status"),
        "summary_items": summary_items,
        "compact_line": "dashboard_hub_source_diagnostics=" + ";".join(summary_items),
    }
