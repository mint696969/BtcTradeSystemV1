# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_real_data_validation_evidence_consumption.py
# desc: Tests for read-only Health/WarRoom real-data validation evidence consumption model.

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[4]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
    HealthWarRoomEvidenceConsumptionModel,
    build_health_warroom_evidence_consumption_model,
    health_warroom_evidence_consumption_model_to_snapshot,
)
from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import (
    build_real_data_validation_evidence_summary,
)


def _summary():
    return build_real_data_validation_evidence_summary(
        source_output_ref="source.json",
        review_output_ref="review.json",
        evidence_trace_refs=("extended:36rows",),
    )


def test_health_warroom_evidence_consumption_model_minimal_shape() -> None:
    model = build_health_warroom_evidence_consumption_model(_summary())

    assert isinstance(model, HealthWarRoomEvidenceConsumptionModel)
    assert model.consumer_model_version == "phase4a.health_warroom_evidence_consumption.v1"
    assert model.health_consumption_status == "read_only_diagnostic_observer"
    assert model.warroom_consumption_status == "read_only_operator_support"
    assert model.evidence_presence == "present"
    assert model.diagnostic_status == "clean"
    assert model.channel_count == 4
    assert model.replay_row_count == 36
    assert model.board_row_count == 18
    assert model.trade_row_count == 18
    assert model.monotonic_check_count == 7
    assert model.diagnostic_note_count == 0
    assert model.evidence_trace_refs == ("extended:36rows",)


def test_health_warroom_evidence_consumption_model_is_boundary_safe() -> None:
    snapshot = health_warroom_evidence_consumption_model_to_snapshot(
        build_health_warroom_evidence_consumption_model(_summary())
    )

    assert snapshot["snapshot_stage"] == "health_warroom_evidence_consumption_read_only_snapshot"
    assert snapshot["read_only_consumption"] is True
    assert snapshot["diagnostic_evidence_only"] is True
    assert snapshot["operator_support_only"] is True
    assert snapshot["not_runtime_signal"] is True
    assert snapshot["not_runtime_wiring"] is True
    assert snapshot["not_ui_rendering"] is True
    assert snapshot["not_market_engine_input"] is True
    assert snapshot["not_collector_writer"] is True
    assert snapshot["not_broker_or_order_automation"] is True
    assert snapshot["not_inference_or_training"] is True

    forbidden_keys = [
        "component",
        "widget",
        "route",
        "runtime" + "_" + "state" + "_" + "path",
        "market" + "_" + "engine" + "_" + "signal",
        "collector" + "_" + "write" + "_" + "path",
        "order" + "_" + "size",
        "place" + "_" + "order",
        "broker" + "_" + "order",
        "training" + "_" + "dataset",
        "inference" + "_" + "job",
    ]
    for key in forbidden_keys:
        assert key not in snapshot


def test_health_warroom_evidence_consumption_model_accepts_snapshot_mapping() -> None:
    summary = _summary()
    evidence_snapshot = {
        "evidence_type": summary.evidence_type,
        "evidence_version": summary.evidence_version,
        "source_kind": summary.source_kind,
        "market_uid": summary.market_uid,
        "exchange": summary.exchange,
        "symbol": summary.symbol,
        "validation_phase": summary.validation_phase,
        "sample_window_label": summary.sample_window_label,
        "channel_count": summary.channel_count,
        "replay_row_count": summary.replay_row_count,
        "board_row_count": summary.board_row_count,
        "trade_row_count": summary.trade_row_count,
        "monotonic_check_count": summary.monotonic_check_count,
        "diagnostic_note_count": summary.diagnostic_note_count,
        "evidence_trace_refs": list(summary.evidence_trace_refs),
        "read_only_contract": True,
        "diagnostic_evidence_only": True,
    }

    model = build_health_warroom_evidence_consumption_model(evidence_snapshot)

    assert model.health_consumption_status == "read_only_diagnostic_observer"
    assert model.warroom_consumption_status == "read_only_operator_support"
    assert model.exchange == "bitflyer"
    assert model.symbol == "BTC_JPY"


