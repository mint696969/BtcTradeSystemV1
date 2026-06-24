# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ab_safe_display_mount_panel.py
# desc: PS-Q18AB safe WarRoom display mount panel for latest_prediction_summary_widget preflight rows only. No real widget render, source read, filesystem check, refresh, writes, AutoTrade, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

import streamlit as st

from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18z_display_packet import (
    FALSE_BOUNDARIES as Q18Z_FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_VERSION,
    TRUE_BOUNDARIES as Q18Z_TRUE_BOUNDARIES,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18aa_mount_preflight_gate_rows import (
    build_latest_prediction_summary_widget_q18aa_mount_preflight_gate_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ab_safe_display_mount_panel.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_ACK = "PS_Q18AB_MOUNT_SAFE_WARROOM_DISPLAY_PANEL_FOR_PREFLIGHT_ROWS_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_KIND = "safe_warroom_display_mount_panel_for_q18aa_preflight_rows"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_STATE = "mounted_read_only_preflight_rows_real_widget_render_disabled"

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "safe_display_mount_panel_only",
    "q18aa_mount_preflight_gate_consumed",
    "q18ab_safe_display_mount_panel_declared",
    "safe_display_mount_panel_mounted",
    "warroom_page_mutation_allowed_for_this_slice",
    "warroom_import_mutation_allowed_for_this_slice",
    "warroom_body_call_allowed_for_this_slice",
    "warroom_display_mount_allowed",
    "warroom_display_mounted",
    "source_candidate_count_fixed_to_one",
    "path_shape_preview_string_only",
)

FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed",
    "render_latest_prediction_summary_widget_invoked",
    "component_runtime_binding_allowed",
    "filesystem_existence_check_dry_run_result_available",
    "filesystem_existence_check_dry_run_execution_allowed",
    "filesystem_existence_check_dry_run_executed",
    "source_artifact_exists_check_allowed",
    "source_artifact_exists_checked",
    "source_artifact_exists_result_available",
    "source_artifact_schema_check_allowed",
    "source_artifact_schema_checked",
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "payload_reparse_allowed",
    "refresh_invocation_allowed",
    "scheduler_enabled",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_write_runtime_artifact",
    "would_send_to_broker",
)

EXPECTED_PATH_SHAPE_PREVIEW = "D:/btc_ts_hot/prediction_sources/BTC-USD/2026-06-22T00:00:00Z/latest_prediction.json"
EXPECTED_SELECTED = {
    "selected_candidate_generated_at": "2026-06-22T00:00:00Z",
    "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    "selected_candidate_market_uid": "BTC-USD",
}


