# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_real_data_validation_evidence_presentation_upstream.py
# desc: Verify pure Health/WarRoom evidence presentation upstream payload producer.

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[4]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_presentation_upstream import (  # noqa: E402
    build_health_warroom_evidence_presentation_upstream_payload,
    health_snapshot_evidence_presentation_payload_fields,
    lower_health_warroom_evidence_presentation_payload,
    warroom_session_state_evidence_presentation_payload_fields,
)
from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import (  # noqa: E402
    build_real_data_validation_evidence_summary,
)


def _summary():
    return build_real_data_validation_evidence_summary(
        source_output_ref="source.json",
        review_output_ref="review.json",
        evidence_trace_refs=("extended:36rows",),
    )


def main() -> int:
    payload = build_health_warroom_evidence_presentation_upstream_payload(_summary())

    assert payload["upstream_payload_kind"] == "health_warroom_evidence_presentation_upstream_payload"
    assert payload["upstream_payload_version"] == "phase4a.health_warroom_evidence_presentation_upstream.v1"
    assert payload["presentation_kind"] == "health_warroom_evidence_consumption_presentation"
    assert payload["status_key"] == "available"
    assert payload["severity_key"] == "info"
    assert payload["counts"]["replay_row_count"] == 36
    assert payload["boundary"]["read_only_consumption"] is True
    assert payload["boundary"]["diagnostic_evidence_only"] is True
    assert payload["boundary"]["operator_support_only"] is True
    assert payload["boundary"]["not_runtime_signal"] is True
    assert payload["boundary"]["not_runtime_wiring"] is True
    assert payload["boundary"]["not_ui_rendering"] is True
    assert payload["boundary"]["not_market_engine_input"] is True
    assert payload["boundary"]["not_collector_writer"] is True
    assert payload["boundary"]["not_broker_or_order_automation"] is True
    assert payload["boundary"]["not_inference_or_training"] is True
    assert payload["not_runtime_wiring"] is True
    assert payload["not_collector_writer"] is True
    assert payload["not_inference_or_training"] is True

    health_fields = health_snapshot_evidence_presentation_payload_fields(payload)
    assert set(health_fields) == {
        "evidence_presentation_payload",
        "health_warroom_evidence_presentation_payload",
        "real_data_validation_evidence_presentation",
    }
    assert health_fields["evidence_presentation_payload"]["status_key"] == "available"

    warroom_fields = warroom_session_state_evidence_presentation_payload_fields(payload)
    assert set(warroom_fields) == {
        "warroom_evidence_presentation_payload",
        "health_warroom_evidence_presentation_payload",
        "real_data_validation_evidence_presentation",
        "evidence_presentation_payload",
    }
    assert warroom_fields["warroom_evidence_presentation_payload"]["status_key"] == "available"

    lowered = lower_health_warroom_evidence_presentation_payload(_summary())
    assert lowered["lowering_kind"] == "health_warroom_evidence_presentation_payload_lowering"
    assert lowered["payload"]["status_key"] == "available"
    assert lowered["health_snapshot_fields"]["evidence_presentation_payload"]["status_key"] == "available"
    assert lowered["warroom_session_state_fields"]["warroom_evidence_presentation_payload"]["status_key"] == "available"
    assert lowered["not_runtime_wiring"] is True
    assert lowered["not_market_engine_input"] is True
    assert lowered["not_collector_writer"] is True

    missing = lower_health_warroom_evidence_presentation_payload(None)
    assert missing["payload"]["status_key"] == "missing"
    assert missing["payload"]["severity_key"] == "blocked"

    forbidden_keys = [
        "route",
        "runtime" + "_" + "state" + "_" + "path",
        "market" + "_" + "engine" + "_" + "signal",
        "collector" + "_" + "write" + "_" + "path",
        "place" + "_" + "order",
        "broker" + "_" + "order",
        "training" + "_" + "dataset",
        "inference" + "_" + "job",
    ]
    for key in forbidden_keys:
        assert key not in payload
        assert key not in lowered

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
