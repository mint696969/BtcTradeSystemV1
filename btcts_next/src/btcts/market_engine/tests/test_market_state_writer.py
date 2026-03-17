# path: ./btcts_next/src/btcts/market_engine/tests/test_market_state_writer.py
# desc: Verify market_state writer pathing and append behavior for stable JSONL output.

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.market_state.writer import MarketStateWriter
from btcts.market_engine.types import BoundaryReason, TrustState


def _cfg() -> MarketEngineConfig:
    return MarketEngineConfig(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        instrument_id="bitflyer.spot.BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        profile_name="bitflyer",
        near_zone_levels=2,
        far_zone_levels=2,
        replay_batch_size=1000,
        write_market_state=True,
    )


def _record(*, best_bid: float, best_ask: float, spread: float, mid_price: float, source_series_id: str) -> MarketStateRecord:
    return MarketStateRecord(
        market_uid="bitflyer.spot.BTC_JPY",
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        collector_ts="2026-03-16T13:00:00Z",
        exchange_ts="2026-03-16T13:00:00Z",
        trust_state=TrustState.TRUSTED,
        boundary_reason=BoundaryReason.NONE,
        continuity_state="continuous",
        best_bid=best_bid,
        best_ask=best_ask,
        spread=spread,
        mid_price=mid_price,
        near_zone_bids=[{"price": best_bid, "size": 0.7}],
        near_zone_asks=[{"price": best_ask, "size": 1.5}],
        top_book_summary={
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "mid_price": mid_price,
        },
        near_zone_liquidity_summary={
            "bid_size_total": 0.7,
            "ask_size_total": 1.5,
        },
        imbalance_summary={
            "near_size_imbalance": -0.3636363636,
        },
        zone_density_metadata={"mode": "hybrid"},
        source_series_id=source_series_id,
        source_stream_session_id="bf-sess-1",
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[5]
    tmp_root = repo_root / "tmp" / "_market_state_writer_test"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    os.environ["BTC_TS_DATA_DIR"] = str(tmp_root / "data")

    writer = MarketStateWriter()
    cfg = _cfg()

    out1 = writer.write(
        cfg=cfg,
        state_type="market.overview",
        record=_record(
            best_bid=100.5,
            best_ask=101.0,
            spread=0.5,
            mid_price=100.75,
            source_series_id="bf-sess-1:series:100",
        ),
        date_str="2026-03-16",
        part_no=1,
    )

    out2 = writer.write(
        cfg=cfg,
        state_type="market.overview",
        record=_record(
            best_bid=100.4,
            best_ask=101.0,
            spread=0.6,
            mid_price=100.7,
            source_series_id="bf-sess-1:series:101",
        ),
        date_str="2026-03-16",
        part_no=1,
    )

    assert out1 == out2
    assert out1.exists()
    assert "market_state" in str(out1)
    assert "exchange=bitflyer" in str(out1)
    assert "symbol=BTC_JPY" in str(out1)
    assert "type=market.overview" in str(out1)
    assert "date=2026-03-16" in str(out1)

    lines = out1.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2

    row1 = json.loads(lines[0])
    row2 = json.loads(lines[1])

    assert row1["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert row1["best_bid"] == 100.5
    assert row1["best_ask"] == 101.0
    assert row1["spread"] == 0.5
    assert row1["mid_price"] == 100.75
    assert row1["trust_state"] == "trusted"
    assert row1["boundary_reason"] == "none"
    assert row1["continuity_state"] == "continuous"
    assert row1["zone_density_metadata"]["mode"] == "hybrid"

    assert row2["best_bid"] == 100.4
    assert row2["best_ask"] == 101.0
    assert row2["spread"] == 0.6
    assert row2["mid_price"] == 100.7
    assert row2["source_series_id"] == "bf-sess-1:series:101"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())