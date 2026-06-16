# path: ./btcts_next/src/btcts/market_engine/config.py
# desc: Runtime configuration model and environment loader for Market Engine.

from __future__ import annotations

import os
from dataclasses import dataclass

from .types import ExchangeProfileName


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value if value else default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class MarketEngineConfig:
    exchange: str
    symbol_raw: str
    instrument_id: str
    market_uid: str
    profile_name: ExchangeProfileName
    near_zone_levels: int = 50
    far_zone_levels: int = 200
    replay_batch_size: int = 1000
    write_market_state: bool = True


def load_market_engine_config() -> MarketEngineConfig:
    exchange = _env_str("BTCTS_MARKET_ENGINE_EXCHANGE", "bitflyer")
    symbol_raw = _env_str("BTCTS_MARKET_ENGINE_SYMBOL", "BTC_JPY")
    instrument_id = _env_str("BTCTS_MARKET_ENGINE_INSTRUMENT_ID", "bitflyer.spot.BTC_JPY")
    market_uid = _env_str("BTCTS_MARKET_ENGINE_MARKET_UID", f"{exchange}.spot.{symbol_raw}")
    profile_name = ExchangeProfileName(_env_str("BTCTS_MARKET_ENGINE_PROFILE", exchange))

    return MarketEngineConfig(
        exchange=exchange,
        symbol_raw=symbol_raw,
        instrument_id=instrument_id,
        market_uid=market_uid,
        profile_name=profile_name,
        near_zone_levels=_env_int("BTCTS_MARKET_ENGINE_NEAR_ZONE_LEVELS", 50),
        far_zone_levels=_env_int("BTCTS_MARKET_ENGINE_FAR_ZONE_LEVELS", 200),
        replay_batch_size=_env_int("BTCTS_MARKET_ENGINE_REPLAY_BATCH_SIZE", 1000),
        write_market_state=_env_bool("BTCTS_MARKET_ENGINE_WRITE_MARKET_STATE", True),
    )