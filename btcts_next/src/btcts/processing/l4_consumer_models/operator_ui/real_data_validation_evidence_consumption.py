# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_consumption.py
# desc: Read-only Health/WarRoom consumer model for real-data validation evidence summary.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import (
    RealDataValidationEvidenceSummary,
    real_data_validation_evidence_summary_to_snapshot,
)


@dataclass(frozen=True)
class HealthWarRoomEvidenceConsumptionModel:
    """
    Thin read-only consumer model for Health / WarRoom evidence context.

    Boundary:
    - read-only evidence-summary consumption
    - diagnostic/operator-support context only
    - not UI rendering
    - not runtime wiring
    - not runtime signal
    - not market_engine input
    - not collector writer/backfill
    - not broker/order automation
    - not inference or training input
    """

    evidence_type: str
    evidence_version: str
    consumer_model_version: str
    source_kind: str
    market_uid: str
    exchange: str
    symbol: str
    validation_phase: str
    sample_window_label: str

    health_consumption_status: str
    warroom_consumption_status: str
    evidence_presence: str
    diagnostic_status: str

    channel_count: int
    replay_row_count: int
    board_row_count: int
    trade_row_count: int
    monotonic_check_count: int
    diagnostic_note_count: int

    evidence_trace_refs: Sequence[str] = field(default_factory=tuple)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)


def _coerce_snapshot(
    evidence: RealDataValidationEvidenceSummary | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(evidence, RealDataValidationEvidenceSummary):
        return real_data_validation_evidence_summary_to_snapshot(evidence)
    return dict(evidence)


def build_health_warroom_evidence_consumption_model(
    evidence: RealDataValidationEvidenceSummary | Mapping[str, Any],
) -> HealthWarRoomEvidenceConsumptionModel:
    snapshot = _coerce_snapshot(evidence)
    diagnostic_only = snapshot.get("diagnostic_evidence_only") is True
    read_only = snapshot.get("read_only_contract") is True
    note_count = int(snapshot.get("diagnostic_note_count") or 0)

    return HealthWarRoomEvidenceConsumptionModel(
        evidence_type=str(snapshot.get("evidence_type") or "real_data_validation_evidence_summary"),
        evidence_version=str(snapshot.get("evidence_version") or "unknown"),
        consumer_model_version="phase4a.health_warroom_evidence_consumption.v1",
        source_kind=str(snapshot.get("source_kind") or "unknown"),
        market_uid=str(snapshot.get("market_uid") or "unknown"),
        exchange=str(snapshot.get("exchange") or "unknown"),
        symbol=str(snapshot.get("symbol") or "unknown"),
        validation_phase=str(snapshot.get("validation_phase") or "unknown"),
        sample_window_label=str(snapshot.get("sample_window_label") or "unknown"),
        health_consumption_status="read_only_diagnostic_observer" if read_only and diagnostic_only else "untrusted_evidence_boundary",
        warroom_consumption_status="read_only_operator_support" if read_only and diagnostic_only else "untrusted_evidence_boundary",
        evidence_presence="present" if snapshot else "missing",
        diagnostic_status="clean" if note_count == 0 else "has_diagnostic_notes",
        channel_count=int(snapshot.get("channel_count") or 0),
        replay_row_count=int(snapshot.get("replay_row_count") or 0),
        board_row_count=int(snapshot.get("board_row_count") or 0),
        trade_row_count=int(snapshot.get("trade_row_count") or 0),
        monotonic_check_count=int(snapshot.get("monotonic_check_count") or 0),
        diagnostic_note_count=note_count,
        evidence_trace_refs=tuple(snapshot.get("evidence_trace_refs") or ()),
        diagnostics={
            "builder_type": "health_warroom_evidence_consumption_model",
            "builder_stage": "read_only_consumer_skeleton",
            "read_only_consumption": True,
            "diagnostic_evidence_only": diagnostic_only,
            "operator_support_only": True,
            "not_runtime_signal": True,
            "not_runtime_wiring": True,
            "not_ui_rendering": True,
            "not_market_engine_input": True,
            "not_collector_writer": True,
            "not_broker_or_order_automation": True,
            "not_inference_or_training": True,
        },
    )


def health_warroom_evidence_consumption_model_to_snapshot(
    model: HealthWarRoomEvidenceConsumptionModel,
) -> dict[str, Any]:
    return {
        "evidence_type": model.evidence_type,
        "evidence_version": model.evidence_version,
        "consumer_model_version": model.consumer_model_version,
        "source_kind": model.source_kind,
        "market_uid": model.market_uid,
        "exchange": model.exchange,
        "symbol": model.symbol,
        "validation_phase": model.validation_phase,
        "sample_window_label": model.sample_window_label,
        "health_consumption_status": model.health_consumption_status,
        "warroom_consumption_status": model.warroom_consumption_status,
        "evidence_presence": model.evidence_presence,
        "diagnostic_status": model.diagnostic_status,
        "channel_count": model.channel_count,
        "replay_row_count": model.replay_row_count,
        "board_row_count": model.board_row_count,
        "trade_row_count": model.trade_row_count,
        "monotonic_check_count": model.monotonic_check_count,
        "diagnostic_note_count": model.diagnostic_note_count,
        "evidence_trace_refs": list(model.evidence_trace_refs),
        "diagnostics": dict(model.diagnostics),
        "snapshot_stage": "health_warroom_evidence_consumption_read_only_snapshot",
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
    }

def health_warroom_evidence_consumption_status_payload(
    model_or_evidence: HealthWarRoomEvidenceConsumptionModel | RealDataValidationEvidenceSummary | Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Return a layout-free, read-only Health/WarRoom evidence status payload."""
    if model_or_evidence is None:
        return {
            "payload_kind": "health_warroom_evidence_consumption_status",
            "payload_version": "phase4a.health_warroom_evidence_consumption_status.v1",
            "evidence_presence": "missing",
            "health_consumption_status": "missing",
            "warroom_consumption_status": "missing",
            "diagnostic_status": "unknown",
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
        }

    if isinstance(model_or_evidence, HealthWarRoomEvidenceConsumptionModel):
        model = model_or_evidence
    else:
        model = build_health_warroom_evidence_consumption_model(model_or_evidence)

    snapshot = health_warroom_evidence_consumption_model_to_snapshot(model)
    return {
        "payload_kind": "health_warroom_evidence_consumption_status",
        "payload_version": "phase4a.health_warroom_evidence_consumption_status.v1",
        "consumer_model_version": model.consumer_model_version,
        "evidence_type": model.evidence_type,
        "evidence_version": model.evidence_version,
        "source_kind": model.source_kind,
        "market_uid": model.market_uid,
        "exchange": model.exchange,
        "symbol": model.symbol,
        "validation_phase": model.validation_phase,
        "sample_window_label": model.sample_window_label,
        "health_consumption_status": model.health_consumption_status,
        "warroom_consumption_status": model.warroom_consumption_status,
        "evidence_presence": model.evidence_presence,
        "diagnostic_status": model.diagnostic_status,
        "counts": {
            "channel_count": model.channel_count,
            "replay_row_count": model.replay_row_count,
            "board_row_count": model.board_row_count,
            "trade_row_count": model.trade_row_count,
            "monotonic_check_count": model.monotonic_check_count,
            "diagnostic_note_count": model.diagnostic_note_count,
        },
        "evidence_trace_refs": list(model.evidence_trace_refs),
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
        "snapshot_stage": snapshot.get("snapshot_stage"),
        "diagnostics": dict(model.diagnostics),
    }

