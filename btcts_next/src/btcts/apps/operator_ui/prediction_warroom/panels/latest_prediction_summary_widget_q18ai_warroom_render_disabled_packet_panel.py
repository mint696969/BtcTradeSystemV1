# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel.py
# desc: PS-Q18AI WarRoom mount panel for latest_prediction_summary_widget render-disabled packet status/value rows. No refresh, real widget render, runtime writes, AutoTrade, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

import streamlit as st

from btcts.apps.operator_ui.prediction_warroom.mapping.latest_prediction_summary_widget_q18ah_render_disabled_packet_builder_validation import (
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18ah_render_disabled_packet_rows import (
    build_latest_prediction_summary_widget_q18ah_render_disabled_packet_result_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AI_WARROOM_PANEL_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ai_warroom_render_disabled_packet_panel.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AI_WARROOM_PANEL_ACK = "PS_Q18AI_MOUNT_WARROOM_RENDER_DISABLED_PACKET_STATUS_VALUE_PANEL_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AI_WARROOM_PANEL_STATE = "warroom_render_disabled_packet_status_value_panel_mounted_refresh_disabled"

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "warroom_render_disabled_packet_panel_only",
    "q18ah_render_disabled_packet_validation_consumed",
    "component_packet_valid",
    "component_packet_render_disabled",
    "warroom_page_mutation_allowed_for_this_slice",
    "warroom_import_mutation_allowed_for_this_slice",
    "warroom_body_call_allowed_for_this_slice",
    "warroom_display_mount_allowed",
    "warroom_display_mounted",
    "status_value_rows_ready",
)

FALSE_BOUNDARIES = (
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "payload_reparse_allowed",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "refresh_invocation_allowed",
    "auto_refresh_enabled",
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


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def latest_prediction_summary_widget_q18ai_display_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    rows: list[dict[str, Any]] = []
    for item in data.get("render_disabled_packet_rows") or []:
        row = _as_mapping(item)
        rows.append(
            {
                "item": row.get("render_disabled_packet_item"),
                "value": row.get("value"),
                "state": row.get("state"),
                "note": row.get("operator_note"),
                "real_widget_render": "false",
                "refresh": "false",
                "runtime_write": "false",
                "autotrade": "false",
                "broker": "false",
            }
        )
    return rows


def build_latest_prediction_summary_widget_q18ai_warroom_panel_packet(
    *,
    supplied_q18ah_render_disabled_packet_result: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    source = _as_mapping(supplied_q18ah_render_disabled_packet_result)
    if not source:
        source = build_latest_prediction_summary_widget_q18ah_render_disabled_packet_result_packet(
            execute_packet_builder_validation=True,
            explicit_ack=LATEST_PREDICTION_SUMMARY_WIDGET_Q18AH_RENDER_DISABLED_PACKET_BUILDER_VALIDATION_ACK,
        )
    display_rows = latest_prediction_summary_widget_q18ai_display_rows(source)
    failures: list[str] = []
    if source.get("ok") is not True:
        failures.append("q18ah_render_disabled_packet_result_not_ok")
    if source.get("component_packet_valid") is not True:
        failures.append("component_packet_not_valid")
    if source.get("component_packet_render_disabled") is not True:
        failures.append("component_packet_not_render_disabled")
    if source.get("render_disabled_packet_row_count") != 12:
        failures.append("q18ah_render_disabled_packet_row_count_mismatch")
    if len(display_rows) != 12:
        failures.append("q18ai_display_row_count_mismatch")
    for key in ("streamlit_render_invoked", "real_prediction_widget_render_invoked", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
        if source.get(key) is not False:
            failures.append(f"q18ah_boundary_not_false:{key}")
    ok = not failures
    packet: dict[str, Any] = {
        "ok": ok,
        "warroom_panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AI_WARROOM_PANEL_VERSION,
        "warroom_panel_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AI_WARROOM_PANEL_ACK,
        "warroom_panel_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AI_WARROOM_PANEL_STATE if ok else "warroom_render_disabled_packet_panel_blocked",
        "q18ah_render_disabled_packet_ready": source.get("ok") is True,
        "component_packet_valid": source.get("component_packet_valid") is True,
        "component_packet_render_disabled": source.get("component_packet_render_disabled") is True,
        "component_packet_state": _clean(source.get("component_packet_state")),
        "component_source_generated_at": _clean(source.get("component_source_generated_at")),
        "mapped_record_count": int(source.get("mapped_record_count") or 0),
        "display_row_count": len(display_rows),
        "display_rows": display_rows,
        "panel_failures": failures,
        "operator_caption": "PS-Q18AI mounts latest prediction summary render-disabled packet status/value rows in WarRoom. Refresh and real widget rendering remain disabled.",
        "recommended_next_slice": "bounded auto-refresh runner/panel for latest prediction packet; keep AutoTrade, broker, parameter, ledger, and runtime writes disabled.",
    }
    packet.update({key: ok for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["read_only"] = True
    packet["non_executing"] = True
    packet["display_only"] = True
    packet["warroom_render_disabled_packet_panel_only"] = True
    packet["warroom_page_mutation_allowed_for_this_slice"] = True
    packet["warroom_import_mutation_allowed_for_this_slice"] = True
    packet["warroom_body_call_allowed_for_this_slice"] = True
    packet["warroom_display_mount_allowed"] = True
    packet["warroom_display_mounted"] = ok
    return packet


def render_latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel(
    *,
    supplied_q18ah_render_disabled_packet_result: Mapping[str, Any] | Any | None = None,
) -> Mapping[str, Any]:
    packet = build_latest_prediction_summary_widget_q18ai_warroom_panel_packet(
        supplied_q18ah_render_disabled_packet_result=supplied_q18ah_render_disabled_packet_result,
    )
    st.caption(str(packet.get("operator_caption") or "PS-Q18AI WarRoom render-disabled packet panel"))
    st.caption(
        "render_disabled_rows={rows} / component_state={state} / generated_at={generated_at} / real_render=false / refresh=false".format(
            rows=packet.get("display_row_count"),
            state=packet.get("component_packet_state"),
            generated_at=packet.get("component_source_generated_at"),
        )
    )
    rows = list(packet.get("display_rows") or [])
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    return packet
