# path: ./btcts_next/src/btcts/autotrade/strategy/selector.py
# desc: Deterministic strategy candidate builder for AutoTrade shadow decisions.

from __future__ import annotations

from btcts.autotrade.config.models import AggressivenessProfile, ParameterSet
from btcts.autotrade.read_model.models import AutoTradeSnapshot, Confidence, Forecast5m, ForecastDirection, GroundDirection
from btcts.autotrade.strategy.models import ActionCandidate, CandidateAction, StrategyProfile
from btcts.autotrade.strategy import reason_codes as rc


def _candidate_id(snapshot_id: str, action: CandidateAction, parameter_set_id: str) -> str:
    return f"cand_{snapshot_id.removeprefix('snap_')}_{action.value.lower()}_{parameter_set_id}"


def entry_threshold_for(parameter_set: ParameterSet) -> int:
    if parameter_set.aggressiveness == AggressivenessProfile.CONSERVATIVE:
        return parameter_set.entry_quality.live_threshold_conservative
    if parameter_set.aggressiveness == AggressivenessProfile.OPPORTUNISTIC:
        return parameter_set.entry_quality.live_threshold_opportunistic
    return parameter_set.entry_quality.live_threshold_balanced


def compute_entry_quality(snapshot: AutoTradeSnapshot, forecast: Forecast5m | None, parameter_set: ParameterSet) -> tuple[int, tuple[str, ...]]:
    score = 0
    reasons: list[str] = []

    if snapshot.usability.liquidity:
        score += 20
    else:
        reasons.append(rc.LIQUIDITY_UNUSABLE)
    if snapshot.usability.trade:
        score += 15
    else:
        reasons.append(rc.TRADE_UNUSABLE)
    if snapshot.usability.temporal:
        score += 25
    else:
        reasons.append(rc.TEMPORAL_FLOW_UNUSABLE)

    if snapshot.ground.confidence == Confidence.MEDIUM:
        score += 15
    elif snapshot.ground.confidence == Confidence.HIGH:
        score += 25
    else:
        reasons.append(rc.LOW_CONFIDENCE)

    if forecast is not None and forecast.confidence in {Confidence.MEDIUM, Confidence.HIGH}:
        if snapshot.ground.direction == GroundDirection.SELL_LEANING and forecast.forecast_direction == ForecastDirection.DOWN:
            score += 25
            reasons.append(rc.FORECAST_ALIGNED_SELL)
        elif snapshot.ground.direction == GroundDirection.BUY_LEANING and forecast.forecast_direction == ForecastDirection.UP:
            score += 25
            reasons.append(rc.FORECAST_ALIGNED_BUY)

    # Cost/spread-aware placeholder. Actual cost model comes later.
    if snapshot.inputs.spread is not None and snapshot.inputs.spread <= 5000:
        score += 10

    return min(score, 100), tuple(dict.fromkeys(reasons))


def build_action_candidate(snapshot: AutoTradeSnapshot, forecast: Forecast5m | None, parameter_set: ParameterSet) -> ActionCandidate:
    quality, quality_reasons = compute_entry_quality(snapshot, forecast, parameter_set)
    reasons: list[str] = list(quality_reasons)
    blocked_hint: list[str] = []

    if snapshot.stale_reasons:
        reasons.extend(snapshot.stale_reasons)
        blocked_hint.append(rc.STALE_INPUT)
    if not snapshot.usability.temporal:
        blocked_hint.append(rc.TEMPORAL_FLOW_UNUSABLE)
    if not snapshot.usability.trade:
        blocked_hint.append(rc.TRADE_UNUSABLE)

    threshold = entry_threshold_for(parameter_set)
    watch_threshold = parameter_set.entry_quality.watch_threshold

    action = CandidateAction.WAIT
    side: str | None = None
    profile = StrategyProfile.LOW_CONFIDENCE

    if blocked_hint:
        action = CandidateAction.NO_NEW_ENTRY
        profile = StrategyProfile.STALE_GUARD
    elif snapshot.ground.direction == GroundDirection.SELL_LEANING:
        reasons.append(rc.SELL_GROUND)
        if quality >= threshold:
            action = CandidateAction.ENTRY_SELL
            side = "sell"
            profile = StrategyProfile.SELL_LEANING_MEDIUM
            reasons.append(rc.ENTRY_THRESHOLD_MET)
        elif quality >= watch_threshold:
            action = CandidateAction.WATCH_SELL
            side = "sell"
            profile = StrategyProfile.SELL_LEANING_MEDIUM
            reasons.append(rc.WATCH_THRESHOLD_MET)
    elif snapshot.ground.direction == GroundDirection.BUY_LEANING:
        reasons.append(rc.BUY_GROUND)
        if quality >= threshold:
            action = CandidateAction.ENTRY_BUY
            side = "buy"
            profile = StrategyProfile.BUY_LEANING_MEDIUM
            reasons.append(rc.ENTRY_THRESHOLD_MET)
        elif quality >= watch_threshold:
            action = CandidateAction.WATCH_BUY
            side = "buy"
            profile = StrategyProfile.BUY_LEANING_MEDIUM
            reasons.append(rc.WATCH_THRESHOLD_MET)
    elif snapshot.ground.direction == GroundDirection.MIXED:
        reasons.append(rc.MIXED_GROUND)
        profile = StrategyProfile.NORMAL_MIXED
    else:
        reasons.append(rc.UNKNOWN_GROUND)
        profile = StrategyProfile.LOW_CONFIDENCE

    return ActionCandidate(
        candidate_id=_candidate_id(snapshot.snapshot_id, action, parameter_set.parameter_set_id),
        snapshot_id=snapshot.snapshot_id,
        forecast_id=forecast.forecast_id if forecast is not None else None,
        parameter_set_id=parameter_set.parameter_set_id,
        logic_version=parameter_set.logic_version,
        action=action,
        strategy_profile=profile,
        side=side,
        entry_quality=quality,
        reason_codes=tuple(dict.fromkeys(reasons)),
        blocked_hint=tuple(dict.fromkeys(blocked_hint)),
    )
