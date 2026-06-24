# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py
# desc: PS-Q18AJ bounded auto-refresh panel for latest_prediction_summary_widget WarRoom display. Uses Streamlit fragment slot refresh only; no broad page reload, runtime writes, AutoTrade, broker, parameter, or ledger behavior.

from __future__ import annotations

from typing import Any, Mapping

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel import (
    build_latest_prediction_summary_widget_q18ai_warroom_panel_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_BOUNDED_AUTO_REFRESH_PANEL_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18aj_bounded_auto_refresh_panel.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_BOUNDED_AUTO_REFRESH_PANEL_ACK = "PS_Q18AJ_ENABLE_BOUNDED_WARROOM_FRAGMENT_AUTO_REFRESH_FOR_LATEST_PREDICTION_DISPLAY_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_BOUNDED_AUTO_REFRESH_PANEL_STATE = "bounded_fragment_auto_refresh_enabled_for_latest_prediction_display_only"
Q18AJ_PAGE_ID = "warroom"
Q18AJ_ZONE_ID = "prediction_overview_zone"
Q18AJ_WIDGET_ID = "latest_prediction_summary_widget_bounded_auto_refresh_panel"
Q18AJ_REFRESH_MODE = "poll_normal"
Q18AJ_DEFAULT_REFRESH_SEC = 5

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "bounded_auto_refresh_panel_only",
    "q18ai_warroom_panel_consumed",
    "warroom_display_mounted",
    "status_value_rows_ready",
    "auto_refresh_enabled",
    "fragment_refresh_enabled",
    "fragment_slot_refresh_path_enabled",
    "partial_update_enabled",
    "broad_page_reload_disabled",
    "latest_prediction_display_refresh_target",
)

FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
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


