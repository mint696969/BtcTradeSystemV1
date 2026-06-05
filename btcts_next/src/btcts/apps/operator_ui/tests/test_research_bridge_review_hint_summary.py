# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_research_bridge_review_hint_summary.py
# desc: Verify replay report Position/Execution review hint summaries are exposed as read-only display context.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.research_bridge import (  # noqa: E402
    replay_review_hint_summary_payload,
)


def main() -> int:
    payload = replay_review_hint_summary_payload(
        {
            "report": {
                "prediction_position_review_hint_summary": {
                    "snapshot_count": 1,
                    "latest_prediction_type": "position_review_hint",
                    "latest_management_hint": "review_only_wait",
                    "latest_read_only_contract": True,
                    "latest_not_runtime_wiring": True,
                    "latest_not_ui_wiring": True,
                },
                "prediction_execution_review_hint_summary": {
                    "snapshot_count": 1,
                    "latest_prediction_type": "execution_review_hint",
                    "latest_timing_hint": "review_only_wait_for_confirmation",
                    "latest_execution_side_effect_free": True,
                    "latest_broker_link_free": True,
                    "latest_account_side_effect_free": True,
                    "latest_read_only_contract": True,
                    "latest_not_runtime_wiring": True,
                    "latest_not_ui_wiring": True,
                },
            }
        }
    )

    assert payload["context_type"] == "prediction_review_hint_summary_context"
    assert payload["source_kind"] == "replay_report"
    assert payload["available"] is True
    assert payload["read_only_contract"] is True
    assert payload["not_runtime_wiring"] is True
    assert payload["not_ui_rendering"] is True
    assert payload["position_summary"]["latest_prediction_type"] == "position_review_hint"
    assert payload["execution_summary"]["latest_prediction_type"] == "execution_review_hint"
    assert payload["execution_summary"]["latest_broker_link_free"] is True
    assert payload["execution_summary"]["latest_account_side_effect_free"] is True

    empty = replay_review_hint_summary_payload({"report": {}})
    assert empty["available"] is False
    assert empty["position_summary"] is None
    assert empty["execution_summary"] is None
    assert empty["read_only_contract"] is True

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
