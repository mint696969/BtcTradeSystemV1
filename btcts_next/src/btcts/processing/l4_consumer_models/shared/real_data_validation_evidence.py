# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/real_data_validation_evidence.py
# desc: Read-only real-data validation evidence summary contract skeleton.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class RealDataValidationEvidenceSummary:
    """
    Phase 4-A real-data validation evidence summary skeleton.

    Boundary:
    - read-only evidence summary contract
    - diagnostic evidence only
    - not runtime signal
    - not UI rendering
    - not market_engine input
    - not collector writer/backfill
    - not broker/order automation
    - not inference or training input
    """

    evidence_type: str
    evidence_version: str
    source_kind: str
    market_uid: str
    exchange: str
    symbol: str

    validation_phase: str
    source_output_ref: str
    review_output_ref: str
    sample_window_label: str

    channel_count: int
    replay_row_count: int
    board_row_count: int
    trade_row_count: int
    monotonic_check_count: int
    diagnostic_note_count: int = 0

    evidence_trace_refs: Sequence[str] = field(default_factory=tuple)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)


def build_real_data_validation_evidence_summary(
    *,
    source_output_ref: str,
    review_output_ref: str,
    market_uid: str = "btc_jpy",
    exchange: str = "bitflyer",
    symbol: str = "BTC_JPY",
    validation_phase: str = "phase4a_extended_real_data_validation_review",
    sample_window_label: str = "bounded_3_dates_4_channels_36_rows",
    channel_count: int = 4,
    replay_row_count: int = 36,
    board_row_count: int = 18,
    trade_row_count: int = 18,
    monotonic_check_count: int = 7,
    diagnostic_note_count: int = 0,
    evidence_trace_refs: Sequence[str] = (),
    diagnostics: Mapping[str, Any] | None = None,
) -> RealDataValidationEvidenceSummary:
    return RealDataValidationEvidenceSummary(
        evidence_type="real_data_validation_evidence_summary",
        evidence_version="phase4a.real_data_validation_evidence.v1",
        source_kind="extended_real_data_validation_review_output",
        market_uid=market_uid,
        exchange=exchange,
        symbol=symbol,
        validation_phase=validation_phase,
        source_output_ref=source_output_ref,
        review_output_ref=review_output_ref,
        sample_window_label=sample_window_label,
        channel_count=channel_count,
        replay_row_count=replay_row_count,
        board_row_count=board_row_count,
        trade_row_count=trade_row_count,
        monotonic_check_count=monotonic_check_count,
        diagnostic_note_count=diagnostic_note_count,
        evidence_trace_refs=tuple(evidence_trace_refs),
        diagnostics={
            "builder_type": "real_data_validation_evidence_summary",
            "builder_stage": "read_only_contract_skeleton",
            "read_only_contract": True,
            "diagnostic_evidence_only": True,
            "not_runtime_signal": True,
            "not_runtime_wiring": True,
            "not_ui_rendering": True,
            "not_market_engine_input": True,
            "not_collector_writer": True,
            "not_broker_or_order_automation": True,
            "not_inference_or_training": True,
            **dict(diagnostics or {}),
        },
    )


def real_data_validation_evidence_summary_to_snapshot(
    summary: RealDataValidationEvidenceSummary,
) -> dict[str, Any]:
    return {
        "evidence_type": summary.evidence_type,
        "evidence_version": summary.evidence_version,
        "source_kind": summary.source_kind,
        "market_uid": summary.market_uid,
        "exchange": summary.exchange,
        "symbol": summary.symbol,
        "validation_phase": summary.validation_phase,
        "source_output_ref": summary.source_output_ref,
        "review_output_ref": summary.review_output_ref,
        "sample_window_label": summary.sample_window_label,
        "channel_count": summary.channel_count,
        "replay_row_count": summary.replay_row_count,
        "board_row_count": summary.board_row_count,
        "trade_row_count": summary.trade_row_count,
        "monotonic_check_count": summary.monotonic_check_count,
        "diagnostic_note_count": summary.diagnostic_note_count,
        "evidence_trace_refs": list(summary.evidence_trace_refs),
        "diagnostics": dict(summary.diagnostics),
        "snapshot_stage": "real_data_validation_evidence_read_only_snapshot",
        "read_only_contract": True,
        "diagnostic_evidence_only": True,
        "not_runtime_signal": True,
        "not_runtime_wiring": True,
        "not_ui_rendering": True,
        "not_market_engine_input": True,
        "not_collector_writer": True,
        "not_broker_or_order_automation": True,
        "not_inference_or_training": True,
    }
