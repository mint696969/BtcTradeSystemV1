# path: ./btcts_next/src/btcts/apps/operator_ui/views/health_page.py
# desc: 実運用向けの System Health ページ。collector / audit / market_state を基に短期監視を表示する。

from __future__ import annotations

import pandas as pd
import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components.live_shell import get_registered_slots
from btcts.apps.operator_ui.components.slot_definitions import (
    health_widget_ids,
    health_widget_slot,
    health_widget_zone_ids,
)
from btcts.apps.operator_ui.components.health_chart_panels import (
    render_api_chart_panel,
    render_layer3_chart_panel,
    render_ws_chart_panel,
)
from btcts.apps.operator_ui.components.health_detail_panels import (
    render_current_state_section,
    render_recent_events_section,
)
from btcts.apps.operator_ui.components.health_top_panels import (
    render_continuity_panels,
    render_overview_summary_panel,
    render_read_guide_section,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.health_data_service import load_health_snapshot
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts


def _collector_summary_label(status_payload: dict, health_payload: dict, lang: str) -> str:
    mode = str(status_payload.get("mode") or "")
    ok = health_payload.get("ok")

    if mode == "RUNNING" and ok is True:
        return get_text(lang, "health_value_healthy")
    if mode in {"RUNNING", "DEGRADED"}:
        return get_text(lang, "health_value_caution")
    if mode:
        return get_text(lang, "health_value_broken")
    return get_text(lang, "health_value_no_data")


def _api_summary_label(rate_item: dict, lang: str) -> str:
    if not rate_item:
        return get_text(lang, "health_value_no_data")

    mode = str(rate_item.get("mode") or rate_item.get("summary_state") or "").upper()

    if rate_item.get("last_429_ts"):
        return get_text(lang, "health_value_caution")

    if bool(rate_item.get("engaged")):
        return get_text(lang, "health_value_caution")

    if mode in {"NORMAL"}:
        return get_text(lang, "health_value_healthy")

    if mode in {"WARN", "RECOVERY", "CRIT"}:
        return get_text(lang, "health_value_caution")

    return get_text(lang, "health_value_broken")


def _ws_summary_label(origin_payload: dict, lang: str) -> str:
    ws_state = str(origin_payload.get("ws_state") or "").upper()
    age_sec = _ws_age_seconds(origin_payload.get("ts"))

    if age_sec is not None and age_sec > 300:
        return get_text(lang, "health_value_broken")
    if age_sec is not None and age_sec > 30:
        return get_text(lang, "health_value_caution")

    if ws_state == "LIVE":
        return get_text(lang, "health_value_healthy")
    if ws_state in {"SYNCING", "CONNECTING"}:
        return get_text(lang, "health_value_caution")
    if ws_state:
        return get_text(lang, "health_value_broken")
    return get_text(lang, "health_value_no_data")


def _layer3_summary_label(market_latest: dict, market_diag: dict, lang: str) -> str:
    trust_state = str(market_latest.get("trust_state") or market_diag.get("preferred_row_trust_state") or "")
    interpretation_bucket = str(
        market_latest.get("interpretation_bucket")
        or market_diag.get("preferred_row_interpretation_bucket")
        or ""
    )

    if trust_state == "trusted" and interpretation_bucket == "allow_structural_use":
        return get_text(lang, "health_value_healthy")
    if trust_state in {"provisional", "trusted"} or interpretation_bucket == "observe_only":
        return get_text(lang, "health_value_caution")
    if trust_state or interpretation_bucket:
        return get_text(lang, "health_value_broken")
    return get_text(lang, "health_value_no_data")


def _format_optional_ts(value: str | None, lang: str) -> str:
    if not value:
        return "-"
    return format_ui_ts(value, lang=lang)


def _format_age_seconds(value: str | None) -> str:
    if not value:
        return "-"

    dt = _parse_ui_ts(value)
    if dt is None:
        return "-"

    now = pd.Timestamp.utcnow()
    if getattr(now, "tzinfo", None) is None:
        now = now.tz_localize("UTC")

    age_sec = max(0.0, (now.to_pydatetime() - dt).total_seconds())
    return str(int(round(age_sec)))


def _ws_age_seconds(value: str | None) -> float | None:
    if not value:
        return None

    dt = _parse_ui_ts(value)
    if dt is None:
        return None

    now = pd.Timestamp.utcnow()
    if getattr(now, "tzinfo", None) is None:
        now = now.tz_localize("UTC")

    return max(0.0, (now.to_pydatetime() - dt).total_seconds())


def _ws_freshness_label(origin_payload: dict, lang: str) -> str:
    age_sec = _ws_age_seconds(origin_payload.get("ts"))
    if age_sec is None:
        return "-"

    if age_sec <= 5:
        return get_text(lang, "health_value_live_freshness")
    if age_sec <= 30:
        return get_text(lang, "health_value_quiet_freshness")
    if age_sec <= 300:
        return get_text(lang, "health_value_stale_freshness")
    return get_text(lang, "health_value_broken_freshness")


def _ws_freshness_label_from_ts(value: str | None, lang: str) -> str:
    age_sec = _ws_age_seconds(value)
    if age_sec is None:
        return "-"

    if age_sec <= 5:
        return get_text(lang, "health_value_live_freshness")
    if age_sec <= 30:
        return get_text(lang, "health_value_quiet_freshness")
    if age_sec <= 300:
        return get_text(lang, "health_value_stale_freshness")
    return get_text(lang, "health_value_broken_freshness")


def _parse_ui_ts(value: str | None):
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            return pd.Timestamp(raw.replace("Z", "+00:00")).to_pydatetime()
        return pd.Timestamp(raw).to_pydatetime()
    except Exception:
        return None


def _format_metric_number(
    value,
    *,
    decimals: int = 0,
    percent: bool = False,
) -> str:
    if value is None or value == "":
        return "-"

    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)

    if percent:
        return f"{num * 100:.{decimals}f}%"

    if decimals <= 0:
        return str(int(round(num)))

    return f"{num:.{decimals}f}"


