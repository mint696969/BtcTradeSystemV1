# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_live_shell_refresh_plan.py
# desc: Verify refresh planning keeps health on fragment path and logs on page reload path.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.live_shell as live_shell  # noqa: E402
import btcts.apps.operator_ui.components.slot_definitions as slot_definitions  # noqa: E402


def main() -> int:
    original_page_supports_auto_refresh = live_shell.page_supports_auto_refresh
    original_page_auto_refresh_interval_sec = live_shell.page_auto_refresh_interval_sec
    original_page_non_fragment_refresh_interval_sec = (
        live_shell.page_non_fragment_refresh_interval_sec
    )

    try:
        live_shell.page_supports_auto_refresh = lambda page_id: page_id in {
            "health",
            "warroom",
            "logs",
            "collector",
        }

        def _fake_interval(page_id: str, *, default_sec: int = 15) -> int:
            if page_id == "health":
                return 5
            if page_id == "warroom":
                return 3
            if page_id == "logs":
                return 10
            if page_id == "collector":
                return 3
            return default_sec

        live_shell.page_auto_refresh_interval_sec = _fake_interval

        def _fake_non_fragment_interval(
            page_id: str,
            *,
            default_sec: int = 15,
        ) -> int:
            if page_id == "warroom":
                return 5
            return _fake_interval(page_id, default_sec=default_sec)

        live_shell.page_non_fragment_refresh_interval_sec = (
            _fake_non_fragment_interval
        )

        health_fragment_plan = live_shell.resolve_page_refresh_plan(
            page_key="health",
            ui_auto_refresh=True,
            ui_refresh_interval_sec=15,
            fragment_supported=True,
        )
        assert health_fragment_plan["slot_refresh_target"] is True
        assert health_fragment_plan["fragment_refresh_target"] is True
        assert health_fragment_plan["page_auto_refresh_target"] is False
        assert health_fragment_plan["page_reload_enabled"] is False
        assert health_fragment_plan["fragment_refresh_enabled"] is True
        assert health_fragment_plan["refresh_status_visible"] is True
        assert health_fragment_plan["effective_refresh_interval_sec"] == 5

        health_fallback_plan = live_shell.resolve_page_refresh_plan(
            page_key="health",
            ui_auto_refresh=True,
            ui_refresh_interval_sec=15,
            fragment_supported=False,
        )
        assert health_fallback_plan["slot_refresh_target"] is True
        assert health_fallback_plan["fragment_refresh_target"] is False
        assert health_fallback_plan["page_auto_refresh_target"] is True
        assert health_fallback_plan["page_reload_enabled"] is True
        assert health_fallback_plan["fragment_refresh_enabled"] is False
        assert health_fallback_plan["effective_refresh_interval_sec"] == 5

        warroom_fragment_plan = live_shell.resolve_page_refresh_plan(
            page_key="warroom",
            ui_auto_refresh=True,
            ui_refresh_interval_sec=15,
            fragment_supported=True,
        )
        assert warroom_fragment_plan["slot_refresh_target"] is True
        assert warroom_fragment_plan["fragment_refresh_target"] is True
        assert warroom_fragment_plan["page_auto_refresh_target"] is False
        assert warroom_fragment_plan["page_reload_enabled"] is False
        assert warroom_fragment_plan["fragment_refresh_enabled"] is True
        assert warroom_fragment_plan["effective_refresh_interval_sec"] == 3

        logs_plan = live_shell.resolve_page_refresh_plan(
            page_key="logs",
            ui_auto_refresh=True,
            ui_refresh_interval_sec=15,
            fragment_supported=True,
        )
        assert logs_plan["slot_refresh_target"] is True
        assert logs_plan["fragment_refresh_target"] is False
        assert logs_plan["page_auto_refresh_target"] is True
        assert logs_plan["page_reload_enabled"] is True
        assert logs_plan["fragment_refresh_enabled"] is False
        assert logs_plan["effective_refresh_interval_sec"] == 10

        collector_auto_plan = live_shell.resolve_page_refresh_plan(
            page_key="collector",
            ui_auto_refresh=True,
            ui_refresh_interval_sec=15,
            fragment_supported=True,
        )
        assert collector_auto_plan["slot_refresh_target"] is True
        assert collector_auto_plan["fragment_refresh_target"] is True
        assert collector_auto_plan["page_auto_refresh_target"] is False
        assert collector_auto_plan["page_reload_enabled"] is False
        assert collector_auto_plan["fragment_refresh_enabled"] is True
        assert collector_auto_plan["refresh_status_visible"] is True
        assert collector_auto_plan["effective_refresh_interval_sec"] == 3

        collector_manual_plan = live_shell.resolve_page_refresh_plan(
            page_key="collector",
            ui_auto_refresh=False,
            ui_refresh_interval_sec=15,
            fragment_supported=True,
        )
        assert collector_manual_plan["slot_refresh_target"] is True
        assert collector_manual_plan["fragment_refresh_target"] is True
        assert collector_manual_plan["page_auto_refresh_target"] is False
        assert collector_manual_plan["page_reload_enabled"] is False
        assert collector_manual_plan["fragment_refresh_enabled"] is False
        assert collector_manual_plan["refresh_status_visible"] is False
        assert collector_manual_plan["effective_refresh_interval_sec"] == 3

        static_plan = live_shell.resolve_page_refresh_plan(
            page_key="config",
            ui_auto_refresh=True,
            ui_refresh_interval_sec=15,
            fragment_supported=True,
        )
        assert static_plan["slot_refresh_target"] is False
        assert static_plan["fragment_refresh_target"] is False
        assert static_plan["page_auto_refresh_target"] is False
        assert static_plan["page_reload_enabled"] is False
        assert static_plan["fragment_refresh_enabled"] is False
        assert static_plan["refresh_status_visible"] is False
        assert static_plan["effective_refresh_interval_sec"] == 15

        graph_widget_ids = slot_definitions.warroom_graph_widget_ids()
        assert graph_widget_ids == [
            "market_monitor",
            "liquidity_pressure",
            "trade_flow_monitor",
        ]
        assert (
            slot_definitions.warroom_first_partial_redraw_candidate()
            == "market_monitor"
        )

        for widget_id in graph_widget_ids:
            assert slot_definitions.warroom_partial_update_enabled(widget_id) is True
            assert slot_definitions.warroom_chart_sensitive(widget_id) is True
            assert (
                slot_definitions.warroom_refresh_policy(widget_id).get(
                    "rerender_scope"
                )
                == "widget"
            )

        assert (
            slot_definitions.warroom_widget_slot("warroom_alert_engine").get(
                "refresh_mode"
            )
            == "poll_slow"
        )
        assert (
            slot_definitions.warroom_widget_slot("warroom_timeline").get(
                "refresh_mode"
            )
            == "poll_slow"
        )

    finally:
        live_shell.page_supports_auto_refresh = original_page_supports_auto_refresh
        live_shell.page_auto_refresh_interval_sec = (
            original_page_auto_refresh_interval_sec
        )
        live_shell.page_non_fragment_refresh_interval_sec = (
            original_page_non_fragment_refresh_interval_sec
        )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())