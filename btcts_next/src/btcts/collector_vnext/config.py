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


class ConfigValidationError(ValueError):
    pass


@dataclass(frozen=True)
class RotationPolicy:
    max_bytes: int = 128 * 1024 * 1024
    max_lines: int = 200_000


@dataclass(frozen=True)
class MarketIdentity:
    role: str
    exchange: str
    market_type: str
    product_code: str
    market_uid: str
    enabled: bool = True

    def normalized(self) -> "MarketIdentity":
        return MarketIdentity(
            role=self.role.strip().lower(),
            exchange=self.exchange.strip().lower(),
            market_type=self.market_type.strip().lower(),
            product_code=self.product_code.strip(),
            market_uid=self.market_uid.strip(),
            enabled=bool(self.enabled),
        )

    def as_dict(self) -> Dict[str, object]:
        x = self.normalized()
        return {
            "role": x.role,
            "exchange": x.exchange,
            "market_type": x.market_type,
            "product_code": x.product_code,
            "market_uid": x.market_uid,
            "enabled": x.enabled,
        }


def validate_market_identities(
    reference_market: MarketIdentity,
    execution_market: MarketIdentity,
) -> None:
    ref = reference_market.normalized()
    exe = execution_market.normalized()

    errors: List[str] = []

    if ref.enabled:
        if ref.role != "reference_signal":
            errors.append("reference_market.role must be reference_signal")
        if not ref.exchange:
            errors.append("reference_market.exchange is required")
        if not ref.market_type:
            errors.append("reference_market.market_type is required")
        if not ref.product_code:
            errors.append("reference_market.product_code is required")
        if not ref.market_uid:
            errors.append("reference_market.market_uid is required")

    if exe.enabled:
        if exe.role != "execution":
            errors.append("execution_market.role must be execution")
        if not exe.exchange:
            errors.append("execution_market.exchange is required")
        if not exe.market_type:
            errors.append("execution_market.market_type is required")
        if not exe.product_code:
            errors.append("execution_market.product_code is required")
        if not exe.market_uid:
            errors.append("execution_market.market_uid is required")
        if exe.market_type == "spot":
            errors.append("execution_market.market_type must not be spot")
        if ".spot." in exe.market_uid.lower() or exe.market_uid.lower().endswith(".spot"):
            errors.append("execution_market.market_uid must not be a spot market uid")
        if ref.enabled and exe.market_uid == ref.market_uid:
            errors.append("execution_market.market_uid must differ from reference_market.market_uid")
        if ref.enabled and exe.product_code == ref.product_code and exe.market_type == ref.market_type:
            errors.append("execution_market must not duplicate reference market identity")

    if errors:
        raise ConfigValidationError("; ".join(errors))


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
    reference_market: MarketIdentity = field(
        default_factory=lambda: MarketIdentity(
            role="reference_signal",
            exchange="bitflyer",
            market_type="spot",
            product_code="BTC_JPY",
            market_uid="bitflyer.spot.BTC_JPY",
            enabled=True,
        )
    )
    execution_market: MarketIdentity = field(
        default_factory=lambda: MarketIdentity(
            role="execution",
            exchange="bitflyer",
            market_type="fx",
            product_code="FX_BTC_JPY",
            market_uid="bitflyer.fx.FX_BTC_JPY",
            enabled=True,
        )
    )
    ws_ssl_verify: bool = True
    ws_ca_file: Path | None = None
    rotation: RotationPolicy = field(default_factory=RotationPolicy)

    def roots(self) -> Dict[str, Path]:
        return {
            "raw": self.data_root / "collector_raw",
            "canonical": self.data_root / "market_data",
            "logs": self.logs_root / "collector_vnext",
            "state": self.state_root / "collector_vnext",
        }

    def market_identity_summary(self) -> Dict[str, object]:
        return {
            "legacy": {
                "market": self.market,
                "symbol": self.symbol,
                "instrument_id": self.instrument_id,
            },
            "reference_market": self.reference_market.as_dict(),
            "execution_market": self.execution_market.as_dict(),
        }


def _load_reference_market() -> MarketIdentity:
    return MarketIdentity(
        role="reference_signal",
        exchange=_env_str("BTCTS_REFERENCE_EXCHANGE", "bitflyer"),
        market_type=_env_str("BTCTS_REFERENCE_MARKET_TYPE", "spot"),
        product_code=_env_str("BTCTS_REFERENCE_PRODUCT_CODE", "BTC_JPY"),
        market_uid=_env_str("BTCTS_REFERENCE_MARKET_UID", "bitflyer.spot.BTC_JPY"),
        enabled=_env_bool("BTCTS_REFERENCE_MARKET_ENABLED", True),
    ).normalized()


def _load_execution_market() -> MarketIdentity:
    product_code = _env_str_fallback(
        ["BTCTS_EXECUTION_PRODUCT_CODE", "BTCTS_BITFLYER_EXECUTION_PRODUCT_CODE"],
        "FX_BTC_JPY",
    )
    default_uid = f"bitflyer.fx.{product_code}"
    return MarketIdentity(
        role="execution",
        exchange=_env_str("BTCTS_EXECUTION_EXCHANGE", "bitflyer"),
        market_type=_env_str("BTCTS_EXECUTION_MARKET_TYPE", "fx"),
        product_code=product_code,
        market_uid=_env_str("BTCTS_EXECUTION_MARKET_UID", default_uid),
        enabled=_env_bool("BTCTS_EXECUTION_MARKET_ENABLED", True),
    ).normalized()


def load_config() -> CollectorConfig:
    data_root = Path(
        _env_str_fallback(
            ["BTC_TS_DATA_DIR", "BTCTS_DATA_ROOT"],
            r"E:\btc_ts\data",
        )
    )
    logs_root = Path(
        _env_str_fallback(
            ["BTC_TS_LOGS_DIR", "BTCTS_LOGS_ROOT"],
            r"E:\btc_ts\logs",
        )
    )
    state_root = Path(
        _env_str_fallback(
            ["BTCTS_STATE_ROOT"],
            r"E:\btc_ts\state",
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

    reference_market = _load_reference_market()
    execution_market = _load_execution_market()
    validate_market_identities(reference_market, execution_market)

    ws_ssl_verify = _env_bool("BTCTS_WS_SSL_VERIFY", True)
    ws_ca_file_raw = os.getenv("BTCTS_WS_CA_FILE", "").strip()
    ws_ca_file = Path(ws_ca_file_raw) if ws_ca_file_raw else None

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
        reference_market=reference_market,
        execution_market=execution_market,
        ws_ssl_verify=ws_ssl_verify,
        ws_ca_file=ws_ca_file,
        rotation=rotation,
    )