def _q18z_fixture_display_packet_report() -> dict[str, Any]:
    report: dict[str, Any] = {
        "ok": True,
        "display_packet_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_VERSION,
        "display_packet_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK,
        "display_packet_kind": LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND,
        "display_packet_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE,
        "display_packet_row_count": 12,
        "source_candidate_count": 1,
        "path_shape_preview": EXPECTED_PATH_SHAPE_PREVIEW,
        **EXPECTED_SELECTED,
    }
    report.update({key: True for key in Q18Z_TRUE_BOUNDARIES})
    report.update({key: False for key in Q18Z_FALSE_BOUNDARIES})
    return report


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet(
    *,
    supplied_q18aa_mount_preflight_gate_packet: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    q18aa_packet = _as_mapping(supplied_q18aa_mount_preflight_gate_packet)
    if not q18aa_packet:
        q18aa_packet = build_latest_prediction_summary_widget_q18aa_mount_preflight_gate_packet(
            supplied_q18z_display_packet_report=_q18z_fixture_display_packet_report(),
        )
    rows = list(q18aa_packet.get("mount_preflight_gate_rows") or [])
    failures: list[str] = []
    if q18aa_packet.get("ok") is not True:
        failures.append("q18aa_mount_preflight_gate_not_ok")
    if q18aa_packet.get("mount_preflight_gate_row_count") != 12:
        failures.append("q18aa_mount_preflight_gate_row_count_mismatch")
    if q18aa_packet.get("safe_display_mount_candidate") is not True:
        failures.append("q18aa_safe_display_mount_candidate_not_true")
    if q18aa_packet.get("warroom_display_mount_allowed") is not False:
        failures.append("q18aa_source_should_not_have_mounted_yet")
    if q18aa_packet.get("actual_source_read_invoked") is not False:
        failures.append("q18aa_actual_source_read_invoked")
    if q18aa_packet.get("streamlit_render_invoked") is not False:
        failures.append("q18aa_streamlit_render_invoked")
    for row in rows:
        row_data = _as_mapping(row)
        if row_data.get("actual_source_read_invoked") is not False:
            failures.append("row_actual_source_read_invoked")
        if row_data.get("streamlit_render_invoked") is not False:
            failures.append("row_streamlit_render_invoked")
        if row_data.get("real_prediction_widget_rendering_allowed") is not False:
            failures.append("row_real_prediction_widget_rendering_allowed")
    packet: dict[str, Any] = {
        "ok": not failures,
        "safe_display_mount_panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_VERSION,
        "safe_display_mount_panel_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_ACK,
        "safe_display_mount_panel_kind": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_KIND,
        "safe_display_mount_panel_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_STATE,
        "q18aa_mount_preflight_gate_ready": q18aa_packet.get("ok") is True,
        "q18aa_mount_preflight_gate_row_count": int(q18aa_packet.get("mount_preflight_gate_row_count") or 0),
        "display_packet_row_count": int(q18aa_packet.get("display_packet_row_count") or 0),
        "source_candidate_count": int(q18aa_packet.get("source_candidate_count") or 0),
        "safe_display_mount_panel_row_count": len(rows),
        "safe_display_mount_panel_rows": rows,
        "safe_display_mount_panel_failures": failures,
        "path_shape_preview": str(q18aa_packet.get("path_shape_preview") or ""),
        "selected_candidate_generated_at": str(q18aa_packet.get("selected_candidate_generated_at") or ""),
        "selected_candidate_source_artifact_ref": str(q18aa_packet.get("selected_candidate_source_artifact_ref") or ""),
        "selected_candidate_market_uid": str(q18aa_packet.get("selected_candidate_market_uid") or ""),
        "operator_caption": "PS-Q18AB mounts a read-only WarRoom panel for Q18AA preflight rows only; real prediction widget rendering and D-hot source reads remain disabled.",
        "recommended_next_slice": "filesystem exists-check execution; keep schema validation, actual D-hot read, real widget render, refresh, AutoTrade, broker, and parameter apply deferred unless explicitly approved.",
    }
    packet.update({key: True for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    return packet


def latest_prediction_summary_widget_q18ab_safe_display_mount_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    rows: list[dict[str, Any]] = []
    for item in list(data.get("safe_display_mount_panel_rows") or []):
        row = _as_mapping(item)
        rows.append(
            {
                "item": row.get("mount_preflight_gate_item"),
                "value": row.get("value"),
                "state": row.get("state"),
                "note": row.get("operator_note"),
                "real_widget_render": "false",
                "actual_source_read": "false",
                "refresh": "false",
                "runtime_write": "false",
                "autotrade": "false",
                "broker": "false",
            }
        )
    return rows


def render_latest_prediction_summary_widget_q18ab_safe_display_mount_panel(
    *,
    supplied_q18aa_mount_preflight_gate_packet: Mapping[str, Any] | Any | None = None,
) -> Mapping[str, Any]:
    packet = build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet(
        supplied_q18aa_mount_preflight_gate_packet=supplied_q18aa_mount_preflight_gate_packet,
    )
    st.caption(str(packet.get("operator_caption") or "PS-Q18AB safe display mount panel"))
    st.caption(
        "safe_mount_rows={rows} / q18aa_gate_rows={gate_rows} / actual_source_read=false / real_widget_render=false / refresh=false".format(
            rows=packet.get("safe_display_mount_panel_row_count"),
            gate_rows=packet.get("q18aa_mount_preflight_gate_row_count"),
        )
    )
    rows = latest_prediction_summary_widget_q18ab_safe_display_mount_rows(packet)
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    return packet
