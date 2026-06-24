# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py
# desc: PS-Q18AK freshness/error fallback polish for latest_prediction_summary_widget auto-refresh display. UI-only fragment refresh companion; no runtime writes, AutoTrade, broker, parameter, or ledger behavior.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ak_freshness_error_fallback_panel.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_ACK = "PS_Q18AK_ADD_FRESHNESS_ERROR_FALLBACK_POLISH_TO_AUTO_REFRESH_DISPLAY_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_STATE = "auto_refresh_display_freshness_error_fallback_visible"
Q18AK_PAGE_ID = "warroom"
Q18AK_ZONE_ID = "prediction_overview_zone"
Q18AK_WIDGET_ID = "latest_prediction_summary_widget_freshness_error_fallback_panel"
Q18AK_REFRESH_MODE = "poll_normal"
Q18AK_DEFAULT_REFRESH_SEC = 5
FRESH_THRESHOLD_SEC = 900
DELAYED_THRESHOLD_SEC = 3600

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "freshness_error_fallback_panel_only",
    "q18aj_bounded_auto_refresh_panel_consumed",
    "auto_refresh_enabled",
    "fragment_slot_refresh_path_enabled",
    "partial_update_enabled",
    "freshness_monitor_enabled",
    "error_fallback_visible",
    "operator_safe_fallback_reason_codes_visible",
    "broad_page_reload_disabled",
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


