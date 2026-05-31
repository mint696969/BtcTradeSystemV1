# path: ./btcts_next/src/btcts/apps/operator_ui/views/health_page.py
# desc: 実運用向けの System Health ページ。collector / audit / market_state を基に短期監視を表示する。

from __future__ import annotations

import pandas as pd
import streamlit as st

from btcts.apps.operator_ui.components import live_shell
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
    build_health_digest_current_state_caption,
    render_current_state_section,
    render_recent_events_section,
)
from btcts.apps.operator_ui.components.health_top_panels import (
    build_health_digest_api_summary_caption,
    build_health_digest_collector_summary_caption,
    build_health_digest_layer3_summary_caption,
    build_health_digest_operational_reading_caption,
    build_health_digest_ws_summary_caption,
    render_api_summary_metric,
    render_collector_summary_metric,
    render_continuity_panels,
    render_layer3_summary_metric,
    render_read_guide_section,
    render_ws_summary_metric,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)

from btcts.apps.operator_ui.components.health_digest_bridge import (
    build_health_digest_ui_bundle,
)
from btcts.apps.operator_ui.components.evidence_presentation_panel import (
    render_evidence_presentation_panel,
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
        return get_text(lang, "health_table_empty_value")
    return format_ui_ts(value, lang=lang)


def _format_age_seconds(value: str | None, lang: str) -> str:
    if not value:
        return get_text(lang, "health_table_empty_value")

    dt = _parse_ui_ts(value)
    if dt is None:
        return get_text(lang, "health_table_empty_value")

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


def _ws_freshness_label_from_ts(value: str | None, lang: str) -> str:
    age_sec = _ws_age_seconds(value)
    if age_sec is None:
        return get_text(lang, "health_table_empty_value")

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
    lang: str = "en",
) -> str:
    if value is None or value == "":
        return get_text(lang, "health_table_empty_value")

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
        return get_text(lang, "health_table_empty_value")

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
        "missing": "health_value_missing_wiring",
        "partial": "health_value_partial_wiring",
        "wired": "health_value_wired",
        "fallback": "health_value_fallback_wiring",
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


def _range_label(range_key: str, lang: str) -> str:
    key_map = {
        "1h": "health_range_1h",
        "24h": "health_range_24h",
        "1w": "health_range_1w",
    }
    text_key = key_map.get(range_key)
    if not text_key:
        return range_key
    return get_text(lang, text_key)


def _section_title_with_range(title: str, range_key: str, lang: str) -> str:
    return f"{title}（{_range_label(range_key, lang)}）"


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


@st.cache_data(show_spinner=False, ttl=1)
def _load_cached_health_snapshot(range_key: str) -> dict:
    return load_health_snapshot(range_key=range_key)


@st.cache_data(show_spinner=False, ttl=1)
def _load_cached_market_summary_widget_model():
    return load_market_summary_widget_model()


def _snapshot_current_state_bundle(snapshot: dict) -> dict:
    bundle = snapshot.get("current_state_bundle")
    if isinstance(bundle, dict):
        return bundle
    return snapshot


def _snapshot_timeline_bundle(snapshot: dict) -> dict:
    bundle = snapshot.get("timeline_bundle")
    if isinstance(bundle, dict):
        return bundle
    return snapshot


def _snapshot_anomaly_bundle(snapshot: dict) -> dict:
    bundle = snapshot.get("anomaly_bundle")
    if isinstance(bundle, dict):
        return bundle
    return snapshot


def _snapshot_anomaly_items(snapshot: dict) -> list[dict]:
    anomaly_bundle = _snapshot_anomaly_bundle(snapshot)
    items = anomaly_bundle.get("items")
    if isinstance(items, list):
        return items
    recent_anomalies = anomaly_bundle.get("recent_anomalies")
    if isinstance(recent_anomalies, list):
        return recent_anomalies
    return []


def _snapshot_continuity_bundle(snapshot: dict) -> dict:
    bundle = snapshot.get("continuity_bundle")
    if isinstance(bundle, dict):
        return bundle
    timeline_bundle = snapshot.get("timeline_bundle")
    if isinstance(timeline_bundle, dict):
        return timeline_bundle
    return snapshot


def _snapshot_health_digest_ui_bundle(snapshot: dict) -> dict:
    current_state_bundle = _snapshot_current_state_bundle(snapshot)
    return build_health_digest_ui_bundle(
        current_state_bundle.get("health_digest")
    )


