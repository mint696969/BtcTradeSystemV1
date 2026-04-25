# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_summary_refresh_path.py
# desc: Verify WarRoom summary widgets use fragment refresh path and keep slot fallback path.

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.views.warroom_page as warroom_page  # noqa: E402


@contextmanager
def _recording_slot(calls: list[tuple], widget_id: str):
    calls.append(("slot", widget_id))
    yield


def main() -> int:
    original_render_fragment_slot = warroom_page.live_shell.render_fragment_slot
    original_slot_widget_from_meta = warroom_page.live_shell.slot_widget_from_meta

    calls: list[tuple] = []

    try:
        def _fake_render_fragment_slot(
            meta,
            render_body,
            *,
            enabled: bool = True,
            default_sec: int = 15,
        ) -> None:
            calls.append(("fragment", str(meta["widget_id"]), enabled))
            render_body()

        def _fake_slot_widget_from_meta(meta):
            return _recording_slot(calls, str(meta["widget_id"]))

        warroom_page.live_shell.render_fragment_slot = _fake_render_fragment_slot
        warroom_page.live_shell.slot_widget_from_meta = _fake_slot_widget_from_meta

        target_widget_ids = [
            "warroom_header",
            "market_regime",
            "ai_signal",
            "strategy_state",
            "risk_monitor",
            "agent_panels",
        ]
        assert warroom_page._warroom_reading_block_order() == (
            "current_market_summary_reading",
            "current_active_event_reading",
            "current_tactic_prediction_reading",
            "operator_support_review_reading",
        )
        assert warroom_page._warroom_reading_block_captions() == {
            "current_market_summary_reading": (
                "read current regime / source / compact market state first"
            ),
            "current_active_event_reading": (
                "read active event / liquidity / graph context as current market evidence"
            ),
            "current_tactic_prediction_reading": (
                "read tactic stance / prediction as review support, not execution"
            ),
            "operator_support_review_reading": (
                "read watch / timeline / decision support as operator review context"
            ),
        }

        original_load_market_summary_status_payload = (
            warroom_page.load_market_summary_status_payload
        )
        try:
            warroom_page.load_market_summary_status_payload = lambda: {
                "orderbook_active_event_contracts": [
                    {
                        "event_name": "near_wall_continued",
                        "event_family": "wall",
                        "usage_grade": "strong",
                        "actionability": "review",
                        "forecast_horizon_hint": "short",
                        "half_life_sec": 30,
                        "side": "bid",
                    }
                ]
            }
            assert warroom_page._warroom_active_event_reading_caption() == (
                "near_wall_continued (wall / strong / review / short / half_life=30 / bid)"
            )
        finally:
            warroom_page.load_market_summary_status_payload = (
                original_load_market_summary_status_payload
            )
        for widget_id in target_widget_ids:
            warroom_page._render_fragmentable_warroom_widget(
                widget_id,
                lambda widget_id=widget_id: calls.append(("render", widget_id)),
                fragment_enabled=True,
            )

        fragment_widget_ids = [
            row[1]
            for row in calls
            if row[0] == "fragment"
        ]
        rendered_widget_ids = [
            row[1]
            for row in calls
            if row[0] == "render"
        ]
        slot_widget_ids = [
            row[1]
            for row in calls
            if row[0] == "slot"
        ]

        assert fragment_widget_ids == target_widget_ids
        assert rendered_widget_ids == target_widget_ids
        assert slot_widget_ids == []

        calls.clear()

        warroom_page._render_fragmentable_warroom_widget(
            "warroom_header",
            lambda: calls.append(("render", "warroom_header")),
            fragment_enabled=False,
        )

        assert ("fragment", "warroom_header", True) not in calls
        assert ("slot", "warroom_header") in calls
        assert ("render", "warroom_header") in calls

    finally:
        warroom_page.live_shell.render_fragment_slot = original_render_fragment_slot
        warroom_page.live_shell.slot_widget_from_meta = original_slot_widget_from_meta

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())