# path: ./btcts_next/src/btcts/prediction/rule_based_v0.py
# desc: Non-executing rule-based v0 prediction-family skeletons. Emits PredictionOutput only; no AutoTrade or broker side effects.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from .contracts import PredictionConfidence, PredictionFamily, PredictionOutput, SourceIdentity
from .cross_venue import CrossVenueReferenceSummary
from .feature_depth import FeatureDepthSnapshot
from .horizons import horizon_by_seconds
from .parameter_sets import default_prediction_parameter_set_for_family
from .technical import HumanTechnicalSummary

LOGIC_VERSION = "prediction_rule_based_v0.s128.v1"
INITIAL_FAMILIES: Tuple[PredictionFamily, ...] = (
    PredictionFamily.MARKET_REGIME,
    PredictionFamily.TREND_BIAS,
    PredictionFamily.REVERSAL_ZONE,
    PredictionFamily.VOLATILITY_RISK,
    PredictionFamily.LIQUIDITY_EXECUTION_QUALITY,
    PredictionFamily.BREAKOUT_FALSE_BREAK,
    PredictionFamily.OPPORTUNITY_PARTICIPATION,
    PredictionFamily.CROSS_VENUE_CONFIRMATION,
    PredictionFamily.MACRO_RISK_CONTEXT,
    PredictionFamily.ALGORITHMIC_PARTICIPANT_FOOTPRINT,
    PredictionFamily.HUMAN_TECHNICAL_STRUCTURE,
)


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _source(summary_kind: str) -> SourceIdentity:
    return SourceIdentity(
        source_id=f"rule_based_v0_{summary_kind}",
        source_family="derived_prediction_summary",
        venue=None,
        symbol=None,
        market_role="derived_reference",
        public_data_only=True,
        execution_enabled=False,
    )


def _confidence(score: float | None, blockers: Tuple[str, ...] = ()) -> PredictionConfidence:
    if blockers or score is None:
        return PredictionConfidence.UNKNOWN
    if score >= 0.70:
        return PredictionConfidence.HIGH
    if score >= 0.45:
        return PredictionConfidence.MEDIUM
    return PredictionConfidence.LOW


def _output(
    *,
    family: PredictionFamily,
    generated_at: str,
    horizon_sec: int,
    primary_label: str,
    score: float | None,
    drivers: Tuple[str, ...] = (),
    blockers: Tuple[str, ...] = (),
    warnings: Tuple[str, ...] = (),
    values: Dict[str, Any] | None = None,
) -> PredictionOutput:
    parameter_set = default_prediction_parameter_set_for_family(family).identity()
    return PredictionOutput(
        prediction_id=f"{LOGIC_VERSION}:{family.value}:{int(horizon_sec)}s",
        generated_at=generated_at,
        family=family,
        horizon=horizon_by_seconds(horizon_sec),
        parameter_set=parameter_set,
        sources=(_source(family.value),),
        confidence=_confidence(score, blockers),
        primary_label=primary_label,
        score=score,
        drivers=drivers,
        blockers=blockers,
        warnings=warnings,
        values=values or {},
    )


