# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/presenters/latest_prediction_summary_widget_q18aa_mount_preflight_gate_rows.py
# desc: PS-Q18AA pure-data presenter rows for latest_prediction_summary_widget WarRoom mount preflight gate. No Streamlit import and no source access.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18aa_mount_preflight_gate import (
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_KIND,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_STATE,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18aa_mount_preflight_gate_contract,
)

Q18AA_PREFLIGHT_GATE_ROW_ITEMS = (
    "mount_preflight_gate_kind",
    "mount_preflight_gate_state",
    "source_display_packet_ready",
    "display_packet_row_count",
    "selected_candidate_generated_at",
    "selected_candidate_source_artifact_ref",
    "selected_candidate_market_uid",
    "path_shape_preview",
    "safe_display_mount_candidate",
    "preflight_gate_decision",
    "explicit_mount_preflight_gate_ack",
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
        "mount_preflight_gate_item": item,
        "value": _clean(value),
        "state": "declared" if _clean(value) else "not_supplied",
        "operator_note": note,
    }
    row.update({key: True for key in TRUE_BOUNDARIES})
    row.update({key: False for key in FALSE_BOUNDARIES})
    return row


def build_latest_prediction_summary_widget_q18aa_mount_preflight_gate_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        _row("mount_preflight_gate_kind", LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_KIND, "Q18AA gate kind; not a mount or render permission."),
        _row("mount_preflight_gate_state", LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_STATE, "Preflight gate is ready but mount remains disabled."),
        _row("source_display_packet_ready", data.get("source_display_packet_ready"), "Q18Z display packet was consumed as source."),
        _row("display_packet_row_count", data.get("display_packet_row_count"), "Q18Z display packet row count must stay 12."),
        _row("selected_candidate_generated_at", data.get("selected_candidate_generated_at"), "Candidate timestamp copied from Q18Z report."),
        _row("selected_candidate_source_artifact_ref", data.get("selected_candidate_source_artifact_ref"), "Source artifact ref remains text only and unresolved."),
        _row("selected_candidate_market_uid", data.get("selected_candidate_market_uid"), "Market uid copied from Q18Z report."),
        _row("path_shape_preview", data.get("path_shape_preview"), "Path shape remains a string preview only."),
        _row("safe_display_mount_candidate", data.get("safe_display_mount_candidate"), "A later slice may mount a display-only panel after explicit approval."),
        _row("preflight_gate_decision", data.get("preflight_gate_decision"), "Decision keeps WarRoom page mutation, mount, render, checks, reads, refresh, and writes deferred."),
        _row("explicit_mount_preflight_gate_ack", LATEST_PREDICTION_SUMMARY_WIDGET_Q18AA_MOUNT_PREFLIGHT_GATE_ACK, "Acknowledgement is not approval for warroom_page mutation, Streamlit rendering, filesystem checks, source reads, or refresh."),
        _row("deferred_runtime_boundary", "page_mutation=false; mount=false; render=false; exists_check=false; schema_check=false; actual_read=false; refresh=false; writes=false", "Runtime behavior remains deferred to later guarded slices."),
    ]


def build_latest_prediction_summary_widget_q18aa_mount_preflight_gate_packet(*, supplied_q18z_display_packet_report: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    contract = build_latest_prediction_summary_widget_q18aa_mount_preflight_gate_contract(supplied_q18z_display_packet_report=supplied_q18z_display_packet_report)
    rows = build_latest_prediction_summary_widget_q18aa_mount_preflight_gate_rows(contract) if contract.get("ok") is True else []
    failures: list[str] = list(contract.get("source_display_packet_failures") or [])
    if contract.get("ok") is True and len(rows) != len(Q18AA_PREFLIGHT_GATE_ROW_ITEMS):
        failures.append("q18aa_mount_preflight_gate_row_count_mismatch")
    for row in rows:
        item = str(row.get("mount_preflight_gate_item") or "")
        if item not in Q18AA_PREFLIGHT_GATE_ROW_ITEMS:
            failures.append(f"unexpected_q18aa_mount_preflight_gate_row:{item}")
        for key in TRUE_BOUNDARIES:
            if row.get(key) is not True:
                failures.append(f"row_true_boundary_missing:{item}:{key}")
        for key in FALSE_BOUNDARIES:
            if row.get(key) is not False:
                failures.append(f"row_false_boundary_not_false:{item}:{key}")
    packet = dict(contract)
    packet.update({
        "ok": contract.get("ok") is True and not failures,
        "mount_preflight_gate_row_count": len(rows),
        "mount_preflight_gate_rows": rows,
        "mount_preflight_gate_validation_failures": failures,
        "mount_preflight_gate_ready": contract.get("ok") is True and not failures,
    })
    return packet
