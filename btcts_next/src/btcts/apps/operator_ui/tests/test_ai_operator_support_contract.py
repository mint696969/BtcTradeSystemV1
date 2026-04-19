# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_support_contract.py
# desc: Verify ai_operator deterministic support contract stays advisory-only and structurally stable.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.ai_operator_support_contract import (  # noqa: E402
    build_operator_support_contract,
)


def main() -> int:
    state = {
        "spread": 1800.0,
        "imbalance": 0.35,
        "delta": 0.28,
        "wall_ratio": 0.31,
        "event_ts": "2026-04-17T01:40:00Z",
        "regime": "trend_up",
        "best_strategy": "microstructure_v2",
        "pressure_bias": "buy_pressure",
    }

    contract = build_operator_support_contract(
        state=state,
        runtime_source="external",
    )

    assert contract["action"] == "long_watch"
    assert contract["risk"] == "low"

    decision_row = contract["decision_row"]
    assert decision_row == {
        "ts": "2026-04-17T01:40:00Z",
        "regime": "trend_up",
        "spread_state": "tight",
        "imbalance_state": "bid_bias",
        "delta_state": "buy_flow",
        "wall_state": "bid_wall",
        "action": "long_watch",
        "risk": "low",
        "runtime_source": "external",
    }

    support_context = contract["support_context"]
    assert support_context == {
        "event_ts": "2026-04-17T01:40:00Z",
        "regime": "trend_up",
        "best_strategy": "microstructure_v2",
        "pressure_bias": "buy_pressure",
        "advisory_action": "long_watch",
        "advisory_risk": "low",
        "runtime_source": "external",
    }

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())