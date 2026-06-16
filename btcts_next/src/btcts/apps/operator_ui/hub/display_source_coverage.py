# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_coverage.py
# desc: Dashboard hub display source coverage summary. No rendering/layout/runtime wiring.

from __future__ import annotations

from btcts.apps.operator_ui.hub.display_source_matrix import (
    dashboard_hub_display_source_matrix,
)

DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT = {
    "coverage_type": "dashboard_hub_display_source_coverage",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
}


def _page_rows(matrix: dict) -> tuple[dict, ...]:
    return tuple(row for row in (matrix.get("page_rows") or ()) if isinstance(row, dict))


def _source_rows(matrix: dict) -> tuple[dict, ...]:
    return tuple(row for row in (matrix.get("source_rows") or ()) if isinstance(row, dict))


def _source_count_range(page_rows: tuple[dict, ...]) -> dict:
    counts = tuple(int(row.get("source_count") or 0) for row in page_rows)
    if not counts:
        return {"min": 0, "max": 0}
    return {"min": min(counts), "max": max(counts)}


def _page_count_range(source_rows: tuple[dict, ...]) -> dict:
    counts = tuple(int(row.get("page_count") or 0) for row in source_rows)
    if not counts:
        return {"min": 0, "max": 0}
    return {"min": min(counts), "max": max(counts)}


def dashboard_hub_display_source_coverage(matrix: dict | None = None) -> dict:
    payload = matrix or dashboard_hub_display_source_matrix()
    page_rows = _page_rows(payload)
    source_rows = _source_rows(payload)

    empty_page_keys = tuple(str(row.get("page_key") or "unknown") for row in page_rows if int(row.get("source_count") or 0) == 0)
    orphan_source_keys = tuple(str(row.get("source_key") or "unknown") for row in source_rows if int(row.get("page_count") or 0) == 0)
    future_widget_source_keys = tuple(
        str(row.get("source_key") or "unknown")
        for row in source_rows
        if row.get("available_for_future_widget") is True
    )
    referenced_source_keys = tuple(
        str(row.get("source_key") or "unknown")
        for row in source_rows
        if int(row.get("page_count") or 0) > 0
    )
    page_source_counts = tuple(
        {
            "page_key": str(row.get("page_key") or "unknown"),
            "consumer_scope": str(row.get("consumer_scope") or "unknown"),
            "source_count": int(row.get("source_count") or 0),
        }
        for row in page_rows
    )
    source_page_counts = tuple(
        {
            "source_key": str(row.get("source_key") or "unknown"),
            "page_count": int(row.get("page_count") or 0),
            "status": str(row.get("status") or "unknown"),
        }
        for row in source_rows
    )
    page_source_count_range = _source_count_range(page_rows)
    source_page_count_range = _page_count_range(source_rows)
    coverage_ok = not empty_page_keys and not orphan_source_keys and not tuple(payload.get("missing_references") or ())
    return {
        **DASHBOARD_HUB_SOURCE_COVERAGE_CONTRACT,
        "matrix_type": payload.get("matrix_type"),
        "page_count": len(page_rows),
        "source_count": len(source_rows),
        "referenced_source_count": len(referenced_source_keys),
        "future_widget_source_count": len(future_widget_source_keys),
        "empty_page_keys": empty_page_keys,
        "orphan_source_keys": orphan_source_keys,
        "missing_references": tuple(payload.get("missing_references") or ()),
        "future_widget_source_keys": future_widget_source_keys,
        "referenced_source_keys": referenced_source_keys,
        "page_source_counts": page_source_counts,
        "source_page_counts": source_page_counts,
        "page_source_count_range": page_source_count_range,
        "source_page_count_range": source_page_count_range,
        "coverage_ok": coverage_ok,
        "compact_line": (
            "dashboard_hub_source_coverage="
            f"pages:{len(page_rows)};sources:{len(source_rows)};"
            f"empty_pages:{','.join(empty_page_keys) or 'none'};"
            f"orphan_sources:{','.join(orphan_source_keys) or 'none'}"
        ),
    }
