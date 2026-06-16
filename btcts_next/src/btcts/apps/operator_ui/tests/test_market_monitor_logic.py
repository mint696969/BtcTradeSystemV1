# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_monitor_logic.py
# desc: Verify Market Monitor status resolution can consume shared market summary payload.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.market_monitor_logic import monitor_status_values
from btcts.apps.operator_ui.components.market_monitor_presenter import summary_contract_caption


def main() -> int:
    board = {
        "trust_state": None,
        "continuity_state": None,
        "interpretation_bucket": None,
        "interpretation_reason": None,
    }
    state = {
        "trust_state": "provisional",
        "continuity_state": "resynced",
        "interpretation_bucket": "observe_only",
        "interpretation_reason": "state_side_reason",
    }
    summary = {
        "trust_state": "trusted",
        "continuity_state": "continuous",
        "interpretation_bucket": "allow_structural_use",
        "interpretation_reason": "summary_side_reason",
    }

    resolved = monitor_status_values(board, state, summary)
    assert resolved["trust_state"] == "trusted"
    assert resolved["continuity_state"] == "continuous"
    assert resolved["interpretation_bucket"] == "allow_structural_use"
    assert resolved["interpretation_reason"] == "summary_side_reason"

    board_override = {
        "trust_state": "board_trusted",
        "continuity_state": "board_continuous",
        "interpretation_bucket": "board_allow",
        "interpretation_reason": "board_reason",
    }
    resolved_override = monitor_status_values(board_override, state, summary)
    assert resolved_override["trust_state"] == "trusted"
    assert resolved_override["continuity_state"] == "continuous"
    assert resolved_override["interpretation_bucket"] == "allow_structural_use"
    assert resolved_override["interpretation_reason"] == "summary_side_reason"

    resolved_board_fallback = monitor_status_values(board_override, None, None)
    assert resolved_board_fallback["trust_state"] == "board_trusted"
    assert resolved_board_fallback["continuity_state"] == "board_continuous"
    assert resolved_board_fallback["interpretation_bucket"] == "board_allow"
    assert resolved_board_fallback["interpretation_reason"] == "board_reason"

    contract_caption = summary_contract_caption(
        lang="en",
        summary={
            "semantic_usage_contract_rows_kind": "event_family_contract_rows",
            "semantic_usage_contract_rows_count": 2,
            "orderbook_active_event_contracts_kind": "active_event_contract_rows",
            "orderbook_active_event_contracts_count": 1,
        },
    )
    assert "family_rows=2" in contract_caption
    assert "event_family_contract_rows" in contract_caption
    assert "active_event_rows=1" in contract_caption
    assert "active_event_contract_rows" in contract_caption

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())