# path: ./btcts_next/src/btcts/prediction/market_regime/feature_scoring.py
# desc: MR-F3 pure explainable candidate scoring with feature-group decomposition and explicit missing/blocker semantics. No reads, writes, UI, broker, scheduler, or AutoTrade.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .contracts import FeatureGroup
from .features import MarketRegimeFeatureBundle
from .parameter_set import MarketRegimeParameterSet, build_default_market_regime_parameter_set

MARKET_REGIME_FEATURE_SCORING_VERSION = "prediction.market_regime.feature_scoring.mr_f3.v1"
CANDIDATE_NAMES = (
    "trend_score",
    "range_score",
    "breakout_score",
    "high_vol_chop_score",
    "compression_score",
    "reversal_score",
    "panic_score",
)


@dataclass(frozen=True)
class FeatureContribution:
    feature_group: str
    status: str
    raw_support: float | None
    weight: float
    weighted_support: float | None
    evidence: Mapping[str, Any]
    contradictory: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clamp(value: float) -> float:
    return round(max(0.0, min(float(value), 1.0)), 4)


def _signals(bundle: MarketRegimeFeatureBundle, group: FeatureGroup) -> dict[str, Any]:
    return {signal.name: signal for signal in bundle.signals_by_group(group)}


def _available_value(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str) -> tuple[bool, Any]:
    signal = _signals(bundle, group).get(name)
    if signal is None or not signal.available:
        return False, None
    return True, signal.value


def _number(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str) -> float | None:
    available, value = _available_value(bundle, group, name)
    if not available:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _boolean(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str) -> bool | None:
    available, value = _available_value(bundle, group, name)
    return bool(value) if available else None


def _text(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str) -> str | None:
    available, value = _available_value(bundle, group, name)
    return str(value) if available and value is not None else None


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return _clamp(abs(numerator) / denominator)


