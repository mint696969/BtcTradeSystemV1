# path: ./btcts_next/src/btcts/prediction/system.py
# desc: Standalone Prediction System PS-G-lite runner over current rule_based_v0 family logic. Non-executing; no Collector, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, Sequence, Tuple

from .bundle_assembly import build_inference_bundle_from_outputs
from .contracts import PredictionOutput
from .cross_venue import CrossVenueReferenceSummary, build_cross_venue_reference_summary
from .forecast_ledger import ForecastLedgerBatch, build_forecast_ledger_records_from_bundle
from .ohlcv import OHLCVAggregationDiagnostics, OHLCVCandle, TIMEFRAME_SECONDS, aggregate_ohlcv_from_rows
from .rule_based_v0 import INITIAL_FAMILIES, build_rule_based_v0_outputs
from .source_quality import SourceQualityStatus
from .system_contract import (
    DEFAULT_HORIZON_GROUPS,
    DEFAULT_HORIZONS_BY_GROUP,
    DISPLAY_LABEL_JA_BY_GROUP,
    HorizonGroup,
    HorizonGroupSummary,
    PredictionLifetime,
    PredictionRevisionSummary,
    PredictionRunIdentity,
    PredictionSystemInput,
    PredictionSystemResult,
    PredictionTriggerEligibility,
    ScenarioCoreOutput,
)
from .technical import HumanTechnicalSummary, build_human_technical_summary

LOGIC_VERSION = "prediction_system.ps_g_lite.v1"


_STALE_AFTER_SEC_BY_GROUP: Mapping[HorizonGroup, int] = {
    HorizonGroup.NOWCAST: 60,
    HorizonGroup.SHORT_HORIZON: 300,
    HorizonGroup.MID_HORIZON: 1800,
    HorizonGroup.LONG_HORIZON: 14400,
}


_TECHNICAL_TIMEFRAME_BY_HORIZON_SEC: Mapping[int, int] = {
    15: 60,
    30: 60,
    60: 60,
    180: 300,
    300: 300,
    600: 600,
    900: 900,
    1800: 1800,
    3600: 3600,
    14400: 14400,
    86400: 86400,
}


