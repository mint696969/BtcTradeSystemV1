# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py
# desc: PS-Q19D display-only WarRoom panel for the PS-Q19C latest prediction read model. Streamlit presentation only; no runtime/status/prediction writes, scheduler, AutoTrade, broker, ledger, or parameter behavior.

from __future__ import annotations

from typing import Any, Mapping

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
    load_latest_prediction_warroom_read_model,
)

LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_VERSION = "prediction_warroom.latest_prediction_warroom_display_panel.ps_q19d.v1"
LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_STATE = "warroom_realtime_prediction_display_only_panel_mounted"
Q19D_PAGE_ID = "warroom"
Q19D_ZONE_ID = "prediction_overview_zone"
Q19D_WIDGET_ID = "latest_prediction_warroom_read_model_display_panel"
Q19D_REFRESH_MODE = "poll_normal"
Q19D_REFRESH_SEC = 5

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "warroom_realtime_prediction_widget_display_only",
    "ps_q19c_read_model_consumed",
    "streamlit_display_panel_render_allowed",
    "warroom_display_panel_mounted",
    "fragment_slot_refresh_path_enabled",
    "operator_visible_prediction_rows",
    "operator_visible_market_snapshot",
    "operator_visible_safety_flags",
)

FALSE_BOUNDARIES = (
    "component_runtime_binding_allowed",
    "real_prediction_component_render_invoked",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "prediction_artifact_write_allowed",
    "view_artifact_write_allowed",
    "scheduler_enabled",
    "producer_enabled",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_write_runtime_artifact",
    "would_write_status_artifact",
    "would_write_prediction_artifact",
    "would_write_warroom_view_artifact",
    "would_send_to_broker",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _format_score(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except Exception:
        return "-"


def _bool_text(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return _clean(value) or "-"


def latest_prediction_warroom_display_rows(read_model: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    model = _as_mapping(read_model)
    selected = _as_mapping(model.get("selected_records_by_horizon"))
    rows: list[dict[str, Any]] = []
    for horizon_key in [str(item) for item in model.get("selected_horizon_sec") or []]:
        horizon_rows = selected.get(horizon_key) or []
        if not isinstance(horizon_rows, list):
            continue
        for item in horizon_rows:
            row = _as_mapping(item)
            rows.append(
                {
                    "horizon": f"{horizon_key}s",
                    "family": _clean(row.get("family")) or "-",
                    "label": _clean(row.get("primary_label")) or "-",
                    "confidence": _clean(row.get("confidence")) or "-",
                    "score": _format_score(row.get("score")),
                    "usable": _bool_text(row.get("usable")),
                    "warnings": ",".join(str(v) for v in (row.get("warnings") or [])[:2]),
                    "drivers": ",".join(str(v) for v in (row.get("drivers") or [])[:2]),
                }
            )
    return rows


def latest_prediction_warroom_safety_rows(read_model: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    model = _as_mapping(read_model)
    safety = _as_mapping(model.get("safety_flags"))
    return [
        {"item": "read_model_ok", "value": _bool_text(model.get("ok")), "note": "PS-Q19C read model status."},
        {"item": "freshness_state", "value": _clean(model.get("freshness_state")) or "-", "note": "fresh / delayed / stale / unknown."},
        {"item": "age_sec", "value": _clean(model.get("age_sec")) or "-", "note": "Age of latest prediction artifact."},
        {"item": "record_count", "value": _clean(model.get("record_count")) or "0", "note": "forecast_batch record count."},
        {"item": "records_all_safe", "value": _bool_text(safety.get("records_all_safe")), "note": "All displayed records remain read-only/non-executing/no broker/no writes."},
        {"item": "view_artifact_write_allowed", "value": "false", "note": "Declared WarRoom view artifact is not written in PS-Q19D."},
        {"item": "autotrade_broker", "value": "false", "note": "No AutoTrade trigger and no broker/private API."},
    ]


def latest_prediction_warroom_market_rows(read_model: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    model = _as_mapping(read_model)
    market = _as_mapping(model.get("market_snapshot"))
    return [
        {"item": "market_uid", "value": _clean(market.get("market_uid")) or "-"},
        {"item": "freshness", "value": _clean(market.get("freshness")) or "UNKNOWN"},
        {"item": "trust_state", "value": _clean(market.get("trust_state")) or "-"},
        {"item": "continuity_state", "value": _clean(market.get("continuity_state")) or "-"},
        {"item": "interpretation_bucket", "value": _clean(market.get("interpretation_bucket")) or "-"},
        {"item": "best_bid", "value": _clean(market.get("best_bid")) or "-"},
        {"item": "best_ask", "value": _clean(market.get("best_ask")) or "-"},
        {"item": "spread", "value": _clean(market.get("spread")) or "-"},
    ]


def build_latest_prediction_warroom_display_panel_packet(
    *,
    read_model: Mapping[str, Any] | Any | None = None,
    fragment_enabled: bool = True,
) -> dict[str, Any]:
    model = dict(_as_mapping(read_model)) if read_model is not None else load_latest_prediction_warroom_read_model()
    prediction_rows = latest_prediction_warroom_display_rows(model)
    safety_rows = latest_prediction_warroom_safety_rows(model)
    market_rows = latest_prediction_warroom_market_rows(model)
    failures: list[str] = []
    if not model:
        failures.append("read_model_missing")
    if model.get("read_model_version") != LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION:
        failures.append("read_model_version_mismatch")
    if model.get("read_only") is not True:
        failures.append("read_model_not_read_only")
    if model.get("non_executing") is not True:
        failures.append("read_model_not_non_executing")
    if model.get("display_only") is not True:
        failures.append("read_model_not_display_only")
    for key in (
        "view_artifact_write_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_send_to_broker",
    ):
        if model.get(key) is not False:
            failures.append(f"read_model_boundary_not_false:{key}")
    ok = bool(model and not failures)
    packet: dict[str, Any] = {
        "ok": ok,
        "display_panel_version": LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_VERSION,
        "display_panel_state": LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_STATE if ok else "warroom_realtime_prediction_display_panel_blocked",
        "read_model_version": _clean(model.get("read_model_version")),
        "read_model_ok": model.get("ok") is True,
        "generated_at": _clean(model.get("generated_at")),
        "age_sec": model.get("age_sec"),
        "freshness_state": _clean(model.get("freshness_state")),
        "warning_reason_codes": list(model.get("warning_reason_codes") or []),
        "blocker_reason_codes": list(model.get("blocker_reason_codes") or []),
        "prediction_row_count": len(prediction_rows),
        "prediction_rows": prediction_rows,
        "market_rows": market_rows,
        "safety_rows": safety_rows,
        "fragment_enabled": bool(fragment_enabled),
        "refresh_mode": Q19D_REFRESH_MODE,
        "refresh_interval_sec": Q19D_REFRESH_SEC,
        "page_id": Q19D_PAGE_ID,
        "zone_id": Q19D_ZONE_ID,
        "widget_id": Q19D_WIDGET_ID,
        "panel_failures": failures,
        "operator_caption": "PS-Q19D displays the PS-Q19C latest prediction WarRoom read model. This is display-only: no view artifact write, no scheduler, no parameter apply, no AutoTrade, no broker.",
    }
    packet.update({key: ok for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["read_only"] = True
    packet["non_executing"] = True
    packet["display_only"] = True
    packet["streamlit_display_panel_render_allowed"] = True
    packet["warroom_display_panel_mounted"] = ok
    packet["fragment_slot_refresh_path_enabled"] = bool(fragment_enabled)
    return packet


def _render_panel_body() -> dict[str, Any]:
    packet = build_latest_prediction_warroom_display_panel_packet(
        fragment_enabled=live_shell.supports_streamlit_fragment(),
    )
    st.caption(str(packet.get("operator_caption") or "Latest prediction WarRoom display"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("freshness", _clean(packet.get("freshness_state")) or "unknown")
    c2.metric("age sec", "-" if packet.get("age_sec") is None else str(packet.get("age_sec")))
    c3.metric("prediction rows", str(packet.get("prediction_row_count") or 0))
    c4.metric("safe", "true" if packet.get("ok") is True else "false")
    st.caption(
        "source_generated_at={generated_at} / warnings={warnings} / blockers={blockers} / view_write=false / autotrade=false / broker=false".format(
            generated_at=packet.get("generated_at") or "-",
            warnings=packet.get("warning_reason_codes") or [],
            blockers=packet.get("blocker_reason_codes") or [],
        )
    )
    prediction_rows = list(packet.get("prediction_rows") or [])
    if prediction_rows:
        st.dataframe(prediction_rows, width="stretch", hide_index=True)
    else:
        st.info("No selected prediction rows available in the read model.")
    with st.expander("Market snapshot / safety flags", expanded=False):
        market_rows = list(packet.get("market_rows") or [])
        if market_rows:
            st.dataframe(market_rows, width="stretch", hide_index=True)
        safety_rows = list(packet.get("safety_rows") or [])
        if safety_rows:
            st.dataframe(safety_rows, width="stretch", hide_index=True)
    st.text(
        "PS_Q19D_WARROOM_REALTIME_PREDICTION_DISPLAY_ONLY "
        f"freshness_state={packet.get('freshness_state')} "
        f"prediction_row_count={packet.get('prediction_row_count')} "
        f"view_artifact_write_allowed=false autotrade=false broker=false"
    )
    return packet


def render_latest_prediction_warroom_display_panel(*, fragment_enabled: bool = True) -> Mapping[str, Any]:
    packet_holder: dict[str, Any] = {}

    def _render_body() -> None:
        packet_holder.update(_render_panel_body())

    meta = live_shell.make_slot_meta(
        Q19D_PAGE_ID,
        Q19D_ZONE_ID,
        Q19D_WIDGET_ID,
        label="Realtime prediction read model",
        tone="primary",
        help_text="Display-only latest prediction read model. No AutoTrade, broker, parameter, ledger, scheduler, or artifact writes.",
        refresh_mode=Q19D_REFRESH_MODE,
        priority=17,
        overlay_enabled=False,
        partial_update_enabled=True,
    )
    live_shell.render_fragment_slot(
        meta,
        _render_body,
        enabled=bool(fragment_enabled),
        default_sec=Q19D_REFRESH_SEC,
    )
    return packet_holder or build_latest_prediction_warroom_display_panel_packet(
        fragment_enabled=bool(fragment_enabled),
    )