def _market_regime(technical: HumanTechnicalSummary | None, cross: CrossVenueReferenceSummary | None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    blockers: list[str] = []
    drivers: list[str] = []
    if technical is None or not technical.usable:
        blockers.append("human_technical_summary_missing_or_blocked")
    if cross is None or not cross.usable:
        blockers.append("cross_venue_summary_missing_or_blocked")
    if blockers:
        return "unknown", None, tuple(drivers), tuple(blockers), {}
    vol_state = technical.volatility.state
    ma_state = technical.moving_average.slope_label
    agreement = cross.agreement_state
    if vol_state == "expanding" or agreement == "divergent":
        label = "volatile_or_divergent"
        score = 0.68
        drivers.append("volatility_or_cross_venue_divergence")
    elif ma_state in ("rising", "falling") and technical.moving_average.cross_state != "aligned":
        label = "trend_candidate"
        score = 0.62
        drivers.append("moving_average_directional_structure")
    elif technical.range_boundary.close_position in ("mid_range", "near_range_high", "near_range_low"):
        label = "range_candidate"
        score = 0.52
        drivers.append("range_boundary_visible")
    else:
        label = "unclear"
        score = 0.30
    return label, score, tuple(drivers), tuple(), {"volatility_state": vol_state, "ma_state": ma_state, "cross_venue_agreement": agreement}


def _trend_bias(technical: HumanTechnicalSummary | None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    if technical is None or not technical.usable:
        return "unknown", None, tuple(), ("human_technical_summary_missing_or_blocked",), {}
    ma = technical.moving_average
    vwap = technical.vwap_relation
    drivers: list[str] = []
    if ma.slope_label == "rising" and ma.cross_state == "short_above_long":
        label = "long_bias"
        score = 0.66
        drivers.append("ma_rising_short_above_long")
    elif ma.slope_label == "falling" and ma.cross_state == "short_below_long":
        label = "short_bias"
        score = 0.66
        drivers.append("ma_falling_short_below_long")
    else:
        label = "neutral_bias"
        score = 0.35
    if vwap.relation in ("above_vwap", "below_vwap", "near_vwap"):
        drivers.append(f"vwap_{vwap.relation}")
    return label, score, tuple(drivers), tuple(), {"ma": ma.to_dict(), "vwap": vwap.to_dict()}


def _reversal_zone(technical: HumanTechnicalSummary | None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    if technical is None or not technical.usable:
        return "unknown", None, tuple(), ("human_technical_summary_missing_or_blocked",), tuple(), {}
    rb = technical.range_boundary
    wick = technical.wick_body
    vwap = technical.vwap_relation
    drivers: list[str] = []
    warnings: list[str] = []
    values = {
        "range_boundary": rb.to_dict(),
        "wick_body": wick.to_dict(),
        "vwap_relation": vwap.to_dict(),
        "support_zones": [zone.to_dict() for zone in technical.support_zones],
        "resistance_zones": [zone.to_dict() for zone in technical.resistance_zones],
    }
    if rb.close_position in ("near_range_high", "near_range_low"):
        drivers.append(f"range_boundary_{rb.close_position}")
    if wick.wick_signal in ("upper_wick_rejection", "lower_wick_rejection"):
        drivers.append(f"wick_{wick.wick_signal}")
    if vwap.relation in ("above_vwap", "below_vwap", "near_vwap"):
        drivers.append(f"vwap_{vwap.relation}")

    if rb.close_position == "near_range_high" and wick.wick_signal == "upper_wick_rejection":
        label = "reversal_watch"
        score = 0.72
        warnings.append("upper_range_reversal_watch")
    elif rb.close_position == "near_range_low" and wick.wick_signal == "lower_wick_rejection":
        label = "reversal_watch"
        score = 0.72
        warnings.append("lower_range_reversal_watch")
    elif rb.close_position in ("near_range_high", "near_range_low"):
        label = "reaction_zone_watch"
        score = 0.58
    elif vwap.relation == "near_vwap" and wick.wick_signal in ("upper_wick_rejection", "lower_wick_rejection", "mixed_wick_body"):
        label = "vwap_reversion_watch"
        score = 0.50
    else:
        label = "low_reversal_signal"
        score = 0.32
    return label, score, tuple(drivers or ("no_strong_reversal_driver",)), tuple(), tuple(warnings), values


def _volatility_risk(technical: HumanTechnicalSummary | None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    if technical is None or not technical.usable:
        return "unknown", None, tuple(), ("human_technical_summary_missing_or_blocked",), {}
    vol = technical.volatility
    if vol.state == "expanding":
        label = "elevated_risk"
        score = 0.72
    elif vol.state == "compressed":
        label = "compression_watch"
        score = 0.58
    elif vol.state == "normal":
        label = "normal_risk"
        score = 0.50
    else:
        label = "unknown"
        score = None
    return label, score, (f"volatility_state_{vol.state}",), tuple(), vol.to_dict()



def _apply_liquidity_feature_depth_context(
    *,
    values: Dict[str, Any],
    drivers: list[str],
    warnings: list[str],
    feature_depth_snapshot: FeatureDepthSnapshot | None,
) -> None:
    if feature_depth_snapshot is None:
        return
    snapshot = feature_depth_snapshot.to_dict()
    orderbook = dict(snapshot.get("orderbook", {}))
    tradeflow = dict(snapshot.get("tradeflow", {}))
    values["feature_depth_context"] = {
        "version": "ps_e2.v1",
        "feature_depth_state": snapshot.get("feature_depth_state"),
        "context_only": bool(snapshot.get("context_only", True)),
        "primary_direction_owner": bool(snapshot.get("primary_direction_owner", False)),
        "usable_for_primary_short_horizon": bool(snapshot.get("usable_for_primary_short_horizon", False)),
        "orderbook_state": orderbook.get("state"),
        "orderbook_average_spread_bps": orderbook.get("average_spread_bps"),
        "orderbook_spread_warning": bool(orderbook.get("spread_warning", False)),
        "orderbook_thin_book_warning": bool(orderbook.get("thin_book_warning", False)),
        "tradeflow_state": tradeflow.get("state"),
        "tradeflow_buy_sell_imbalance_ratio": tradeflow.get("buy_sell_imbalance_ratio"),
        "tradeflow_burst_warning": bool(tradeflow.get("burst_warning", False)),
    }
    values["feature_depth_input_ref_count"] = len(snapshot.get("input_refs", []))
    drivers.append("liquidity_feature_depth_context_supplied")
    if not bool(snapshot.get("context_only", True)):
        warnings.append("feature_depth_not_context_only_ignored_for_primary_direction")
    if bool(snapshot.get("primary_direction_owner", False)) or bool(snapshot.get("usable_for_primary_short_horizon", False)):
        warnings.append("feature_depth_primary_direction_disabled_in_ps_e2")
    if snapshot.get("feature_depth_state") in ("unavailable", "warning_context"):
        warnings.append(f"feature_depth_{snapshot.get('feature_depth_state')}")
    if orderbook.get("spread_warning"):
        warnings.append("feature_depth_orderbook_spread_warning")
    if orderbook.get("thin_book_warning"):
        warnings.append("feature_depth_orderbook_thin_book_warning")
    if tradeflow.get("burst_warning"):
        warnings.append("feature_depth_tradeflow_burst_warning")
    for item in list(snapshot.get("warnings", []))[:4]:
        warnings.append(f"feature_depth_warning:{item}")

def _liquidity_execution_quality(technical: HumanTechnicalSummary | None, cross: CrossVenueReferenceSummary | None, feature_depth_snapshot: FeatureDepthSnapshot | None = None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    drivers: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []
    values: Dict[str, Any] = {
        "proxy_kind": "summary_based_liquidity_proxy_v1",
        "note": "uses technical volatility and cross-venue summary; optional feature_depth_snapshot is context/warning only",
    }
    technical_usable = bool(technical and technical.usable)
    cross_usable = bool(cross and cross.usable)
    if not technical_usable and not cross_usable:
        blockers.append("liquidity_proxy_inputs_missing_or_blocked")
        _apply_liquidity_feature_depth_context(values=values, drivers=drivers, warnings=warnings, feature_depth_snapshot=feature_depth_snapshot)
        return "liquidity_unknown", None, tuple(drivers or ("liquidity_proxy_no_strong_driver",)), tuple(blockers), tuple(dict.fromkeys(warnings)), values

    score = 0.62
    if technical_usable and technical is not None:
        vol_state = technical.volatility.state
        values["volatility_state"] = vol_state
        values["technical_warning_count"] = len(technical.warnings)
        drivers.append(f"technical_volatility_{vol_state}")
        if vol_state == "expanding":
            score -= 0.18
            warnings.append("expanding_volatility_liquidity_caution")
        elif vol_state == "compressed":
            score -= 0.05
            warnings.append("compressed_volatility_liquidity_watch")
        if technical.warnings:
            score -= min(0.10, 0.03 * len(technical.warnings))
            warnings.extend(f"technical_warning:{item}" for item in technical.warnings[:3])
    else:
        score -= 0.12
        warnings.append("technical_summary_missing_for_liquidity_proxy")

    if cross_usable and cross is not None:
        values["cross_venue_agreement_state"] = cross.agreement_state
        values["usable_venue_count"] = cross.usable_venue_count
        values["max_deviation_pct"] = cross.max_deviation_pct
        values["spot_fx_basis_state"] = cross.spot_fx_basis.premium_discount_state
        drivers.append(f"cross_venue_{cross.agreement_state}")
        if cross.usable_venue_count < 2:
            score -= 0.15
            warnings.append("low_usable_venue_count_liquidity_caution")
        if cross.agreement_state == "divergent":
            score -= 0.20
            warnings.append("cross_venue_divergence_liquidity_caution")
        elif cross.agreement_state == "confirmed":
            score += 0.04
        if cross.spot_fx_basis.blockers:
            score -= 0.08
            warnings.extend(f"basis_blocker:{item}" for item in cross.spot_fx_basis.blockers[:3])
        if cross.spot_fx_basis.premium_discount_state in ("fx_premium", "fx_discount"):
            score -= 0.05
            warnings.append(f"spot_fx_basis_{cross.spot_fx_basis.premium_discount_state}")
        if cross.warnings:
            score -= min(0.10, 0.03 * len(cross.warnings))
            warnings.extend(f"cross_warning:{item}" for item in cross.warnings[:3])
    else:
        score -= 0.15
        warnings.append("cross_venue_summary_missing_for_liquidity_proxy")

    _apply_liquidity_feature_depth_context(values=values, drivers=drivers, warnings=warnings, feature_depth_snapshot=feature_depth_snapshot)

    score = max(0.0, min(1.0, score))
    if score >= 0.64 and not warnings:
        label = "liquidity_proxy_adequate"
    elif score >= 0.44:
        label = "liquidity_caution"
    elif score >= 0.20:
        label = "poor_liquidity"
    else:
        label = "liquidity_unknown"
    return label, round(score, 6), tuple(drivers or ("liquidity_proxy_no_strong_driver",)), tuple(blockers), tuple(dict.fromkeys(warnings)), values



def _apply_feature_depth_context_for_family(
    *,
    target_family: str,
    values: Dict[str, Any],
    drivers: list[str],
    warnings: list[str],
    feature_depth_snapshot: FeatureDepthSnapshot | None,
) -> None:
    if feature_depth_snapshot is None:
        return
    snapshot = feature_depth_snapshot.to_dict()
    orderbook = dict(snapshot.get("orderbook", {}))
    tradeflow = dict(snapshot.get("tradeflow", {}))
    values["feature_depth_context"] = {
        "version": "ps_e3.v1",
        "target_family": target_family,
        "feature_depth_state": snapshot.get("feature_depth_state"),
        "context_only": bool(snapshot.get("context_only", True)),
        "primary_direction_owner": bool(snapshot.get("primary_direction_owner", False)),
        "usable_for_primary_short_horizon": bool(snapshot.get("usable_for_primary_short_horizon", False)),
        "orderbook_state": orderbook.get("state"),
        "orderbook_average_spread_bps": orderbook.get("average_spread_bps"),
        "orderbook_max_abs_imbalance_ratio": orderbook.get("max_abs_imbalance_ratio"),
        "orderbook_spread_warning": bool(orderbook.get("spread_warning", False)),
        "orderbook_thin_book_warning": bool(orderbook.get("thin_book_warning", False)),
        "tradeflow_state": tradeflow.get("state"),
        "tradeflow_buy_sell_imbalance_ratio": tradeflow.get("buy_sell_imbalance_ratio"),
        "tradeflow_aggressive_flow_ratio": tradeflow.get("aggressive_flow_ratio"),
        "tradeflow_burst_warning": bool(tradeflow.get("burst_warning", False)),
    }
    values["feature_depth_input_ref_count"] = len(snapshot.get("input_refs", []))
    if target_family == "breakout_false_break":
        drivers.append("breakout_false_break_feature_depth_context_supplied")
    elif target_family == "algorithmic_participant_footprint":
        drivers.append("algorithmic_participant_footprint_feature_depth_context_supplied")
    else:
        drivers.append(f"{target_family}_feature_depth_context_supplied")
    if not bool(snapshot.get("context_only", True)):
        warnings.append(f"{target_family}_feature_depth_not_context_only_ignored")
    if bool(snapshot.get("primary_direction_owner", False)) or bool(snapshot.get("usable_for_primary_short_horizon", False)):
        warnings.append(f"{target_family}_feature_depth_primary_direction_disabled")
    if snapshot.get("feature_depth_state") in ("unavailable", "warning_context"):
        warnings.append(f"{target_family}_feature_depth_{snapshot.get('feature_depth_state')}")
    if orderbook.get("spread_warning"):
        warnings.append(f"{target_family}_orderbook_spread_warning")
    if orderbook.get("thin_book_warning"):
        warnings.append(f"{target_family}_orderbook_thin_book_warning")
    if tradeflow.get("burst_warning"):
        warnings.append(f"{target_family}_tradeflow_burst_warning")
    for item in list(snapshot.get("warnings", []))[:4]:
        warnings.append(f"{target_family}_feature_depth_warning:{item}")

def _breakout_false_break(technical: HumanTechnicalSummary | None, cross: CrossVenueReferenceSummary | None, feature_depth_snapshot: FeatureDepthSnapshot | None = None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    if technical is None or not technical.usable:
        drivers: list[str] = []
        warnings: list[str] = []
        values: Dict[str, Any] = {"proxy_kind": "technical_cross_venue_breakout_proxy_v1", "note": "feature_depth_snapshot is context/warning only when technical summary is missing"}
        _apply_feature_depth_context_for_family(target_family="breakout_false_break", values=values, drivers=drivers, warnings=warnings, feature_depth_snapshot=feature_depth_snapshot)
        return "unknown", None, tuple(drivers), ("human_technical_summary_missing_or_blocked",), tuple(dict.fromkeys(warnings)), values
    rb = technical.range_boundary
    wick = technical.wick_body
    ma = technical.moving_average
    vwap = technical.vwap_relation
    cross_state = cross.agreement_state if cross and cross.usable else "missing_or_blocked"
    drivers: list[str] = []
    warnings: list[str] = []
    score = 0.35
    values: Dict[str, Any] = {
        "proxy_kind": "technical_cross_venue_breakout_proxy_v1",
        "range_close_position": rb.close_position,
        "wick_signal": wick.wick_signal,
        "ma_slope_label": ma.slope_label,
        "ma_cross_state": ma.cross_state,
        "vwap_relation": vwap.relation,
        "cross_venue_agreement_state": cross_state,
    }

    near_boundary = rb.close_position in ("near_range_high", "near_range_low")
    directional = ma.slope_label in ("rising", "falling") and ma.cross_state in ("short_above_long", "short_below_long")
    strong_body = wick.wick_signal == "strong_body"
    rejection = wick.wick_signal in ("upper_wick_rejection", "lower_wick_rejection")
    cross_confirmed = cross_state == "confirmed"
    cross_divergent = cross_state == "divergent"

    if near_boundary:
        score += 0.12
        drivers.append(f"range_boundary_{rb.close_position}")
    if directional:
        score += 0.10
        drivers.append(f"ma_directional_{ma.slope_label}_{ma.cross_state}")
    if strong_body:
        score += 0.10
        drivers.append("strong_body_near_breakout")
    if vwap.relation in ("above_vwap", "below_vwap"):
        score += 0.04
        drivers.append(f"vwap_{vwap.relation}")
    if cross_confirmed:
        score += 0.08
        drivers.append("cross_venue_confirmed")
    if cross_divergent:
        score -= 0.12
        warnings.append("cross_venue_divergence_false_break_caution")
    if rejection and near_boundary:
        score -= 0.16
        warnings.append("wick_rejection_near_boundary_false_break_risk")
    if cross_state == "missing_or_blocked":
        score -= 0.08
        warnings.append("cross_venue_missing_for_breakout_confirmation")

    _apply_feature_depth_context_for_family(target_family="breakout_false_break", values=values, drivers=drivers, warnings=warnings, feature_depth_snapshot=feature_depth_snapshot)

    score = max(0.0, min(1.0, score))
    if rejection and near_boundary:
        label = "false_break_risk"
    elif near_boundary and directional and cross_confirmed and score >= 0.58:
        label = "breakout_candidate"
    elif near_boundary and score >= 0.48:
        label = "breakout_watch"
    elif rb.close_position == "mid_range":
        label = "range_continuation"
    else:
        label = "no_breakout_signal"
    return label, round(score, 6), tuple(drivers or ("no_strong_breakout_driver",)), tuple(), tuple(dict.fromkeys(warnings)), values


def _opportunity_participation(
    *,
    trend_label: str,
    reversal_label: str,
    volatility_label: str,
    liquidity_label: str,
    breakout_label: str,
    cross_label: str,
) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    drivers: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    values: Dict[str, Any] = {
        "proxy_kind": "summary_based_opportunity_proxy_v1",
        "trend_bias": trend_label,
        "reversal_zone": reversal_label,
        "volatility_risk": volatility_label,
        "liquidity_execution_quality": liquidity_label,
        "breakout_false_break": breakout_label,
        "cross_venue_confirmation": cross_label,
        "note": "uses current family labels until outcome/near-miss ledger context is wired",
    }
    labels = {trend_label, reversal_label, volatility_label, liquidity_label, breakout_label, cross_label}
    if "unknown" in labels and labels == {"unknown"}:
        blockers.append("opportunity_proxy_family_labels_missing")
        return "unknown", None, tuple(), tuple(blockers), tuple(), values

    score = 0.40
    if trend_label in ("long_bias", "short_bias"):
        score += 0.12
        drivers.append(f"trend_{trend_label}")
    elif trend_label in ("neutral_bias", "flat", "unknown"):
        warnings.append("trend_not_directional_for_participation")

    if cross_label == "confirmed":
        score += 0.08
        drivers.append("cross_venue_confirmed")
    elif cross_label == "divergent_warning":
        score -= 0.16
        warnings.append("cross_venue_divergent_wait")

    if liquidity_label == "liquidity_proxy_adequate":
        score += 0.08
        drivers.append("liquidity_proxy_adequate")
    elif liquidity_label in ("liquidity_caution", "poor_liquidity", "liquidity_unknown"):
        score -= 0.14
        warnings.append(f"liquidity_{liquidity_label}")

    if breakout_label == "breakout_candidate":
        score += 0.10
        drivers.append("breakout_candidate")
    elif breakout_label in ("breakout_watch", "range_continuation"):
        warnings.append(f"breakout_{breakout_label}")
    elif breakout_label == "false_break_risk":
        score -= 0.18
        warnings.append("false_break_risk_wait")

    if reversal_label in ("reversal_watch", "reaction_zone_watch", "vwap_reversion_watch"):
        score -= 0.10
        warnings.append(f"reversal_{reversal_label}")
    if volatility_label == "elevated_risk":
        score -= 0.15
        warnings.append("elevated_volatility_wait")
    elif volatility_label == "normal_risk":
        score += 0.03

    score = max(0.0, min(1.0, score))
    hard_wait = any(item in warnings for item in ("cross_venue_divergent_wait", "false_break_risk_wait", "elevated_volatility_wait")) or liquidity_label in ("poor_liquidity", "liquidity_unknown")
    if hard_wait:
        label = "opportunity_blocked"
    elif score >= 0.62 and trend_label in ("long_bias", "short_bias") and liquidity_label == "liquidity_proxy_adequate" and cross_label == "confirmed":
        label = "participation_candidate"
    elif warnings:
        label = "wait_for_confirmation"
    elif trend_label in ("neutral_bias", "flat", "unknown"):
        label = "no_edge"
    else:
        label = "opportunity_watch"
    return label, round(score, 6), tuple(drivers or ("opportunity_proxy_no_strong_driver",)), tuple(blockers), tuple(dict.fromkeys(warnings)), values


def _cross_venue_confirmation(cross: CrossVenueReferenceSummary | None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    if cross is None or not cross.usable:
        return "unknown", None, tuple(), ("cross_venue_summary_missing_or_blocked",), tuple(), {}
    warnings = tuple(cross.warnings)
    if cross.agreement_state == "confirmed":
        label = "confirmed"
        score = 0.70
    elif cross.agreement_state == "divergent":
        label = "divergent_warning"
        score = 0.62
    else:
        label = "unknown"
        score = None
    drivers = (f"agreement_{cross.agreement_state}", f"spot_fx_{cross.spot_fx_basis.premium_discount_state}")
    return label, score, drivers, tuple(), warnings, {"cross_venue": cross.to_dict()}


def _macro_risk_context(technical: HumanTechnicalSummary | None, cross: CrossVenueReferenceSummary | None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    drivers: list[str] = []
    warnings: list[str] = []
    values: Dict[str, Any] = {
        "proxy_kind": "summary_based_macro_risk_proxy_v1",
        "primary_direction_owner": False,
        "note": "context/warning only; no live macro collection and no short-horizon direction ownership",
    }
    score = 0.40
    technical_usable = bool(technical and technical.usable)
    cross_usable = bool(cross and cross.usable)
    if technical_usable and technical is not None:
        vol_state = technical.volatility.state
        values["volatility_state"] = vol_state
        if vol_state == "expanding":
            score += 0.16
            warnings.append("macro_proxy_elevated_due_to_expanding_volatility")
        elif vol_state == "normal":
            drivers.append("volatility_normal")
        elif vol_state == "compressed":
            drivers.append("volatility_compressed")
    else:
        values["volatility_state"] = "unknown"
        warnings.append("technical_summary_missing_for_macro_proxy")

    if cross_usable and cross is not None:
        values["cross_venue_agreement_state"] = cross.agreement_state
        values["max_deviation_pct"] = cross.max_deviation_pct
        if cross.agreement_state == "divergent":
            score += 0.18
            warnings.append("macro_proxy_cross_venue_divergence")
        elif cross.agreement_state == "confirmed":
            drivers.append("cross_venue_confirmed")
        if cross.spot_fx_basis.premium_discount_state in ("fx_premium", "fx_discount"):
            score += 0.04
            warnings.append(f"macro_proxy_spot_fx_basis_{cross.spot_fx_basis.premium_discount_state}")
    else:
        values["cross_venue_agreement_state"] = "unknown"
        warnings.append("cross_venue_summary_missing_for_macro_proxy")

    score = max(0.0, min(1.0, score))
    if warnings:
        label = "macro_risk_watch"
    elif drivers:
        label = "macro_context_neutral"
    else:
        label = "macro_context_unavailable"
    return label, round(score, 6), tuple(drivers or ("macro_proxy_context_only",)), tuple(), tuple(dict.fromkeys(warnings)), values


def _algorithmic_participant_footprint(technical: HumanTechnicalSummary | None, cross: CrossVenueReferenceSummary | None, feature_depth_snapshot: FeatureDepthSnapshot | None = None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    drivers: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    values: Dict[str, Any] = {
        "proxy_kind": "summary_based_algorithmic_footprint_proxy_v1",
        "primary_direction_owner": False,
        "note": "uses technical/cross-venue summaries only; no live tradeflow/orderbook collection",
    }
    technical_usable = bool(technical and technical.usable)
    cross_usable = bool(cross and cross.usable)
    if not technical_usable and not cross_usable:
        blockers.append("algorithmic_footprint_proxy_inputs_missing_or_blocked")
        _apply_feature_depth_context_for_family(target_family="algorithmic_participant_footprint", values=values, drivers=drivers, warnings=warnings, feature_depth_snapshot=feature_depth_snapshot)
        return "algorithmic_footprint_unavailable", None, tuple(drivers), tuple(blockers), tuple(dict.fromkeys(warnings)), values

    score = 0.36
    if technical_usable and technical is not None:
        vol = technical.volatility.state
        wick = technical.wick_body.wick_signal
        ma_slope = technical.moving_average.slope_label
        ma_cross = technical.moving_average.cross_state
        range_pos = technical.range_boundary.close_position
        values.update({
            "volatility_state": vol,
            "wick_signal": wick,
            "ma_slope_label": ma_slope,
            "ma_cross_state": ma_cross,
            "range_close_position": range_pos,
        })
        if vol == "expanding":
            score += 0.16
            warnings.append("expanding_volatility_algorithmic_activity_watch")
        elif vol == "compressed":
            drivers.append("compressed_volatility_no_clear_footprint")
        if wick in ("upper_wick_rejection", "lower_wick_rejection") and range_pos in ("near_range_high", "near_range_low"):
            score += 0.14
            warnings.append("boundary_wick_possible_sweep_footprint")
        if wick == "strong_body" and ma_slope in ("rising", "falling") and ma_cross in ("short_above_long", "short_below_long"):
            score += 0.12
            drivers.append("strong_body_directional_ma_footprint")
    else:
        values["technical_state"] = "missing_or_blocked"
        warnings.append("technical_summary_missing_for_algorithmic_footprint_proxy")

    if cross_usable and cross is not None:
        values["cross_venue_agreement_state"] = cross.agreement_state
        values["max_deviation_pct"] = cross.max_deviation_pct
        values["spot_fx_basis_state"] = cross.spot_fx_basis.premium_discount_state
        if cross.agreement_state == "divergent":
            score += 0.14
            warnings.append("cross_venue_divergence_possible_algorithmic_dislocation")
        elif cross.agreement_state == "confirmed":
            drivers.append("cross_venue_confirmed")
        if cross.spot_fx_basis.premium_discount_state in ("fx_premium", "fx_discount"):
            score += 0.04
            warnings.append(f"spot_fx_basis_{cross.spot_fx_basis.premium_discount_state}_footprint_watch")
    else:
        values["cross_venue_agreement_state"] = "unknown"
        warnings.append("cross_venue_summary_missing_for_algorithmic_footprint_proxy")

    _apply_feature_depth_context_for_family(target_family="algorithmic_participant_footprint", values=values, drivers=drivers, warnings=warnings, feature_depth_snapshot=feature_depth_snapshot)

    score = max(0.0, min(1.0, score))
    activity_watch_warnings = {
        "expanding_volatility_algorithmic_activity_watch",
        "cross_venue_divergence_possible_algorithmic_dislocation",
    }
    if "boundary_wick_possible_sweep_footprint" in warnings:
        label = "potential_sweep_reversal_footprint"
    elif activity_watch_warnings.intersection(warnings):
        label = "algorithmic_activity_watch"
    elif "strong_body_directional_ma_footprint" in drivers:
        label = "directional_algorithmic_flow_watch"
    elif blockers:
        label = "algorithmic_footprint_unavailable"
    else:
        label = "algorithmic_footprint_neutral"
    return label, round(score, 6), tuple(drivers or ("algorithmic_footprint_proxy_context_only",)), tuple(blockers), tuple(dict.fromkeys(warnings)), values


def _human_technical_structure(technical: HumanTechnicalSummary | None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    if technical is None or not technical.usable:
        return "unknown", None, tuple(), ("human_technical_summary_missing_or_blocked",), tuple(), {}
    rb = technical.range_boundary
    wick = technical.wick_body
    ma = technical.moving_average
    drivers = (f"range_{rb.close_position}", f"wick_{wick.wick_signal}", f"ma_{ma.slope_label}")
    if wick.wick_signal in ("upper_wick_rejection", "lower_wick_rejection"):
        label = "rejection_structure"
        score = 0.64
    elif rb.close_position in ("near_range_high", "near_range_low"):
        label = "range_boundary_structure"
        score = 0.58
    elif ma.slope_label in ("rising", "falling"):
        label = "directional_structure"
        score = 0.55
    else:
        label = "neutral_structure"
        score = 0.35
    return label, score, drivers, tuple(), tuple(technical.warnings), {"technical": technical.to_dict()}


def build_rule_based_v0_outputs(
    *,
    technical_summary: HumanTechnicalSummary | None = None,
    cross_venue_summary: CrossVenueReferenceSummary | None = None,
    horizon_sec: int = 300,
    now: datetime | None = None,
    feature_depth_snapshot: FeatureDepthSnapshot | None = None,
) -> Tuple[PredictionOutput, ...]:
    generated_at = _generated_at(now)
    mr_label, mr_score, mr_drivers, mr_blockers, mr_values = _market_regime(technical_summary, cross_venue_summary)
    tb_label, tb_score, tb_drivers, tb_blockers, tb_values = _trend_bias(technical_summary)
    rz_label, rz_score, rz_drivers, rz_blockers, rz_warnings, rz_values = _reversal_zone(technical_summary)
    vr_label, vr_score, vr_drivers, vr_blockers, vr_values = _volatility_risk(technical_summary)
    lq_label, lq_score, lq_drivers, lq_blockers, lq_warnings, lq_values = _liquidity_execution_quality(technical_summary, cross_venue_summary, feature_depth_snapshot)
    bf_label, bf_score, bf_drivers, bf_blockers, bf_warnings, bf_values = _breakout_false_break(technical_summary, cross_venue_summary, feature_depth_snapshot)
    cv_label, cv_score, cv_drivers, cv_blockers, cv_warnings, cv_values = _cross_venue_confirmation(cross_venue_summary)
    mc_label, mc_score, mc_drivers, mc_blockers, mc_warnings, mc_values = _macro_risk_context(technical_summary, cross_venue_summary)
    af_label, af_score, af_drivers, af_blockers, af_warnings, af_values = _algorithmic_participant_footprint(technical_summary, cross_venue_summary, feature_depth_snapshot)
    op_label, op_score, op_drivers, op_blockers, op_warnings, op_values = _opportunity_participation(
        trend_label=tb_label,
        reversal_label=rz_label,
        volatility_label=vr_label,
        liquidity_label=lq_label,
        breakout_label=bf_label,
        cross_label=cv_label,
    )
    ht_label, ht_score, ht_drivers, ht_blockers, ht_warnings, ht_values = _human_technical_structure(technical_summary)
    return (
        _output(family=PredictionFamily.MARKET_REGIME, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=mr_label, score=mr_score, drivers=mr_drivers, blockers=mr_blockers, values=mr_values),
        _output(family=PredictionFamily.TREND_BIAS, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=tb_label, score=tb_score, drivers=tb_drivers, blockers=tb_blockers, values=tb_values),
        _output(family=PredictionFamily.REVERSAL_ZONE, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=rz_label, score=rz_score, drivers=rz_drivers, blockers=rz_blockers, warnings=rz_warnings, values=rz_values),
        _output(family=PredictionFamily.VOLATILITY_RISK, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=vr_label, score=vr_score, drivers=vr_drivers, blockers=vr_blockers, values=vr_values),
        _output(family=PredictionFamily.LIQUIDITY_EXECUTION_QUALITY, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=lq_label, score=lq_score, drivers=lq_drivers, blockers=lq_blockers, warnings=lq_warnings, values=lq_values),
        _output(family=PredictionFamily.BREAKOUT_FALSE_BREAK, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=bf_label, score=bf_score, drivers=bf_drivers, blockers=bf_blockers, warnings=bf_warnings, values=bf_values),
        _output(family=PredictionFamily.OPPORTUNITY_PARTICIPATION, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=op_label, score=op_score, drivers=op_drivers, blockers=op_blockers, warnings=op_warnings, values=op_values),
        _output(family=PredictionFamily.CROSS_VENUE_CONFIRMATION, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=cv_label, score=cv_score, drivers=cv_drivers, blockers=cv_blockers, warnings=cv_warnings, values=cv_values),
        _output(family=PredictionFamily.MACRO_RISK_CONTEXT, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=mc_label, score=mc_score, drivers=mc_drivers, blockers=mc_blockers, warnings=mc_warnings, values=mc_values),
        _output(family=PredictionFamily.ALGORITHMIC_PARTICIPANT_FOOTPRINT, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=af_label, score=af_score, drivers=af_drivers, blockers=af_blockers, warnings=af_warnings, values=af_values),
        _output(family=PredictionFamily.HUMAN_TECHNICAL_STRUCTURE, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=ht_label, score=ht_score, drivers=ht_drivers, blockers=ht_blockers, warnings=ht_warnings, values=ht_values),
    )
