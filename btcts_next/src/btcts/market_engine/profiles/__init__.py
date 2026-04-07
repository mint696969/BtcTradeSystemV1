# path: ./btcts_next/src/btcts/market_engine/profiles/__init__.py
# desc: Public exports for Market Engine exchange profiles.

from .base import ExchangeProfile
from .bitflyer import BitflyerProfile


def create_exchange_profile(profile_name: str) -> ExchangeProfile:
    normalized = str(profile_name or "").strip().lower()
    if normalized in {"bitflyer", "bitflyer.spot", "bf"}:
        return BitflyerProfile()
    raise ValueError(f"unsupported exchange profile: {profile_name}")


__all__ = [
    "ExchangeProfile",
    "BitflyerProfile",
    "create_exchange_profile",
]