def build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(
    *,
    supplied_q18ai_warroom_panel_packet: Mapping[str, Any] | Any | None = None,
    fragment_supported: bool = True,
    ui_auto_refresh: bool = True,
) -> dict[str, Any]:
    source = _as_mapping(supplied_q18ai_warroom_panel_packet)
    if not source:
        source = build_latest_prediction_summary_widget_q18ai_warroom_panel_packet()
    failures: list[str] = []
    if source.get("ok") is not True:
        failures.append("q18ai_warroom_panel_not_ok")
    if source.get("warroom_display_mounted") is not True:
        failures.append("q18ai_warroom_display_not_mounted")
    if source.get("display_row_count") != 12:
        failures.append("q18ai_display_row_count_mismatch")
    if source.get("real_prediction_widget_render_invoked") is not False:
        failures.append("q18ai_real_prediction_widget_render_invoked")
    if source.get("runtime_artifact_write_allowed") is not False:
        failures.append("q18ai_runtime_artifact_write_allowed")
    if source.get("autotrade_trigger_allowed") is not False:
        failures.append("q18ai_autotrade_trigger_allowed")
    if source.get("broker_private_api_allowed") is not False:
        failures.append("q18ai_broker_private_api_allowed")
    refresh_plan = live_shell.resolve_page_refresh_plan(
        page_key=Q18AJ_PAGE_ID,
        ui_auto_refresh=bool(ui_auto_refresh),
        ui_refresh_interval_sec=Q18AJ_DEFAULT_REFRESH_SEC,
        fragment_supported=bool(fragment_supported),
    )
    ok = bool(not failures and source and ui_auto_refresh and fragment_supported)
    packet: dict[str, Any] = {
        "ok": ok,
        "bounded_auto_refresh_panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_BOUNDED_AUTO_REFRESH_PANEL_VERSION,
        "bounded_auto_refresh_panel_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_BOUNDED_AUTO_REFRESH_PANEL_ACK,
        "bounded_auto_refresh_panel_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_BOUNDED_AUTO_REFRESH_PANEL_STATE if ok else "bounded_auto_refresh_panel_blocked",
        "source_q18ai_warroom_panel_ready": source.get("ok") is True,
        "warroom_display_mounted": source.get("warroom_display_mounted") is True,
        "status_value_rows_ready": source.get("status_value_rows_ready") is True,
        "display_row_count": int(source.get("display_row_count") or 0),
        "component_packet_state": _clean(source.get("component_packet_state")),
        "component_source_generated_at": _clean(source.get("component_source_generated_at")),
        "mapped_record_count": int(source.get("mapped_record_count") or 0),
        "fragment_supported": bool(fragment_supported),
        "ui_auto_refresh": bool(ui_auto_refresh),
        "refresh_mode": Q18AJ_REFRESH_MODE,
        "refresh_interval_sec": Q18AJ_DEFAULT_REFRESH_SEC,
        "page_id": Q18AJ_PAGE_ID,
        "zone_id": Q18AJ_ZONE_ID,
        "widget_id": Q18AJ_WIDGET_ID,
        "refresh_plan": dict(refresh_plan),
        "refresh_invocation_allowed": ok,
        "auto_refresh_enabled": ok,
        "fragment_refresh_enabled": ok,
        "fragment_slot_refresh_path_enabled": ok,
        "partial_update_enabled": ok,
        "broad_page_reload_disabled": True,
        "latest_prediction_display_refresh_target": ok,
        "panel_failures": failures,
        "operator_caption": "PS-Q18AJ enables bounded WarRoom fragment auto-refresh for the latest prediction display panel only. Runtime writes, AutoTrade, broker, parameter, and ledger behavior remain disabled.",
        "recommended_next_slice": "freshness/error fallback polish or close intermediate-goal guard; keep AutoTrade, broker, parameter, ledger, and runtime writes disabled.",
    }
    packet.update({key: ok for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["read_only"] = True
    packet["non_executing"] = True
    packet["display_only"] = True
    packet["broad_page_reload_disabled"] = True
    return packet


def latest_prediction_summary_widget_q18aj_display_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        {"item": "auto_refresh_enabled", "value": _clean(data.get("auto_refresh_enabled")), "note": "UI fragment auto-refresh for latest prediction display only."},
        {"item": "refresh_mode", "value": _clean(data.get("refresh_mode")), "note": "Bounded live_shell refresh mode."},
        {"item": "refresh_interval_sec", "value": _clean(data.get("refresh_interval_sec")), "note": "Refresh interval for this display fragment."},
        {"item": "component_source_generated_at", "value": _clean(data.get("component_source_generated_at")), "note": "Latest prediction source timestamp visible in refreshed panel."},
        {"item": "mapped_record_count", "value": _clean(data.get("mapped_record_count")), "note": "Mapped forecast_batch record count."},
        {"item": "broad_page_reload", "value": "false", "note": "Uses fragment slot path; parent-page reload remains disabled."},
        {"item": "real_widget_render", "value": "false", "note": "Real widget rendering remains disabled."},
        {"item": "autotrade_broker", "value": "false", "note": "AutoTrade and broker APIs remain disabled."},
    ]


def _render_q18aj_body() -> dict[str, Any]:
    packet = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet()
    st.caption(str(packet.get("operator_caption") or "PS-Q18AJ bounded auto-refresh panel"))
    st.caption(
        "auto_refresh={auto} / mode={mode} / interval={interval}s / generated_at={generated_at} / real_render=false / autotrade=false / broker=false".format(
            auto=packet.get("auto_refresh_enabled"),
            mode=packet.get("refresh_mode"),
            interval=packet.get("refresh_interval_sec"),
            generated_at=packet.get("component_source_generated_at"),
        )
    )
    rows = latest_prediction_summary_widget_q18aj_display_rows(packet)
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    return packet


def render_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel(
    *,
    fragment_enabled: bool = True,
) -> Mapping[str, Any]:
    packet_holder: dict[str, Any] = {}

    def _render_body() -> None:
        packet_holder.update(_render_q18aj_body())

    meta = live_shell.make_slot_meta(
        Q18AJ_PAGE_ID,
        Q18AJ_ZONE_ID,
        Q18AJ_WIDGET_ID,
        label="Latest prediction auto-refresh display",
        tone="primary",
        help_text="Bounded fragment refresh for the latest prediction display only. No AutoTrade, broker, parameter, ledger, or runtime writes.",
        refresh_mode=Q18AJ_REFRESH_MODE,
        priority=18,
        overlay_enabled=False,
        partial_update_enabled=True,
    )
    live_shell.render_fragment_slot(
        meta,
        _render_body,
        enabled=bool(fragment_enabled),
        default_sec=Q18AJ_DEFAULT_REFRESH_SEC,
    )
    return packet_holder or build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(
        fragment_supported=live_shell.supports_streamlit_fragment(),
        ui_auto_refresh=bool(fragment_enabled),
    )
