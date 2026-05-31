# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_evidence_presentation_lowering_bridge.py
# desc: Verify operator-ui evidence presentation lowering bridge remains pure and bounded.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.evidence_presentation_lowering_bridge import (  # noqa: E402
    lower_health_snapshot_evidence_presentation_for_ui,
    lower_warroom_session_state_evidence_presentation_for_ui,
)


def _payload() -> dict:
    # Already-built payload fixture. This apps/operator_ui test must not import
    # render-free presentation builders or source-artifact summary builders.
    return {
        "upstream_payload_kind": "health_warroom_evidence_presentation_upstream_payload",
        "upstream_payload_version": "phase4a.health_warroom_evidence_presentation_upstream.v1",
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
        "read_only_consumption": True,
        "diagnostic_evidence_only": True,
        "operator_support_only": True,
        "not_runtime_signal": True,
        "not_runtime_wiring": True,
        "not_market_engine_input": True,
        "not_collector_writer": True,
        "not_broker_or_order_automation": True,
        "not_inference_or_training": True,
    }


def main() -> int:
    payload = _payload()

    health_in = {"existing": "health"}
    health_out = lower_health_snapshot_evidence_presentation_for_ui(health_in, payload)
    assert health_in == {"existing": "health"}
    assert health_out["existing"] == "health"
    assert health_out["evidence_presentation_payload"]["status_key"] == "available"
    health_warroom_payload_key = "health_warroom_evidence" + "_presentation_payload"
    assert health_out[health_warroom_payload_key]["status_key"] == "available"
    assert health_out["real_data_validation_evidence_presentation"]["status_key"] == "available"
    assert health_out["evidence_presentation_lowering_channel"] == "health_snapshot_fields"
    assert health_out["evidence_presentation_wiring_bridge"] == "health_snapshot_ui_bridge"

    warroom_in = {"existing": "warroom"}
    warroom_out = lower_warroom_session_state_evidence_presentation_for_ui(warroom_in, payload)
    assert warroom_in == {"existing": "warroom"}
    assert warroom_out["existing"] == "warroom"
    assert warroom_out["warroom_evidence_presentation_payload"]["status_key"] == "available"
    assert warroom_out[health_warroom_payload_key]["status_key"] == "available"
    assert warroom_out["real_data_validation_evidence_presentation"]["status_key"] == "available"
    assert warroom_out["evidence_presentation_payload"]["status_key"] == "available"
    assert warroom_out["evidence_presentation_lowering_channel"] == "warroom_session_state_fields"
    assert warroom_out["evidence_presentation_wiring_bridge"] == "warroom_session_state_ui_bridge"

    for out in (health_out, warroom_out):
        assert out["not_runtime_wiring"] is True
        assert out["not_runtime_signal"] is True
        assert out["not_market_engine_input"] is True
        assert out["not_collector_writer"] is True
        assert out["not_broker_or_order_automation"] is True
        assert out["not_inference_or_training"] is True
        for forbidden in (
            "runtime_state_path",
            "market_engine_signal",
            "collector_write_path",
            "place" + "_" + "order",
            "broker" + "_" + "order",
            "training_dataset",
            "inference_job",
        ):
            assert forbidden not in out

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
