# path: ./btcts_next/src/btcts/market_engine/tests/test_runtime_profile_resolution.py
# desc: Verify MarketEngineRuntime resolves exchange profile from config.profile_name.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.runtime import MarketEngineRuntime


def _cfg(*, profile_name: str) -> MarketEngineConfig:
    return MarketEngineConfig(
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        instrument_id="bitflyer.spot.BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        profile_name=profile_name,
        near_zone_levels=2,
        far_zone_levels=2,
        replay_batch_size=1000,
        write_market_state=False,
    )


def main() -> int:
    runtime = MarketEngineRuntime(_cfg(profile_name="bitflyer"))
    assert runtime.config.profile_name == "bitflyer"
    assert runtime._profile.__class__.__name__ == "BitflyerProfile"
    assert runtime._engine._profile is runtime._profile

    alias_runtime = MarketEngineRuntime(_cfg(profile_name="bf"))
    assert alias_runtime.config.profile_name == "bf"
    assert alias_runtime._profile.__class__.__name__ == "BitflyerProfile"
    assert alias_runtime._engine._profile is alias_runtime._profile

    baseline = runtime._profile.orderbook_semantic_policy()
    assert baseline["wall_near_rank_threshold"] == 5
    assert baseline["wall_ratio_threshold"] == 0.30
    assert baseline["pressure_threshold"] == 0.20

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())