# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_review_hint_presenter.py
# desc: Verify read-only review hint presenter stays widget-friendly and layout-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.review_hint_presenter import (  # noqa: E402
    review_hint_compact_reading_line,
    review_hint_display_sections,
    review_hint_snapshot_lines,
)


def _context() -> dict:
    return {
        "context_type": "prediction_review_hint_summary_context",
        "source_kind": "replay_report",
        "available": True,
        "read_only_contract": True,
        "not_runtime_wiring": True,
        "not_ui_rendering": True,
        "position_summary": {
            "snapshot_count": 1,
            "latest_prediction_type": "position_review_hint",
            "latest_source_kind": "replay_artifact_only",
            "latest_management_hint": "review_only_wait",
            "latest_exposure_risk_hint": "unknown",
            "latest_read_only_contract": True,
            "latest_not_runtime_wiring": True,
            "latest_not_ui_wiring": True,
        },
        "execution_summary": {
            "snapshot_count": 1,
            "latest_prediction_type": "execution_review_hint",
            "latest_source_kind": "replay_artifact_only",
            "latest_timing_hint": "review_only_wait_for_confirmation",
            "latest_urgency_hint": "low",
            "latest_feasibility_hint": "feasible_for_review_only",
            "latest_execution_side_effect_free": True,
            "latest_broker_link_free": True,
            "latest_account_side_effect_free": True,
            "latest_read_only_contract": True,
            "latest_not_runtime_wiring": True,
            "latest_not_ui_wiring": True,
        },
    }


def main() -> int:
    context = _context()
    assert review_hint_compact_reading_line(context) == (
        "review_hint_reading=position:review_only_wait(1) / "
        "execution:review_only_wait_for_confirmation(1) / review_only"
    )

    lines = review_hint_snapshot_lines(context)
    assert "context_type=prediction_review_hint_summary_context" in lines
    assert "source_kind=replay_report" in lines
    assert "available=true" in lines
    assert "read_only_contract=true" in lines
    assert "not_runtime_wiring=true" in lines
    assert "not_ui_rendering=true" in lines
    assert "position_prediction_type=position_review_hint" in lines
    assert "position_management_hint=review_only_wait" in lines
    assert "position_not_ui_wiring=true" in lines
    assert "execution_prediction_type=execution_review_hint" in lines
    assert "execution_timing_hint=review_only_wait_for_confirmation" in lines
    assert "execution_broker_link_free=true" in lines
    assert "execution_account_side_effect_free=true" in lines
    assert "execution_not_ui_wiring=true" in lines

    sections = review_hint_display_sections(context)
    assert sections["section_type"] == "prediction_review_hint_display_context"
    assert sections["compact_line"] == review_hint_compact_reading_line(context)
    assert sections["snapshot_lines"] == lines
    assert sections["read_only_contract"] is True
    assert sections["not_runtime_wiring"] is True
    assert sections["not_ui_rendering"] is True
    assert sections["widget_reusable"] is True

    assert review_hint_compact_reading_line(None) == "review_hint_reading unavailable"
    assert review_hint_snapshot_lines(None) == ()
    assert review_hint_display_sections(None)["snapshot_lines"] == ()

    forbidden_keys = {
        "_".join(("order", "size")),
        "_".join(("order", "price")),
        "".join(("lever", "age")),
        "_".join(("broker", "account")),
        "_".join(("place", "order")),
        "_".join(("broker", "order")),
        "_".join(("live", "order", "placement")),
        "_".join(("auto", "trade")),
        "_".join(("account", "mutation")),
        "streamlit",
    }
    joined = "\n".join(lines)
    assert not any(token in joined for token in forbidden_keys)

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
