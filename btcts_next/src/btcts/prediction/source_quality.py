# path: ./btcts_next/src/btcts/prediction/source_quality.py
# desc: Non-executing source quality contracts for freshness, continuity, and trust diagnostics.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Tuple

LOGIC_VERSION = "prediction_source_quality.s125.v1"


class SourceTrustState(str, Enum):
    TRUSTED = "trusted"
    DEGRADED = "degraded"
    UNTRUSTED = "untrusted"
    UNKNOWN = "unknown"


class ContinuityState(str, Enum):
    CONTINUOUS = "continuous"
    GAPPED = "gapped"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SourceQualityStatus:
    source_id: str
    source_family: str
    generated_at: str
    trust_state: SourceTrustState = SourceTrustState.UNKNOWN
    continuity_state: ContinuityState = ContinuityState.UNKNOWN
    latest_event_ts: str | None = None
    latest_age_sec: float | None = None
    max_age_sec: float | None = None
    gap_count: int = 0
    missing_window_count: int = 0
    usable: bool = False
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["trust_state"] = self.trust_state.value
        data["continuity_state"] = self.continuity_state.value
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["logic_version"] = LOGIC_VERSION
        return data


def _parse_ts(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def assess_source_quality(
    *,
    source_id: str,
    source_family: str,
    latest_event_ts: str | None,
    now: datetime | None = None,
    max_age_sec: float = 30.0,
    gap_count: int = 0,
    missing_window_count: int = 0,
    trust_state: SourceTrustState = SourceTrustState.TRUSTED,
) -> SourceQualityStatus:
    now_dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    latest_dt = _parse_ts(latest_event_ts)
    blockers: list[str] = []
    warnings: list[str] = []
    continuity = ContinuityState.CONTINUOUS
    age: float | None = None

    if latest_dt is None:
        blockers.append("source_latest_event_ts_missing_or_invalid")
        continuity = ContinuityState.UNKNOWN
    else:
        age = max((now_dt - latest_dt).total_seconds(), 0.0)
        if age > float(max_age_sec):
            blockers.append("source_stale")
            continuity = ContinuityState.STALE
    if gap_count > 0 or missing_window_count > 0:
        blockers.append("source_gapped")
        continuity = ContinuityState.GAPPED if continuity != ContinuityState.STALE else continuity
    if trust_state in (SourceTrustState.UNTRUSTED, SourceTrustState.UNKNOWN):
        blockers.append("source_not_trusted")
    if trust_state == SourceTrustState.DEGRADED:
        warnings.append("source_trust_degraded")

    return SourceQualityStatus(
        source_id=source_id,
        source_family=source_family,
        generated_at=_iso(now_dt),
        trust_state=trust_state,
        continuity_state=continuity,
        latest_event_ts=_iso(latest_dt) if latest_dt else None,
        latest_age_sec=age,
        max_age_sec=float(max_age_sec),
        gap_count=int(gap_count),
        missing_window_count=int(missing_window_count),
        usable=not blockers,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
