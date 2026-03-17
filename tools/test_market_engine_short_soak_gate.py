# path: ./tools/test_market_engine_short_soak_gate.py
# desc: Verify the minimum short-soak gate conditions for Market Engine market_state production and UI observability.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import shutil
from pathlib import Path

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_overview,
    market_monitor_metrics,
    market_state_status_caption,
)
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.runtime import MarketEngineRuntime


REPO_ROOT = Path(__file__).resolve().parents[1]


def _snapshot_event() -> dict:
    return {
        "record_type": "market.orderbook.snapshot",
        "stream_session_id": "gate-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": 100,
        "source_event_id": "gate-snap-1",
        "collector_ts": "2026-03-16T14:00:00Z",
        "exchange_ts": "2026-03-16T14:00:00Z",
        "payload": {
            "event_type": "snapshot",
            "continuity_state": "resynced",
            "stream_event_no": 1,
            "bids": [
                {"price": 100.0, "size": 1.0},
                {"price": 99.5, "size": 2.0},
            ],
            "asks": [
                {"price": 101.0, "size": 1.5},
                {"price": 101.5, "size": 2.5},
            ],
        },
    }


def _diff_event() -> dict:
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": "gate-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": 101,
        "source_event_id": "gate-diff-1",
        "collector_ts": "2026-03-16T14:00:01Z",
        "exchange_ts": "2026-03-16T14:00:01Z",
        "payload": {
            "event_type": "delta",
            "continuity_state": "continuous",
            "stream_event_no": 2,
            "bids": [{"price": 100.5, "size": 0.7}],
            "asks": [],
        },
    }


def _gap_event() -> dict:
    return {
        "record_type": "stream.gap_detected",
        "stream_session_id": "gate-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": 102,
        "source_event_id": "gate-gap-1",
        "collector_ts": "2026-03-16T14:00:02Z",
        "exchange_ts": "2026-03-16T14:00:02Z",
        "payload": {},
    }


def main() -> int:
    tmp_root = REPO_ROOT / "tmp" / "_market_engine_short_soak_gate"
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

    runtime = MarketEngineRuntime(cfg)

    step1 = runtime.step(_snapshot_event())
    step2 = runtime.step(_diff_event())
    step3 = runtime.step(_gap_event())

    assert step1.output_path is not None
    assert step2.output_path is not None
    assert step3.output_path is not None

    latest = load_market_overview(exchange="bitflyer", symbol_raw="BTC_JPY")
    assert latest["market_uid"] == "bitflyer.spot.BTC_JPY"

    metrics = market_monitor_metrics(latest)
    assert metrics["best_bid"] is not None
    assert metrics["best_ask"] is not None
    assert metrics["spread"] is not None

    caption = market_state_status_caption(latest)
    assert "trust=" in caption
    assert "boundary=" in caption
    assert "series=" in caption

    out_path = Path(step3.output_path)
    lines = out_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 3

    rows = [json.loads(line) for line in lines]
    assert any(row.get("trust_state") in {"trusted", "provisional", "broken", "quarantined"} for row in rows)
    assert any("boundary_reason" in row for row in rows)
    assert any("best_bid" in row and "best_ask" in row for row in rows)

    summary = {
        "ok": True,
        "output_path": str(out_path),
        "record_count": len(rows),
        "latest_trust_state": latest.get("trust_state"),
        "latest_boundary_reason": latest.get("boundary_reason"),
        "latest_best_bid": latest.get("best_bid"),
        "latest_best_ask": latest.get("best_ask"),
        "latest_spread": latest.get("spread"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())