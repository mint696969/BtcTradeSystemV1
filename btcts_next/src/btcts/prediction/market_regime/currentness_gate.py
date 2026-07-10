# path: ./btcts_next/src/btcts/prediction/market_regime/currentness_gate.py
# desc: Pure/read-only MR-VS2 currentness, missing-source, and quality gate report. No runtime reads, writes, prediction, UI, broker, or parameter apply.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from typing import Any, Mapping, Sequence

from .contracts import FeatureGroup, FreshnessState, SourceCoverage
from .evidence_profile import build_market_regime_default_evidence_profile, market_regime_evidence_source_id

MARKET_REGIME_CURRENTNESS_GATE_VERSION = "prediction.market_regime.currentness_gate.2026_07_10.v1"
DEFAULT_SOURCE_QUALITY_FAILURE_THRESHOLD_PERCENT = 40


@dataclass(frozen=True)
class MarketRegimeCurrentnessGateSafetyFlags:
    read_only: bool = True
    non_executing: bool = True
    runtime_source_read: bool = False
    runtime_artifact_write_allowed: bool = False
    producer_enabled: bool = False
    prediction_invoked: bool = False
    warroom_write_allowed: bool = False
    broker_private_api_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    order_intent_submitted: bool = False
    parameter_auto_promotion_allowed: bool = False
    live_parameter_apply_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketRegimeCurrentnessGateReport:
    horizon_sec: int
    horizon_key: str
    parameter_set_id: str
    source_ids: tuple[str, ...]
    required_source_ids: tuple[str, ...]
    missing_source_ids: tuple[str, ...]
    missing_required_source_ids: tuple[str, ...]
    stale_source_ids: tuple[str, ...]
    quality_failure_ids: tuple[str, ...]
    blocking_source_ids: tuple[str, ...]
    applied_confidence_cap_percent: int | None
    gate_state: str
    recovery_conditions: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    logic_version: str = MARKET_REGIME_CURRENTNESS_GATE_VERSION
    safety: MarketRegimeCurrentnessGateSafetyFlags = field(default_factory=MarketRegimeCurrentnessGateSafetyFlags)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = self.safety.to_dict()
        return payload


def _coverage_by_source_id(coverage: Sequence[SourceCoverage]) -> dict[str, SourceCoverage]:
    result: dict[str, SourceCoverage] = {}
    for item in coverage:
        source_id = market_regime_evidence_source_id(item.feature_group)
        if source_id in result:
            raise ValueError(f"duplicate source coverage: {source_id}")
        result[source_id] = item
    return result


def _quality_percent(source_id: str, quality_percent_by_source_id: Mapping[str, int | float] | None) -> int:
    if not quality_percent_by_source_id or source_id not in quality_percent_by_source_id:
        return 100
    raw = float(quality_percent_by_source_id[source_id])
    if not isfinite(raw):
        raise ValueError(f"source quality must be finite: {source_id}")
    value = int(round(raw))
    return max(0, min(value, 100))


def _required_source_ids(profile: Mapping[str, Any]) -> tuple[str, ...]:
    sources = profile.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("evidence profile sources missing")
    required: list[str] = []
    for source in sources:
        if not isinstance(source, Mapping):
            raise ValueError("evidence profile source must be mapping")
        source_id = str(source.get("source_id") or "")
        if not source_id:
            raise ValueError("evidence profile source_id missing")
        if bool(source.get("min_required")):
            required.append(source_id)
    return tuple(dict.fromkeys(required))


def _confidence_cap(
    *,
    missing_required_source_ids: tuple[str, ...],
    stale_source_ids: tuple[str, ...],
    quality_failure_ids: tuple[str, ...],
    required_source_ids: tuple[str, ...],
) -> int | None:
    """Return only an explicit fail-closed cap; detailed confidence policy belongs to MR-VS3/common estimator."""

    required = set(required_source_ids)
    if missing_required_source_ids:
        return 0
    if required.intersection(quality_failure_ids):
        return 0
    if required.intersection(stale_source_ids):
        return 0
    return None


def build_market_regime_currentness_gate_report(
    *,
    horizon_sec: int,
    coverage: Sequence[SourceCoverage],
    parameter_set_id: str | None = None,
    quality_percent_by_source_id: Mapping[str, int | float] | None = None,
    quality_failure_threshold_percent: int = DEFAULT_SOURCE_QUALITY_FAILURE_THRESHOLD_PERCENT,
) -> MarketRegimeCurrentnessGateReport:
    """Build a deterministic gate report from already-built read-only source coverage."""

    profile_kwargs: dict[str, Any] = {"horizon_sec": int(horizon_sec)}
    if parameter_set_id is not None:
        profile_kwargs["parameter_set_id"] = str(parameter_set_id)
    profile = build_market_regime_default_evidence_profile(**profile_kwargs)
    sources = profile["sources"]
    source_ids = tuple(str(source["source_id"]) for source in sources)
    required_source_ids = _required_source_ids(profile)
    coverage_map = _coverage_by_source_id(coverage)
    unknown_quality_source_ids = tuple(
        sorted(set(quality_percent_by_source_id or {}).difference(source_ids))
    )
    if unknown_quality_source_ids:
        raise ValueError(f"unknown quality source ids: {','.join(unknown_quality_source_ids)}")

    missing: list[str] = []
    stale: list[str] = []
    quality_failures: list[str] = []
    warnings: list[str] = []
    threshold = max(0, min(int(quality_failure_threshold_percent), 100))

    for source_id in source_ids:
        item = coverage_map.get(source_id)
        if item is None or not item.available or item.freshness_state == FreshnessState.MISSING:
            missing.append(source_id)
            continue
        if item.freshness_state == FreshnessState.STALE:
            stale.append(source_id)
        quality = _quality_percent(source_id, quality_percent_by_source_id)
        if quality < threshold:
            quality_failures.append(source_id)
        warnings.extend(str(value) for value in item.warnings if value)

    missing_required = tuple(source_id for source_id in required_source_ids if source_id in missing)
    blocking = tuple(dict.fromkeys((*missing_required, *(source_id for source_id in stale if source_id in required_source_ids), *(source_id for source_id in quality_failures if source_id in required_source_ids))))
    cap = _confidence_cap(
        missing_required_source_ids=missing_required,
        stale_source_ids=tuple(stale),
        quality_failure_ids=tuple(quality_failures),
        required_source_ids=required_source_ids,
    )
    gate_state = "BLOCKED" if blocking else ("DEGRADED" if missing or stale or quality_failures else "CURRENT")

    recovery: list[str] = []
    for source_id in missing:
        recovery.append(f"restore_available_source:{source_id}")
    for source_id in stale:
        recovery.append(f"refresh_source_to_live_or_warm:{source_id}")
    for source_id in quality_failures:
        recovery.append(f"restore_source_quality_at_or_above_{threshold}:{source_id}")

    return MarketRegimeCurrentnessGateReport(
        horizon_sec=int(horizon_sec),
        horizon_key=str(profile["horizon_key"]),
        parameter_set_id=str(profile["parameter_set_id"]),
        source_ids=source_ids,
        required_source_ids=required_source_ids,
        missing_source_ids=tuple(missing),
        missing_required_source_ids=missing_required,
        stale_source_ids=tuple(stale),
        quality_failure_ids=tuple(quality_failures),
        blocking_source_ids=blocking,
        applied_confidence_cap_percent=cap,
        gate_state=gate_state,
        recovery_conditions=tuple(recovery),
        warnings=tuple(dict.fromkeys(warnings)),
    )
