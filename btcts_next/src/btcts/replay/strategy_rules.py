# path: ./btcts_next/src/btcts/replay/strategy_rules.py
# desc: Minimal strategy decision rules for replay sandbox based on replay microstructure outputs.

from __future__ import annotations

from typing import Dict, List, Optional


def _event_names(row: Dict) -> List[str]:
    names: List[str] = []

    for event in row.get("microstructure", []):
        if isinstance(event, dict):
            name = event.get("event_name")
            if name:
                names.append(str(name))

    result = row.get("result")
    if isinstance(result, dict):
        for event in result.get("events", []):
            if isinstance(event, dict):
                name = event.get("event_name")
                if name:
                    names.append(str(name))

    return names


def _micro_side(row: Dict, event_name: str) -> Optional[str]:
    for event in row.get("microstructure", []):
        if isinstance(event, dict) and event.get("event_name") == event_name:
            side = event.get("side")
            if side is not None:
                return str(side)
    return None


def decide_entry(row: Dict) -> Optional[Dict]:
    names = set(_event_names(row))

    if "absorption_detected" in names:
        side = _micro_side(row, "absorption_detected")
        if side == "ask":
            return {
                "action": "enter_long",
                "reason": "absorption_detected_ask",
            }
        if side == "bid":
            return {
                "action": "enter_short",
                "reason": "absorption_detected_bid",
            }

    if "liquidity_sweep" in names:
        side = _micro_side(row, "liquidity_sweep")
        if side == "ask":
            return {
                "action": "enter_long",
                "reason": "liquidity_sweep_ask",
            }
        if side == "bid":
            return {
                "action": "enter_short",
                "reason": "liquidity_sweep_bid",
            }

    return None


def decide_exit(row: Dict, position_side: str) -> Optional[Dict]:
    names = set(_event_names(row))

    if position_side == "long":
        if "pressure_shift" in names or "wall_created" in names:
            return {
                "action": "exit_long",
                "reason": "pressure_shift_or_wall_created",
            }

    if position_side == "short":
        if "pressure_shift" in names or "wall_created" in names:
            return {
                "action": "exit_short",
                "reason": "pressure_shift_or_wall_created",
            }

    return None


def microstructure_strategy(row: Dict, position) -> Optional[Dict]:
    if position is None:
        return decide_entry(row)

    return decide_exit(row, position.side)


def regime_aware_microstructure_strategy(row: Dict, position, context: Optional[Dict] = None) -> Optional[Dict]:
    regime = "unknown"
    if isinstance(context, dict):
        regime_report = context.get("regime_report")
        if isinstance(regime_report, dict):
            regime = str(regime_report.get("regime") or "unknown")

    decision = microstructure_strategy(row, position)
    if decision is None:
        return None

    action = str(decision.get("action") or "")

    if position is not None:
        return decision

    if regime == "liquidity_vacuum":
        return None

    if regime == "range":
        return None

    if regime == "trend_up" and action == "enter_short":
        return None

    if regime == "trend_down" and action == "enter_long":
        return None

    return {
        **decision,
        "reason": f"{decision.get('reason')}_regime_{regime}",
    }