# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_push_widgets_rt_live_receiver_default_launch.py
# desc: Verifies WarRoom RT0 default launch uses bitFlyer collector provider connector and launch script sets default endpoint.

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
LAUNCH = REPO_ROOT / "tools/run_operator_ui_sr_fx_dhot.ps1"
RT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/rt_live_receiver_bridge.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_WARROOM_PUSH_WIDGET_RT0_DEFAULT_LAUNCH_2026-07-05.md"

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets import rt_live_receiver_bridge as rt  # noqa: E402


class FakeBoardMessage:
    channel = "lightning_board_snapshot_FX_BTC_JPY"
    payload = {"bids": [{"price": 100.0, "size": 1.2}], "asks": [{"price": 101.0, "size": 0.8}]}
    received_ts = "2026-07-05T00:00:00Z"


class FakeExecutionMessage:
    channel = "lightning_executions_FX_BTC_JPY"
    payload = [{"price": 100.5, "size": 0.1, "side": "BUY"}]
    received_ts = "2026-07-05T00:00:01Z"


def test_bitflyer_provider_connection_maps_board_and_execution_messages(monkeypatch) -> None:
    def fake_board(symbol: str, *, ssl_verify: bool = True, ca_file: str | None = None):
        assert symbol == "FX_BTC_JPY"
        yield FakeBoardMessage()

    def fake_exec(symbol: str, *, ssl_verify: bool = True, recv_timeout_sec: float = 60.0, ca_file: str | None = None):
        assert symbol == "FX_BTC_JPY"
        yield FakeExecutionMessage()

    monkeypatch.setattr(rt, "_connect_and_stream_board", fake_board)
    monkeypatch.setattr(rt, "_connect_and_stream_executions", fake_exec)
    conn = rt._BitflyerCollectorConnection("FX_BTC_JPY", {"ssl_verify": False})
    first = conn.recv()
    second = conn.recv()
    assert first["messages"][0]["topic_key"] in {"market.depth", "market.liquidity"}
    assert second["messages"][0]["topic_key"] == "market.trades"
    assert second["messages"][0]["value"]["last_price"] == 100.5


def test_default_launch_script_sets_warroom_push_widget_endpoint() -> None:
    launch = LAUNCH.read_text(encoding="utf-8-sig")
    assert "WARROOM_PUSH_WIDGET_WS_URL" in launch
    assert 'WARROOM_PUSH_WIDGET_WS_URL = "dhot://unified_market_state"' in launch
    assert 'WARROOM_PUSH_WIDGET_SOURCE = "dhot_unified_market_state_provider"' in launch
    rt_text = RT.read_text(encoding="utf-8-sig")
    assert "class _BitflyerCollectorConnection" in rt_text
    assert "connect_and_stream_board" in rt_text
    assert "connect_and_stream_executions" in rt_text
    doc = DOC.read_text(encoding="utf-8-sig")
    assert "warroom_push_widget_realtime_observation_default=true" in doc
    assert "warroom_push_widget_endpoint_default=dhot://unified_market_state" in doc
    assert "warroom_push_widget_source_default=dhot_unified_market_state_provider" in doc
    assert "extra_exchange_websocket_opened_by_default=false" in doc
