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


@dataclass(frozen=True)
class ProviderReliabilityStatus:
    provider_id: str
    provider_family: str
    generated_at: str
    trust_state: SourceTrustState = SourceTrustState.UNKNOWN
    provider_role: str = "reference_context"
    source_ids: Tuple[str, ...] = ()
    usable_source_count: int = 0
    total_source_count: int = 0
    reliability_state: str = "unknown"
    primary_direction_owner: bool = False
    usable_for_primary_short_horizon: bool = False
    context_only: bool = True
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers and self.usable_source_count > 0 and self.trust_state != SourceTrustState.UNTRUSTED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_family": self.provider_family,
            "generated_at": self.generated_at,
            "trust_state": self.trust_state.value,
            "provider_role": self.provider_role,
            "source_ids": list(self.source_ids),
            "usable_source_count": self.usable_source_count,
            "total_source_count": self.total_source_count,
            "reliability_state": self.reliability_state,
            "primary_direction_owner": self.primary_direction_owner,
            "usable_for_primary_short_horizon": self.usable_for_primary_short_horizon,
            "context_only": self.context_only,
            "usable": self.usable,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "logic_version": LOGIC_VERSION,
        }


@dataclass(frozen=True)
class ProviderReliabilityRegistry:
    generated_at: str
    providers: Tuple[ProviderReliabilityStatus, ...] = ()
    unknown_source_ids: Tuple[str, ...] = ()
    context_only: bool = True
    primary_direction_owner_allowed: bool = False
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    @property
    def provider_count(self) -> int:
        return len(self.providers)

    @property
    def usable_provider_count(self) -> int:
        return sum(1 for provider in self.providers if provider.usable)

    @property
    def warnings(self) -> Tuple[str, ...]:
        out: list[str] = []
        if self.unknown_source_ids:
            out.append("unknown_provider_sources_context_only")
        for provider in self.providers:
            out.extend(provider.warnings)
        return tuple(dict.fromkeys(out))

    @property
    def blockers(self) -> Tuple[str, ...]:
        out: list[str] = []
        for provider in self.providers:
            out.extend(provider.blockers)
        return tuple(dict.fromkeys(out))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "provider_count": self.provider_count,
            "usable_provider_count": self.usable_provider_count,
            "providers": [provider.to_dict() for provider in self.providers],
            "unknown_source_ids": list(self.unknown_source_ids),
            "context_only": self.context_only,
            "primary_direction_owner_allowed": self.primary_direction_owner_allowed,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "logic_version": LOGIC_VERSION,
        }


_DEFAULT_PROVIDER_FAMILIES: Dict[str, str] = {
    "bf_spot": "bitflyer_local_spot",
    "bf_fx": "bitflyer_local_fx",
    "bitflyer_spot": "bitflyer_local_spot",
    "bitflyer_fx": "bitflyer_local_fx",
    "binance": "global_spot_reference",
    "coinbase": "global_spot_reference",
    "kraken": "global_spot_reference",
    "okx": "global_spot_reference",
}


def _provider_family_for_source_id(source_id: str, source_family: str | None = None) -> str:
    source_id_l = str(source_id or "").lower()
    source_family_l = str(source_family or "").lower()
    for key, family in _DEFAULT_PROVIDER_FAMILIES.items():
        if key in source_id_l or key in source_family_l:
            return family
    return "unknown_provider"


def build_provider_reliability_registry(
    *,
    source_quality_by_id: Dict[str, SourceQualityStatus] | None = None,
    observed_source_ids: Tuple[str, ...] = (),
    now: datetime | None = None,
) -> ProviderReliabilityRegistry:
    """Build a conservative, non-collecting provider reliability registry from already-provided source quality.

    Unknown providers are kept context-only and are never primary short-horizon direction owners.
    This function does not collect data, write artifacts, or call external APIs.
    """
    now_dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    by_provider: Dict[str, list[SourceQualityStatus]] = {}
    source_quality_by_id = dict(source_quality_by_id or {})
    for status in source_quality_by_id.values():
        provider_family = _provider_family_for_source_id(status.source_id, status.source_family)
        by_provider.setdefault(provider_family, []).append(status)

    unknown_source_ids: list[str] = []
    for source_id in observed_source_ids:
        sid = str(source_id or "").strip()
        if not sid:
            continue
        if sid not in source_quality_by_id:
            unknown_source_ids.append(sid)
            provider_family = _provider_family_for_source_id(sid)
            placeholder = SourceQualityStatus(
                source_id=sid,
                source_family=provider_family,
                generated_at=_iso(now_dt),
                trust_state=SourceTrustState.UNKNOWN,
                continuity_state=ContinuityState.UNKNOWN,
                usable=False,
                blockers=("source_quality_status_missing",),
                warnings=("provider_quality_context_only_until_source_quality_supplied",),
            )
            by_provider.setdefault(provider_family, []).append(placeholder)

    providers: list[ProviderReliabilityStatus] = []
    for provider_family in sorted(by_provider):
        statuses = tuple(by_provider[provider_family])
        usable_count = sum(1 for status in statuses if status.usable)
        total_count = len(statuses)
        source_ids = tuple(dict.fromkeys(status.source_id for status in statuses))
        blockers: list[str] = []
        warnings: list[str] = []
        trust_states = {status.trust_state for status in statuses}
        if total_count == 0 or usable_count == 0:
            blockers.append("provider_has_no_usable_sources")
        if SourceTrustState.UNTRUSTED in trust_states:
            blockers.append("provider_contains_untrusted_source")
        if SourceTrustState.UNKNOWN in trust_states:
            warnings.append("provider_trust_unknown_context_only")
        if any(status.warnings for status in statuses):
            warnings.append("provider_source_warnings_present")
        if provider_family == "unknown_provider":
            warnings.append("unknown_provider_context_only")
        if blockers:
            reliability_state = "blocked"
        elif warnings:
            reliability_state = "warning_context_only"
        else:
            reliability_state = "usable_context"
        if SourceTrustState.UNTRUSTED in trust_states:
            trust_state = SourceTrustState.UNTRUSTED
        elif SourceTrustState.UNKNOWN in trust_states:
            trust_state = SourceTrustState.UNKNOWN
        elif SourceTrustState.DEGRADED in trust_states:
            trust_state = SourceTrustState.DEGRADED
        else:
            trust_state = SourceTrustState.TRUSTED
        providers.append(
            ProviderReliabilityStatus(
                provider_id=provider_family,
                provider_family=provider_family,
                generated_at=_iso(now_dt),
                trust_state=trust_state,
                provider_role="context_provider",
                source_ids=source_ids,
                usable_source_count=usable_count,
                total_source_count=total_count,
                reliability_state=reliability_state,
                primary_direction_owner=False,
                usable_for_primary_short_horizon=False,
                context_only=True,
                blockers=tuple(dict.fromkeys(blockers)),
                warnings=tuple(dict.fromkeys(warnings)),
            )
        )

    return ProviderReliabilityRegistry(
        generated_at=_iso(now_dt),
        providers=tuple(providers),
        unknown_source_ids=tuple(dict.fromkeys(unknown_source_ids)),
        context_only=True,
        primary_direction_owner_allowed=False,
    )

