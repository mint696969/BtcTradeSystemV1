# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_evidence_presentation_panel.py
# desc: Verify shared evidence presentation panel helpers stay render-boundary safe.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.evidence_presentation_panel import (  # noqa: E402
    build_evidence_presentation_caption,
    build_evidence_presentation_lines,
)


def _payload() -> dict:
    return {
        "presentation_kind": "health_warroom_evidence_consumption_presentation",
        "presentation_version": "phase4a.health_warroom_evidence_presentation.v1",
        "title": "Real-data validation evidence",
        "status_key": "available",
        "severity_key": "info",
        "health_line": "Evidence summary available for bitflyer/BTC_JPY.",
        "warroom_line": "Review support: replay=36, board=18, trade=18, notes=0.",
        "summary_lines": [
            "status=available",
            "severity=info",
            "exchange=bitflyer",
            "symbol=BTC_JPY",
        ],
        "counts": {
            "replay_row_count": 36,
            "board_row_count": 18,
            "trade_row_count": 18,
            "diagnostic_note_count": 0,
        },
        "evidence_trace_refs": ["extended:36rows"],
        "boundary": {
            "read_only_consumption": True,
            "diagnostic_evidence_only": True,
            "operator_support_only": True,
            "not_runtime_signal": True,
            "not_runtime_wiring": True,
            "not_ui_rendering": True,
            "not_market_engine_input": True,
            "not_collector_writer": True,
            "not_broker_or_order_automation": True,
            "not_inference_or_training": True,
        },
    }


def main() -> int:
    caption = build_evidence_presentation_caption(_payload())
    assert "evidence_presentation" in caption
    assert "status=available" in caption
    assert "severity=info" in caption
    assert "read_only_consumption=True" in caption
    assert "diagnostic_evidence_only=True" in caption
    assert "operator_support_only=True" in caption
    assert "not_runtime_signal=True" in caption
    assert "not_ui_rendering=True" in caption
    assert "not_market_engine_input=True" in caption
    assert "not_collector_writer=True" in caption
    assert "not_broker_or_order_automation=True" in caption
    assert "not_inference_or_training=True" in caption

    lines = build_evidence_presentation_lines(_payload())
    assert "title=Real-data validation evidence" in lines
    assert "status=available" in lines
    assert "severity=info" in lines
    assert "replay_rows=36" in lines
    assert "board_rows=18" in lines
    assert "trade_rows=18" in lines
    assert "diagnostic_notes=0" in lines
    assert "summary=exchange=bitflyer" in lines
    assert "trace_refs=extended:36rows" in lines

    empty_caption = build_evidence_presentation_caption(None)
    assert "status=unknown" in empty_caption
    assert "boundary=unavailable" in empty_caption

    empty_lines = build_evidence_presentation_lines(None)
    assert "status=unknown" in empty_lines
    assert "replay_rows=0" in empty_lines

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
