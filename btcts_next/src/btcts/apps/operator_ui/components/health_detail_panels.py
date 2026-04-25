# path: ./btcts_next/src/btcts/apps/operator_ui/components/health_detail_panels.py
# desc: Health ページの Current State / Recent Events を外出しした helper。

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.ui_time import format_ui_ts


def _health_orderbook_active_event_observer_line(
    orderbook_block: dict,
) -> str:
    normalized_block = dict(orderbook_block or {})

    active_event_contracts = normalized_block.get("active_event_contracts") or []
    if not isinstance(active_event_contracts, list):
        active_event_contracts = []

    active_event_names = normalized_block.get("active_event_names") or []
    if not isinstance(active_event_names, list):
        active_event_names = []

    active_event_count = int(normalized_block.get("active_event_count") or 0)

    if active_event_contracts:
        first_event = dict(active_event_contracts[0] or {})
        event_name = str(first_event.get("event_name") or "-").strip() or "-"
        event_family = str(first_event.get("event_family") or "-").strip() or "-"
        usage_grade = str(first_event.get("usage_grade") or "-").strip() or "-"
        horizon = str(first_event.get("forecast_horizon_hint") or "-").strip() or "-"
        side = str(first_event.get("side") or "-").strip() or "-"
        suffix = (
            f" +{len(active_event_contracts) - 1} more"
            if len(active_event_contracts) > 1
            else ""
        )
        return (
            f"active_events={active_event_count} / "
            f"{event_name} ({event_family} / {usage_grade} / {horizon} / {side})"
            f"{suffix}"
        )

    normalized_names = [
        str(name).strip()
        for name in active_event_names
        if str(name).strip()
    ]
    if normalized_names:
        suffix = (
            f" +{len(normalized_names) - 1} more"
            if len(normalized_names) > 1
            else ""
        )
        return f"active_events={active_event_count} / {normalized_names[0]}{suffix}"

    return f"active_events={active_event_count} / none"


def build_health_digest_block_captions(
    *,
    widget,
    payload: dict | None,
) -> dict[str, str]:
    if widget is None or not payload:
        return {
            "collector_ingestion_observability": "health_digest unavailable",
            "market_runtime_truth": "health_digest unavailable",
            "semantic_observability": "health_digest unavailable",
            "orderbook_active_event_observability": "health_digest unavailable",
        }

    collector_block = dict(payload.get("collector_ingestion_observability") or {})
    market_block = dict(payload.get("market_runtime_truth") or {})
    semantic_block = dict(payload.get("semantic_observability") or {})
    orderbook_block = dict(payload.get("orderbook_active_event_observability") or {})

    collector_runtime = dict(collector_block.get("collector_runtime") or {})
    api_runtime = dict(collector_block.get("api_runtime") or {})
    ws_runtime = dict(collector_block.get("ws_runtime") or {})
    market_runtime = dict(market_block.get("market_runtime") or {})

    freshness = str(getattr(widget, "freshness_key", None) or "UNKNOWN")
    source_kind = str(getattr(widget, "source_kind", None) or "unknown")
    event_ts = str(getattr(widget, "event_ts", None) or "-")
    age_sec = getattr(widget, "age_sec", None)
    age_text = "-" if age_sec is None else f"{float(age_sec):.1f}s"

    collector_caption = (
        f"collector_mode={collector_runtime.get('mode') or '-'} / "
        f"collector_ok={collector_runtime.get('ok')} / "
        f"api_mode={api_runtime.get('mode') or '-'} / "
        f"ws_board={ws_runtime.get('board_state') or '-'} / "
        f"ws_exec={ws_runtime.get('executions_state') or '-'} / "
        f"freshness={collector_block.get('freshness') or freshness}"
    )

    market_caption = (
        f"trust={market_runtime.get('trust_state') or '-'} / "
        f"continuity={market_runtime.get('continuity_state') or '-'} / "
        f"interpretation={market_runtime.get('interpretation_bucket') or '-'} / "
        f"source={market_block.get('source_kind') or source_kind} / "
        f"event_ts={market_block.get('event_ts') or event_ts}"
    )

    semantic_caption = (
        f"observer_status={semantic_block.get('observer_status') or '-'} / "
        f"wiring={semantic_block.get('runtime_wiring_status') or '-'} / "
        f"observer_present={bool(semantic_block.get('observer_present'))} / "
        f"summary_present={bool(semantic_block.get('usage_summary_present'))} / "
        f"contract_rows_present={bool(semantic_block.get('contract_rows_present'))} / "
        f"contract_rows={int(semantic_block.get('contract_rows_count') or 0)}"
    )

    orderbook_active_event_line = _health_orderbook_active_event_observer_line(
        orderbook_block
    )
    orderbook_caption = (
        f"wiring={orderbook_block.get('runtime_wiring_status') or '-'} / "
        f"slots={int(orderbook_block.get('summary_slots_count') or 0)} / "
        f"slots_present={','.join(list(orderbook_block.get('summary_slots_present') or [])) or '-'} / "
        f"{orderbook_active_event_line} / "
        f"persistence_present={bool(orderbook_block.get('persistence_present'))} / "
        f"persistence_observable={bool(orderbook_block.get('persistence_observable'))} / "
        f"age={age_text}"
    )

    return {
        "collector_ingestion_observability": collector_caption,
        "market_runtime_truth": market_caption,
        "semantic_observability": semantic_caption,
        "orderbook_active_event_observability": orderbook_caption,
    }


