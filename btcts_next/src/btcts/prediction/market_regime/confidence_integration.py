# path: ./btcts_next/src/btcts/prediction/market_regime/confidence_integration.py
# desc: Pure MR-VS3 shadow confidence adapter from existing signal scoring/currentness inputs to the parent/common estimator. Does not replace classifier output.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

from btcts.prediction.evidence_sources import estimate_prediction_display_confidence_from_evidence_profile

from .contracts import FreshnessState, MarketRegimeCode, SourceCoverage
from .currentness_gate import MarketRegimeCurrentnessGateReport
from .evidence_profile import build_market_regime_default_evidence_profile, market_regime_evidence_source_id

MARKET_REGIME_CONFIDENCE_INTEGRATION_VERSION = "prediction.market_regime.confidence_integration.2026_07_10.v1"


@dataclass(frozen=True)
class MarketRegimeShadowConfidenceSafety:
    read_only: bool = True
    shadow_only: bool = True
    classifier_output_replaced: bool = False
    runtime_source_read: bool = False
    runtime_artifact_write_allowed: bool = False
    producer_enabled: bool = False
    broker_private_api_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    order_intent_submitted: bool = False
    parameter_auto_promotion_allowed: bool = False
    live_parameter_apply_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketRegimeShadowConfidenceReport:
    horizon_sec: int
    horizon_key: str
    parameter_set_id: str
    predicted_regime: str
    legacy_confidence_percent: int | None
    shadow_display_confidence_percent: int
    confidence_delta_percent: int | None
    source_signals: Mapping[str, Mapping[str, Any]]
    estimator: Mapping[str, Any]
    currentness_gate_state: str
    currentness_gate_blockers: tuple[str, ...]
    logic_version: str = MARKET_REGIME_CONFIDENCE_INTEGRATION_VERSION
    safety: MarketRegimeShadowConfidenceSafety = field(default_factory=MarketRegimeShadowConfidenceSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_signals"] = {key: dict(value) for key, value in self.source_signals.items()}
        payload["estimator"] = dict(self.estimator)
        payload["safety"] = self.safety.to_dict()
        return payload


def _freshness_percent(state: FreshnessState) -> int:
    return {
        FreshnessState.LIVE: 100,
        FreshnessState.WARM: 75,
        FreshnessState.STALE: 25,
        FreshnessState.MISSING: 0,
    }[state]


def _coverage_by_source_id(coverage: Sequence[SourceCoverage]) -> dict[str, SourceCoverage]:
    result: dict[str, SourceCoverage] = {}
    for item in coverage:
        source_id = market_regime_evidence_source_id(item.feature_group)
        if source_id in result:
            raise ValueError(f"duplicate source coverage: {source_id}")
        result[source_id] = item
    return result


def _horizon_signal_row(signal_score_report: Mapping[str, Any], horizon_key: str) -> Mapping[str, Any]:
    rows = signal_score_report.get("horizons")
    if not isinstance(rows, list):
        raise ValueError("signal scoring horizons missing")
    matches = [row for row in rows if isinstance(row, Mapping) and str(row.get("horizon_key") or "") == horizon_key]
    if len(matches) != 1:
        raise ValueError(f"signal scoring horizon row count must be one: {horizon_key}:{len(matches)}")
    return matches[0]


def _source_signal_from_votes(
    *,
    source_id: str,
    source_family: str,
    predicted_regime: str,
    votes: Sequence[Mapping[str, Any]],
    coverage: SourceCoverage | None,
    blocked: bool,
    quality_failed: bool,
) -> dict[str, Any]:
    family_votes = [vote for vote in votes if str(vote.get("source_family") or "") == source_family]
    supporting = [vote for vote in family_votes if str(vote.get("supports_regime") or "") == predicted_regime]
    strongest_support = max((float(vote.get("strength") or 0.0) for vote in supporting), default=0.0)
    strongest_any = max(family_votes, key=lambda vote: float(vote.get("strength") or 0.0), default=None)
    direction = predicted_regime if strongest_support > 0 else str((strongest_any or {}).get("supports_regime") or "unknown")
    freshness = _freshness_percent(coverage.freshness_state) if coverage is not None else 0
    available = bool(coverage and coverage.available)
    signal = {
        "direction": direction,
        "signal_strength_percent": int(round(max(0.0, min(strongest_support, 1.0)) * 100.0)),
        "freshness_percent": freshness,
        "quality_percent": 0 if quality_failed else (100 if available else 0),
        "blocked": bool(blocked),
        "source_ref": source_id,
    }
    if blocked:
        signal["confidence_cap_percent"] = 0
    return signal


def build_market_regime_shadow_confidence_report(
    *,
    horizon_sec: int,
    predicted_regime: MarketRegimeCode | str,
    signal_score_report: Mapping[str, Any],
    coverage: Sequence[SourceCoverage],
    currentness_gate: MarketRegimeCurrentnessGateReport,
    legacy_confidence_percent: int | None = None,
    parameter_set_id: str | None = None,
) -> MarketRegimeShadowConfidenceReport:
    """Build a shadow-only confidence report without mutating classifier/runtime output."""

    profile_kwargs: dict[str, Any] = {"horizon_sec": int(horizon_sec)}
    if parameter_set_id is not None:
        profile_kwargs["parameter_set_id"] = str(parameter_set_id)
    profile = build_market_regime_default_evidence_profile(**profile_kwargs)
    horizon_key = str(profile["horizon_key"])
    if currentness_gate.horizon_key != horizon_key:
        raise ValueError(f"currentness gate horizon mismatch: {currentness_gate.horizon_key}!={horizon_key}")
    if currentness_gate.parameter_set_id != str(profile["parameter_set_id"]):
        raise ValueError(
            f"currentness gate parameter_set mismatch: {currentness_gate.parameter_set_id}!={profile['parameter_set_id']}"
        )

    regime = predicted_regime if isinstance(predicted_regime, MarketRegimeCode) else MarketRegimeCode(str(predicted_regime))
    row = _horizon_signal_row(signal_score_report, horizon_key)
    votes = row.get("signal_votes_top_n")
    if not isinstance(votes, list):
        raise ValueError("signal votes missing")
    coverage_map = _coverage_by_source_id(coverage)
    blockers = set(currentness_gate.blocking_source_ids)
    quality_failures = set(currentness_gate.quality_failure_ids)

    source_signals: dict[str, dict[str, Any]] = {}
    for source in profile["sources"]:
        source_id = str(source["source_id"])
        source_family = source_id.removeprefix("market_regime.")
        source_signals[source_id] = _source_signal_from_votes(
            source_id=source_id,
            source_family=source_family,
            predicted_regime=regime.value,
            votes=votes,
            coverage=coverage_map.get(source_id),
            blocked=source_id in blockers,
            quality_failed=source_id in quality_failures,
        )

    estimator = estimate_prediction_display_confidence_from_evidence_profile(
        profile,
        predicted_direction=regime.value,
        source_signals=source_signals,
    )
    shadow = int(estimator["display_confidence_percent"])
    legacy = None if legacy_confidence_percent is None else max(0, min(int(legacy_confidence_percent), 99))
    delta = None if legacy is None else shadow - legacy
    return MarketRegimeShadowConfidenceReport(
        horizon_sec=int(horizon_sec),
        horizon_key=horizon_key,
        parameter_set_id=str(profile["parameter_set_id"]),
        predicted_regime=regime.value,
        legacy_confidence_percent=legacy,
        shadow_display_confidence_percent=shadow,
        confidence_delta_percent=delta,
        source_signals=source_signals,
        estimator=estimator,
        currentness_gate_state=currentness_gate.gate_state,
        currentness_gate_blockers=tuple(currentness_gate.blocking_source_ids),
    )
