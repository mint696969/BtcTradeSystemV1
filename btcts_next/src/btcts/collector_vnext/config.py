# path: ./btcts_next/src/btcts/collector_vnext/config.py
# desc: Collector vNext runtime configuration loader with environment overrides.

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from ._env_utils import env_int


def _env_str(name: str, default: str) -> str:
    v = os.getenv(name, "").strip()
    return v if v else default


def _env_str_fallback(names: List[str], default: str) -> str:
    for name in names:
        v = os.getenv(name, "").strip()
        if v:
            return v
    return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _env_list(name: str, default: List[str]) -> List[str]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return list(default)
    return [x.strip() for x in raw.split(",") if x.strip()]


@dataclass(frozen=True)
class RotationPolicy:
    max_bytes: int = 128 * 1024 * 1024
    max_lines: int = 200_000


@dataclass(frozen=True)
class CollectorConfig:
    collector_id: str
    collector_role: str
    host_name: str
    data_root: Path
    logs_root: Path
    state_root: Path
    enabled_exchanges: List[str] = field(default_factory=lambda: ["bitflyer"])
    enabled_streams: List[str] = field(default_factory=lambda: ["stream.started"])
    market: str = "spot"
    symbol: str = "BTC_JPY"
    instrument_id: str = "bitflyer.spot.BTC_JPY"
    ws_ssl_verify: bool = True
    rotation: RotationPolicy = field(default_factory=RotationPolicy)

    def roots(self) -> Dict[str, Path]:
        return {
            "raw": self.data_root / "collector_raw",
            "canonical": self.data_root / "market_data",
            "logs": self.logs_root / "collector_vnext",
            "state": self.state_root / "collector_vnext",
        }


def load_config() -> CollectorConfig:
    data_root = Path(
        _env_str_fallback(
            ["BTC_TS_DATA_DIR", "BTCTS_DATA_ROOT"],
            r"E:\\btc_ts\\data",
        )
    )
    logs_root = Path(
        _env_str_fallback(
            ["BTC_TS_LOGS_DIR", "BTCTS_LOGS_ROOT"],
            r"E:\\btc_ts\\logs",
        )
    )
    state_root = Path(
        _env_str_fallback(
            ["BTCTS_STATE_ROOT"],
            r"E:\\btc_ts\\state",
        )
    )

    collector_id = _env_str("BTCTS_COLLECTOR_ID", "collector_main")
    collector_role = _env_str("BTCTS_COLLECTOR_ROLE", "production")
    host_name = _env_str("BTCTS_HOST_NAME", os.getenv("COMPUTERNAME", "unknown-host"))

    enabled_exchanges = _env_list("BTCTS_ENABLED_EXCHANGES", ["bitflyer"])
    enabled_streams = _env_list("BTCTS_ENABLED_STREAMS", ["stream.started"])

    market = _env_str("BTCTS_MARKET", "spot")
    symbol = _env_str("BTCTS_SYMBOL", "BTC_JPY")
    instrument_id = _env_str("BTCTS_INSTRUMENT_ID", "bitflyer.spot.BTC_JPY")

    ws_ssl_verify = _env_bool("BTCTS_WS_SSL_VERIFY", True)

    rotation = RotationPolicy(
        max_bytes=env_int("BTCTS_ROTATE_MAX_BYTES", 128 * 1024 * 1024),
        max_lines=env_int("BTCTS_ROTATE_MAX_LINES", 200_000),
    )

    return CollectorConfig(
        collector_id=collector_id,
        collector_role=collector_role,
        host_name=host_name,
        data_root=data_root,
        logs_root=logs_root,
        state_root=state_root,
        enabled_exchanges=enabled_exchanges,
        enabled_streams=enabled_streams,
        market=market,
        symbol=symbol,
        instrument_id=instrument_id,
        ws_ssl_verify=ws_ssl_verify,
        rotation=rotation,
    )