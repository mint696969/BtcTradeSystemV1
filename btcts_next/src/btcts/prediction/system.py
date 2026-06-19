# path: ./btcts_next/src/btcts/prediction/system.py
# desc: Standalone Prediction System PS-G-lite runner over current rule_based_v0 family logic. Non-executing; no Collector, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, Sequence, Tuple

from .bundle_assembly import build_inference_bundle_from_outputs
from .contracts import PredictionOutput
from .cross_venue import CrossVenueReferenceSummary, build_cross_venue_reference_summary
from .feature_depth import FeatureDepthSnapshot
from .forecast_ledger import ForecastLedgerBatch, build_forecast_ledger_records_from_bundle
from .ohlcv import OHLCVAggregationDiagnostics, OHLCVCandle, TIMEFRAME_SECONDS, aggregate_ohlcv_from_rows
from .rule_based_v0 import INITIAL_FAMILIES, build_rule_based_v0_outputs
from .source_quality import SourceQualityStatus, build_provider_reliability_registry
from .system_contract import (
    DEFAULT_HORIZON_GROUPS,
    DEFAULT_HORIZONS_BY_GROUP,
    DISPLAY_LABEL_JA_BY_GROUP,
    HorizonGroup,
    HorizonGroupSummary,
    PredictionEvidenceRef,
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



def _observed_source_ids(venue_snapshots: Iterable[Mapping[str, Any]] | None) -> Tuple[str, ...]:
    if venue_snapshots is None:
        return tuple()
    out: list[str] = []
    for item in venue_snapshots:
        if isinstance(item, Mapping):
            source_id = str(item.get("source_id") or item.get("source") or "").strip()
            if source_id:
                out.append(source_id)
    return tuple(dict.fromkeys(out))

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
    feature_depth_snapshot: FeatureDepthSnapshot | None = None,
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
                feature_depth_snapshot=feature_depth_snapshot,
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
    if warnings or labels.intersection({"elevated_risk", "divergent_warning", "volatile_or_divergent", "poor_liquidity", "liquidity_unknown", "false_break_risk", "opportunity_blocked", "macro_risk_watch", "algorithmic_activity_watch", "potential_sweep_reversal_footprint"}):
        return "high"
    if labels.intersection({"compression_watch", "rejection_structure", "range_boundary_structure", "reversal_watch", "reaction_zone_watch", "vwap_reversion_watch", "liquidity_caution", "breakout_watch", "breakout_candidate", "wait_for_confirmation", "opportunity_watch"}):
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


def _refresh_decision_from_scenario_lite(scenario_lite: Mapping[str, Any] | None) -> dict[str, Any]:
    data = dict(scenario_lite or {})
    invalidation = str(data.get("invalidation_state") or "unknown")
    conflict = str(data.get("evidence_conflict_state") or "unknown")
    switch_hint = str(data.get("scenario_switch_hint") or "unknown")
    turning = str(data.get("turning_point_risk") or "unknown")
    if invalidation == "blocked_inputs":
        return {
            "refresh_required": True,
            "refresh_reason": "blocked_prediction_inputs",
            "refresh_trigger": "input_recovery_or_manual_refresh",
            "state": "refresh_required_blocked",
        }
    if invalidation == "active_invalidation_watch":
        return {
            "refresh_required": True,
            "refresh_reason": "active_invalidation_watch",
            "refresh_trigger": "scenario_switch_or_reversal_resolution",
            "state": "refresh_required_invalidation_watch",
        }
    if switch_hint.startswith("watch_for_scenario_switch"):
        return {
            "refresh_required": True,
            "refresh_reason": "scenario_switch_watch",
            "refresh_trigger": "scenario_switch_confirmation",
            "state": "refresh_required_switch_watch",
        }
    if conflict == "conflicting_evidence":
        return {
            "refresh_required": True,
            "refresh_reason": "conflicting_evidence_watch",
            "refresh_trigger": "evidence_reconfirmation",
            "state": "refresh_required_conflict_watch",
        }
    if turning == "high":
        return {
            "refresh_required": True,
            "refresh_reason": "high_turning_point_risk",
            "refresh_trigger": "turning_point_resolution",
            "state": "refresh_required_turning_point_watch",
        }
    return {
        "refresh_required": False,
        "refresh_reason": None,
        "refresh_trigger": None,
        "state": "current_until_stale_after",
    }


def _lifetime(now_dt: datetime, group: HorizonGroup, scenario_lite: Mapping[str, Any] | None = None) -> PredictionLifetime:
    stale_after = int(_STALE_AFTER_SEC_BY_GROUP[group])
    refresh = _refresh_decision_from_scenario_lite(scenario_lite)
    return PredictionLifetime(
        valid_from=_iso(now_dt),
        valid_until=_iso(now_dt + timedelta(seconds=stale_after)),
        stale_after_sec=stale_after,
        refresh_required=bool(refresh["refresh_required"]),
        refresh_reason=refresh["refresh_reason"],
        refresh_trigger=refresh["refresh_trigger"],
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



def _family_label_map(outputs: Tuple[PredictionOutput, ...]) -> dict[str, str]:
    return {
        "market_regime": _best_label(outputs, "market_regime"),
        "trend_bias": _best_label(outputs, "trend_bias"),
        "reversal_zone": _best_label(outputs, "reversal_zone"),
        "volatility_risk": _best_label(outputs, "volatility_risk"),
        "liquidity_execution_quality": _best_label(outputs, "liquidity_execution_quality"),
        "breakout_false_break": _best_label(outputs, "breakout_false_break"),
        "opportunity_participation": _best_label(outputs, "opportunity_participation"),
        "cross_venue_confirmation": _best_label(outputs, "cross_venue_confirmation"),
        "macro_risk_context": _best_label(outputs, "macro_risk_context"),
        "algorithmic_participant_footprint": _best_label(outputs, "algorithmic_participant_footprint"),
        "human_technical_structure": _best_label(outputs, "human_technical_structure"),
    }


def _scenario_signal_summary(labels: Mapping[str, str], blockers: Tuple[str, ...], warnings: Tuple[str, ...]) -> dict[str, Any]:
    trend = labels.get("trend_bias", "unknown")
    reversal = labels.get("reversal_zone", "unknown")
    volatility = labels.get("volatility_risk", "unknown")
    liquidity = labels.get("liquidity_execution_quality", "unknown")
    breakout = labels.get("breakout_false_break", "unknown")
    opportunity = labels.get("opportunity_participation", "unknown")
    cross = labels.get("cross_venue_confirmation", "unknown")
    macro = labels.get("macro_risk_context", "unknown")
    algo = labels.get("algorithmic_participant_footprint", "unknown")
    technical = labels.get("human_technical_structure", "unknown")

    continuation_score = 0.0
    reversal_score = 0.0
    conflict_reasons: list[str] = []
    watch_next: list[str] = []
    switch_reasons: list[str] = []

    if blockers:
        conflict_reasons.append("blocked_family_outputs")
        watch_next.append("restore_missing_or_blocked_prediction_inputs")

    if trend in ("long_bias", "short_bias"):
        continuation_score += 2.0
    elif trend in ("neutral_bias", "unknown"):
        conflict_reasons.append("trend_not_directional")
        watch_next.append("wait_for_directional_trend_bias")

    if breakout == "breakout_candidate":
        continuation_score += 1.0
        watch_next.append("watch_breakout_follow_through")
    elif breakout == "breakout_watch":
        continuation_score += 0.5
        watch_next.append("watch_breakout_confirmation")
    elif breakout == "false_break_risk":
        reversal_score += 2.0
        switch_reasons.append("false_break_risk")
        watch_next.append("watch_false_break_resolution")

    if reversal in ("reversal_watch", "reaction_zone_watch", "vwap_reversion_watch"):
        reversal_score += 2.0
        switch_reasons.append(reversal)
        watch_next.append("watch_reversal_zone_reaction")
    elif reversal == "low_reversal_signal":
        continuation_score += 0.5

    if cross == "confirmed":
        continuation_score += 1.0
    elif cross == "divergent_warning":
        reversal_score += 1.5
        conflict_reasons.append("cross_venue_divergence")
        switch_reasons.append("cross_venue_divergence")
        watch_next.append("watch_cross_venue_reconfirmation")

    if liquidity == "liquidity_proxy_adequate":
        continuation_score += 0.5
    elif liquidity in ("liquidity_caution", "poor_liquidity", "liquidity_unknown"):
        conflict_reasons.append(f"liquidity_{liquidity}")
        watch_next.append("watch_liquidity_quality_recovery")

    if volatility == "elevated_risk":
        reversal_score += 1.0
        switch_reasons.append("elevated_volatility")
        watch_next.append("watch_volatility_normalization")
    elif volatility == "normal_risk":
        continuation_score += 0.5

    if macro == "macro_risk_watch":
        reversal_score += 0.5
        conflict_reasons.append("macro_risk_watch")
        watch_next.append("watch_macro_context_cooldown")

    if algo in ("algorithmic_activity_watch", "potential_sweep_reversal_footprint"):
        reversal_score += 1.0
        switch_reasons.append(algo)
        watch_next.append("watch_algorithmic_footprint_resolution")
    elif algo == "directional_algorithmic_flow_watch":
        continuation_score += 0.5

    if opportunity in ("opportunity_blocked", "wait_for_confirmation"):
        conflict_reasons.append(opportunity)
        watch_next.append("wait_for_participation_confirmation")

    if technical in ("directional_structure", "range_boundary_structure"):
        continuation_score += 0.25
    elif technical == "rejection_structure":
        reversal_score += 0.5
        watch_next.append("watch_rejection_structure_follow_through")

    if continuation_score > reversal_score + 1.0:
        balance_state = "continuation_bias"
    elif reversal_score > continuation_score + 1.0:
        balance_state = "reversal_risk_bias"
    else:
        balance_state = "mixed_or_transition"

    turning_point_risk = "high" if reversal_score >= 3.0 else ("medium" if reversal_score >= 1.5 else "low")
    evidence_conflict_state = "conflicting_evidence" if conflict_reasons else "aligned_or_low_conflict"

    if blockers:
        invalidation_state = "blocked_inputs"
    elif "false_break_risk" in switch_reasons or reversal == "reversal_watch":
        invalidation_state = "active_invalidation_watch"
    elif evidence_conflict_state == "conflicting_evidence":
        invalidation_state = "soft_invalidation_watch"
    else:
        invalidation_state = "valid_until_new_conflict"

    if switch_reasons:
        scenario_switch_hint = "watch_for_scenario_switch:" + ",".join(dict.fromkeys(switch_reasons[:4]))
    elif evidence_conflict_state == "conflicting_evidence":
        scenario_switch_hint = "wait_for_confirmation"
    else:
        scenario_switch_hint = "no_immediate_switch"

    rewrite_state = "rewrite_if_switch_confirms" if scenario_switch_hint.startswith("watch_for_scenario_switch") else "no_rewrite_required"
    evidence_weighting_summary = {
        "state": "deterministic_family_label_weighting_v1",
        "continuation_score": round(continuation_score, 6),
        "reversal_score": round(reversal_score, 6),
        "dominant_side": balance_state,
        "weighted_families": list(labels.keys()),
    }
    if not watch_next:
        watch_next.append("continue_monitoring_family_label_changes")

    return {
        "continuation_vs_reversal_balance": {
            "state": balance_state,
            "continuation_score": round(continuation_score, 6),
            "reversal_score": round(reversal_score, 6),
            "drivers": list(dict.fromkeys(switch_reasons + conflict_reasons))[:8],
        },
        "turning_point_risk": turning_point_risk,
        "evidence_conflict_state": evidence_conflict_state,
        "conflict_reasons": list(dict.fromkeys(conflict_reasons))[:8],
        "scenario_switch_hint": scenario_switch_hint,
        "invalidation_state": invalidation_state,
        "rewrite_state": rewrite_state,
        "what_to_watch_next": list(dict.fromkeys(watch_next))[:8],
        "evidence_weighting_summary": evidence_weighting_summary,
    }


def _aggregate_core_signals(outlooks: Tuple[HorizonGroupSummary, ...]) -> dict[str, Any]:
    summaries = [dict(outlook.gpt_review_digest.get("scenario_lite", {})) for outlook in outlooks]
    conflict_reasons: list[str] = []
    watch_next: list[str] = []
    turning_ranks = {"unknown": 0, "low": 1, "medium": 2, "high": 3}
    top_turning = "unknown"
    switch_hint = "no_immediate_switch"
    invalidation = "valid_until_new_conflict"
    rewrite = "no_rewrite_required"
    for summary in summaries:
        if turning_ranks.get(str(summary.get("turning_point_risk", "unknown")), 0) > turning_ranks.get(top_turning, 0):
            top_turning = str(summary.get("turning_point_risk", "unknown"))
        conflict_reasons.extend(str(item) for item in summary.get("conflict_reasons", []))
        watch_next.extend(str(item) for item in summary.get("what_to_watch_next", []))
        hint = str(summary.get("scenario_switch_hint", ""))
        if hint.startswith("watch_for_scenario_switch"):
            switch_hint = hint
        if str(summary.get("invalidation_state", "")) in ("active_invalidation_watch", "blocked_inputs"):
            invalidation = str(summary.get("invalidation_state"))
        if str(summary.get("rewrite_state", "")) == "rewrite_if_switch_confirms":
            rewrite = "rewrite_if_switch_confirms"
    evidence_conflict_state = "conflicting_evidence" if conflict_reasons else "aligned_or_low_conflict"
    return {
        "turning_point_risk": top_turning,
        "evidence_conflict_state": evidence_conflict_state,
        "scenario_switch_hint": switch_hint,
        "invalidation_state": invalidation,
        "rewrite_state": rewrite,
        "what_to_watch_next": list(dict.fromkeys(watch_next or ["continue_monitoring_family_label_changes"]))[:10],
        "conflict_reasons": list(dict.fromkeys(conflict_reasons))[:10],
    }


def _best_output_by_family(outputs: Tuple[PredictionOutput, ...]) -> dict[str, PredictionOutput]:
    best: dict[str, PredictionOutput] = {}
    for output in outputs:
        family = output.family.value
        current = best.get(family)
        if current is None:
            best[family] = output
            continue
        current_score = float(current.score or 0.0) if not current.blockers else -1.0
        new_score = float(output.score or 0.0) if not output.blockers else -1.0
        if new_score > current_score:
            best[family] = output
    return best


def _evidence_kind_for_family(family: str, label: str, scenario_lite: Mapping[str, Any]) -> str:
    conflict_reasons = {str(item) for item in scenario_lite.get("conflict_reasons", [])}
    if family == "trend_bias" and label in ("long_bias", "short_bias"):
        return "dominant_direction"
    if family == "cross_venue_confirmation" and (label == "divergent_warning" or "cross_venue_divergence" in conflict_reasons):
        return "conflicting_evidence"
    if family == "liquidity_execution_quality" and label in ("liquidity_caution", "poor_liquidity", "liquidity_unknown"):
        return "risk_or_blocker_evidence"
    if family == "breakout_false_break" and label == "false_break_risk":
        return "scenario_switch_evidence"
    if family == "reversal_zone" and label in ("reversal_watch", "reaction_zone_watch", "vwap_reversion_watch"):
        return "turning_point_evidence"
    if family == "volatility_risk" and label == "elevated_risk":
        return "risk_or_blocker_evidence"
    if family == "macro_risk_context" and label == "macro_risk_watch":
        return "context_risk_evidence"
    if family == "algorithmic_participant_footprint" and label in ("algorithmic_activity_watch", "potential_sweep_reversal_footprint"):
        return "footprint_warning_evidence"
    if family == "opportunity_participation" and label in ("opportunity_blocked", "wait_for_confirmation"):
        return "participation_filter_evidence"
    return "supporting_context_evidence"


def _prediction_output_summary(output: PredictionOutput) -> str:
    bits = [f"{output.family.value}={output.primary_label}"]
    if output.score is not None:
        bits.append(f"score={round(float(output.score), 6)}")
    if output.drivers:
        bits.append("drivers=" + ",".join(str(item) for item in output.drivers[:3]))
    if output.warnings:
        bits.append("warnings=" + ",".join(str(item) for item in output.warnings[:3]))
    if output.blockers:
        bits.append("blockers=" + ",".join(str(item) for item in output.blockers[:3]))
    return "; ".join(bits)


def _scenario_evidence_refs(
    *,
    group: HorizonGroup,
    group_horizons: Tuple[int, ...],
    outputs: Tuple[PredictionOutput, ...],
    family_labels: Mapping[str, str],
    scenario_lite: Mapping[str, Any],
) -> Tuple[PredictionEvidenceRef, ...]:
    by_family = _best_output_by_family(outputs)
    preferred_order = (
        "trend_bias",
        "market_regime",
        "reversal_zone",
        "breakout_false_break",
        "volatility_risk",
        "liquidity_execution_quality",
        "cross_venue_confirmation",
        "opportunity_participation",
        "macro_risk_context",
        "algorithmic_participant_footprint",
        "human_technical_structure",
    )
    refs: list[PredictionEvidenceRef] = []
    horizon_label = "-".join(str(int(item)) for item in group_horizons) or "none"
    for family in preferred_order:
        output = by_family.get(family)
        if output is None:
            continue
        label = str(family_labels.get(family, output.primary_label))
        source_id = output.sources[0].source_id if output.sources else None
        refs.append(
            PredictionEvidenceRef(
                evidence_ref_id=f"{LOGIC_VERSION}:{group.value}:{horizon_label}:{family}",
                evidence_kind=_evidence_kind_for_family(family, label, scenario_lite),
                source_id=source_id,
                family=family,
                horizon_sec=int(output.horizon.horizon_sec),
                summary=_prediction_output_summary(output),
                weight=float(output.score) if output.score is not None else None,
                usable=not output.blockers,
                blockers=tuple(output.blockers),
                warnings=tuple(output.warnings),
            )
        )
    return tuple(refs)


def _scenario_trace_detail(
    *,
    group: HorizonGroup,
    group_horizons: Tuple[int, ...],
    primary_label: str,
    family_labels: Mapping[str, str],
    scenario_lite: Mapping[str, Any],
    evidence_refs: Tuple[PredictionEvidenceRef, ...],
) -> dict[str, Any]:
    balance = dict(scenario_lite.get("continuation_vs_reversal_balance", {}))
    return {
        "trace_version": "ps_h2.v1",
        "horizon_group": group.value,
        "display_label_ja": DISPLAY_LABEL_JA_BY_GROUP[group],
        "horizons_sec": list(group_horizons),
        "primary_label": primary_label,
        "continuation_vs_reversal_state": balance.get("state", "unknown"),
        "continuation_score": balance.get("continuation_score"),
        "reversal_score": balance.get("reversal_score"),
        "turning_point_risk": scenario_lite.get("turning_point_risk", "unknown"),
        "evidence_conflict_state": scenario_lite.get("evidence_conflict_state", "unknown"),
        "invalidation_state": scenario_lite.get("invalidation_state", "unknown"),
        "rewrite_state": scenario_lite.get("rewrite_state", "unknown"),
        "scenario_switch_hint": scenario_lite.get("scenario_switch_hint", "unknown"),
        "conflict_reasons": list(scenario_lite.get("conflict_reasons", [])),
        "what_to_watch_next": list(scenario_lite.get("what_to_watch_next", [])),
        "family_labels": dict(family_labels),
        "evidence_ref_ids": [item.evidence_ref_id for item in evidence_refs],
        "dominant_evidence_refs": [item.evidence_ref_id for item in evidence_refs if item.evidence_kind in ("dominant_direction", "scenario_switch_evidence", "turning_point_evidence")],
        "conflicting_evidence_refs": [item.evidence_ref_id for item in evidence_refs if item.evidence_kind in ("conflicting_evidence", "risk_or_blocker_evidence", "context_risk_evidence", "footprint_warning_evidence", "participation_filter_evidence")],
    }

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
    breakout = _best_label(group_outputs, "breakout_false_break")
    opportunity = _best_label(group_outputs, "opportunity_participation")
    cross = _best_label(group_outputs, "cross_venue_confirmation")
    macro = _best_label(group_outputs, "macro_risk_context")
    algo = _best_label(group_outputs, "algorithmic_participant_footprint")
    technical = _best_label(group_outputs, "human_technical_structure")
    family_labels = _family_label_map(group_outputs)
    scenario_lite = _scenario_signal_summary(family_labels, blockers, warnings)
    primary = _primary_label(group_outputs, blockers)
    evidence_refs = _scenario_evidence_refs(group=group, group_horizons=group_horizons, outputs=group_outputs, family_labels=family_labels, scenario_lite=scenario_lite)
    trace_detail = _scenario_trace_detail(group=group, group_horizons=group_horizons, primary_label=primary, family_labels=family_labels, scenario_lite=scenario_lite, evidence_refs=evidence_refs)
    lifetime_refresh = _refresh_decision_from_scenario_lite(scenario_lite)
    lifetime = _lifetime(now_dt, group, scenario_lite)
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
            "opportunity_participation": opportunity,
            "macro_risk_context": macro,
            "algorithmic_participant_footprint": algo,
            "invalidation_state": scenario_lite["invalidation_state"],
            "scenario_switch_hint": scenario_lite["scenario_switch_hint"],
            "evidence_conflict_state": scenario_lite["evidence_conflict_state"],
            "lifetime_refresh_required": lifetime.refresh_required,
            "lifetime_refresh_reason": lifetime.refresh_reason,
            "lifetime_refresh_trigger": lifetime.refresh_trigger,
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
        breakout_false_break_risk=breakout,
        volatility_risk=volatility,
        liquidity_execution_quality=liquidity,
        confidence=confidence,
        caution_level=caution,
        score=score,
        invalidation_state=scenario_lite["invalidation_state"],
        scenario_switch_hint=scenario_lite["scenario_switch_hint"],
        lifetime=lifetime,
        trigger_eligibility=trigger,
        evidence_refs=evidence_refs,
        human_narrative_ja=narrative,
        gpt_review_digest={
            "logic_version": LOGIC_VERSION,
            "family_labels": {
                "market_regime": regime,
                "trend_bias": trend,
                "reversal_zone": reversal,
                "volatility_risk": volatility,
                "liquidity_execution_quality": liquidity,
                "breakout_false_break": breakout,
                "opportunity_participation": opportunity,
                "cross_venue_confirmation": cross,
                "macro_risk_context": macro,
                "algorithmic_participant_footprint": algo,
                "human_technical_structure": technical,
            },
            "output_count": len(group_outputs),
            "blockers": list(blockers),
            "warnings": list(warnings),
            "scenario_lite": scenario_lite,
            "scenario_trace_detail": trace_detail,
            "evidence_ref_count": len(evidence_refs),
            "lifetime_refresh": lifetime_refresh,
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
    core_signals = _aggregate_core_signals(outlooks)
    outlook_traces = [dict(outlook.gpt_review_digest.get("scenario_trace_detail", {})) for outlook in outlooks if outlook.gpt_review_digest.get("scenario_trace_detail")]
    evidence_ref_count = sum(len(outlook.evidence_refs) for outlook in outlooks)
    refresh_required_count = sum(1 for outlook in outlooks if outlook.lifetime and outlook.lifetime.refresh_required)
    lifetime_state = "refresh_required" if refresh_required_count else "current_until_stale_after"
    first_balance = next((dict(outlook.gpt_review_digest.get("scenario_lite", {})).get("continuation_vs_reversal_balance") for outlook in outlooks if outlook.gpt_review_digest.get("scenario_lite")), {"state": "unknown"})
    evidence_weighting = next((dict(outlook.gpt_review_digest.get("scenario_lite", {})).get("evidence_weighting_summary") for outlook in outlooks if outlook.gpt_review_digest.get("scenario_lite")), {"state": "deterministic_family_label_weighting_v1"})
    return ScenarioCoreOutput(
        scenario_id=f"{LOGIC_VERSION}:scenario:{run_id}",
        generated_at=generated_at,
        current_regime_state=current_regime,
        current_hypothesis_health=health,
        outlooks=outlooks,
        continuation_vs_reversal_balance=first_balance if isinstance(first_balance, Mapping) else {"state": "unknown"},
        turning_point_risk=core_signals["turning_point_risk"],
        invalidation_state=core_signals["invalidation_state"],
        rewrite_state=core_signals["rewrite_state"],
        scenario_switch_hint=core_signals["scenario_switch_hint"],
        evidence_weighting_summary=evidence_weighting if isinstance(evidence_weighting, Mapping) else {"state": "deterministic_family_label_weighting_v1"},
        evidence_conflict_state=core_signals["evidence_conflict_state"],
        scenario_trace={
            "logic_version": LOGIC_VERSION,
            "families": [family.value for family in INITIAL_FAMILIES],
            "horizons_sec": sorted({int(output.horizon.horizon_sec) for output in outputs}),
            "output_count": len(outputs),
            "what_to_watch_next": core_signals["what_to_watch_next"],
            "conflict_reasons": core_signals["conflict_reasons"],
            "outlook_traces": outlook_traces,
            "evidence_ref_count": evidence_ref_count,
            "refresh_required_count": refresh_required_count,
            "prediction_lifetime_state": lifetime_state,
        },
        trigger_eligibility_state="blocked",
        human_narrative_ja="\n".join(outlook.human_narrative_ja for outlook in outlooks),
        gpt_review_digest={"logic_version": LOGIC_VERSION, "scenario_core_lite_version": "ps_h1.v1", "scenario_trace_detail_version": "ps_h2.v1", "lifetime_refresh_version": "ps_i1.v1", "outlook_count": len(outlooks), "evidence_ref_count": evidence_ref_count, "refresh_required_count": refresh_required_count, "prediction_lifetime_state": lifetime_state, "blockers": list(blockers), "warnings": list(warnings), "what_to_watch_next": core_signals["what_to_watch_next"], "conflict_reasons": core_signals["conflict_reasons"]},
        blockers=blockers,
        warnings=warnings,
    )



def _build_revision_summary(
    *,
    previous_prediction_run_id: str | None,
    scenario: ScenarioCoreOutput,
    horizons_sec: Tuple[int, ...],
) -> PredictionRevisionSummary:
    if not previous_prediction_run_id:
        return PredictionRevisionSummary()
    first_outlook = next((outlook for outlook in scenario.outlooks if outlook.usable), None)
    new_primary = first_outlook.primary_label if first_outlook else None
    new_confidence = first_outlook.confidence if first_outlook else None
    return PredictionRevisionSummary(
        previous_prediction_run_id=previous_prediction_run_id,
        revision_reason="previous_run_supplied_revision_lite_no_previous_snapshot",
        revision_trigger=scenario.scenario_switch_hint or "manual_or_scheduled_reprediction",
        changed_families=tuple(family.value for family in INITIAL_FAMILIES),
        changed_horizons_sec=tuple(sorted(int(item) for item in horizons_sec)),
        previous_primary_label=None,
        new_primary_label=new_primary,
        previous_confidence=None,
        new_confidence=new_confidence,
        previous_invalidation_state=None,
        new_invalidation_state=scenario.invalidation_state,
        change_summary_for_human="前回予測IDは指定されています。PS-I1では前回結果本体との差分比較は未実装ですが、現行シナリオの更新状態・失効監視・再予測理由を revision-lite として記録します。",
        change_summary_for_gpt={
            "revision_lite_version": "ps_i1.v1",
            "previous_prediction_run_id": previous_prediction_run_id,
            "new_primary_label": new_primary,
            "new_confidence": new_confidence,
            "new_invalidation_state": scenario.invalidation_state,
            "scenario_switch_hint": scenario.scenario_switch_hint,
            "evidence_conflict_state": scenario.evidence_conflict_state,
            "horizons_sec": sorted(int(item) for item in horizons_sec),
            "families": [family.value for family in INITIAL_FAMILIES],
            "full_previous_run_diff_available": False,
        },
    )


def _scenario_review_summary(
    *,
    scenario: ScenarioCoreOutput,
    outputs: Tuple[PredictionOutput, ...],
    forecast_batch: ForecastLedgerBatch,
    revision: PredictionRevisionSummary,
    provider_registry_summary: Mapping[str, Any],
    feature_depth_snapshot: FeatureDepthSnapshot | None,
    blockers: Tuple[str, ...],
    warnings: Tuple[str, ...],
) -> dict[str, Any]:
    """Build a review-only top-level scenario digest from already-emitted fields."""
    outlooks = tuple(scenario.outlooks)
    evidence_refs = tuple(ref for outlook in outlooks for ref in outlook.evidence_refs)
    support_kinds = {"dominant_direction", "supporting_context_evidence", "turning_point_evidence", "scenario_switch_evidence"}
    conflict_kinds = {"conflicting_evidence", "risk_or_blocker_evidence", "context_risk_evidence", "footprint_warning_evidence", "participation_filter_evidence"}

    def _ref_payload(ref: PredictionEvidenceRef) -> dict[str, Any]:
        return {
            "evidence_ref_id": ref.evidence_ref_id,
            "evidence_kind": ref.evidence_kind,
            "family": ref.family,
            "horizon_sec": ref.horizon_sec,
            "summary": ref.summary,
            "usable": ref.usable,
            "blockers": list(ref.blockers),
            "warnings": list(ref.warnings),
        }

    watch_next = list(dict.fromkeys(str(item) for item in scenario.scenario_trace.get("what_to_watch_next", [])))
    if not watch_next:
        watch_next = ["continue_monitoring_family_label_changes"]
    refresh_required_count = int(scenario.gpt_review_digest.get("refresh_required_count", 0) or 0)
    prediction_lifetime_state = str(scenario.gpt_review_digest.get("prediction_lifetime_state", "current_until_stale_after"))
    return {
        "version": "ps_n1.v1",
        "review_only": True,
        "primary_story": {
            "current_regime_state": scenario.current_regime_state,
            "current_hypothesis_health": scenario.current_hypothesis_health,
            "turning_point_risk": scenario.turning_point_risk,
            "evidence_conflict_state": scenario.evidence_conflict_state,
            "scenario_switch_hint": scenario.scenario_switch_hint,
            "headline_ja": scenario.human_narrative_ja.splitlines()[0] if scenario.human_narrative_ja else "",
        },
        "scenario_health": {
            "invalidation_state": scenario.invalidation_state,
            "rewrite_state": scenario.rewrite_state,
            "trigger_eligibility_state": scenario.trigger_eligibility_state,
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
        },
        "evidence_support": [_ref_payload(ref) for ref in evidence_refs if ref.evidence_kind in support_kinds][:8],
        "evidence_conflicts": [_ref_payload(ref) for ref in evidence_refs if ref.evidence_kind in conflict_kinds][:8],
        "watch_next": watch_next[:10],
        "refresh_or_rewrite": {
            "prediction_lifetime_state": prediction_lifetime_state,
            "refresh_required_count": refresh_required_count,
            "invalidation_state": scenario.invalidation_state,
            "rewrite_state": scenario.rewrite_state,
            "scenario_switch_hint": scenario.scenario_switch_hint,
        },
        "context_versions": {
            "scenario_core_lite_version": "ps_h1.v1",
            "scenario_trace_detail_version": "ps_h2.v1",
            "lifetime_refresh_version": "ps_i1.v1",
            "revision_lite_version": "ps_i1.v1",
            "provider_reliability_version": "ps_d1.v1",
            "liquidity_feature_depth_context_version": "ps_e2.v1" if feature_depth_snapshot is not None else None,
            "orderbook_breakout_algo_context_version": "ps_e3.v1" if feature_depth_snapshot is not None else None,
            "opportunity_tradeflow_context_version": "ps_e4.v1" if feature_depth_snapshot is not None else None,
        },
        "output_counts": {
            "family_count": len(INITIAL_FAMILIES),
            "output_count": len(outputs),
            "forecast_record_count": forecast_batch.record_count if isinstance(forecast_batch, ForecastLedgerBatch) else 0,
            "outlook_count": len(outlooks),
            "evidence_ref_count": len(evidence_refs),
            "provider_count": int(provider_registry_summary.get("provider_count", 0) or 0),
            "usable_provider_count": int(provider_registry_summary.get("usable_provider_count", 0) or 0),
        },
        "boundaries": {
            "read_only": True,
            "non_executing": True,
            "would_collect_public_source": False,
            "would_send_to_broker": False,
            "broker_execution_requested": False,
            "mode_apply_requested": False,
            "command_ledger_append_requested": False,
            "trigger_eligibility_state": scenario.trigger_eligibility_state,
            "feature_depth_context_only": bool(feature_depth_snapshot.context_only) if feature_depth_snapshot is not None else None,
            "feature_depth_primary_direction_owner": bool(feature_depth_snapshot.primary_direction_owner) if feature_depth_snapshot is not None else None,
            "has_revision": revision.has_revision,
        },
    }

def build_prediction_system_result(
    *,
    rows: Iterable[Mapping[str, Any]] | None = None,
    candles: Iterable[OHLCVCandle] | None = None,
    venue_snapshots: Iterable[Mapping[str, Any]] | None = None,
    source_quality_by_id: Mapping[str, SourceQualityStatus] | None = None,
    requested_horizon_groups: Iterable[HorizonGroup | str] | None = None,
    requested_horizons_sec: Iterable[int] | None = None,
    previous_prediction_run_id: str | None = None,
    feature_depth_snapshot: FeatureDepthSnapshot | None = None,
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
    observed_source_ids = _observed_source_ids(venue_snapshots)
    cross = _build_cross_venue(venue_snapshots=venue_snapshots, source_quality_by_id=source_quality_by_id, now_dt=now_dt)
    provider_registry = build_provider_reliability_registry(source_quality_by_id=dict(source_quality_by_id or {}), observed_source_ids=observed_source_ids, now=now_dt)
    provider_registry_summary = provider_registry.to_dict()
    outputs, technical_by_horizon = _build_outputs(candles=built_candles, cross_venue_summary=cross, horizons_sec=horizons_sec, now_dt=now_dt, feature_depth_snapshot=feature_depth_snapshot)

    source_quality_summary: dict[str, Any] = {
        "logic_version": LOGIC_VERSION,
        "source_quality_count": len(source_quality_by_id or {}),
        "ohlcv_diagnostics": ohlcv_diagnostics.to_dict() if ohlcv_diagnostics else None,
        "cross_venue_summary": cross.to_dict() if cross else None,
        "technical_timeframes": {str(h): (summary.timeframe_sec if summary else None) for h, summary in technical_by_horizon.items()},
        "provider_reliability_registry": provider_registry_summary,
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
        provider_quality_summary={"source_quality_count": len(source_quality_by_id or {}), "observed_source_ids": list(observed_source_ids), "provider_reliability_registry": provider_registry_summary},
        feature_snapshot={
            "row_count": _input_rows_count(rows),
            "candle_count": len(built_candles),
            "venue_snapshot_supplied": venue_snapshots is not None,
            "horizons_sec": list(horizons_sec),
            "families": [family.value for family in INITIAL_FAMILIES],
            "feature_depth_snapshot_supplied": feature_depth_snapshot is not None,
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
    revision = _build_revision_summary(previous_prediction_run_id=previous_prediction_run_id, scenario=scenario, horizons_sec=horizons_sec)
    prediction_lifetime_state = str(scenario.gpt_review_digest.get("prediction_lifetime_state", "current_until_stale_after"))

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
            "prediction_lifetime_state": prediction_lifetime_state,
            "refresh_required_count": scenario.gpt_review_digest.get("refresh_required_count", 0),
            "revision_lite_version": "ps_i1.v1",
            "has_revision": revision.has_revision,
            "provider_reliability_version": "ps_d1.v1",
            "provider_reliability_context_only": provider_registry.context_only,
            "liquidity_feature_depth_context_version": "ps_e2.v1" if feature_depth_snapshot is not None else None,
            "orderbook_breakout_algo_context_version": "ps_e3.v1" if feature_depth_snapshot is not None else None,
            "opportunity_tradeflow_context_version": "ps_e4.v1" if feature_depth_snapshot is not None else None,
            "feature_depth_context_only": bool(feature_depth_snapshot.context_only) if feature_depth_snapshot is not None else None,
            "feature_depth_primary_direction_owner": bool(feature_depth_snapshot.primary_direction_owner) if feature_depth_snapshot is not None else None,
            "provider_count": provider_registry.provider_count,
            "usable_provider_count": provider_registry.usable_provider_count,
            "unknown_provider_source_count": len(provider_registry.unknown_source_ids),
            "scenario_review_summary": _scenario_review_summary(
                scenario=scenario,
                outputs=outputs,
                forecast_batch=forecast_batch,
                revision=revision,
                provider_registry_summary=provider_registry_summary,
                feature_depth_snapshot=feature_depth_snapshot,
                blockers=tuple(dict.fromkeys(blockers)),
                warnings=tuple(dict.fromkeys(warnings)),
            ),
            "blockers": list(dict.fromkeys(blockers)),
            "warnings": list(dict.fromkeys(warnings)),
        },
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
