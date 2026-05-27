# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_real_data_validation_evidence.py
# desc: Tests for read-only real-data validation evidence summary skeleton.

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[4]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import (
    RealDataValidationEvidenceSummary,
    build_real_data_validation_evidence_summary,
    real_data_validation_evidence_summary_to_snapshot,
)


def test_real_data_validation_evidence_summary_minimal_shape() -> None:
    summary = build_real_data_validation_evidence_summary(
        source_output_ref="tmp/work/phase4a_extended_real_data_validation_review/probe_phase4a_extended_real_data_validation_review.out.json",
        review_output_ref="tmp/work/phase4a_extended_real_data_validation_review_entry/review_extended_real_data_validation_review_output_v1.out.json",
        evidence_trace_refs=("extended:36rows",),
    )

    assert isinstance(summary, RealDataValidationEvidenceSummary)
    assert summary.evidence_type == "real_data_validation_evidence_summary"
    assert summary.evidence_version == "phase4a.real_data_validation_evidence.v1"
    assert summary.source_kind == "extended_real_data_validation_review_output"
    assert summary.exchange == "bitflyer"
    assert summary.symbol == "BTC_JPY"
    assert summary.channel_count == 4
    assert summary.replay_row_count == 36
    assert summary.board_row_count == 18
    assert summary.trade_row_count == 18
    assert summary.monotonic_check_count == 7
    assert summary.diagnostic_note_count == 0
    assert summary.evidence_trace_refs == ("extended:36rows",)


def test_real_data_validation_evidence_summary_is_read_only_diagnostic_contract() -> None:
    summary = build_real_data_validation_evidence_summary(
        source_output_ref="source.json",
        review_output_ref="review.json",
        diagnostics={"source": "unit_test"},
    )

    assert summary.diagnostics["builder_stage"] == "read_only_contract_skeleton"
    assert summary.diagnostics["read_only_contract"] is True
    assert summary.diagnostics["diagnostic_evidence_only"] is True
    assert summary.diagnostics["not_runtime_signal"] is True
    assert summary.diagnostics["not_runtime_wiring"] is True
    assert summary.diagnostics["not_ui_rendering"] is True
    assert summary.diagnostics["not_market_engine_input"] is True
    assert summary.diagnostics["not_collector_writer"] is True
    assert summary.diagnostics["not_broker_or_order_automation"] is True
    assert summary.diagnostics["not_inference_or_training"] is True


def test_real_data_validation_evidence_snapshot_is_read_only_and_layout_free() -> None:
    summary = build_real_data_validation_evidence_summary(
        source_output_ref="source.json",
        review_output_ref="review.json",
    )
    snapshot = real_data_validation_evidence_summary_to_snapshot(summary)

    assert snapshot["snapshot_stage"] == "real_data_validation_evidence_read_only_snapshot"
    assert snapshot["read_only_contract"] is True
    assert snapshot["diagnostic_evidence_only"] is True
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


def test_real_data_validation_evidence_summary_does_not_own_runtime_or_order_fields() -> None:
    fields = RealDataValidationEvidenceSummary.__dataclass_fields__
    forbidden_fields = [
        "runtime" + "_" + "state" + "_" + "path",
        "ui" + "_" + "route",
        "market" + "_" + "engine" + "_" + "signal",
        "collector" + "_" + "write" + "_" + "path",
        "order" + "_" + "size",
        "order" + "_" + "price",
        "broker" + "_" + "account",
        "place" + "_" + "order",
        "broker" + "_" + "order",
        "live" + "_" + "order" + "_" + "placement",
        "auto" + "_" + "trade",
        "training" + "_" + "dataset",
        "inference" + "_" + "job",
    ]
    for field_name in forbidden_fields:
        assert field_name not in fields
