# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_refresh_diagnostics.py
# desc: Verify WarRoom diagnostics summarize fragment refresh without page reload.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.views.warroom_page as warroom_page  # noqa: E402


def main() -> int:
    original_page_non_fragment_refresh_interval_sec = (
        warroom_page.live_shell.page_non_fragment_refresh_interval_sec
    )

    try:
        warroom_page.live_shell.page_non_fragment_refresh_interval_sec = (
            lambda page_id, *, default_sec=15: (
                5 if page_id == "warroom" else default_sec
            )
        )

        summary = warroom_page._warroom_refresh_diagnostics_summary()

        assert summary["fragment_widget_count"] == 9
        assert summary["fragment_interval_sec"] == 3
        assert summary["page_reload_interval_sec"] == 5
        assert summary["hybrid_refresh"] is True

    finally:
        warroom_page.live_shell.page_non_fragment_refresh_interval_sec = (
            original_page_non_fragment_refresh_interval_sec
        )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())