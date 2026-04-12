# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_live_shell_refresh_plan.py
# desc: Verify refresh planning keeps health on fragment path and logs on page reload path.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.live_shell as live_shell  # noqa: E402


def main() -> int:
    original_page_supports_auto_refresh = live_shell.page_supports_auto_refresh
    original_page_auto_refresh_interval_sec = live_shell.page_auto_refresh_interval_sec

    try:
        live_shell.page_supports_auto_refresh = lambda page_id: page_id in {
            "health",
            "logs",
            "collector",
        }

        def _fake_interval(page_id: str, *, default_sec: int = 15) -> int:
            if page_id == "health":
                return 5
            if page_id == "logs":
                return 10
            if page_id == "collector":
                return 3
            return default_sec

        live_shell.page_auto_refresh_interval_sec = _fake_interval

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

        collector_plan = live_shell.resolve_page_refresh_plan(
            page_key="collector",
            ui_auto_refresh=False,
            ui_refresh_interval_sec=15,
            fragment_supported=True,
        )
        assert collector_plan["slot_refresh_target"] is True
        assert collector_plan["page_auto_refresh_target"] is True
        assert collector_plan["page_reload_enabled"] is False
        assert collector_plan["fragment_refresh_enabled"] is False
        assert collector_plan["refresh_status_visible"] is False
        assert collector_plan["effective_refresh_interval_sec"] == 3

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

    finally:
        live_shell.page_supports_auto_refresh = original_page_supports_auto_refresh
        live_shell.page_auto_refresh_interval_sec = (
            original_page_auto_refresh_interval_sec
        )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())