# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_presenter.py
# desc: Verify ai_operator presenter keeps display captions and live-local fallback wording stable.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.ai_operator_presenter import (  # noqa: E402
    build_display_state,
)


def main() -> int:
    state = {
        "event_ts": "2026-04-17T02:10:00Z",
        "regime": "trend_up",
        "best_strategy": "scenario_prediction_core",
        "pressure_bias": "buy_pressure",
        "data_source": "live_canonical",
    }

    display_state = build_display_state(
        lang="en",
        state=state,
        action="long_watch",
        risk="low",
        answer=(
            "external AI failed -> fallback local\n"
            "reason: timeout\n\n"
            "Current market state is stable."
        ),
        runtime_source="fallback-local",
        ai_mode="external",
    )

    assert display_state["is_live_market"] is True
    assert display_state["display_action_label"] == "LONG WATCH"
    assert display_state["display_risk_label"] == "LOW"
    assert display_state["display_ai_mode"] == "live-local"
    assert display_state["display_notice_kind"] == "info"
    assert display_state["display_answer"].startswith(
        "local AI mode active: generating a local summary based on live_canonical"
    )
    assert "Current market state is stable." in display_state["display_answer"]
    assert "regime=trend_up" in display_state["status_caption"]
    assert "best_strategy=scenario_prediction_core" in display_state["status_caption"]
    assert "pressure_bias=buy_pressure" in display_state["status_caption"]
    assert "Runtime Source=live-local" in display_state["runtime_caption"]

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())