# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_live_bridge_origin_feed_state_cp16.py
# desc: CP16 tests for Collector live_bridge feed-state resolution from unified_origin_status.json. Display snapshot only; no runtime control side effects.

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.live_bridge import (  # noqa: E402
    _build_live_summary,
    _origin_status_feed_state,
)


def _iso(seconds_ago: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def test_cp16_origin_status_live_event_resolves_feed_live() -> None:
    status = {
        "ts": _iso(300),
        "ws_state": "LIVE",
        "lane_state": "live",
        "last_event_ts": _iso(3),
        "gap_detected": False,
        "resync_active": False,
    }
    assert _origin_status_feed_state(status) == "LIVE"


def test_cp16_origin_status_stale_event_resolves_feed_stale() -> None:
    status = {
        "ts": _iso(300),
        "ws_state": "LIVE",
        "lane_state": "live",
        "last_event_ts": _iso(180),
    }
    assert _origin_status_feed_state(status) == "STALE"


def test_cp16_origin_status_non_live_resolves_feed_stale() -> None:
    status = {"ts": _iso(2), "ws_state": "CLOSED", "lane_state": "stopped", "last_event_ts": _iso(2)}
    assert _origin_status_feed_state(status) == "STALE"


def test_cp16_live_summary_prefers_unified_origin_status_over_empty_audit() -> None:
    summary = _build_live_summary(
        status={"ts": _iso(300), "mode": "RUNNING"},
        health={"ts": _iso(5), "status": "healthy", "checks": []},
        daemon_health={"ts": _iso(5), "status": "healthy", "consecutive_failures": 0},
        checkpoint={"ts": _iso(5)},
        origin_status={"ts": _iso(300), "ws_state": "LIVE", "lane_state": "live", "last_event_ts": _iso(4)},
        audit_rows=[],
    )
    assert summary["feed_state"] == "LIVE"
    assert summary["overall_state"] == "RUNNING"
    assert summary["overall_reason"] == "all live checks aligned"


def test_cp16_live_bridge_source_has_no_runtime_control_side_effects() -> None:
    path = Path(__file__).resolve().parents[1] / "components/live_bridge.py"
    text = path.read_text(encoding="utf-8")
    forbidden = [
        "start_stack_detached",
        "start_chart_engine_detached",
        "start_market_regime_producer_loop_detached",
        "request_market_regime_producer_loop_safe_stop",
        "write_unified_supervisor_request",
        "subprocess.Popen",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
