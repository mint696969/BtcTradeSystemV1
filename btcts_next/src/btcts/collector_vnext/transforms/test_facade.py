# path: ./btcts_next/src/btcts/collector_vnext/transforms/test_facade.py
# desc: Plain tests for Phase F collector transform facade skeleton.

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[5]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from typing import Any, Dict

from btcts.collector_vnext.transforms import facade
from btcts.collector_vnext.transforms.board_structural_hints import apply_board_structural_hints as direct_apply_board_structural_hints
from btcts.collector_vnext.transforms.raw_to_canonical import canonical_board_snapshot as direct_canonical_board_snapshot
from btcts.collector_vnext.transforms.raw_to_canonical_trades import canonical_trades as direct_canonical_trades
from btcts.collector_vnext.transforms.trade_structural_hints import apply_trade_structural_hints as direct_apply_trade_structural_hints
from btcts.collector_vnext.transforms.ws_board_to_canonical import canonical_board_event as direct_canonical_board_event
from btcts.collector_vnext.transforms.ws_trade_to_canonical import canonical_ws_trade as direct_canonical_ws_trade
from btcts.collector_vnext.venue_adapters.bitflyer_board import NormalizedBoardLevels


class _Adapter:
    def extract_board_levels(self, payload: Dict[str, Any]) -> NormalizedBoardLevels:
        return NormalizedBoardLevels(
            bids=payload.get("bids", []),
            asks=payload.get("asks", []),
        )


def _assert_facade_contract() -> None:
    expected = {
        "COLLECTOR_TRANSFORM_FACADE_VERSION",
        "BoardLevelsAdapter",
        "canonical_board_snapshot",
        "canonical_board_event",
        "canonical_trades",
        "canonical_ws_trade",
        "apply_board_structural_hints",
        "apply_trade_structural_hints",
    }
    assert set(facade.__all__) == expected
    assert facade.COLLECTOR_TRANSFORM_FACADE_VERSION == "collector_transform_facade.v1"


def _assert_board_snapshot_delegation() -> None:
    source = {"bids": [[100, 1]], "asks": [[101, 2]]}
    facade_payload = facade.canonical_board_snapshot(source, depth=1, snapshot_id="snap-1")
    direct_payload = direct_canonical_board_snapshot(source, depth=1, snapshot_id="snap-1")
    assert facade_payload == direct_payload


def _assert_board_event_delegation() -> None:
    source = {"bids": [[100, 1]], "asks": [[101, 2]]}
    adapter = _Adapter()
    facade_payload = facade.canonical_board_event(source, snapshot=False, adapter=adapter)
    direct_payload = direct_canonical_board_event(source, snapshot=False, adapter=adapter)
    assert facade_payload == direct_payload


def _assert_trade_delegation() -> None:
    source = {
        "items": [
            {"id": 1, "side": "BUY", "price": 100, "size": 0.1, "exec_date": "2026-01-01T00:00:00Z"},
            "bad",
        ]
    }
    facade_rows = facade.canonical_trades(source)
    direct_rows = direct_canonical_trades(source)
    assert facade_rows == direct_rows
    assert len(facade_rows) == 1
    assert facade.canonical_ws_trade(facade_rows[0]) == direct_canonical_ws_trade(facade_rows[0])


def _assert_structural_hint_delegation() -> None:
    board_payload = {"bids": [], "asks": []}
    board_kwargs = {
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "channel": "lightning_board_BTC_JPY",
        "provider": "bitflyer",
        "transport": "ws",
        "transport_role": "delta",
        "origin_role": "live_stream",
        "collector_id": "collector-1",
        "stream_session_id": "session-1",
        "current_event_id": "event-1",
        "base_snapshot_id": "base-1",
        "continuity_state": "continuous",
        "is_resync": False,
        "description": "test",
    }
    assert facade.apply_board_structural_hints(board_payload, **board_kwargs) == direct_apply_board_structural_hints(board_payload, **board_kwargs)

    trade_payload = {"trade_id": 1, "price": 100, "size": 0.1, "side": "BUY", "trade_ts": "2026-01-01T00:00:00Z"}
    trade_kwargs = {
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "channel": "lightning_executions_BTC_JPY",
        "provider": "bitflyer",
        "transport": "ws",
        "transport_role": "event",
        "origin_role": "live_stream",
        "collector_id": "collector-1",
        "stream_session_id": "session-1",
        "seen_in_rest": False,
        "seen_in_ws": True,
        "description": "test",
    }
    assert facade.apply_trade_structural_hints(trade_payload, **trade_kwargs) == direct_apply_trade_structural_hints(trade_payload, **trade_kwargs)


def main() -> int:
    _assert_facade_contract()
    _assert_board_snapshot_delegation()
    _assert_board_event_delegation()
    _assert_trade_delegation()
    _assert_structural_hint_delegation()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
