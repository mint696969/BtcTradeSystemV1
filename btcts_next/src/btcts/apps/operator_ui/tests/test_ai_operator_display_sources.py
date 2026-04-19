# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_display_sources.py
# desc: Verify ai_operator display source loader stays a thin boundary over market_state_bridge.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.ai_operator_display_sources as display_sources  # noqa: E402


def main() -> int:
    original_load_market_summary_widget_model = (
        display_sources.load_market_summary_widget_model
    )
    original_load_prediction_summary_widget_model = (
        display_sources.load_prediction_summary_widget_model
    )

    try:
        display_sources.load_market_summary_widget_model = lambda: {
            "widget_kind": "market_summary_widget"
        }
        display_sources.load_prediction_summary_widget_model = lambda: {
            "widget_kind": "prediction_summary_widget"
        }

        loaded = display_sources.load_operator_display_sources()
        assert loaded == {
            "summary_widget": {"widget_kind": "market_summary_widget"},
            "prediction_widget": {"widget_kind": "prediction_summary_widget"},
        }
    finally:
        display_sources.load_market_summary_widget_model = (
            original_load_market_summary_widget_model
        )
        display_sources.load_prediction_summary_widget_model = (
            original_load_prediction_summary_widget_model
        )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())