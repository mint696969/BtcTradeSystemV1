# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_collector_linked_runtime_summary_cp16.py
# desc: Tests Collector top linked runtime summary cards and detail popovers.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
COLLECTOR_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py"
PANELS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/collector_top_panels.py"

from btcts.apps.operator_ui.components.collector_top_panels import (  # noqa: E402
    build_linked_runtime_summary_items,
)


def test_cp16_build_summary_items_have_expected_runtimes_and_severities() -> None:
    items = build_linked_runtime_summary_items(
        live_summary={"overall_state": "RUNNING", "overall_reason": "feed=STALE"},
        runtime={"mode": "RUNNING", "health_status": "healthy", "feed_state": "STALE"},
        chart_engine_snapshot={"mode": "RUNNING", "active": True, "runtime_pid": 123, "status_age_sec": 2},
        market_regime_loop_snapshot={"mode": "RUNNING_WRITE_OK", "active": True, "runtime_pid": 456, "writes": 8, "blocked": 0, "latest_run_id": "mr_run"},
        market_regime_snapshot={"latest_cards_available": True, "card_count": 8, "first_card_label": "レンジ", "first_card_confidence": 70, "latest_run_id": "mr_run"},
    )
    by_id = {item["runtime_id"]: item for item in items}
    assert set(by_id) == {"collector", "chart_engine", "market_regime"}
    assert by_id["collector"]["severity"] == "warning"
    assert by_id["chart_engine"]["severity"] == "healthy"
    assert by_id["market_regime"]["severity"] == "healthy"
    assert by_id["market_regime"]["badge_label"] == "RUNNING"


def test_cp16_summary_items_detect_stopped_runtimes() -> None:
    items = build_linked_runtime_summary_items(
        live_summary={"overall_state": "STOPPED", "overall_reason": "collector stopped"},
        runtime={"mode": "RUNNING", "health_status": "stopped", "feed_state": "STALE"},
        chart_engine_snapshot={"mode": "STOPPED", "active": False},
        market_regime_loop_snapshot={"mode": "STOPPED", "active": False, "writes": 3},
        market_regime_snapshot={"latest_cards_available": True, "card_count": 8, "first_card_label": "レンジ", "first_card_confidence": 70},
    )
    by_id = {item["runtime_id"]: item for item in items}
    assert by_id["collector"]["severity"] == "danger"
    assert by_id["chart_engine"]["severity"] == "danger"
    assert by_id["market_regime"]["severity"] == "warning"


def test_cp16_collector_page_uses_linked_runtime_summary_before_legacy_overview() -> None:
    text = COLLECTOR_PAGE.read_text(encoding="utf-8")
    assert "render_linked_runtime_summary_section" in text
    assert "market_regime_snapshot = market_regime_operator_ui_snapshot()" in text
    linked_index = text.index("render_linked_runtime_summary_section")
    overview_index = text.index("render_overview_summary_panel")
    assert linked_index < overview_index


def test_cp16_top_panels_render_cards_and_detail_popovers() -> None:
    text = PANELS.read_text(encoding="utf-8")
    required = [
        "Linked Runtime Summary",
        "build_linked_runtime_summary_items",
        "_render_runtime_status_card",
        "st.popover(\"詳細\"",
        "_severity_color",
        "#16a34a",
        "#d97706",
        "#dc2626",
        "#64748b",
    ]
    assert [token for token in required if token not in text] == []


def test_cp16_summary_has_no_execution_side_effects() -> None:
    text = PANELS.read_text(encoding="utf-8")
    forbidden = [
        "start_stack_detached",
        "start_chart_engine_detached",
        "start_market_regime_producer_loop_detached",
        "request_market_regime_producer_loop_safe_stop",
        "write_unified_supervisor_request",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