def build_health_digest_current_state_caption(
    *,
    widget,
    payload: dict | None,
) -> str:
    if widget is None or not payload:
        return "health_digest unavailable"

    semantic_block = dict(payload.get("semantic_observability") or {})
    orderbook_block = dict(payload.get("orderbook_active_event_observability") or {})

    freshness = str(getattr(widget, "freshness_key", None) or "UNKNOWN")
    semantic_wiring = str(getattr(widget, "semantic_wiring_key", None) or "missing")
    orderbook_wiring = str(getattr(widget, "orderbook_wiring_key", None) or "missing")
    semantic_source = str(getattr(widget, "semantic_summary_source_key", None) or "unknown")
    observer_status = str(getattr(widget, "semantic_observer_status_key", None) or "unknown")
    orderbook_source = str(
        getattr(widget, "orderbook_contract_status_source_key", None) or "unknown"
    )
    source_kind = str(getattr(widget, "source_kind", None) or "unknown")
    observer_present = bool(
        semantic_block.get("observer_present", payload.get("semantic_usage_observer_present"))
    )
    usage_summary_present = bool(
        semantic_block.get(
            "usage_summary_present",
            payload.get("semantic_usage_summary_present"),
        )
    )
    contract_rows_present = bool(
        semantic_block.get(
            "contract_rows_present",
            payload.get("semantic_usage_contract_rows_present"),
        )
    )
    source_series_present = bool(
        semantic_block.get(
            "source_series_present",
            payload.get("semantic_usage_source_series_present"),
        )
    )
    persistence_present = bool(
        orderbook_block.get(
            "persistence_present",
            payload.get("orderbook_persistence_present"),
        )
    )
    persistence_observable = orderbook_block.get(
        "persistence_observable",
        payload.get("orderbook_persistence_observable"),
    )
    persistence_observable_text = (
        "unknown"
        if persistence_observable is None
        else str(bool(persistence_observable))
    )
    semantic_rows = int(
        semantic_block.get(
            "contract_rows_count",
            payload.get("semantic_usage_contract_rows_count"),
        )
        or 0
    )
    summary_slots = int(
        orderbook_block.get(
            "summary_slots_count",
            payload.get("orderbook_summary_slots_count"),
        )
        or 0
    )
    slots_present = ",".join(
        list(
            orderbook_block.get("summary_slots_present")
            or getattr(widget, "orderbook_summary_slots_present", [])
            or []
        )
    ) or "-"
    active_events = int(
        orderbook_block.get(
            "active_event_count",
            payload.get("orderbook_active_event_count"),
        )
        or 0
    )
    active_event_names = ",".join(
        list(
            orderbook_block.get("active_event_names")
            or getattr(widget, "orderbook_active_event_names", [])
            or []
        )
    ) or "-"
    active_event_rows = int(
        orderbook_block.get(
            "active_event_contracts_count",
            payload.get("orderbook_active_event_contracts_count"),
        )
        or 0
    )
    age_sec = getattr(widget, "age_sec", None)
    age_text = "-" if age_sec is None else f"{float(age_sec):.1f}s"
    event_ts = str(getattr(widget, "event_ts", None) or "-")

    return (
        f"health_digest: freshness={freshness} / "
        f"semantic_wiring={semantic_wiring} / "
        f"semantic_source={semantic_source} / "
        f"observer_status={observer_status} / "
        f"orderbook_wiring={orderbook_wiring} / "
        f"orderbook_source={orderbook_source} / "
        f"source={source_kind} / "
        f"observer_present={observer_present} / "
        f"usage_summary_present={usage_summary_present} / "
        f"contract_rows_present={contract_rows_present} / "
        f"source_series_present={source_series_present} / "
        f"persistence_present={persistence_present} / "
        f"persistence_observable={persistence_observable_text} / "
        f"semantic_rows={semantic_rows} / "
        f"summary_slots={summary_slots} / "
        f"slots_present={slots_present} / "
        f"active_events={active_events} / "
        f"active_event_names={active_event_names} / "
        f"active_event_rows={active_event_rows} / "
        f"age={age_text} / "
        f"event_ts={event_ts}"
    )