def _group_supports(bundle: MarketRegimeFeatureBundle, thresholds: Mapping[str, Any]) -> dict[str, dict[str, float | None]]:
    net = _number(bundle, FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps")
    window_range = _number(bundle, FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_range_bps")
    close_position = _number(bundle, FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_close_position")
    directional = _ratio(net, window_range)
    centered = None if close_position is None else _clamp(1.0 - abs(close_position - 0.5) * 2.0)
    edge = None if close_position is None else _clamp(abs(close_position - 0.5) * 2.0)

    realized_vol = _number(bundle, FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps")
    avg_range = _number(bundle, FeatureGroup.VOLATILITY, "current_l4_candle_average_range_bps")
    vol_scale = max(float(thresholds.get("volatility_reference_bps", 20.0)), 0.0001)
    vol_high = None if realized_vol is None else _clamp(realized_vol / vol_scale)
    vol_low = None if vol_high is None else _clamp(1.0 - vol_high)
    range_high = None if avg_range is None else _clamp(avg_range / vol_scale)

    spread = _number(bundle, FeatureGroup.LIQUIDITY, "spread_bps")
    depth_imbalance = _number(bundle, FeatureGroup.LIQUIDITY, "depth_imbalance")
    disappearance = _number(bundle, FeatureGroup.LIQUIDITY, "liquidity_disappearance_score")
    replenishment = _number(bundle, FeatureGroup.LIQUIDITY, "liquidity_replenishment_score")
    crossed = _boolean(bundle, FeatureGroup.LIQUIDITY, "crossed_or_negative_spread")
    spread_scale = max(float(thresholds.get("spread_stress_bps", 8.0)), 0.0001)
    liquidity_stress = None if spread is None else _clamp(abs(spread) / spread_scale)
    if crossed is True:
        liquidity_stress = 1.0
    liquidity_health = None if liquidity_stress is None else _clamp(1.0 - liquidity_stress)

    orderflow = _number(bundle, FeatureGroup.ORDERFLOW, "orderflow_imbalance")
    acceleration = _number(bundle, FeatureGroup.ORDERFLOW, "volume_acceleration")
    orderflow_directional = None if orderflow is None else _clamp(abs(orderflow))
    orderflow_balanced = None if orderflow_directional is None else _clamp(1.0 - orderflow_directional)
    acceleration_high = None if acceleration is None else _clamp(abs(acceleration))

    agreement = (_text(bundle, FeatureGroup.CROSS_VENUE, "cross_venue_agreement") or "").lower()
    cross_aligned = None if not agreement else (1.0 if agreement in {"aligned", "agree", "agreement"} else 0.0)
    cross_conflict = None if cross_aligned is None else _clamp(1.0 - cross_aligned)

    quality = _number(bundle, FeatureGroup.SOURCE_QUALITY, "source_quality_score")
    current_enough = _boolean(bundle, FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_current_enough")
    source_support = None if quality is None else _clamp(quality)
    if current_enough is False:
        source_support = 0.0

    return {
        "price_structure": {
            "trend_score": directional,
            "range_score": None if directional is None or centered is None else _clamp((1.0 - directional) * 0.6 + centered * 0.4),
            "breakout_score": None if directional is None or edge is None else _clamp(directional * 0.55 + edge * 0.45),
            "high_vol_chop_score": None if directional is None else _clamp(1.0 - directional),
            "compression_score": None if directional is None or centered is None else _clamp((1.0 - directional) * 0.5 + centered * 0.5),
            "reversal_score": edge,
            "panic_score": directional,
        },
        "volatility": {
            "trend_score": None if vol_high is None else _clamp(1.0 - abs(vol_high - 0.55)),
            "range_score": vol_low,
            "breakout_score": vol_high,
            "high_vol_chop_score": None if vol_high is None or range_high is None else _clamp(vol_high * 0.6 + range_high * 0.4),
            "compression_score": vol_low,
            "reversal_score": vol_high,
            "panic_score": vol_high,
        },
        "liquidity": {
            "trend_score": liquidity_health,
            "range_score": liquidity_health,
            "breakout_score": None if disappearance is None else _clamp(disappearance),
            "high_vol_chop_score": liquidity_stress,
            "compression_score": None if replenishment is None else _clamp(replenishment),
            "reversal_score": None if depth_imbalance is None else _clamp(abs(depth_imbalance)),
            "panic_score": None if liquidity_stress is None or disappearance is None else _clamp(liquidity_stress * 0.6 + _clamp(disappearance) * 0.4),
        },
        "orderflow": {
            "trend_score": orderflow_directional,
            "range_score": orderflow_balanced,
            "breakout_score": None if orderflow_directional is None or acceleration_high is None else _clamp(orderflow_directional * 0.6 + acceleration_high * 0.4),
            "high_vol_chop_score": orderflow_balanced,
            "compression_score": orderflow_balanced,
            "reversal_score": orderflow_directional,
            "panic_score": None if orderflow_directional is None or acceleration_high is None else _clamp(orderflow_directional * 0.5 + acceleration_high * 0.5),
        },
        "cross_venue": {
            "trend_score": cross_aligned,
            "range_score": cross_aligned,
            "breakout_score": cross_aligned,
            "high_vol_chop_score": cross_conflict,
            "compression_score": cross_aligned,
            "reversal_score": cross_conflict,
            "panic_score": cross_conflict,
        },
        "source_quality": {name: source_support for name in CANDIDATE_NAMES},
    }


def summarize_market_regime_candidate_scores(
    packet: Mapping[str, Any],
    *,
    parameter_set: MarketRegimeParameterSet | None = None,
) -> dict[str, Any]:
    params = parameter_set or build_default_market_regime_parameter_set()
    thresholds = dict(params.thresholds.get("explainable_candidate_scoring", {}))
    rows = packet.get("candidate_scores") if isinstance(packet.get("candidate_scores"), Mapping) else {}
    min_weight = float(thresholds.get("label_selection_min_available_weight", 0.65))
    min_score = float(thresholds.get("label_selection_min_top_score", 0.55))
    min_margin = float(thresholds.get("label_selection_min_margin", 0.08))
    required_groups = tuple(str(item) for item in thresholds.get(
        "label_selection_required_feature_groups",
        ("price_structure", "volatility", "liquidity", "source_quality"),
    ))
    all_ranked = sorted(
        (
            (str(name), float(row.get("score")), row)
            for name, row in rows.items()
            if isinstance(row, Mapping) and row.get("score") is not None
        ),
        key=lambda item: (-item[1], item[0]),
    )
    eligible_ranked = []
    ineligible_candidates: dict[str, list[str]] = {}
    for name, score, row in all_ranked:
        reasons: list[str] = []
        available_weight = float(row.get("available_weight") or 0.0)
        missing = {str(item) for item in row.get("missing_feature_groups") or []}
        if available_weight < min_weight:
            reasons.append("available_weight_below_minimum")
        missing_required = sorted(set(required_groups) & missing)
        if missing_required:
            reasons.extend(f"required_feature_group_missing:{group}" for group in missing_required)
        if reasons:
            ineligible_candidates[name] = reasons
        else:
            eligible_ranked.append((name, score, row))
    top_name, top_score, top_row = all_ranked[0] if all_ranked else ("", None, {})
    runner_name, runner_score, _ = all_ranked[1] if len(all_ranked) > 1 else ("", None, {})
    margin = None if top_score is None or runner_score is None else round(top_score - runner_score, 4)
    eligible_top_name, eligible_top_score, eligible_top_row = (
        eligible_ranked[0] if eligible_ranked else ("", None, {})
    )
    eligible_runner_name, eligible_runner_score, _ = (
        eligible_ranked[1] if len(eligible_ranked) > 1 else ("", None, {})
    )
    eligible_margin = (
        None
        if eligible_top_score is None or eligible_runner_score is None
        else round(eligible_top_score - eligible_runner_score, 4)
    )
    available_weight = float(top_row.get("available_weight") or 0.0) if isinstance(top_row, Mapping) else 0.0
    blockers = list(packet.get("blockers") or [])
    readiness_blockers = list(blockers)
    if not eligible_ranked:
        readiness_blockers.append("no_label_selection_eligible_candidate")
    if eligible_top_score is not None and eligible_top_score < min_score:
        readiness_blockers.append("top_score_below_minimum")
    if eligible_margin is None:
        readiness_blockers.append("eligible_runner_up_missing")
    elif eligible_margin < min_margin:
        readiness_blockers.append("score_margin_below_minimum")
    ready = not readiness_blockers
    return {
        "top_candidate": top_name,
        "top_candidate_score": top_score,
        "runner_up_candidate": runner_name,
        "runner_up_score": runner_score,
        "score_margin": margin,
        "top_candidate_available_weight": round(available_weight, 4),
        "top_candidate_missing_feature_groups": list(top_row.get("missing_feature_groups") or []) if isinstance(top_row, Mapping) else [],
        "top_candidate_contradictory_feature_groups": list(top_row.get("contradictory_feature_groups") or []) if isinstance(top_row, Mapping) else [],
        "top_candidate_contributions": list(top_row.get("contributions") or []) if isinstance(top_row, Mapping) else [],
        "eligible_top_candidate": eligible_top_name,
        "eligible_top_candidate_score": eligible_top_score,
        "eligible_runner_up_candidate": eligible_runner_name,
        "eligible_runner_up_score": eligible_runner_score,
        "eligible_score_margin": eligible_margin,
        "eligible_top_candidate_available_weight": round(
            float(eligible_top_row.get("available_weight") or 0.0), 4
        ) if isinstance(eligible_top_row, Mapping) else 0.0,
        "scoring_blockers": blockers,
        "label_selection_readiness_blockers": readiness_blockers,
        "label_selection_ineligible_candidates": ineligible_candidates,
        "label_selection_eligible_candidates": [name for name, _, _ in eligible_ranked],
        "scoring_ready_for_label_selection": ready,
        "label_selection_enabled": False,
        "label_selection_deferred_reason": "mr_f3_observe_before_cutover",
        "readiness_thresholds": {
            "min_available_weight": min_weight,
            "min_top_score": min_score,
            "min_margin": min_margin,
            "required_feature_groups": list(required_groups),
        },
    }


def score_market_regime_candidates(
    bundle: MarketRegimeFeatureBundle,
    *,
    parameter_set: MarketRegimeParameterSet | None = None,
) -> dict[str, Any]:
    params = parameter_set or build_default_market_regime_parameter_set()
    scoring_thresholds = dict(params.thresholds.get("explainable_candidate_scoring", {}))
    supports = _group_supports(bundle, scoring_thresholds)
    current_enough = _boolean(bundle, FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_current_enough")
    blockers = [] if current_enough is True else ["current_l4_candle_window_not_current"]
    candidates: dict[str, Any] = {}

    for candidate in CANDIDATE_NAMES:
        contributions: list[FeatureContribution] = []
        weighted_total = 0.0
        available_weight = 0.0
        missing_groups: list[str] = []
        contradictory_groups: list[str] = []
        for group in params.required_feature_groups:
            group_name = group.value
            support = supports.get(group_name, {}).get(candidate)
            weight = float(params.weights.get(group_name, 0.0))
            if support is None:
                missing_groups.append(group_name)
                contributions.append(FeatureContribution(group_name, "missing", None, weight, None, {}))
                continue
            support = _clamp(support)
            contradictory = support <= float(scoring_thresholds.get("contradictory_support_max", 0.2))
            if contradictory:
                contradictory_groups.append(group_name)
            weighted = round(support * weight, 6)
            weighted_total += weighted
            available_weight += weight
            contributions.append(
                FeatureContribution(
                    group_name,
                    "available",
                    support,
                    weight,
                    weighted,
                    {"candidate": candidate},
                    contradictory,
                )
            )
        score = None if blockers or available_weight <= 0 else round(weighted_total / available_weight, 4)
        candidates[candidate] = {
            "score": score,
            "score_status": "blocked" if blockers else ("available" if score is not None else "missing"),
            "available_weight": round(available_weight, 4),
            "missing_feature_groups": missing_groups,
            "contradictory_feature_groups": contradictory_groups,
            "blockers": list(blockers),
            "contributions": [item.to_dict() for item in contributions],
        }

    return {
        "ok": not blockers,
        "logic_version": MARKET_REGIME_FEATURE_SCORING_VERSION,
        "parameter_set_id": params.parameter_set_id,
        "candidate_scores": candidates,
        "missing_feature_is_zero_evidence": False,
        "freshness_and_quality_separate": True,
        "blockers": blockers,
        "read_only": True,
        "non_executing": True,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }
