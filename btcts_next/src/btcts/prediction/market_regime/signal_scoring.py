# path: ./btcts_next/src/btcts/prediction/market_regime/signal_scoring.py
# desc: Pure signal-registry-v1 style scoring from market-regime feature bundles to explainable votes/conflicts. No UI, filesystem write, scheduler, broker, or AutoTrade behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Sequence

from .contracts import FeatureGroup, MarketRegimeCode
from .features import FeatureSignal, MarketRegimeFeatureBundle
from .horizon_policy import build_default_horizon_policy

MARKET_REGIME_SIGNAL_SCORING_VERSION = "prediction.market_regime.signal_scoring.2026_07_08.v1"
MARKET_REGIME_SIGNAL_REGISTRY_VERSION = "market_regime_signal_registry.2026_07_08.v1"
MARKET_REGIME_HORIZON_WEIGHT_VERSION = "market_regime_horizon_weight.2026_07_08.v1"

_HORIZON_FAMILY_WEIGHTS: dict[str, dict[str, float]] = {
    "current": {"source_quality": 1.00, "liquidity": 1.00, "orderflow": 0.90, "volatility": 0.60, "price_structure": 0.50, "cross_venue": 0.25},
    "300s": {"source_quality": 1.00, "liquidity": 0.85, "orderflow": 0.85, "price_structure": 0.60, "volatility": 0.60, "cross_venue": 0.35},
    "900s": {"source_quality": 1.00, "price_structure": 0.80, "volatility": 0.65, "orderflow": 0.65, "liquidity": 0.50, "cross_venue": 0.50},
    "1800s": {"source_quality": 1.00, "price_structure": 0.75, "volatility": 0.70, "orderflow": 0.55, "cross_venue": 0.55, "liquidity": 0.35},
    "3600s": {"source_quality": 1.00, "price_structure": 0.70, "volatility": 0.75, "cross_venue": 0.60, "orderflow": 0.40, "liquidity": 0.25},
    "21600s": {"source_quality": 1.00, "price_structure": 0.75, "volatility": 0.85, "cross_venue": 0.70, "orderflow": 0.20, "liquidity": 0.10},
    "43200s": {"source_quality": 1.00, "price_structure": 0.70, "volatility": 0.85, "cross_venue": 0.75, "orderflow": 0.15, "liquidity": 0.05},
    "86400s": {"source_quality": 1.00, "price_structure": 0.65, "volatility": 0.85, "cross_venue": 0.80, "orderflow": 0.10, "liquidity": 0.05},
}


@dataclass(frozen=True)
class MarketRegimeSignalVote:
    signal_id: str
    source_family: str
    supports_regime: str
    strength: float
    weighted_strength: float
    horizon_key: str
    reason: str
    value: Any = None
    against_regimes: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["against_regimes"] = list(self.against_regimes)
        data["source_refs"] = list(self.source_refs)
        return data


def _signals(bundle: MarketRegimeFeatureBundle, group: FeatureGroup) -> Mapping[str, FeatureSignal]:
    return {signal.name: signal for signal in bundle.signals_by_group(group)}


def _value(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str, default: Any = None) -> Any:
    signal = _signals(bundle, group).get(name)
    if signal is None or not signal.available:
        return default
    return signal.value


def _refs(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str) -> tuple[str, ...]:
    signal = _signals(bundle, group).get(name)
    return tuple(signal.source_refs) if signal else ()


def _float(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str) -> float | None:
    try:
        value = _value(bundle, group, name)
        return None if value is None else float(value)
    except Exception:
        return None


def _family_key(group: FeatureGroup) -> str:
    return group.value


def _weight(horizon_key: str, group: FeatureGroup) -> float:
    return _HORIZON_FAMILY_WEIGHTS.get(horizon_key, _HORIZON_FAMILY_WEIGHTS["900s"]).get(_family_key(group), 0.25)


def _clamp01(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def _vote(
    *,
    bundle: MarketRegimeFeatureBundle,
    horizon_key: str,
    group: FeatureGroup,
    signal_id: str,
    supports: MarketRegimeCode,
    strength: float,
    reason: str,
    value: Any,
    against: Sequence[MarketRegimeCode] = (),
) -> MarketRegimeSignalVote:
    family_weight = _weight(horizon_key, group)
    strength01 = _clamp01(strength)
    return MarketRegimeSignalVote(
        signal_id=signal_id,
        source_family=_family_key(group),
        supports_regime=supports.value,
        strength=round(strength01, 4),
        weighted_strength=round(strength01 * family_weight, 4),
        horizon_key=horizon_key,
        reason=reason,
        value=value,
        against_regimes=tuple(regime.value for regime in against),
        source_refs=_refs(bundle, group, signal_id),
    )


def _base_votes(bundle: MarketRegimeFeatureBundle, horizon_key: str) -> list[MarketRegimeSignalVote]:
    votes: list[MarketRegimeSignalVote] = []
    missing_count = _float(bundle, FeatureGroup.SOURCE_QUALITY, "missing_source_count")
    source_quality_score = _float(bundle, FeatureGroup.SOURCE_QUALITY, "source_quality_score")
    if missing_count and missing_count > 0:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.SOURCE_QUALITY, signal_id="missing_source_count", supports=MarketRegimeCode.UNKNOWN, strength=min(missing_count / 4.0, 1.0), reason="required or useful source is missing", value=missing_count))
    if source_quality_score is not None and source_quality_score >= 0.80:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.SOURCE_QUALITY, signal_id="source_quality_score", supports=MarketRegimeCode.RANGE, strength=0.25, reason="source quality is usable; permits non-UNKNOWN scoring", value=source_quality_score))

    depth_imbalance = _float(bundle, FeatureGroup.LIQUIDITY, "depth_imbalance")
    if depth_imbalance is not None and abs(depth_imbalance) >= 0.12:
        regime = MarketRegimeCode.UP_TREND if depth_imbalance > 0 else MarketRegimeCode.DOWN_TREND
        against = (MarketRegimeCode.DOWN_TREND,) if depth_imbalance > 0 else (MarketRegimeCode.UP_TREND,)
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.LIQUIDITY, signal_id="depth_imbalance", supports=regime, strength=abs(depth_imbalance), reason="orderbook depth imbalance shows directional liquidity pressure", value=depth_imbalance, against=against))
    micro_bias = _float(bundle, FeatureGroup.LIQUIDITY, "microprice_bias_bps")
    if micro_bias is not None and abs(micro_bias) >= 0.05:
        regime = MarketRegimeCode.UP_TREND if micro_bias > 0 else MarketRegimeCode.DOWN_TREND
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.LIQUIDITY, signal_id="microprice_bias_bps", supports=regime, strength=min(abs(micro_bias) / 3.0, 1.0), reason="microprice drift indicates near-book pressure", value=micro_bias))
    absorption = _float(bundle, FeatureGroup.LIQUIDITY, "absorption_score")
    if absorption is not None and absorption >= 0.55:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.LIQUIDITY, signal_id="absorption_score", supports=MarketRegimeCode.RANGE, strength=absorption, reason="liquidity absorption can keep price in range or set reversal watch", value=absorption, against=(MarketRegimeCode.UP_TREND, MarketRegimeCode.DOWN_TREND)))
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.LIQUIDITY, signal_id="absorption_score", supports=MarketRegimeCode.REVERSAL_WATCH, strength=absorption * 0.75, reason="absorption against flow may precede reversal attempt", value=absorption))
    disappearance = _float(bundle, FeatureGroup.LIQUIDITY, "liquidity_disappearance_score")
    if disappearance is not None and disappearance >= 0.55:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.LIQUIDITY, signal_id="liquidity_disappearance_score", supports=MarketRegimeCode.BREAKOUT, strength=disappearance, reason="liquidity disappearance raises break/run risk", value=disappearance, against=(MarketRegimeCode.RANGE,)))
    spread_bps = _float(bundle, FeatureGroup.LIQUIDITY, "spread_bps")
    if spread_bps is not None and spread_bps >= 3.0:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.LIQUIDITY, signal_id="spread_bps", supports=MarketRegimeCode.HIGH_VOL_CHOP, strength=min(spread_bps / 12.0, 1.0), reason="wide spread / thin book reduces directional quality", value=spread_bps, against=(MarketRegimeCode.UP_TREND, MarketRegimeCode.DOWN_TREND)))

    orderflow_imbalance = _float(bundle, FeatureGroup.ORDERFLOW, "orderflow_imbalance")
    if orderflow_imbalance is not None and abs(orderflow_imbalance) >= 0.12:
        regime = MarketRegimeCode.UP_TREND if orderflow_imbalance > 0 else MarketRegimeCode.DOWN_TREND
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.ORDERFLOW, signal_id="orderflow_imbalance", supports=regime, strength=abs(orderflow_imbalance), reason="aggressive flow imbalance shows participant pressure", value=orderflow_imbalance))
    cvd = _float(bundle, FeatureGroup.ORDERFLOW, "cvd")
    if cvd is not None and abs(cvd) >= 1.0:
        regime = MarketRegimeCode.UP_TREND if cvd > 0 else MarketRegimeCode.DOWN_TREND
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.ORDERFLOW, signal_id="cvd", supports=regime, strength=min(abs(cvd) / 10.0, 1.0), reason="CVD direction supports directional pressure", value=cvd))

    ma_slope = _float(bundle, FeatureGroup.PRICE_STRUCTURE, "ma_slope")
    if ma_slope is not None and abs(ma_slope) >= 0.05:
        regime = MarketRegimeCode.UP_TREND if ma_slope > 0 else MarketRegimeCode.DOWN_TREND
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.PRICE_STRUCTURE, signal_id="ma_slope", supports=regime, strength=min(abs(ma_slope), 1.0), reason="moving-average slope is human/systematic trend context", value=ma_slope))
    price_pos = _float(bundle, FeatureGroup.PRICE_STRUCTURE, "price_position_in_range")
    false_break = _float(bundle, FeatureGroup.PRICE_STRUCTURE, "false_break_count")
    if price_pos is not None and 0.20 <= price_pos <= 0.80:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.PRICE_STRUCTURE, signal_id="price_position_in_range", supports=MarketRegimeCode.RANGE, strength=0.45, reason="price remains inside range body", value=price_pos))
    if false_break is not None and false_break >= 1:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.PRICE_STRUCTURE, signal_id="false_break_count", supports=MarketRegimeCode.RANGE, strength=min(false_break / 3.0, 1.0), reason="false breaks favor range or reversal-watch interpretation", value=false_break, against=(MarketRegimeCode.BREAKOUT,)))
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.PRICE_STRUCTURE, signal_id="false_break_count", supports=MarketRegimeCode.REVERSAL_WATCH, strength=min(false_break / 4.0, 0.75), reason="failed break may become reversal watch", value=false_break))
    break_hold = _float(bundle, FeatureGroup.PRICE_STRUCTURE, "break_hold_count")
    if break_hold is not None and break_hold >= 1:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.PRICE_STRUCTURE, signal_id="break_hold_count", supports=MarketRegimeCode.BREAKOUT, strength=min(break_hold / 3.0, 1.0), reason="confirmed break-and-hold supports breakout watch", value=break_hold, against=(MarketRegimeCode.RANGE,)))

    vol_state = str(_value(bundle, FeatureGroup.VOLATILITY, "volatility_state", "") or "").lower()
    if "compression" in vol_state or "low" in vol_state:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.VOLATILITY, signal_id="volatility_state", supports=MarketRegimeCode.LOW_VOL_COMPRESSION, strength=0.60, reason="volatility state indicates compression", value=vol_state))
    compression = _float(bundle, FeatureGroup.VOLATILITY, "volatility_compression_score")
    if compression is not None and compression >= 0.55:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.VOLATILITY, signal_id="volatility_compression_score", supports=MarketRegimeCode.LOW_VOL_COMPRESSION, strength=compression, reason="ATR/realized-vol compression", value=compression))
    expansion = _float(bundle, FeatureGroup.VOLATILITY, "volatility_expansion_score")
    if expansion is not None and expansion >= 0.55:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.VOLATILITY, signal_id="volatility_expansion_score", supports=MarketRegimeCode.HIGH_VOL_CHOP, strength=expansion, reason="volatility expansion without clean direction", value=expansion))
    realized = _float(bundle, FeatureGroup.VOLATILITY, "realized_volatility")
    if realized is not None and realized >= 0.03:
        votes.append(_vote(bundle=bundle, horizon_key=horizon_key, group=FeatureGroup.VOLATILITY, signal_id="realized_volatility", supports=MarketRegimeCode.HIGH_VOL_CHOP, strength=min(realized / 0.08, 1.0), reason="realized volatility is elevated", value=realized))
    return votes


