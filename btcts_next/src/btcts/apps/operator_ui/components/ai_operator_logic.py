# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_logic.py
# desc: AI Operator の行動判定 / リスク判定 / 表示ラベルを分離したロジック層。

from __future__ import annotations

from btcts.apps.operator_ui.ui_text import get_text


def operator_action(state: dict) -> str:
    imbalance = state["imbalance"]
    delta = state["delta"]
    wall_ratio = state["wall_ratio"]
    regime = state["regime"]

    if regime == "trend_up" and imbalance > 0.2 and delta > 0.2:
        return "long_watch"

    if regime == "trend_down" and imbalance < -0.2 and delta < -0.2:
        return "short_watch"

    if abs(wall_ratio) > 0.45:
        return "trap_caution"

    return "wait"


def operator_risk(state: dict) -> str:
    spread = state["spread"]
    imbalance = state["imbalance"]
    delta = state["delta"]
    wall_ratio = state["wall_ratio"]

    score = 0

    if spread > 7000:
        score += 2
    elif spread > 4500:
        score += 1

    if (imbalance > 0.2 and delta < 0) or (imbalance < -0.2 and delta > 0):
        score += 2

    if abs(wall_ratio) > 0.45:
        score += 2
    elif abs(wall_ratio) > 0.25:
        score += 1

    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def operator_action_label(lang: str, value: str) -> str:
    mapping = {
        "long_watch": get_text(lang, "ai_operator_action_long_watch"),
        "short_watch": get_text(lang, "ai_operator_action_short_watch"),
        "trap_caution": get_text(lang, "ai_operator_action_trap_caution"),
        "wait": get_text(lang, "ai_operator_action_wait"),
    }
    return mapping.get(value, value)


def operator_risk_label(lang: str, value: str) -> str:
    mapping = {
        "low": get_text(lang, "ai_operator_risk_low"),
        "medium": get_text(lang, "ai_operator_risk_medium"),
        "high": get_text(lang, "ai_operator_risk_high"),
    }
    return mapping.get(value, value)