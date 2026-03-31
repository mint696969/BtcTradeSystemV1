# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_alert_presenter.py
# desc: War Room alert の表示用派生値をまとめる presenter 層。

from __future__ import annotations


def pressure_bias_from_imbalance(imbalance) -> str:
    pressure_bias = "neutral_bias"
    if isinstance(imbalance, (int, float)):
        if imbalance > 0.2:
            pressure_bias = "buy_pressure"
        elif imbalance < -0.2:
            pressure_bias = "sell_pressure"
    return pressure_bias


def strategy_label(best_strategy) -> str:
    return best_strategy if best_strategy not in {None, "", "unknown"} else "live_active"


def severity_order_value(severity: str) -> int:
    mapping = {
        "critical": 0,
        "warning": 1,
        "info": 2,
    }
    return mapping.get(severity, 9)


def live_probe_message(spread, delta, best_strategy, regime) -> str:
    return (
        f"[live_probe] spread={spread} delta={delta} "
        f"best_strategy={best_strategy} regime={regime}"
    )