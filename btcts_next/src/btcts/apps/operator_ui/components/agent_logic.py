# path: ./btcts_next/src/btcts/apps/operator_ui/components/agent_logic.py
# desc: Agent Panels の analyst / strategy / risk 表示ロジックを分離した logic 層。

from __future__ import annotations

from btcts.apps.operator_ui.ui_text import get_text


def analyst_view(lang: str, regime, spread, pressure_bias):
    regime_label = get_text(lang, "agent_value_range")
    if regime in {"trend_up", "trend_down"}:
        regime_label = get_text(lang, "agent_value_trend")
    elif regime == "absorption_zone":
        regime_label = get_text(lang, "warroom_value_absorption")
    elif regime == "liquidity_vacuum":
        regime_label = get_text(lang, "warroom_value_liquidity_vacuum")

    pressure = get_text(lang, "agent_value_neutral")
    if pressure_bias == "buy_pressure":
        pressure = get_text(lang, "agent_value_buy")
    elif pressure_bias == "sell_pressure":
        pressure = get_text(lang, "agent_value_sell")

    spread_state = get_text(lang, "agent_value_normal")
    if isinstance(spread, (int, float)):
        if spread > 7000:
            spread_state = get_text(lang, "agent_value_wide")
        elif spread < 3000:
            spread_state = get_text(lang, "agent_value_tight")

    return regime_label, spread_state, pressure


def strategy_view(lang: str, regime, best_strategy, imbalance, delta):
    archetype = best_strategy
    stance = get_text(lang, "agent_value_wait")

    if regime == "trend_up" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance > 0 and delta > 0:
            stance = get_text(lang, "agent_value_long_bias")

    elif regime == "trend_down" and isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if imbalance < 0 and delta < 0:
            stance = get_text(lang, "agent_value_short_bias")

    elif regime == "absorption_zone":
        if isinstance(delta, (int, float)) and delta < 0:
            stance = get_text(lang, "agent_value_short_bias")
        elif isinstance(delta, (int, float)) and delta > 0:
            stance = get_text(lang, "agent_value_long_bias")
        else:
            stance = get_text(lang, "agent_value_prepare")

    return archetype, stance


def risk_view(lang: str, spread, imbalance, delta, wall_ratio, audit_rows):
    latencies = [
        float(row["latency_ms"])
        for row in audit_rows
        if row.get("latency_ms") is not None
    ]
    avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else 0.0

    risk = get_text(lang, "agent_value_low")
    score = 0

    if isinstance(spread, (int, float)):
        if spread > 7000:
            score += 2
        elif spread > 4500:
            score += 1

    if avg_latency >= 450:
        score += 2
    elif avg_latency >= 320:
        score += 1

    if isinstance(imbalance, (int, float)) and isinstance(delta, (int, float)):
        if (imbalance > 0.15 and delta < 0) or (imbalance < -0.15 and delta > 0):
            score += 2

    if isinstance(wall_ratio, (int, float)):
        if abs(wall_ratio) > 0.45:
            score += 2
        elif abs(wall_ratio) > 0.25:
            score += 1

    if score >= 6:
        risk = get_text(lang, "agent_value_high")
    elif score >= 3:
        risk = get_text(lang, "agent_value_medium")

    return risk, avg_latency