def _snapshot_evidence_presentation_payload(snapshot: dict) -> dict | None:
    """Return already-provided evidence presentation payload from the Health snapshot only."""
    if not isinstance(snapshot, dict):
        return None
    direct_payload = snapshot.get("evidence_presentation_payload")
    if isinstance(direct_payload, dict):
        return direct_payload
    current_state_bundle = _snapshot_current_state_bundle(snapshot)
    for key in (
        "evidence_presentation_payload",
        "health_warroom_evidence_presentation_payload",
        "real_data_validation_evidence_presentation",
    ):
        payload = current_state_bundle.get(key)
        if isinstance(payload, dict):
            return payload
    return None


def _render_health_fragment(*, refresh_mode: str, render_body) -> None:
    live_shell.render_fragment_block(
        render_body,
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
        refresh_mode=refresh_mode,
    )


def _render_live_tick_caption(lang: str) -> None:
    now = pd.Timestamp.utcnow()
    if getattr(now, "tzinfo", None) is None:
        now = now.tz_localize("UTC")
    tick_text = now.strftime("%H:%M:%S UTC")
    st.caption(get_text(lang, "health_caption_live_tick_prefix") + tick_text)


def render():
    lang = st.session_state.get("ui_lang", "en")

    def format_metric_number_local(value, **kwargs) -> str:
        return _format_metric_number(value, lang=lang, **kwargs)

    def section_title_with_range_local(title: str, range_key: str) -> str:
        return _section_title_with_range(title, range_key, lang)

    live_shell.render_compact_page_header(get_text(lang, "health_title"))
    selected_range_key = _render_health_range_selector(lang)

    live_shell.render_fragment_slot(
        health_widget_slot("live_tick_caption"),
        lambda: _render_live_tick_caption(lang),
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
    )


    def _render_collector_summary_section() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        current_state_bundle = _snapshot_current_state_bundle(snapshot)

        collector_state = current_state_bundle.get("collector_state") or {}
        status_payload = collector_state.get("status") or {}
        health_payload = collector_state.get("health") or {}
        health_digest_bundle = _snapshot_health_digest_ui_bundle(snapshot)
        digest_caption = build_health_digest_collector_summary_caption(
            widget=health_digest_bundle["widget"],
            payload=health_digest_bundle["payload"],
        )

        render_collector_summary_metric(
            lang=lang,
            status_payload=status_payload,
            health_payload=health_payload,
            get_text=get_text,
            collector_summary_label=_collector_summary_label,
            digest_caption=digest_caption,
        )

    def _render_api_summary_section() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        current_state_bundle = _snapshot_current_state_bundle(snapshot)

        collector_state = current_state_bundle.get("collector_state") or {}
        rate_payload = collector_state.get("rate") or {}
        rate_items = rate_payload.get("items") or {}
        bitflyer_rate = rate_items.get("bitflyer") or {}
        health_digest_bundle = _snapshot_health_digest_ui_bundle(snapshot)
        digest_caption = build_health_digest_api_summary_caption(
            widget=health_digest_bundle["widget"],
            payload=health_digest_bundle["payload"],
        )

        render_api_summary_metric(
            lang=lang,
            bitflyer_rate=bitflyer_rate,
            get_text=get_text,
            api_summary_label=_api_summary_label,
            digest_caption=digest_caption,
        )

    def _render_ws_summary_section() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        current_state_bundle = _snapshot_current_state_bundle(snapshot)

        collector_state = current_state_bundle.get("collector_state") or {}
        origin_payload = collector_state.get("origin") or {}
        health_digest_bundle = _snapshot_health_digest_ui_bundle(snapshot)
        digest_caption = build_health_digest_ws_summary_caption(
            widget=health_digest_bundle["widget"],
            payload=health_digest_bundle["payload"],
        )

        render_ws_summary_metric(
            lang=lang,
            origin_payload=origin_payload,
            get_text=get_text,
            ws_summary_label=_ws_summary_label,
            digest_caption=digest_caption,
        )

    def _render_layer3_summary_section() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        current_state_bundle = _snapshot_current_state_bundle(snapshot)

        market_latest = current_state_bundle.get("market_latest") or {}
        market_diag = current_state_bundle.get("market_diag") or {}
        health_digest_bundle = _snapshot_health_digest_ui_bundle(snapshot)
        digest_caption = build_health_digest_layer3_summary_caption(
            widget=health_digest_bundle["widget"],
            payload=health_digest_bundle["payload"],
        )
        operational_reading_caption = build_health_digest_operational_reading_caption(
            widget=health_digest_bundle["widget"],
            payload=health_digest_bundle["payload"],
        )

        render_layer3_summary_metric(
            lang=lang,
            market_latest=market_latest,
            market_diag=market_diag,
            get_text=get_text,
            layer3_summary_label=_layer3_summary_label,
            digest_caption=digest_caption,
            operational_reading_caption=operational_reading_caption,
        )

    def _render_evidence_presentation_section() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        evidence_payload = _snapshot_evidence_presentation_payload(snapshot)
        render_evidence_presentation_panel(evidence_payload, expanded=False)

    live_shell.render_fragment_slot(
        health_widget_slot("evidence_presentation_panel"),
        _render_evidence_presentation_section,
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
    )

    def _render_api_chart_section() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        current_state_bundle = _snapshot_current_state_bundle(snapshot)
        timeline_bundle = _snapshot_timeline_bundle(snapshot)

        collector_state = current_state_bundle.get("collector_state") or {}
        rate_payload = collector_state.get("rate") or {}
        rate_items = rate_payload.get("items") or {}
        bitflyer_rate = rate_items.get("bitflyer") or {}
        bitflyer_rate_classes = bitflyer_rate.get("request_classes") or {}
        bitflyer_rate_snapshot = bitflyer_rate_classes.get("board_snapshot") or {}
        bitflyer_rate_trades = bitflyer_rate_classes.get("rest_trades") or {}

        render_api_chart_panel(
            lang=lang,
            range_key=selected_range_key,
            api_ws_series=timeline_bundle.get("api_ws_series") or [],
            rate_overlay=timeline_bundle.get("rate_overlay") or [],
            bitflyer_rate=bitflyer_rate,
            bitflyer_rate_snapshot=bitflyer_rate_snapshot,
            bitflyer_rate_trades=bitflyer_rate_trades,
            get_text=get_text,
            section_title_with_range=section_title_with_range_local,
            format_metric_number=format_metric_number_local,
            api_chart_columns_and_labels=_api_chart_columns_and_labels,
        )

    def _render_ws_chart_section() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        timeline_bundle = _snapshot_timeline_bundle(snapshot)

        render_ws_chart_panel(
            lang=lang,
            range_key=selected_range_key,
            api_ws_series=timeline_bundle.get("api_ws_series") or [],
            get_text=get_text,
            section_title_with_range=section_title_with_range_local,
            format_metric_number=format_metric_number_local,
        )

    def _render_layer3_chart_section() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        current_state_bundle = _snapshot_current_state_bundle(snapshot)
        timeline_bundle = _snapshot_timeline_bundle(snapshot)

        render_layer3_chart_panel(
            lang=lang,
            range_key=selected_range_key,
            layer3_series=timeline_bundle.get("layer3_series") or [],
            layer3_semantic_usage_rows=current_state_bundle.get("layer3_semantic_usage_rows") or [],
            layer3_semantic_usage_summary=current_state_bundle.get("layer3_semantic_usage_summary") or {},
            layer3_runtime_contract_summary=current_state_bundle.get("layer3_runtime_contract_summary") or {},
            layer3_orderbook_runtime_summary=current_state_bundle.get("layer3_orderbook_runtime_summary") or {},
            market_latest=current_state_bundle.get("market_latest") or {},
            market_diag=current_state_bundle.get("market_diag") or {},
            get_text=get_text,
            section_title_with_range=section_title_with_range_local,
            health_value_label=_health_value_label,
        )

    def _render_current_state_section_fragment() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        current_state_bundle = _snapshot_current_state_bundle(snapshot)

        collector_state = current_state_bundle.get("collector_state") or {}
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
        runtime_mode = str(bitflyer_rate.get("mode") or bitflyer_rate.get("summary_state") or "")
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

        market_latest = current_state_bundle.get("market_latest") or {}
        market_diag = current_state_bundle.get("market_diag") or {}
        health_digest_bundle = _snapshot_health_digest_ui_bundle(snapshot)

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
            health_digest_widget=health_digest_bundle["widget"],
            health_digest_payload=health_digest_bundle["payload"],
            daemon_status_payload=daemon_status_payload,
            daemon_health_payload=daemon_health_payload,
            get_text=get_text,
            health_value_label=_health_value_label,
            format_optional_ts=_format_optional_ts,
            format_age_seconds=lambda value: _format_age_seconds(value, lang),
            format_metric_number=format_metric_number_local,
            ws_freshness_label_from_ts=_ws_freshness_label_from_ts,
        )

    def _render_recent_events_section_fragment() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)

        render_recent_events_section(
            lang=lang,
            recent_anomalies=_snapshot_anomaly_items(snapshot),
            get_text=get_text,
            health_event_label=_health_event_label,
        )

    def _render_continuity_section() -> None:
        snapshot = _load_cached_health_snapshot(selected_range_key)
        continuity_bundle = _snapshot_continuity_bundle(snapshot)

        render_continuity_panels(
            lang=lang,
            range_key=selected_range_key,
            api_continuity_rail=continuity_bundle.get("api_continuity_rail") or [],
            ws_continuity_rail=continuity_bundle.get("ws_continuity_rail") or [],
            get_text=get_text,
            section_title_with_range=section_title_with_range_local,
        )

    c1, c2, c3, c4 = live_shell.responsive_columns(4, compact=True)

    with c1:
        live_shell.render_fragment_slot(
            health_widget_slot("collector_summary"),
            _render_collector_summary_section,
            enabled=bool(st.session_state.get("ui_auto_refresh", True)),
        )

    with c2:
        live_shell.render_fragment_slot(
            health_widget_slot("api_summary"),
            _render_api_summary_section,
            enabled=bool(st.session_state.get("ui_auto_refresh", True)),
        )

    with c3:
        live_shell.render_fragment_slot(
            health_widget_slot("ws_summary"),
            _render_ws_summary_section,
            enabled=bool(st.session_state.get("ui_auto_refresh", True)),
        )

    with c4:
        live_shell.render_fragment_slot(
            health_widget_slot("layer3_summary"),
            _render_layer3_summary_section,
            enabled=bool(st.session_state.get("ui_auto_refresh", True)),
        )
    live_shell.render_fragment_slot(
        health_widget_slot("api_chart_panel"),
        _render_api_chart_section,
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
    )
    live_shell.render_fragment_slot(
        health_widget_slot("ws_chart_panel"),
        _render_ws_chart_section,
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
    )
    live_shell.render_fragment_slot(
        health_widget_slot("layer3_chart_panel"),
        _render_layer3_chart_section,
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
    )
    live_shell.render_fragment_slot(
        health_widget_slot("current_state_section"),
        _render_current_state_section_fragment,
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
    )
    live_shell.render_fragment_slot(
        health_widget_slot("recent_events_section"),
        _render_recent_events_section_fragment,
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
    )

    render_read_guide_section(
        lang=lang,
        get_text=get_text,
    )

    _render_health_fragment(
        refresh_mode="poll_normal",
        render_body=_render_continuity_section,
    )

    def _render_market_summary_caption() -> None:
        latest_summary_widget = _load_cached_market_summary_widget_model()
        if latest_summary_widget:
            st.caption(summary_widget_caption(latest_summary_widget))

    live_shell.render_fragment_slot(
        health_widget_slot("market_summary_caption"),
        _render_market_summary_caption,
        enabled=bool(st.session_state.get("ui_auto_refresh", True)),
    )

    _render_health_diagnostics(lang)
def _render_health_diagnostics(lang: str) -> None:
    with live_shell.render_folded_section(get_text(lang, "ui_slot_diagnostics_title"), expanded=False):
        st.caption(get_text(lang, "ui_slot_diagnostics_health_caption"))
        slot_rows = live_shell.get_registered_slots("health")
        if slot_rows:
            st.dataframe(slot_rows, width="stretch")

            expected_widget_ids = set(health_widget_ids())
            actual_widget_ids = {str(row.get("widget_id")) for row in slot_rows}
            missing_widget_ids = sorted(
                expected_widget_ids.difference(actual_widget_ids)
            )
            if missing_widget_ids:
                st.warning(
                    get_text(lang, "health_warning_missing_slot_registrations_prefix")
                    + ", ".join(missing_widget_ids)
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
                    get_text(lang, "health_warning_unexpected_zone_ids_prefix")
                    + ", ".join(unexpected_zone_ids)
                )
        else:
            st.info(get_text(lang, "ui_slot_registry_empty_health"))