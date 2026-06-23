# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18z_display_rows.py
# desc: PS-Q18Z pure-data presenter rows for latest_prediction_summary_widget display packet. No Streamlit import and no source access.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18z_display_packet import (
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18z_display_packet_contract,
)

Q18Z_DISPLAY_ROW_ITEMS = (
    "display_packet_kind",
    "display_packet_state",
    "widget_family_id",
    "source_packet_id",
    "selected_candidate_generated_at",
    "selected_candidate_source_artifact_ref",
    "selected_candidate_market_uid",
    "path_shape_preview",
    "source_display_contract_ready",
    "display_packet_decision",
    "explicit_display_packet_ack",
    "deferred_runtime_boundary",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _row(item: str, value: Any, note: str) -> dict[str, Any]:
    row = {
        "display_packet_item": item,
        "value": _clean(value),
        "state": "declared" if _clean(value) else "not_supplied",
        "operator_note": note,
    }
    row.update({key: True for key in TRUE_BOUNDARIES})
    row.update({key: False for key in FALSE_BOUNDARIES})
    return row


def build_latest_prediction_summary_widget_q18z_display_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        _row("display_packet_kind", LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND, "Q18Z display packet kind; not a mount or render permission."),
        _row("display_packet_state", LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE, "Display packet is declared only."),
        _row("widget_family_id", data.get("widget_family_id"), "Scoped to latest_prediction_summary_widget."),
        _row("source_packet_id", data.get("source_packet_id"), "Scoped to latest prediction source packet."),
        _row("selected_candidate_generated_at", data.get("selected_candidate_generated_at"), "Candidate timestamp copied from Q18Y report."),
        _row("selected_candidate_source_artifact_ref", data.get("selected_candidate_source_artifact_ref"), "Source artifact ref remains text only and unresolved."),
        _row("selected_candidate_market_uid", data.get("selected_candidate_market_uid"), "Market uid copied from Q18Y report."),
        _row("path_shape_preview", data.get("path_shape_preview"), "Path shape is a string preview only; no path materialization."),
        _row("source_display_contract_ready", data.get("source_display_contract_ready"), "Q18Y display contract was consumed as source contract."),
        _row("display_packet_decision", data.get("display_packet_decision"), "Decision keeps mount/render/read/check/write behavior deferred."),
        _row("explicit_display_packet_ack", LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK, "Acknowledgement is not approval for filesystem checks, source reads, or rendering."),
        _row("deferred_runtime_boundary", "mount=false; render=false; exists_check=false; schema_check=false; actual_read=false; refresh=false; writes=false", "Runtime behavior remains deferred to later guarded slices."),
    ]


def build_latest_prediction_summary_widget_q18z_display_packet(*, supplied_q18y_display_contract_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    contract = build_latest_prediction_summary_widget_q18z_display_packet_contract(supplied_q18y_display_contract_report=supplied_q18y_display_contract_report)
    rows = build_latest_prediction_summary_widget_q18z_display_rows(contract) if contract.get("ok") is True else []
    failures: list[str] = list(contract.get("source_display_contract_failures") or [])
    if contract.get("ok") is True and len(rows) != len(Q18Z_DISPLAY_ROW_ITEMS):
        failures.append("q18z_display_row_count_mismatch")
    for row in rows:
        item = str(row.get("display_packet_item") or "")
        if item not in Q18Z_DISPLAY_ROW_ITEMS:
            failures.append(f"unexpected_q18z_display_row:{item}")
        for key in TRUE_BOUNDARIES:
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in FALSE_BOUNDARIES:
            if row.get(key) is not False:
                failures.append(f"row_false_boundary_not_false:{item}:{key}")
    packet = dict(contract)
    packet.update(
        {
            "ok": contract.get("ok") is True and not failures,
            "display_packet_row_count": len(rows),
            "display_packet_rows": rows,
            "display_packet_validation_failures": failures,
            "display_packet_ready": contract.get("ok") is True and not failures,
        }
    )
    return packet