def render_current_state_section(
    *,
    lang: str,
    status_payload: dict,
    health_payload: dict,
    bitflyer_rate: dict,
    runtime_kind: str,
    runtime_mode: str,
    runtime_utilization,
    origin_payload: dict,
    checkpoint_payload: dict,
    ws_board_lane: dict,
    ws_executions_lane: dict,
    executions_payload: dict,
    ws_board_state: str,
    ws_board_last_error: str,
    ws_executions_state: str,
    ws_executions_last_error: str,
    market_latest: dict,
    market_diag: dict,
    health_digest_widget=None,
    health_digest_payload: dict | None = None,
    daemon_status_payload: dict,
    daemon_health_payload: dict,
    get_text: Callable[[str, str], str],
    health_value_label: Callable[[str | None, str], str],
    format_optional_ts: Callable[[str | None, str], str],
    format_age_seconds: Callable[[str | None], str],
    format_metric_number: Callable[..., str],
    ws_freshness_label_from_ts: Callable[[str | None, str], str],
) -> None:
    with live_shell.render_folded_section(
        get_text(lang, "health_section_current_state"),
        expanded=False,
    ):
        import streamlit as st

        def bool_flag_label(flag: bool) -> str:
            return get_text(lang, "health_value_on") if flag else get_text(lang, "health_value_off")

        st.caption(
            build_health_digest_current_state_caption(
                widget=health_digest_widget,
                payload=health_digest_payload,
            )
        )

        digest_block_captions = build_health_digest_block_captions(
            widget=health_digest_widget,
            payload=health_digest_payload,
        )
        st.caption(
            "collector_ingestion_observability: "
            + digest_block_captions["collector_ingestion_observability"]
        )
        st.caption(
            "market_runtime_truth: "
            + digest_block_captions["market_runtime_truth"]
        )
        st.caption(
            "semantic_observability: "
            + digest_block_captions["semantic_observability"]
        )
        st.caption(
            "orderbook_active_event_observability: "
            + digest_block_captions["orderbook_active_event_observability"]
        )

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric(
            get_text(lang, "health_metric_status"),
            health_value_label(status_payload.get("mode"), lang),
            runtime_kind.upper() if runtime_kind else None,
        )
        m2.metric(
            get_text(lang, "health_metric_wait_ms"),
            get_text(lang, "health_table_empty_value")
            if not bitflyer_rate
            else health_value_label(runtime_mode, lang),
        )
        m3.metric(
            get_text(lang, "health_metric_util_ratio"),
            get_text(lang, "health_table_empty_value")
            if not bitflyer_rate
            else format_metric_number(
                runtime_utilization if runtime_utilization is not None else bitflyer_rate.get("util_ratio"),
                decimals=1,
                percent=True,
            ),
        )
        m4.metric(
            get_text(lang, "health_metric_last_429"),
            format_optional_ts(bitflyer_rate.get("last_429_ts"), lang),
        )
        m5.metric(
            get_text(lang, "health_metric_hold_until"),
            format_optional_ts(bitflyer_rate.get("hold_until_ts"), lang)
            if runtime_mode == "CRIT"
            else "-",
        )

        st.markdown(f"##### {get_text(lang, 'health_label_ws_board_exec_section')}")

        nb1, nb2, nb3, nb4, nb5 = st.columns(5)
        nb1.metric(
            get_text(lang, "health_metric_ws_board_state"),
            health_value_label(
                ws_board_lane.get("ws_state") or origin_payload.get("ws_state"),
                lang,
            ),
            ws_board_state if ws_board_state else None,
        )
        nb2.metric(
            get_text(lang, "health_metric_ws_board_freshness"),
            health_value_label(
                ws_board_lane.get("ws_freshness")
                or ws_freshness_label_from_ts(
                    ws_board_lane.get("last_event_ts") or origin_payload.get("ts"),
                    lang,
                ),
                lang,
            ),
        )
        nb3.metric(
            get_text(lang, "health_metric_ws_board_last_update"),
            format_optional_ts(
                ws_board_lane.get("last_event_ts") or origin_payload.get("ts"),
                lang,
            ),
        )
        nb4.metric(
            get_text(lang, "health_metric_ws_board_age_sec"),
            format_age_seconds(
                ws_board_lane.get("last_event_ts") or origin_payload.get("ts"),
            ),
        )
        nb5.metric(
            get_text(lang, "health_metric_ws_board_restart"),
            format_metric_number(ws_board_lane.get("restart_count")),
            ws_board_last_error if ws_board_last_error else None,
        )

        ne1, ne2, ne3, ne4, ne5 = st.columns(5)
        ne1.metric(
            get_text(lang, "health_metric_ws_exec_state"),
            health_value_label(
                ws_executions_lane.get("ws_state") or executions_payload.get("ws_state"),
                lang,
            ),
            ws_executions_state if ws_executions_state else None,
        )
        ne2.metric(
            get_text(lang, "health_metric_ws_exec_freshness"),
            health_value_label(
                ws_executions_lane.get("ws_freshness")
                or health_payload.get("ws_executions_freshness")
                or ws_freshness_label_from_ts(
                    ws_executions_lane.get("last_event_ts")
                    or ws_executions_lane.get("connected_ts")
                    or executions_payload.get("last_event_ts")
                    or executions_payload.get("connected_ts")
                    or executions_payload.get("ts"),
                    lang,
                ),
                lang,
            ),
        )
        ne3.metric(
            get_text(lang, "health_metric_ws_exec_last_update"),
            format_optional_ts(
                ws_executions_lane.get("last_event_ts")
                or ws_executions_lane.get("connected_ts")
                or executions_payload.get("last_event_ts")
                or executions_payload.get("connected_ts")
                or executions_payload.get("ts"),
                lang,
            ),
        )
        ne4.metric(
            get_text(lang, "health_metric_ws_exec_age_sec"),
            format_age_seconds(
                ws_executions_lane.get("last_event_ts")
                or ws_executions_lane.get("connected_ts")
                or executions_payload.get("last_event_ts")
                or executions_payload.get("connected_ts")
                or executions_payload.get("ts"),
            ),
        )
        ne5.metric(
            get_text(lang, "health_metric_ws_exec_trades"),
            format_metric_number(
                ws_executions_lane.get("trade_count")
                if ws_executions_lane
                else executions_payload.get("trade_count"),
            ),
            ws_executions_last_error if ws_executions_last_error else None,
        )

        n1, n2, n3 = st.columns(3)
        n1.metric(
            get_text(lang, "health_metric_snapshot_to_live"),
            format_metric_number(origin_payload.get("snapshot_to_live_ms")),
        )
        n2.metric(
            get_text(lang, "health_metric_resync"),
            bool_flag_label(bool(origin_payload.get("resync_active"))),
            bool_flag_label(bool(origin_payload.get("gap_detected"))),
        )
        n3.metric(
            get_text(lang, "health_metric_last_sequence_id"),
            format_metric_number(checkpoint_payload.get("last_sequence_id")),
        )

        p1, p2, p3, p4, p5, p6 = st.columns(6)
        p1.metric(
            get_text(lang, "health_metric_boundary_reason"),
            health_value_label(market_latest.get("boundary_reason"), lang),
        )
        p2.metric(
            get_text(lang, "health_metric_interpretation"),
            health_value_label(
                market_latest.get("interpretation_bucket")
                or market_diag.get("preferred_row_interpretation_bucket"),
                lang,
            ),
        )
        p3.metric(
            get_text(lang, "health_metric_daemon_status"),
            health_value_label(daemon_status_payload.get("mode"), lang),
        )
        p4.metric(
            get_text(lang, "health_metric_daemon_last_error"),
            str(daemon_status_payload.get("last_error") or "-"),
            ws_board_last_error if ws_board_last_error else None,
        )
        p5.metric(
            get_text(lang, "health_metric_daemon_failures"),
            format_metric_number(
                daemon_health_payload.get("consecutive_failures")
                if daemon_health_payload
                else None
            ),
        )
        p6.metric(
            get_text(lang, "health_metric_daemon_last_success"),
            format_optional_ts(daemon_health_payload.get("last_success_ts"), lang),
            format_optional_ts(origin_payload.get("ts"), lang),
        )