def _now(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_groups(groups: Iterable[HorizonGroup | str] | None) -> Tuple[HorizonGroup, ...]:
    if groups is None:
        return DEFAULT_HORIZON_GROUPS
    normalized: list[HorizonGroup] = []
    for item in groups:
        group = item if isinstance(item, HorizonGroup) else HorizonGroup(str(item))
        if group not in normalized:
            normalized.append(group)
    return tuple(normalized or DEFAULT_HORIZON_GROUPS)


def _horizons_for_groups(groups: Tuple[HorizonGroup, ...], requested_horizons_sec: Iterable[int] | None) -> Tuple[int, ...]:
    if requested_horizons_sec:
        return tuple(dict.fromkeys(int(item) for item in requested_horizons_sec))
    out: list[int] = []
    for group in groups:
        out.extend(DEFAULT_HORIZONS_BY_GROUP[group])
    return tuple(dict.fromkeys(out))


def _horizons_by_group(groups: Tuple[HorizonGroup, ...], horizons_sec: Tuple[int, ...]) -> dict[HorizonGroup, Tuple[int, ...]]:
    available = set(int(item) for item in horizons_sec)
    out: dict[HorizonGroup, Tuple[int, ...]] = {}
    for group in groups:
        group_horizons = tuple(item for item in DEFAULT_HORIZONS_BY_GROUP[group] if int(item) in available)
        out[group] = group_horizons or tuple(h for h in horizons_sec if h in DEFAULT_HORIZONS_BY_GROUP[group])
    return out


def _input_rows_count(rows: Iterable[Mapping[str, Any]] | None) -> int:
    if rows is None:
        return 0
    if isinstance(rows, Sequence):
        return len(rows)
    return 0


def _build_candles(
    *,
    rows: Iterable[Mapping[str, Any]] | None,
    candles: Iterable[OHLCVCandle] | None,
    horizons_sec: Tuple[int, ...],
    now_dt: datetime,
) -> tuple[Tuple[OHLCVCandle, ...], OHLCVAggregationDiagnostics | None, Tuple[str, ...]]:
    if candles is not None:
        return tuple(candles), None, ()
    if rows is None:
        return tuple(), None, ("rows_or_candles_missing",)
    requested_timeframes = tuple(item for item in dict.fromkeys(_TECHNICAL_TIMEFRAME_BY_HORIZON_SEC.get(h, h) for h in horizons_sec) if item in TIMEFRAME_SECONDS)
    built, diagnostics = aggregate_ohlcv_from_rows(
        rows,
        timeframes_sec=requested_timeframes or TIMEFRAME_SECONDS,
        now=now_dt,
        source_family="prediction_system_provided_rows",
    )
    warnings = tuple(diagnostics.warnings)
    return built, diagnostics, warnings


def _technical_for_horizon(candles: Tuple[OHLCVCandle, ...], horizon_sec: int) -> HumanTechnicalSummary | None:
    if not candles:
        return None
    timeframe_sec = _TECHNICAL_TIMEFRAME_BY_HORIZON_SEC.get(int(horizon_sec), int(horizon_sec))
    return build_human_technical_summary(candles, timeframe_sec=timeframe_sec)


def _build_cross_venue(
    *,
    venue_snapshots: Iterable[Mapping[str, Any]] | None,
    source_quality_by_id: Mapping[str, SourceQualityStatus] | None,
    now_dt: datetime,
) -> CrossVenueReferenceSummary | None:
    if venue_snapshots is None:
        return None
    return build_cross_venue_reference_summary(venue_snapshots, source_quality_by_id=source_quality_by_id, now=now_dt)


def _build_outputs(
    *,
    candles: Tuple[OHLCVCandle, ...],
    cross_venue_summary: CrossVenueReferenceSummary | None,
    horizons_sec: Tuple[int, ...],
    now_dt: datetime,
) -> tuple[Tuple[PredictionOutput, ...], Mapping[int, HumanTechnicalSummary | None]]:
    outputs: list[PredictionOutput] = []
    technical_by_horizon: dict[int, HumanTechnicalSummary | None] = {}
    for horizon_sec in horizons_sec:
        technical = _technical_for_horizon(candles, horizon_sec)
        technical_by_horizon[int(horizon_sec)] = technical
        outputs.extend(
            build_rule_based_v0_outputs(
                technical_summary=technical,
                cross_venue_summary=cross_venue_summary,
                horizon_sec=int(horizon_sec),
                now=now_dt,
            )
        )
    return tuple(outputs), technical_by_horizon


def _best_label(outputs: Tuple[PredictionOutput, ...], family: str, default: str = "unknown") -> str:
    candidates = [output for output in outputs if output.family.value == family and not output.blockers]
    if not candidates:
        return default
    candidates.sort(key=lambda item: float(item.score or 0.0), reverse=True)
    return candidates[0].primary_label


def _average_score(outputs: Tuple[PredictionOutput, ...]) -> float | None:
    scores = [float(output.score) for output in outputs if output.score is not None and not output.blockers]
    if not scores:
        return None
    return round(sum(scores) / len(scores), 6)


def _confidence(score: float | None, blockers: Tuple[str, ...]) -> str:
    if blockers or score is None:
        return "unknown"
    if score >= 0.70:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _caution(outputs: Tuple[PredictionOutput, ...], blockers: Tuple[str, ...], warnings: Tuple[str, ...]) -> str:
    labels = {output.primary_label for output in outputs}
    if blockers:
        return "blocked"
    if warnings or labels.intersection({"elevated_risk", "divergent_warning", "volatile_or_divergent", "poor_liquidity", "liquidity_unknown"}):
        return "high"
    if labels.intersection({"compression_watch", "rejection_structure", "range_boundary_structure", "reversal_watch", "reaction_zone_watch", "vwap_reversion_watch", "liquidity_caution"}):
        return "medium"
    return "low"


def _primary_label(outputs: Tuple[PredictionOutput, ...], blockers: Tuple[str, ...]) -> str:
    if blockers:
        return "unknown"
    trend = _best_label(outputs, "trend_bias", default="unknown")
    if trend in ("long_bias", "short_bias"):
        return trend
    regime = _best_label(outputs, "market_regime", default="unknown")
    if trend in ("neutral_bias", "flat", "no_change") and regime in ("range_candidate", "unclear", "unknown"):
        return "no_edge"
    return regime if regime != "unknown" else trend


def _lifetime(now_dt: datetime, group: HorizonGroup) -> PredictionLifetime:
    stale_after = int(_STALE_AFTER_SEC_BY_GROUP[group])
    return PredictionLifetime(
        valid_from=_iso(now_dt),
        valid_until=_iso(now_dt + timedelta(seconds=stale_after)),
        stale_after_sec=stale_after,
        refresh_required=False,
    )


def _group_narrative(group: HorizonGroup, primary_label: str, trend_bias: str, regime: str, caution: str, confidence: str) -> str:
    label_ja = DISPLAY_LABEL_JA_BY_GROUP[group]
    if primary_label in ("unknown", "no_edge"):
        direction = "明確な優位はまだありません"
    elif primary_label == "long_bias":
        direction = "上方向がやや優勢です"
    elif primary_label == "short_bias":
        direction = "下方向がやや優勢です"
    else:
        direction = f"{primary_label} を主シナリオとして見ています"
    return f"{label_ja}は{direction}。地合い={regime}、トレンド={trend_bias}、警戒={caution}、信頼度={confidence}。"


def _horizon_group_summary(
    *,
    group: HorizonGroup,
    group_horizons: Tuple[int, ...],
    outputs: Tuple[PredictionOutput, ...],
    now_dt: datetime,
) -> HorizonGroupSummary:
    group_outputs = tuple(output for output in outputs if int(output.horizon.horizon_sec) in set(group_horizons))
    blockers = tuple(dict.fromkeys(blocker for output in group_outputs for blocker in output.blockers))
    warnings = tuple(dict.fromkeys(warning for output in group_outputs for warning in output.warnings))
    score = _average_score(group_outputs)
    confidence = _confidence(score, blockers)
    caution = _caution(group_outputs, blockers, warnings)
    regime = _best_label(group_outputs, "market_regime")
    trend = _best_label(group_outputs, "trend_bias")
    reversal = _best_label(group_outputs, "reversal_zone")
    volatility = _best_label(group_outputs, "volatility_risk")
    liquidity = _best_label(group_outputs, "liquidity_execution_quality")
    cross = _best_label(group_outputs, "cross_venue_confirmation")
    technical = _best_label(group_outputs, "human_technical_structure")
    primary = _primary_label(group_outputs, blockers)
    trigger = PredictionTriggerEligibility(
        trigger_eligibility_state="blocked",
        reason="standalone_prediction_output_not_enabled_for_trigger",
        confidence=confidence,
        caution_level=caution,
        blockers=("autonomous_trigger_not_enabled_in_ps_g_lite",),
        machine_fields={
            "horizon_group": group.value,
            "primary_label": primary,
            "trend_bias": trend,
            "regime_state": regime,
            "confidence": confidence,
            "caution_level": caution,
            "liquidity_execution_quality": liquidity,
        },
    )
    narrative = _group_narrative(group, primary, trend, regime, caution, confidence)
    return HorizonGroupSummary(
        horizon_group=group,
        display_label_ja=DISPLAY_LABEL_JA_BY_GROUP[group],
        horizons_sec=group_horizons,
        primary_label=primary,
        regime_state=regime,
        trend_bias=trend,
        reversal_risk=reversal,
        breakout_false_break_risk="not_implemented_ps_g_lite",
        volatility_risk=volatility,
        liquidity_execution_quality=liquidity,
        confidence=confidence,
        caution_level=caution,
        score=score,
        invalidation_state="not_evaluated_ps_g_lite",
        scenario_switch_hint="not_evaluated_ps_g_lite",
        lifetime=_lifetime(now_dt, group),
        trigger_eligibility=trigger,
        human_narrative_ja=narrative,
        gpt_review_digest={
            "logic_version": LOGIC_VERSION,
            "family_labels": {
                "market_regime": regime,
                "trend_bias": trend,
                "reversal_zone": reversal,
                "volatility_risk": volatility,
                "liquidity_execution_quality": liquidity,
                "cross_venue_confirmation": cross,
                "human_technical_structure": technical,
            },
            "output_count": len(group_outputs),
            "blockers": list(blockers),
            "warnings": list(warnings),
        },
        blockers=blockers,
        warnings=warnings,
    )


def _scenario_core(
    *,
    run_id: str,
    generated_at: str,
    groups: Tuple[HorizonGroup, ...],
    horizons_by_group: Mapping[HorizonGroup, Tuple[int, ...]],
    outputs: Tuple[PredictionOutput, ...],
    now_dt: datetime,
) -> ScenarioCoreOutput:
    outlooks = tuple(
        _horizon_group_summary(group=group, group_horizons=horizons_by_group.get(group, ()), outputs=outputs, now_dt=now_dt)
        for group in groups
    )
    blockers = tuple(dict.fromkeys(blocker for outlook in outlooks for blocker in outlook.blockers))
    warnings = tuple(dict.fromkeys(warning for outlook in outlooks for warning in outlook.warnings))
    first_usable = next((outlook for outlook in outlooks if outlook.usable), None)
    current_regime = first_usable.regime_state if first_usable else "unknown"
    health = "blocked" if blockers else ("caution" if warnings else "stable")
    return ScenarioCoreOutput(
        scenario_id=f"{LOGIC_VERSION}:scenario:{run_id}",
        generated_at=generated_at,
        current_regime_state=current_regime,
        current_hypothesis_health=health,
        outlooks=outlooks,
        continuation_vs_reversal_balance={"state": "not_evaluated_ps_g_lite"},
        turning_point_risk="not_evaluated_ps_g_lite",
        invalidation_state="not_evaluated_ps_g_lite",
        rewrite_state="not_evaluated_ps_g_lite",
        scenario_switch_hint="not_evaluated_ps_g_lite",
        evidence_weighting_summary={"state": "rule_based_v0_unweighted"},
        evidence_conflict_state="basic_bundle_only_ps_g_lite",
        scenario_trace={
            "logic_version": LOGIC_VERSION,
            "families": [family.value for family in INITIAL_FAMILIES],
            "horizons_sec": sorted({int(output.horizon.horizon_sec) for output in outputs}),
            "output_count": len(outputs),
        },
        trigger_eligibility_state="blocked",
        human_narrative_ja="\n".join(outlook.human_narrative_ja for outlook in outlooks),
        gpt_review_digest={"logic_version": LOGIC_VERSION, "outlook_count": len(outlooks), "blockers": list(blockers), "warnings": list(warnings)},
        blockers=blockers,
        warnings=warnings,
    )


def build_prediction_system_result(
    *,
    rows: Iterable[Mapping[str, Any]] | None = None,
    candles: Iterable[OHLCVCandle] | None = None,
    venue_snapshots: Iterable[Mapping[str, Any]] | None = None,
    source_quality_by_id: Mapping[str, SourceQualityStatus] | None = None,
    requested_horizon_groups: Iterable[HorizonGroup | str] | None = None,
    requested_horizons_sec: Iterable[int] | None = None,
    previous_prediction_run_id: str | None = None,
    now: datetime | None = None,
    market_uid: str = "BTC_JPY:bitFlyer",
    run_reason: str = "ps_g_lite_multi_horizon_runner",
) -> PredictionSystemResult:
    """Build a standalone, non-executing PredictionSystemResult from already-provided inputs.

    This PS-G-lite runner intentionally uses only current rule_based_v0 family logic.
    It does not collect data, write artifacts, import Collector runtime, or publish trigger decisions.
    """
    now_dt = _now(now)
    generated_at = _iso(now_dt)
    groups = _normalize_groups(requested_horizon_groups)
    horizons_sec = _horizons_for_groups(groups, requested_horizons_sec)
    horizons_by_group = _horizons_by_group(groups, horizons_sec)
    run_id = f"{LOGIC_VERSION}:{market_uid}:{generated_at}"

    built_candles, ohlcv_diagnostics, candle_warnings = _build_candles(rows=rows, candles=candles, horizons_sec=horizons_sec, now_dt=now_dt)
    cross = _build_cross_venue(venue_snapshots=venue_snapshots, source_quality_by_id=source_quality_by_id, now_dt=now_dt)
    outputs, technical_by_horizon = _build_outputs(candles=built_candles, cross_venue_summary=cross, horizons_sec=horizons_sec, now_dt=now_dt)

    source_quality_summary: dict[str, Any] = {
        "logic_version": LOGIC_VERSION,
        "source_quality_count": len(source_quality_by_id or {}),
        "ohlcv_diagnostics": ohlcv_diagnostics.to_dict() if ohlcv_diagnostics else None,
        "cross_venue_summary": cross.to_dict() if cross else None,
        "technical_timeframes": {str(h): (summary.timeframe_sec if summary else None) for h, summary in technical_by_horizon.items()},
    }
    bundle = build_inference_bundle_from_outputs(outputs, now=now_dt, source_quality_summary=source_quality_summary)
    forecast_batch = build_forecast_ledger_records_from_bundle(bundle, now=now_dt)
    scenario = _scenario_core(run_id=run_id, generated_at=generated_at, groups=groups, horizons_by_group=horizons_by_group, outputs=outputs, now_dt=now_dt)

    blockers = list(bundle.blockers)
    warnings = list(bundle.warnings)
    warnings.extend(candle_warnings)
    if not built_candles:
        warnings.append("prediction_system_candles_missing_or_unusable")
    if cross is None:
        warnings.append("prediction_system_cross_venue_summary_missing")

    system_input = PredictionSystemInput(
        input_id=f"{LOGIC_VERSION}:input:{generated_at}",
        generated_at=generated_at,
        market_uid=market_uid,
        requested_horizon_groups=groups,
        requested_horizons_sec=horizons_sec,
        provider_quality_summary={"source_quality_count": len(source_quality_by_id or {})},
        feature_snapshot={
            "row_count": _input_rows_count(rows),
            "candle_count": len(built_candles),
            "venue_snapshot_supplied": venue_snapshots is not None,
            "horizons_sec": list(horizons_sec),
            "families": [family.value for family in INITIAL_FAMILIES],
        },
        previous_prediction_run_id=previous_prediction_run_id,
        diagnostics={"logic_version": LOGIC_VERSION, "ps_g_lite": True},
    )
    run_identity = PredictionRunIdentity(
        prediction_run_id=run_id,
        generated_at=generated_at,
        market_uid=market_uid,
        system_version=LOGIC_VERSION,
        previous_prediction_run_id=previous_prediction_run_id,
        run_reason=run_reason,
    )
    revision = PredictionRevisionSummary(previous_prediction_run_id=previous_prediction_run_id)
    if previous_prediction_run_id:
        revision = replace(revision, revision_reason="previous_run_supplied_no_diff_engine_yet", change_summary_for_human="前回予測IDは指定されていますが、PS-G-liteでは差分比較はまだ未実装です。")

    return PredictionSystemResult(
        run_identity=run_identity,
        system_input=system_input,
        outputs=outputs,
        scenario_core=scenario,
        inference_bundle=bundle,
        forecast_batch=forecast_batch,
        revision_summary=revision,
        human_narrative_ja=scenario.human_narrative_ja,
        gpt_review_digest={
            "logic_version": LOGIC_VERSION,
            "family_count": len(INITIAL_FAMILIES),
            "output_count": len(outputs),
            "forecast_record_count": forecast_batch.record_count if isinstance(forecast_batch, ForecastLedgerBatch) else 0,
            "blockers": list(dict.fromkeys(blockers)),
            "warnings": list(dict.fromkeys(warnings)),
        },
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
