# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_state_bridge.py
# desc: Small UI bridge test for reading latest market_state records into operator UI helpers.

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_overview,
    market_monitor_metrics,
    market_state_status_caption,
)
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.market_state.writer import MarketStateWriter
from btcts.market_engine.types import BoundaryReason, TrustState


def main() -> int:
    repo_root = Path(__file__).resolve().parents[5]
    tmp_root = repo_root / "tmp" / "_ui_market_state_bridge_test"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    os.environ["BTC_TS_DATA_DIR"] = str(tmp_root / "data")

    cfg = MarketEngineConfig(
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

    record = MarketStateRecord(
        market_uid="bitflyer.spot.BTC_JPY",
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        collector_ts="2026-03-16T13:00:00Z",
        exchange_ts="2026-03-16T13:00:00Z",
        trust_state=TrustState.TRUSTED,
        boundary_reason=BoundaryReason.NONE,
        continuity_state="continuous",
        best_bid=100.5,
        best_ask=101.0,
        spread=0.5,
        near_zone_bids=[{"price": 100.5, "size": 0.7}],
        near_zone_asks=[{"price": 101.0, "size": 1.5}],
        mid_price=100.75,
        top_book_summary={"best_bid": 100.5, "best_ask": 101.0, "spread": 0.5},
        near_zone_liquidity_summary={"bid_size_total": 1.7, "ask_size_total": 1.5},
        imbalance_summary={"near_size_imbalance": 0.0625},
        zone_density_metadata={"mode": "hybrid"},
        source_series_id="bf-sess-1:series:100",
        source_stream_session_id="bf-sess-1",
    )

    writer = MarketStateWriter()
    out = writer.write(
        cfg=cfg,
        state_type="market.overview",
        record=record,
        date_str="2026-03-16",
        part_no=1,
    )
    assert out.exists()

    loaded = load_market_overview(exchange="bitflyer", symbol_raw="BTC_JPY")
    assert loaded["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert loaded["best_bid"] == 100.5
    assert loaded["best_ask"] == 101.0
    assert loaded["spread"] == 0.5

    metrics = market_monitor_metrics(loaded)
    assert metrics["best_bid"] == 100.5
    assert metrics["best_ask"] == 101.0
    assert metrics["spread"] == 0.5
    assert metrics["bid_depth"] == 1.7
    assert metrics["ask_depth"] == 1.5
    assert metrics["imbalance"] == 0.0625

    caption = market_state_status_caption(loaded)
    assert "trust=trusted" in caption
    assert "boundary=none" in caption
    assert "series=bf-sess-1:series:100" in caption

    saved = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert saved["market_uid"] == "bitflyer.spot.BTC_JPY"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())