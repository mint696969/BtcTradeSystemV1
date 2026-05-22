# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_header_reading_caption.py
# desc: Verify WarRoom header exposes a compact market-reading caption.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.warroom_header import (  # noqa: E402
    build_warroom_market_reading_caption,
    build_warroom_operational_reading_caption,
)


def main() -> int:
    caption = build_warroom_market_reading_caption(
        state={
            "regime": "trend_up",
            "source_label": "live_canonical + research_experiment",
            "prediction_bias": "bullish",
            "prediction_caution": "medium",
            "prediction_switch_hint": "watch_reversal_path",
            "prediction_trace_summary": (
                "transition_sign:weakening_continuation / watch_reversal_path"
            ),
        }
    )
    assert "market_reading=trend_up" in caption
    assert "source=live_canonical + research_experiment" in caption
    assert "prediction_bias=bullish" in caption
    assert "prediction_caution=medium" in caption
    assert "prediction_switch_hint=watch_reversal_path" in caption
    assert (
        "prediction_trace=transition_sign:weakening_continuation / "
        "watch_reversal_path"
    ) in caption

    operational_caption = build_warroom_operational_reading_caption(
        state={
            "regime": "trend_up",
            "source_label": "live_canonical + research_experiment",
            "prediction_bias": "bullish",
            "prediction_caution": "medium",
        },
        summary_payload={
            "orderbook_active_event_compact_rows": [
                {
                    "event_name": "near_wall_continued",
                    "event_family": "wall",
                    "usage_grade": "strong",
                    "actionability": "review",
                    "forecast_horizon_hint": "short",
                    "half_life_sec": 30,
                    "side": "bid",
                }
            ],
            "orderbook_active_event_contracts": [
                {
                    "event_name": "raw_contract_should_not_be_used",
                    "event_family": "raw_contract",
                }
            ],
        },
    )
    assert "operational_reading=trend_up" in operational_caption
    assert "source=live_canonical + research_experiment" in operational_caption
    assert "active_event=near_wall_continued" in operational_caption
    assert "prediction_bias=bullish" in operational_caption
    assert "prediction_caution=medium" in operational_caption
    assert "review_mode=operator_review_only" in operational_caption
    assert "execution=not_instruction" in operational_caption

    empty_caption = build_warroom_market_reading_caption(state=None)
    assert empty_caption == "warroom_reading unavailable"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())