def _health_value_label(value: str | None, lang: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "-"

    key_map = {
        "RUNNING": "health_value_running",
        "DEGRADED": "health_value_degraded",
        "STOPPED": "health_value_stopped",
        "NORMAL": "health_value_normal_mode",
        "WARN": "health_value_warn_mode",
        "RECOVERY": "health_value_recovery_mode",
        "CRIT": "health_value_crit_mode",
        "continuous": "health_value_continuous",
        "disrupted": "health_value_disrupted",
        "LIVE": "health_value_live_freshness",
        "QUIET": "health_value_quiet_freshness",
        "STALE": "health_value_stale_freshness",
        "trusted": "health_value_trusted",
        "provisional": "health_value_provisional",
        "broken": "health_value_broken_trust",
        "allow_structural_use": "health_value_allow_structural_use",
        "observe_only": "health_value_observe_only",
        "none": "health_value_none_boundary",
    }

    text_key = key_map.get(raw)
    if text_key:
        return get_text(lang, text_key)
    return raw


def _health_event_label(value: str | None, lang: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return get_text(lang, "health_table_empty_value")

    key_map = {
        "origin.stream_gap_detected": "health_event_gap_detected",
        "origin.stream_resync_started": "health_event_resync_started",
        "origin.stream_resync_completed": "health_event_resync_completed",
        "crit": "health_event_exploration_crit",
        "recovery": "health_event_exploration_recovery",
        "warn": "health_event_exploration_warn",
        "normal": "health_event_exploration_normal",
        "delta_arrived_before_snapshot": "health_reason_delta_arrived_before_snapshot",
        "snapshot_received_after_gap": "health_reason_snapshot_received_after_gap",
        "none": "health_table_empty_value",
        "None": "health_table_empty_value",
    }

    if raw == "collector_vnext.unified.mode.changed":
        return get_text(lang, "health_event_exploration_normal")

    if raw == "collector_vnext.unified.ws_executions.started":
        return get_text(lang, "health_event_ws_exec_started")
    if raw == "collector_vnext.unified.ws_executions.connected":
        return get_text(lang, "health_event_ws_exec_connected")
    if raw == "collector_vnext.unified.ws_executions.reconnected":
        return get_text(lang, "health_event_ws_exec_reconnected")
    if raw == "collector_vnext.unified.ws_executions.message.received":
        return get_text(lang, "health_event_ws_exec_message_received")
    if raw == "collector_vnext.unified.ws_executions.message.skipped":
        return get_text(lang, "health_event_ws_exec_message_skipped")
    if raw == "collector_vnext.unified.ws_executions.message.meta":
        return get_text(lang, "health_event_ws_exec_meta")
    if raw == "collector_vnext.unified.ws_executions.trade.written":
        return get_text(lang, "health_event_ws_exec_trade_written")

    text_key = key_map.get(raw)
    if text_key:
        return get_text(lang, text_key)

    if (
        raw.startswith("collector_vnext.exploration.")
        or raw.startswith("collector_vnext.unified.")
    ) and raw.endswith(".completed"):
        return get_text(lang, "health_event_exploration_request_completed")

    if (
        raw.startswith("collector_vnext.exploration.")
        or raw.startswith("collector_vnext.unified.")
    ) and raw.endswith(".failed"):
        return get_text(lang, "health_event_exploration_request_failed")

    return raw


def _range_label(range_key: str) -> str:
    mapping = {
        "1h": "1時間",
        "24h": "24時間",
        "1w": "1週間",
    }
    return mapping.get(range_key, range_key)


def _section_title_with_range(title: str, range_key: str) -> str:
    return f"{title}（{_range_label(range_key)}）"


def _api_chart_columns_and_labels(api_df: pd.DataFrame, lang: str) -> tuple[list[str], dict[str, str]]:
    if api_df.empty:
        return [], {}

    latest_row = api_df.iloc[-1].to_dict()
    chart_fields = latest_row.get("api_chart_fields") or []

    label_key_map = {
        "api_events": "health_chart_api_events",
        "api_rolling_5m": "health_chart_api_rolling_5m",
        "api_limit_5m": "health_chart_api_limit_5m",
        "events_429_marker": "health_chart_429_events",
        "events_429": "health_chart_429_events",
        "warn_error_events": "health_chart_warn_error_events",
    }

    labels: dict[str, str] = {}
    columns: list[str] = []

    for field in chart_fields:
        if field not in api_df.columns:
            continue
        columns.append(field)
        labels[field] = get_text(lang, label_key_map.get(field, field))

    return columns, labels


def _render_health_range_selector(lang: str) -> str:
    range_options = {
        "1h": get_text(lang, "health_range_1h"),
        "24h": get_text(lang, "health_range_24h"),
        "1w": get_text(lang, "health_range_1w"),
    }
    selected_range_key = st.session_state.get("health_selected_range_key", "1h")

    range_cols = st.columns([1, 6])
    with range_cols[0]:
        st.session_state.health_selected_range_key = st.selectbox(
            get_text(lang, "health_label_range_selector"),
            options=["1h", "24h", "1w"],
            index=["1h", "24h", "1w"].index(selected_range_key),
            format_func=lambda key: range_options.get(key, key),
            key="health_range_selector",
        )

    return str(st.session_state.health_selected_range_key)


def render():
    lang = st.session_state.get("ui_lang", "en")

    live_shell.render_compact_page_header(get_text(lang, "health_title"))
    selected_range_key = _render_health_range_selector(lang)

    snapshot = load_health_snapshot(range_key=selected_range_key)
    summary_widget = load_market_summary_widget_model()

    collector_state = snapshot.get("collector_state") or {}
    status_payload = collector_state.get("status") or {}
    health_payload = collector_state.get("health") or {}
    rate_payload = collector_state.get("rate") or {}
    origin_payload = collector_state.get("origin") or {}
    checkpoint_payload = collector_state.get("checkpoint") or {}
    executions_payload = collector_state.get("executions") or {}
    daemon_status_payload = (
        collector_state.get("daemon_status")
        or collector_state.get("exploration_daemon_status")
        or {}
    )
    daemon_health_payload = collector_state.get("health") or {}

    runtime_kind = str(
        status_payload.get("runtime_kind")
        or daemon_status_payload.get("runtime_kind")
        or health_payload.get("runtime_kind")
        or ""
    ).lower()

    rate_items = rate_payload.get("items") or {}
    bitflyer_rate = rate_items.get("bitflyer") or {}
    bitflyer_rate_classes = bitflyer_rate.get("request_classes") or {}
    bitflyer_rate_snapshot = bitflyer_rate_classes.get("board_snapshot") or {}
    bitflyer_rate_trades = bitflyer_rate_classes.get("rest_trades") or {}

    runtime_mode = str(bitflyer_rate.get("mode") or bitflyer_rate.get("summary_state") or "")
    runtime_active_target_ratio = bitflyer_rate.get("active_target_ratio")
    runtime_utilization = bitflyer_rate.get("utilization")

    ws_board_lane = status_payload.get("ws_board_lane") or {}
    ws_executions_lane = status_payload.get("ws_executions_lane") or {}

    ws_board_state = str(
        ws_board_lane.get("state")
        or origin_payload.get("lane_state")
        or origin_payload.get("ws_state")
        or ""
    )
    ws_board_last_error = str(
        ws_board_lane.get("last_error")
        or origin_payload.get("last_error")
        or ""
    )

    ws_executions_state = str(
        ws_executions_lane.get("state")
        or executions_payload.get("lane_state")
        or executions_payload.get("ws_state")
        or ""
    )
    ws_executions_last_error = str(
        ws_executions_lane.get("last_error")
        or executions_payload.get("last_error")
        or ""
    )

    market_latest = snapshot.get("market_latest") or {}
    market_diag = snapshot.get("market_diag") or {}

    api_ws_series = snapshot.get("api_ws_series") or []
    rate_overlay = snapshot.get("rate_overlay") or []
    layer3_series = snapshot.get("layer3_series") or []
    api_continuity_rail = snapshot.get("api_continuity_rail") or []
    ws_continuity_rail = snapshot.get("ws_continuity_rail") or []
    recent_anomalies = snapshot.get("recent_anomalies") or []

    render_overview_summary_panel(
        lang=lang,
        status_payload=status_payload,
        health_payload=health_payload,
        bitflyer_rate=bitflyer_rate,
        origin_payload=origin_payload,
        market_latest=market_latest,
        market_diag=market_diag,
        get_text=get_text,
        collector_summary_label=_collector_summary_label,
        api_summary_label=_api_summary_label,
        ws_summary_label=_ws_summary_label,
        layer3_summary_label=_layer3_summary_label,
    )

    with live_shell.slot_widget_from_meta(
        health_widget_slot("api_chart_panel")
    ):
        render_api_chart_panel(
            lang=lang,
            range_key=selected_range_key,
            api_ws_series=api_ws_series,
            rate_overlay=rate_overlay,
            bitflyer_rate=bitflyer_rate,
            bitflyer_rate_snapshot=bitflyer_rate_snapshot,
            bitflyer_rate_trades=bitflyer_rate_trades,
            get_text=get_text,
            section_title_with_range=_section_title_with_range,
            format_metric_number=_format_metric_number,
            api_chart_columns_and_labels=_api_chart_columns_and_labels,
        )

    with live_shell.slot_widget_from_meta(
        health_widget_slot("ws_chart_panel")
    ):
        render_ws_chart_panel(
            lang=lang,
            range_key=selected_range_key,
            api_ws_series=api_ws_series,
            get_text=get_text,
            section_title_with_range=_section_title_with_range,
            format_metric_number=_format_metric_number,
        )

    with live_shell.slot_widget_from_meta(
        health_widget_slot("layer3_chart_panel")
    ):
        render_layer3_chart_panel(
            lang=lang,
            range_key=selected_range_key,
            layer3_series=layer3_series,
            market_latest=market_latest,
            market_diag=market_diag,
            get_text=get_text,
            section_title_with_range=_section_title_with_range,
            health_value_label=_health_value_label,
        )

    with live_shell.slot_widget_from_meta(
        health_widget_slot("current_state_section")
    ):
        render_current_state_section(
            lang=lang,
            status_payload=status_payload,
            health_payload=health_payload,
            bitflyer_rate=bitflyer_rate,
            runtime_kind=runtime_kind,
            runtime_mode=runtime_mode,
            runtime_utilization=runtime_utilization,
            origin_payload=origin_payload,
            checkpoint_payload=checkpoint_payload,
            ws_board_lane=ws_board_lane,
            ws_executions_lane=ws_executions_lane,
            executions_payload=executions_payload,
            ws_board_state=ws_board_state,
            ws_board_last_error=ws_board_last_error,
            ws_executions_state=ws_executions_state,
            ws_executions_last_error=ws_executions_last_error,
            market_latest=market_latest,
            market_diag=market_diag,
            daemon_status_payload=daemon_status_payload,
            daemon_health_payload=daemon_health_payload,
            get_text=get_text,
            health_value_label=_health_value_label,
            format_optional_ts=_format_optional_ts,
            format_age_seconds=_format_age_seconds,
            format_metric_number=_format_metric_number,
            ws_freshness_label_from_ts=_ws_freshness_label_from_ts,
        )

    with live_shell.slot_widget_from_meta(
        health_widget_slot("recent_events_section")
    ):
        render_recent_events_section(
            lang=lang,
            recent_anomalies=recent_anomalies,
            get_text=get_text,
            health_event_label=_health_event_label,
        )

    render_read_guide_section(
        lang=lang,
        get_text=get_text,
    )

    render_continuity_panels(
        lang=lang,
        range_key=selected_range_key,
        api_continuity_rail=api_continuity_rail,
        ws_continuity_rail=ws_continuity_rail,
        get_text=get_text,
        section_title_with_range=_section_title_with_range,
    )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    _render_health_diagnostics(lang)

def _render_health_diagnostics(lang: str) -> None:
    with live_shell.render_folded_section(get_text(lang, "ui_slot_diagnostics_title"), expanded=False):
        st.caption(get_text(lang, "ui_slot_diagnostics_health_caption"))
        slot_rows = get_registered_slots("health")
        if slot_rows:
            st.dataframe(slot_rows, width="stretch")

            expected_widget_ids = set(health_widget_ids())
            actual_widget_ids = {str(row.get("widget_id")) for row in slot_rows}
            missing_widget_ids = sorted(
                expected_widget_ids.difference(actual_widget_ids)
            )
            if missing_widget_ids:
                st.warning(
                    "missing health slot registrations: " + ", ".join(missing_widget_ids)
                )

            actual_zone_ids = {
                str(row.get("zone_id"))
                for row in slot_rows
                if row.get("zone_id") is not None
            }
            unexpected_zone_ids = sorted(
                actual_zone_ids.difference(set(health_widget_zone_ids()))
            )
            if unexpected_zone_ids:
                st.warning(
                    "unexpected health zone ids: " + ", ".join(unexpected_zone_ids)
                )
        else:
            st.info(get_text(lang, "ui_slot_registry_empty_health"))