# path: ./btcts_next/src/btcts/market_engine/tests/test_market_engine_live_lock.py
# desc: Minimal lock contract test for Market Engine live runtime single-instance guard.

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.lock import (
    acquire_live_runtime_lock,
    live_runtime_lock_path,
    read_live_runtime_lock,
    release_live_runtime_lock,
)


def _cfg() -> MarketEngineConfig:
    return MarketEngineConfig(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        instrument_id="bitflyer.spot.BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        profile_name="bitflyer",
        near_zone_levels=50,
        far_zone_levels=200,
        replay_batch_size=1000,
        write_market_state=False,
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[5]
    tmp_root = repo_root / "tmp" / "_market_engine_live_lock_test"

    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    (tmp_root / "data").mkdir(parents=True, exist_ok=True)
    (tmp_root / "logs").mkdir(parents=True, exist_ok=True)

    prev_data = os.environ.get("BTC_TS_DATA_DIR")
    prev_logs = os.environ.get("BTC_TS_LOGS_DIR")

    os.environ["BTC_TS_DATA_DIR"] = str(tmp_root / "data")
    os.environ["BTC_TS_LOGS_DIR"] = str(tmp_root / "logs")

    cfg = _cfg()

    try:
        lock_path = live_runtime_lock_path(cfg)
        if lock_path.exists():
            lock_path.unlink(missing_ok=True)

        acquired1, info1 = acquire_live_runtime_lock(cfg)
        assert acquired1 is True
        assert lock_path.exists()
        assert int(info1["pid"]) == os.getpid()

        existing = read_live_runtime_lock(cfg)
        assert isinstance(existing, dict)
        assert int(existing["pid"]) == os.getpid()

        acquired2, info2 = acquire_live_runtime_lock(cfg)
        assert acquired2 is False
        assert int(info2["pid"]) == os.getpid()

        release_live_runtime_lock(cfg)
        assert not lock_path.exists()

        acquired3, info3 = acquire_live_runtime_lock(cfg)
        assert acquired3 is True
        assert int(info3["pid"]) == os.getpid()

        release_live_runtime_lock(cfg)
        assert not lock_path.exists()

        print("ok")
        return 0
    finally:
        release_live_runtime_lock(cfg)
        if prev_data is None:
            os.environ.pop("BTC_TS_DATA_DIR", None)
        else:
            os.environ["BTC_TS_DATA_DIR"] = prev_data

        if prev_logs is None:
            os.environ.pop("BTC_TS_LOGS_DIR", None)
        else:
            os.environ["BTC_TS_LOGS_DIR"] = prev_logs

if __name__ == "__main__":
    raise SystemExit(main())