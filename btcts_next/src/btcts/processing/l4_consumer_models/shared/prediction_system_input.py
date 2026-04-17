# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_system_input.py
# desc: Thin builder for PredictionSystemInput anchored on MarketSummary with optional HealthDigest caution input.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from btcts.processing.l4_consumer_models.shared.health_digest import HealthDigest
from btcts.processing.l4_consumer_models.shared.market_summary import MarketSummary
from btcts.processing.l4_consumer_models.shared.prediction_liquidity_board_history import (
    PredictionLiquidityBoardHistoryBuildInput,
    build_prediction_liquidity_board_history,
)
from btcts.processing.l4_consumer_models.shared.prediction_regime_turning_point import (
    PredictionRegimeTurningPointBuildInput,
    build_prediction_regime_turning_point,
)
from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    DEFAULT_PREDICTION_SYSTEM_SOURCE_KIND,
    DEFAULT_REQUESTED_HORIZONS,
    PredictionEvidenceBundle,
    PredictionEvidenceTrace,
    PredictionSystemInput,
)

_ACTIVE_FIRST_EVIDENCE_FAMILIES = (
    "market_summary_anchor",
    "liquidity_board_history",
    "regime_turning_point",
)


@dataclass(frozen=True)
class PredictionSystemBuildInput:
    market_summary: MarketSummary | None = None
    health_digest: HealthDigest | None = None
    source_kind: str | None = None
    requested_horizons: tuple[str, ...] | list[str] = field(
        default_factory=lambda: DEFAULT_REQUESTED_HORIZONS
    )
    liquidity_board_history: dict[str, Any] | None = None
    regime_turning_point: dict[str, Any] | None = None
    replay_feedback: dict[str, Any] | None = None
    external_context: dict[str, Any] | None = None
    position_context: dict[str, Any] | None = None
    diagnostics: dict[str, Any] | None = None


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_source_kind(value: Any) -> str:
    return _safe_str(value) or DEFAULT_PREDICTION_SYSTEM_SOURCE_KIND


def _normalize_requested_horizons(
    value: tuple[str, ...] | list[str] | None,
) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return DEFAULT_REQUESTED_HORIZONS

    out: list[str] = []
    for item in value:
        normalized = _safe_str(item)
        if normalized not in DEFAULT_REQUESTED_HORIZONS:
            continue
        if normalized in out:
            continue
        out.append(normalized)

    return tuple(out) or DEFAULT_REQUESTED_HORIZONS


def _resolve_identity(
    market_summary: MarketSummary | None,
    health_digest: HealthDigest | None,
) -> tuple[str | None, str | None, str, bool | None]:
    market_uid = None
    event_ts = None
    freshness = "UNKNOWN"
    is_stale = None

    if market_summary is not None:
        market_uid = market_summary.market_uid
        event_ts = market_summary.event_ts
        freshness = market_summary.freshness
        is_stale = market_summary.is_stale

    if health_digest is not None:
        if market_uid is None:
            market_uid = health_digest.market_uid
        if event_ts is None:
            event_ts = health_digest.event_ts
        if freshness == "UNKNOWN":
            freshness = health_digest.freshness
        if is_stale is None:
            is_stale = health_digest.is_stale

    return market_uid, event_ts, freshness, is_stale


def _normalize_dict(value: dict[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _normalize_external_context(inp: PredictionSystemBuildInput) -> dict[str, Any]:
    out = _normalize_dict(inp.external_context)
    replay_feedback = _normalize_dict(inp.replay_feedback)
    if replay_feedback:
        out["replay_feedback"] = replay_feedback
    return out


def _resolve_liquidity_board_history(inp: PredictionSystemBuildInput) -> dict[str, Any]:
    explicit = _normalize_dict(inp.liquidity_board_history)
    if explicit:
        return explicit

    if inp.market_summary is None and inp.health_digest is None:
        return {}

    return build_prediction_liquidity_board_history(
        PredictionLiquidityBoardHistoryBuildInput(
            market_summary=inp.market_summary,
            health_digest=inp.health_digest,
            source_kind=inp.source_kind,
            diagnostics=inp.diagnostics,
        )
    )


def _resolve_regime_turning_point(inp: PredictionSystemBuildInput) -> dict[str, Any]:
    explicit = _normalize_dict(inp.regime_turning_point)
    if explicit:
        return explicit

    if inp.market_summary is None and inp.health_digest is None:
        return {}

    return build_prediction_regime_turning_point(
        PredictionRegimeTurningPointBuildInput(
            market_summary=inp.market_summary,
            health_digest=inp.health_digest,
            source_kind=inp.source_kind,
            diagnostics=inp.diagnostics,
        )
    )


def _build_evidence_bundle(inp: PredictionSystemBuildInput) -> PredictionEvidenceBundle:
    return PredictionEvidenceBundle(
        market_summary=inp.market_summary,
        health_digest=inp.health_digest,
        liquidity_board_history=_resolve_liquidity_board_history(inp),
        regime_turning_point=_resolve_regime_turning_point(inp),
        external_context=_normalize_external_context(inp),
        position_context=_normalize_dict(inp.position_context),
    )


def _build_evidence_trace(
    bundle: PredictionEvidenceBundle,
    *,
    diagnostics: dict[str, Any] | None = None,
) -> PredictionEvidenceTrace:
    active_families: list[str] = []
    missing_families: list[str] = []
    caution_flags: list[str] = []

    if bundle.market_summary is not None:
        active_families.append("market_summary_anchor")
        if bundle.market_summary.is_stale is True:
            caution_flags.append("market_summary_stale")
    else:
        missing_families.append("market_summary_anchor")
        caution_flags.append("market_summary_absent")

    if bundle.liquidity_board_history:
        active_families.append("liquidity_board_history")
    else:
        missing_families.append("liquidity_board_history")

    if bundle.regime_turning_point:
        active_families.append("regime_turning_point")
    else:
        missing_families.append("regime_turning_point")

    if bundle.health_digest is not None:
        active_families.append("health_digest_caution")
        if bundle.health_digest.is_stale is True:
            caution_flags.append("health_digest_stale")

    return PredictionEvidenceTrace(
        active_families=tuple(active_families),
        missing_families=tuple(missing_families),
        caution_flags=tuple(caution_flags),
        diagnostics={
            "builder_type": "prediction_system_input",
            "active_first_families": _ACTIVE_FIRST_EVIDENCE_FAMILIES,
            **dict(diagnostics or {}),
        },
    )


def build_prediction_system_input(inp: PredictionSystemBuildInput) -> PredictionSystemInput:
    evidence_bundle = _build_evidence_bundle(inp)
    evidence_trace = _build_evidence_trace(
        evidence_bundle,
        diagnostics=inp.diagnostics,
    )
    market_uid, event_ts, freshness, is_stale = _resolve_identity(
        inp.market_summary,
        inp.health_digest,
    )

    return PredictionSystemInput(
        source_kind=_normalize_source_kind(inp.source_kind),
        market_uid=market_uid,
        event_ts=event_ts,
        freshness=freshness,
        is_stale=is_stale,
        requested_horizons=_normalize_requested_horizons(inp.requested_horizons),
        evidence_bundle=evidence_bundle,
        evidence_trace=evidence_trace,
        diagnostics={
            "builder_type": "prediction_system_input",
            "market_summary_present": inp.market_summary is not None,
            "health_digest_present": inp.health_digest is not None,
            **dict(inp.diagnostics or {}),
        },
    )