def test_health_warroom_evidence_consumption_status_payload_from_model() -> None:
    model = build_health_warroom_evidence_consumption_model(_summary())
    from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
        health_warroom_evidence_consumption_status_payload,
    )

    payload = health_warroom_evidence_consumption_status_payload(model)

    assert payload["payload_kind"] == "health_warroom_evidence_consumption_status"
    assert payload["payload_version"] == "phase4a.health_warroom_evidence_consumption_status.v1"
    assert payload["health_consumption_status"] == "read_only_diagnostic_observer"
    assert payload["warroom_consumption_status"] == "read_only_operator_support"
    assert payload["counts"]["replay_row_count"] == 36
    assert payload["counts"]["board_row_count"] == 18
    assert payload["counts"]["trade_row_count"] == 18
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

    forbidden_keys = [
        "component",
        "widget",
        "route",
        "streamlit",
        "runtime" + "_" + "state" + "_" + "path",
        "market" + "_" + "engine" + "_" + "signal",
        "collector" + "_" + "write" + "_" + "path",
        "order" + "_" + "size",
        "place" + "_" + "order",
        "broker" + "_" + "order",
        "training" + "_" + "dataset",
        "inference" + "_" + "job",
    ]
    for key in forbidden_keys:
        assert key not in payload


def test_health_warroom_evidence_consumption_status_payload_missing() -> None:
    from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
        health_warroom_evidence_consumption_status_payload,
    )

    payload = health_warroom_evidence_consumption_status_payload(None)

    assert payload["evidence_presence"] == "missing"
    assert payload["health_consumption_status"] == "missing"
    assert payload["warroom_consumption_status"] == "missing"
    assert payload["read_only_consumption"] is True
    assert payload["not_ui_rendering"] is True


def test_health_warroom_evidence_presentation_model_render_free_shape() -> None:
    from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
        HealthWarRoomEvidencePresentationModel,
        health_warroom_evidence_presentation_model,
        health_warroom_evidence_presentation_payload,
    )

    model = health_warroom_evidence_presentation_model(_summary())
    payload = health_warroom_evidence_presentation_payload(model)

    assert isinstance(model, HealthWarRoomEvidencePresentationModel)
    assert model.presentation_kind == "health_warroom_evidence_consumption_presentation"
    assert model.presentation_version == "phase4a.health_warroom_evidence_presentation.v1"
    assert model.status_key == "available"
    assert model.severity_key == "info"
    assert "Evidence summary available" in model.health_line
    assert "Review support" in model.warroom_line
    assert payload["presentation_kind"] == model.presentation_kind
    assert payload["status_key"] == "available"
    assert payload["counts"]["replay_row_count"] == 36
    assert payload["boundary"]["read_only_consumption"] is True
    assert payload["boundary"]["diagnostic_evidence_only"] is True
    assert payload["boundary"]["operator_support_only"] is True
    assert payload["boundary"]["not_ui_rendering"] is True
    assert payload["boundary"]["not_runtime_signal"] is True
    assert payload["not_ui_rendering"] is True
    assert payload["not_runtime_wiring"] is True

    forbidden_keys = [
        "streamlit",
        "route",
        "component",
        "widget_id",
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


def test_health_warroom_evidence_presentation_model_missing_shape() -> None:
    from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
        health_warroom_evidence_presentation_payload,
    )

    payload = health_warroom_evidence_presentation_payload(None)

    assert payload["status_key"] == "missing"
    assert payload["severity_key"] == "blocked"
    assert payload["boundary"]["read_only_consumption"] is True
    assert payload["boundary"]["not_ui_rendering"] is True
    assert payload["not_runtime_signal"] is True

if __name__ == "__main__":
    test_health_warroom_evidence_consumption_model_minimal_shape()
    test_health_warroom_evidence_consumption_model_is_boundary_safe()
    test_health_warroom_evidence_consumption_model_accepts_snapshot_mapping()
    test_health_warroom_evidence_consumption_status_payload_from_model()
    test_health_warroom_evidence_consumption_status_payload_missing()
    test_health_warroom_evidence_presentation_model_render_free_shape()
    test_health_warroom_evidence_presentation_model_missing_shape()
    print("ok")