def _regime_scores(votes: Sequence[MarketRegimeSignalVote]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for vote in votes:
        scores[vote.supports_regime] = round(scores.get(vote.supports_regime, 0.0) + vote.weighted_strength, 4)
        for against in vote.against_regimes:
            scores[against] = round(scores.get(against, 0.0) - vote.weighted_strength * 0.5, 4)
    return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))


def _source_family_scores(votes: Sequence[MarketRegimeSignalVote]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for vote in votes:
        scores[vote.source_family] = round(scores.get(vote.source_family, 0.0) + abs(vote.weighted_strength), 4)
    return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))


def _conflicts(votes: Sequence[MarketRegimeSignalVote]) -> list[dict[str, Any]]:
    scores = _regime_scores(votes)
    positive = [(regime, score) for regime, score in scores.items() if score > 0.0]
    if len(positive) < 2:
        return []
    top = positive[0]
    conflicts: list[dict[str, Any]] = []
    for regime, score in positive[1:4]:
        if score >= top[1] * 0.45:
            conflicts.append({"primary_regime": top[0], "conflicting_regime": regime, "primary_score": top[1], "conflicting_score": score, "reason": "competing positive signal cluster"})
    return conflicts


def score_market_regime_signals(bundle: MarketRegimeFeatureBundle, *, top_n: int = 10) -> Dict[str, Any]:
    horizons: list[dict[str, Any]] = []
    all_votes: list[MarketRegimeSignalVote] = []
    for horizon in build_default_horizon_policy().horizons:
        horizon_key = horizon.horizon_key
        votes = sorted(_base_votes(bundle, horizon_key), key=lambda vote: abs(vote.weighted_strength), reverse=True)
        all_votes.extend(votes)
        horizons.append({
            "horizon": horizon.label,
            "horizon_sec": horizon.horizon_sec,
            "horizon_key": horizon_key,
            "signal_votes_top_n": [vote.to_dict() for vote in votes[:top_n]],
            "signal_conflicts_top_n": _conflicts(votes)[:top_n],
            "regime_scores": _regime_scores(votes),
            "source_family_scores": _source_family_scores(votes),
            "source_family_weights_used": _HORIZON_FAMILY_WEIGHTS.get(horizon_key, _HORIZON_FAMILY_WEIGHTS["900s"]),
        })
    return {
        "ok": True,
        "signal_scoring_version": MARKET_REGIME_SIGNAL_SCORING_VERSION,
        "signal_registry_version": MARKET_REGIME_SIGNAL_REGISTRY_VERSION,
        "horizon_weight_version": MARKET_REGIME_HORIZON_WEIGHT_VERSION,
        "market_regime_only": True,
        "horizon_count": len(horizons),
        "total_vote_count": len(all_votes),
        "horizons": horizons,
        "read_only": True,
        "non_executing": True,
        "ui_render_invokes_classifier": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "ledger_append_allowed": False,
        "would_send_to_broker": False,
    }
