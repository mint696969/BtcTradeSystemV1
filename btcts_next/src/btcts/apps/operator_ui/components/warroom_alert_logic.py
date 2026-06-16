# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_alert_logic.py
# desc: War Room alert の spread / decision / risk 判定を分離した logic 層。

from __future__ import annotations


def spread_state(spread: float | None) -> str | None:
    if spread is None:
        return None
    if spread >= 7000:
        return "wide"
    if spread <= 3000:
        return "tight"
    return "normal"


def decision_label(regime: str | None, imbalance, delta) -> str:
    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            return "long_bias"

    if regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            return "short_bias"

    return "wait"


def risk_score(spread, imbalance, delta, wall_ratio, latency):
    score = 0

    if isinstance(spread, (int, float)):
        if spread > 7000:
            score += 2
        elif spread > 4500:
            score += 1

    if isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if (imbalance > 0.2 and delta < 0) or (imbalance < -0.2 and delta > 0):
            score += 2

    if isinstance(wall_ratio, (int, float)):
        if abs(wall_ratio) > 0.45:
            score += 2
        elif abs(wall_ratio) > 0.25:
            score += 1

    if isinstance(latency, (int, float)):
        if latency > 450:
            score += 2
        elif latency > 320:
            score += 1

    return score


def risk_level(score: int) -> str:
    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    return "low"