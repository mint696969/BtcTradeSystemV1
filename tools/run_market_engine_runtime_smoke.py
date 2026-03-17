# path: ./tools/run_market_engine_runtime_smoke.py
# desc: Emit synthetic market_engine runtime events for a short continuous smoke so market_state observer tests have live producer input.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import shutil
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.runtime import MarketEngineRuntime


REPO_ROOT = Path(__file__).resolve().parents[1]


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except Exception:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _iso_at(base: datetime, sec_offset: float) -> str:
    ts = base + timedelta(seconds=sec_offset)
    return ts.isoformat().replace("+00:00", "Z")


def _snapshot_event(base: datetime, seq: int) -> dict:
    t = float(seq)
    return {
        "record_type": "market.orderbook.snapshot",
        "stream_session_id": "smoke-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": seq,
        "source_event_id": f"smoke-snap-{seq}",
        "collector_ts": _iso_at(base, t),
        "exchange_ts": _iso_at(base, t),
        "payload": {
            "event_type": "snapshot",
            "continuity_state": "resynced",
            "stream_event_no": seq,
            "bids": [
                {"price": 100.0, "size": 1.0},
                {"price": 99.5, "size": 2.0},
                {"price": 99.0, "size": 3.0},
            ],
            "asks": [
                {"price": 101.0, "size": 1.5},
                {"price": 101.5, "size": 2.5},
                {"price": 102.0, "size": 3.5},
            ],
        },
    }


def _diff_event(base: datetime, seq: int, bid_price: float) -> dict:
    t = float(seq)
    return {
        "record_type": "market.orderbook.diff",
        "stream_session_id": "smoke-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": seq,
        "source_event_id": f"smoke-diff-{seq}",
        "collector_ts": _iso_at(base, t),
        "exchange_ts": _iso_at(base, t),
        "payload": {
            "event_type": "delta",
            "continuity_state": "continuous",
            "stream_event_no": seq,
            "bids": [{"price": bid_price, "size": 0.7}],
            "asks": [],
        },
    }


def _gap_event(base: datetime, seq: int) -> dict:
    t = float(seq)
    return {
        "record_type": "stream.gap_detected",
        "stream_session_id": "smoke-sess-1",
        "instrument_id": "bitflyer.spot.BTC_JPY",
        "exchange": "bitflyer",
        "symbol": "BTC_JPY",
        "sequence_id": seq,
        "source_event_id": f"smoke-gap-{seq}",
        "collector_ts": _iso_at(base, t),
        "exchange_ts": _iso_at(base, t),
        "payload": {},
    }


def main() -> int:
    duration_sec = _env_float("BTCTS_MARKET_ENGINE_SMOKE_SECONDS", 60.0)
    interval_sec = _env_float("BTCTS_MARKET_ENGINE_SMOKE_INTERVAL_SEC", 2.0)
    clean_root = os.getenv("BTCTS_MARKET_ENGINE_SMOKE_CLEAN_ROOT", "0").strip().lower() in {"1", "true", "yes", "on"}

    data_root = os.getenv("BTC_TS_DATA_DIR", "").strip()
    if not data_root:
        data_root = str(REPO_ROOT / "tmp" / "_market_engine_runtime_smoke" / "data")
        os.environ["BTC_TS_DATA_DIR"] = data_root

    data_root_path = Path(data_root)
    if clean_root and data_root_path.exists():
        shutil.rmtree(data_root_path)

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

    started = time.monotonic()
    base = datetime.now(timezone.utc)
    seq = 100
    written = 0
    last_output_path: str | None = None

    # まず anchor を確実に1発入れる
    first = runtime.step(_snapshot_event(base, seq))
    written += 1
    last_output_path = first.output_path
    seq += 1

    while (time.monotonic() - started) < duration_sec:
        cycle = written % 6
        if cycle == 4:
            result = runtime.step(_gap_event(base, seq))
        elif cycle == 5:
            result = runtime.step(_snapshot_event(base, seq))
        else:
            bid_price = 100.1 + ((written % 8) * 0.05)
            result = runtime.step(_diff_event(base, seq, bid_price=bid_price))

        written += 1
        last_output_path = result.output_path
        seq += 1
        time.sleep(interval_sec)

    summary = {
        "ok": True,
        "data_root": data_root,
        "duration_sec": duration_sec,
        "interval_sec": interval_sec,
        "records_written": written,
        "last_output_path": last_output_path,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())