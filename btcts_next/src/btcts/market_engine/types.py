# path: ./btcts_next/src/btcts/market_engine/types.py
# desc: Shared enums, aliases, and common types for Market Engine foundation contracts.

from __future__ import annotations

from enum import Enum
from typing import NewType


MarketUID = NewType("MarketUID", str)
SeriesID = NewType("SeriesID", str)
StreamSessionID = NewType("StreamSessionID", str)
ExchangeProfileName = NewType("ExchangeProfileName", str)


class TrustState(str, Enum):
    TRUSTED = "trusted"
    PROVISIONAL = "provisional"
    BROKEN = "broken"
    QUARANTINED = "quarantined"


class BoundaryReason(str, Enum):
    NONE = "none"
    STREAM_STARTED = "stream_started"
    NEW_STREAM_SESSION = "new_stream_session"
    GAP_DETECTED = "gap_detected"
    RESYNC_STARTED = "resync_started"
    RESYNC_COMPLETED = "resync_completed"
    ANCHOR_REPLACED = "anchor_replaced"
    INVALID_DIFF_ATTACH = "invalid_diff_attach"
    PROFILE_RULE = "profile_rule"
    UNKNOWN = "unknown"


class ZoneScope(str, Enum):
    NEAR = "near"
    FAR = "far"
    FULL = "full"