def render_recent_events_section(
    *,
    lang: str,
    recent_anomalies: list[dict],
    get_text: Callable[[str, str], str],
    health_event_label: Callable[[str | None, str], str],
) -> None:
    with live_shell.render_folded_section(
        get_text(lang, "health_section_recent_events"),
        expanded=False,
    ):
        import streamlit as st

        if not recent_anomalies:
            st.info(get_text(lang, "health_value_no_data"))
            return

        events_df = pd.DataFrame(recent_anomalies)

        if "ts" in events_df.columns:
            events_df["ts"] = events_df["ts"].apply(lambda x: format_ui_ts(x, lang=lang))
        if "event" in events_df.columns:
            events_df["event"] = events_df["event"].apply(lambda x: health_event_label(x, lang))
        if "reason" in events_df.columns:
            events_df["reason"] = events_df["reason"].apply(lambda x: health_event_label(x, lang))
        if "topic" in events_df.columns:
            events_df["topic"] = events_df["topic"].apply(lambda x: health_event_label(x, lang))
        if "exchange" in events_df.columns:
            events_df["exchange"] = events_df["exchange"].apply(lambda x: health_event_label(x, lang))

        events_df = events_df.rename(
            columns={
                "ts": get_text(lang, "health_table_ts"),
                "event": get_text(lang, "health_table_event"),
                "topic": get_text(lang, "health_table_topic"),
                "reason": get_text(lang, "health_table_reason"),
                "exchange": get_text(lang, "health_table_exchange"),
            }
        )

        st.dataframe(events_df, width="stretch", hide_index=True)