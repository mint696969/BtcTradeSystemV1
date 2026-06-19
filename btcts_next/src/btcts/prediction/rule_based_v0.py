# path: ./btcts_next/src/btcts/prediction/rule_based_v0.py
# desc: Non-executing rule-based v0 prediction-family skeletons. Emits PredictionOutput only; no AutoTrade or broker side effects.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from .contracts import PredictionConfidence, PredictionFamily, PredictionOutput, SourceIdentity
from .cross_venue import CrossVenueReferenceSummary
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
    PredictionFamily.CROSS_VENUE_CONFIRMATION,
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


def _liquidity_execution_quality(technical: HumanTechnicalSummary | None, cross: CrossVenueReferenceSummary | None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    drivers: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []
    values: Dict[str, Any] = {
        "proxy_kind": "summary_based_liquidity_proxy_v1",
        "note": "uses technical volatility and cross-venue summary until orderbook liquidity features are wired",
    }
    technical_usable = bool(technical and technical.usable)
    cross_usable = bool(cross and cross.usable)
    if not technical_usable and not cross_usable:
        blockers.append("liquidity_proxy_inputs_missing_or_blocked")
        return "liquidity_unknown", None, tuple(), tuple(blockers), tuple(), values

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


def _breakout_false_break(technical: HumanTechnicalSummary | None, cross: CrossVenueReferenceSummary | None) -> tuple[str, float | None, Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Dict[str, Any]]:
    if technical is None or not technical.usable:
        return "unknown", None, tuple(), ("human_technical_summary_missing_or_blocked",), tuple(), {}
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
) -> Tuple[PredictionOutput, ...]:
    generated_at = _generated_at(now)
    mr_label, mr_score, mr_drivers, mr_blockers, mr_values = _market_regime(technical_summary, cross_venue_summary)
    tb_label, tb_score, tb_drivers, tb_blockers, tb_values = _trend_bias(technical_summary)
    rz_label, rz_score, rz_drivers, rz_blockers, rz_warnings, rz_values = _reversal_zone(technical_summary)
    vr_label, vr_score, vr_drivers, vr_blockers, vr_values = _volatility_risk(technical_summary)
    lq_label, lq_score, lq_drivers, lq_blockers, lq_warnings, lq_values = _liquidity_execution_quality(technical_summary, cross_venue_summary)
    bf_label, bf_score, bf_drivers, bf_blockers, bf_warnings, bf_values = _breakout_false_break(technical_summary, cross_venue_summary)
    cv_label, cv_score, cv_drivers, cv_blockers, cv_warnings, cv_values = _cross_venue_confirmation(cross_venue_summary)
    ht_label, ht_score, ht_drivers, ht_blockers, ht_warnings, ht_values = _human_technical_structure(technical_summary)
    return (
        _output(family=PredictionFamily.MARKET_REGIME, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=mr_label, score=mr_score, drivers=mr_drivers, blockers=mr_blockers, values=mr_values),
        _output(family=PredictionFamily.TREND_BIAS, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=tb_label, score=tb_score, drivers=tb_drivers, blockers=tb_blockers, values=tb_values),
        _output(family=PredictionFamily.REVERSAL_ZONE, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=rz_label, score=rz_score, drivers=rz_drivers, blockers=rz_blockers, warnings=rz_warnings, values=rz_values),
        _output(family=PredictionFamily.VOLATILITY_RISK, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=vr_label, score=vr_score, drivers=vr_drivers, blockers=vr_blockers, values=vr_values),
        _output(family=PredictionFamily.LIQUIDITY_EXECUTION_QUALITY, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=lq_label, score=lq_score, drivers=lq_drivers, blockers=lq_blockers, warnings=lq_warnings, values=lq_values),
        _output(family=PredictionFamily.BREAKOUT_FALSE_BREAK, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=bf_label, score=bf_score, drivers=bf_drivers, blockers=bf_blockers, warnings=bf_warnings, values=bf_values),
        _output(family=PredictionFamily.CROSS_VENUE_CONFIRMATION, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=cv_label, score=cv_score, drivers=cv_drivers, blockers=cv_blockers, warnings=cv_warnings, values=cv_values),
        _output(family=PredictionFamily.HUMAN_TECHNICAL_STRUCTURE, generated_at=generated_at, horizon_sec=horizon_sec, primary_label=ht_label, score=ht_score, drivers=ht_drivers, blockers=ht_blockers, warnings=ht_warnings, values=ht_values),
    )
