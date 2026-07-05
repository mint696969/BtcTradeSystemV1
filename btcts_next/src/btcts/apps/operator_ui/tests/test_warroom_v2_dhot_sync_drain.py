# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_dhot_sync_drain.py
# desc: Verifies D-hot source is synchronously read and drained in the same WarRoom render cycle.

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_DHOT_SYNC_DRAIN_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.rt_live_receiver_bridge import (  # noqa: E402
    WARROOM_RT_LIVE_DRAINED_MESSAGES_STATE_KEY,
    WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY,
    ensure_warroom_push_widget_live_observation_runtime,
)


def _state_root(tmp_path: Path) -> Path:
    root = tmp_path / "state"
    status_dir = root / "collector_vnext"
    status_dir.mkdir(parents=True)
    (status_dir / "unified_market_state_status.json").write_text(
        json.dumps(
            {
                "lane_state": "live",
                "last_event_ts": "2026-07-05T04:11:00Z",
                "last_best_bid": 10100000.0,
                "last_best_ask": 10101000.0,
                "last_spread": 1000.0,
                "last_symbol_raw": "FX_BTC_JPY",
                "last_market_uid": "bitflyer.fx.FX_BTC_JPY",
                "last_source_series_id": "collector.unified_market_state",
                "step_count": 42,
                "last_error": None,
            }
        ),
        encoding="utf-8",
    )
    return root


def test_dhot_source_is_sync_read_and_drained_same_cycle(tmp_path: Path) -> None:
    state: dict[str, Any] = {}
    status = ensure_warroom_push_widget_live_observation_runtime(
        state,
        endpoint_url="dhot://unified_market_state",
        runtime_key="test_dhot_sync_drain",
        runtime_config={"source": "dhot_unified_market_state_provider", "state_root": str(_state_root(tmp_path)), "poll_interval_sec": 999},
    )
    assert status["dhot_sync_read_applied"] is True
    assert status["drained_message_count"] >= 6
    assert state[WARROOM_RT_LIVE_DRAINED_MESSAGES_STATE_KEY]
    topics = {msg["topic_key"] for msg in state[WARROOM_RT_LIVE_DRAINED_MESSAGES_STATE_KEY]}
    assert {"market.depth", "market.spread", "market.liquidity", "receiver.lifecycle", "warroom.summary", "warroom.alerts"}.issubset(topics)
    assert state[WARROOM_RT_LIVE_RUNTIME_STATUS_STATE_KEY]["received_message_count"] >= 6


def test_doc_markers() -> None:
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_v2_dhot_sync_drain_done=true" in doc
    assert "dhot_sync_read_applied=true" in doc
    assert "same_render_cycle_drain_ready=true" in doc