def _parse_utc(value: str) -> datetime | None:
    text = _clean(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _now_utc(value: str | None = None) -> datetime:
    parsed = _parse_utc(value or "")
    if parsed is not None:
        return parsed
    return datetime.now(timezone.utc)


def _freshness_state(age_sec: int | None) -> str:
    if age_sec is None:
        return "unknown"
    if age_sec <= FRESH_THRESHOLD_SEC:
        return "fresh"
    if age_sec <= DELAYED_THRESHOLD_SEC:
        return "delayed"
    return "stale"


def _fallback_reasons(*, q18aj_ok: bool, generated_at: str, age_sec: int | None, state: str) -> list[str]:
    reasons: list[str] = []
    if not q18aj_ok:
        reasons.append("auto_refresh_source_packet_not_ok")
    if not generated_at:
        reasons.append("source_generated_at_missing")
    if age_sec is None:
        reasons.append("source_generated_at_unparseable")
    if state == "delayed":
        reasons.append("source_generated_at_delayed")
    if state == "stale":
        reasons.append("source_generated_at_stale")
    if not reasons:
        reasons.append("source_freshness_ok")
    return reasons


def build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
    *,
    supplied_q18aj_bounded_auto_refresh_packet: Mapping[str, Any] | Any | None = None,
    now_utc: str | None = None,
    fragment_supported: bool = True,
    ui_auto_refresh: bool = True,
) -> dict[str, Any]:
    source = _as_mapping(supplied_q18aj_bounded_auto_refresh_packet)
    if not source:
        source = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(
            fragment_supported=fragment_supported,
            ui_auto_refresh=ui_auto_refresh,
        )
    generated_at = _clean(source.get("component_source_generated_at"))
    source_dt = _parse_utc(generated_at)
    observed_now = _now_utc(now_utc)
    age_sec: int | None = None
    if source_dt is not None:
        age_sec = max(0, int((observed_now - source_dt).total_seconds()))
    state = _freshness_state(age_sec)
    q18aj_ok = source.get("ok") is True
    reasons = _fallback_reasons(q18aj_ok=q18aj_ok, generated_at=generated_at, age_sec=age_sec, state=state)
    failures: list[str] = []
    if not q18aj_ok:
        failures.append("q18aj_bounded_auto_refresh_packet_not_ok")
    if source.get("auto_refresh_enabled") is not True:
        failures.append("q18aj_auto_refresh_not_enabled")
    if source.get("fragment_slot_refresh_path_enabled") is not True:
        failures.append("q18aj_fragment_slot_refresh_not_enabled")
    if source.get("broad_page_reload_disabled") is not True:
        failures.append("q18aj_broad_page_reload_not_disabled")
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed", "parameter_apply_allowed", "ledger_append_allowed"):
        if source.get(key) is not False:
            failures.append(f"q18aj_boundary_not_false:{key}")
    ok = bool(not failures and state != "unknown")
    packet: dict[str, Any] = {
        "ok": ok,
        "freshness_panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_VERSION,
        "freshness_panel_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_ACK,
        "freshness_panel_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_STATE if ok else "freshness_error_fallback_panel_blocked_or_unknown",
        "source_q18aj_bounded_auto_refresh_ready": q18aj_ok,
        "component_source_generated_at": generated_at,
        "observed_now_utc": observed_now.isoformat().replace("+00:00", "Z"),
        "source_age_sec": age_sec,
        "freshness_state": state,
        "fresh_threshold_sec": FRESH_THRESHOLD_SEC,
        "delayed_threshold_sec": DELAYED_THRESHOLD_SEC,
        "stale_source_warning_visible": state in {"delayed", "stale", "unknown"},
        "safe_fallback_reason_codes": reasons,
        "fallback_reason_count": len(reasons),
        "auto_refresh_enabled": source.get("auto_refresh_enabled") is True,
        "fragment_slot_refresh_path_enabled": source.get("fragment_slot_refresh_path_enabled") is True,
        "partial_update_enabled": source.get("partial_update_enabled") is True,
        "broad_page_reload_disabled": True,
        "refresh_mode": _clean(source.get("refresh_mode")) or Q18AK_REFRESH_MODE,
        "refresh_interval_sec": int(source.get("refresh_interval_sec") or Q18AK_DEFAULT_REFRESH_SEC),
        "page_id": Q18AK_PAGE_ID,
        "zone_id": Q18AK_ZONE_ID,
        "widget_id": Q18AK_WIDGET_ID,
        "panel_failures": failures,
        "operator_caption": "PS-Q18AK shows freshness and safe fallback reasons for the automatically refreshed latest prediction display. This is UI-only; trading/runtime behavior remains disabled.",
        "recommended_next_slice": "intermediate-goal close docs or UI smoke/manual visual check; keep AutoTrade, broker, parameter, ledger, and runtime writes disabled.",
    }
    packet.update({key: ok for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["read_only"] = True
    packet["non_executing"] = True
    packet["display_only"] = True
    packet["freshness_monitor_enabled"] = True
    packet["error_fallback_visible"] = True
    packet["operator_safe_fallback_reason_codes_visible"] = True
    packet["broad_page_reload_disabled"] = True
    return packet


def latest_prediction_summary_widget_q18ak_display_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        {"item": "freshness_state", "value": _clean(data.get("freshness_state")), "note": "fresh / delayed / stale / unknown"},
        {"item": "source_age_sec", "value": _clean(data.get("source_age_sec")), "note": "Age from component_source_generated_at to observed_now_utc."},
        {"item": "component_source_generated_at", "value": _clean(data.get("component_source_generated_at")), "note": "Latest prediction timestamp currently visible in WarRoom."},
        {"item": "observed_now_utc", "value": _clean(data.get("observed_now_utc")), "note": "UI observation time for freshness display."},
        {"item": "safe_fallback_reason_codes", "value": ", ".join(str(item) for item in data.get("safe_fallback_reason_codes") or []), "note": "Operator-visible fallback reasons; no execution behavior."},
        {"item": "auto_refresh_enabled", "value": _clean(data.get("auto_refresh_enabled")), "note": "WarRoom display auto-refresh remains enabled."},
        {"item": "broad_page_reload", "value": "false", "note": "Fragment path only; broad page reload remains disabled."},
        {"item": "autotrade_broker", "value": "false", "note": "AutoTrade and broker APIs remain disabled."},
    ]


def _render_q18ak_body() -> dict[str, Any]:
    packet = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        fragment_supported=live_shell.supports_streamlit_fragment(),
        ui_auto_refresh=True,
    )
    st.caption(str(packet.get("operator_caption") or "PS-Q18AK freshness/error fallback panel"))
    st.caption(
        "freshness={state} / age={age}s / fallback={reasons} / auto_refresh={auto} / writes=false / autotrade=false / broker=false".format(
            state=packet.get("freshness_state"),
            age=packet.get("source_age_sec"),
            reasons=packet.get("safe_fallback_reason_codes"),
            auto=packet.get("auto_refresh_enabled"),
        )
    )
    rows = latest_prediction_summary_widget_q18ak_display_rows(packet)
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    return packet


def render_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel(
    *,
    fragment_enabled: bool = True,
) -> Mapping[str, Any]:
    packet_holder: dict[str, Any] = {}

    def _render_body() -> None:
        packet_holder.update(_render_q18ak_body())

    meta = live_shell.make_slot_meta(
        Q18AK_PAGE_ID,
        Q18AK_ZONE_ID,
        Q18AK_WIDGET_ID,
        label="Latest prediction freshness / fallback",
        tone="primary",
        help_text="Freshness and safe fallback display for the auto-refreshed latest prediction panel. No AutoTrade, broker, parameter, ledger, or runtime writes.",
        refresh_mode=Q18AK_REFRESH_MODE,
        priority=19,
        overlay_enabled=False,
        partial_update_enabled=True,
    )
    live_shell.render_fragment_slot(
        meta,
        _render_body,
        enabled=bool(fragment_enabled),
        default_sec=Q18AK_DEFAULT_REFRESH_SEC,
    )
    return packet_holder or build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        fragment_supported=live_shell.supports_streamlit_fragment(),
        ui_auto_refresh=bool(fragment_enabled),
    )
