# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_action_payloads.py
# desc: Verify ai_operator support context can be lowered into research/watch payloads safely.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.ai_operator_action_payloads import (  # noqa: E402
    build_research_replay_context,
    build_watch_item,
)


def main() -> int:
    support_context = {
        "event_ts": "2026-04-17T01:45:00Z",
        "regime": "transition",
        "best_strategy": "scenario_prediction_core",
        "pressure_bias": "sell_pressure",
        "advisory_action": "trap_caution",
        "advisory_risk": "high",
        "runtime_source": "fallback-local",
        "tactic_summary_lines": (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
        ),
    }

    research_replay_context = build_research_replay_context(support_context)
    assert research_replay_context == {
        "session_name": "warroom_ai_operator",
        "start_ts": "",
        "end_ts": "",
        "jump_ts": "2026-04-17T01:45:00Z",
        "kind_filter": "all",
        "event_filter": "sell_pressure",
        "filtered_rows": 1,
        "tactic_summary_lines": (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
        ),
    }

    watch_item = build_watch_item(support_context)
    assert watch_item == {
        "ts": "2026-04-17T01:45:00Z",
        "regime": "transition",
        "action": "trap_caution",
        "risk": "high",
        "tactic_summary_lines": (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
        ),
    }

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())