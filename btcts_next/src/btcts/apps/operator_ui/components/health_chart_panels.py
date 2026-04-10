# path: ./btcts_next/src/btcts/apps/operator_ui/components/health_chart_panels.py
# desc: Health ページの chart panel 群を外出しした helper。

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from btcts.apps.operator_ui.components import live_shell


def render_api_chart_panel(
    *,
    lang: str,
    range_key: str,
    api_ws_series: list[dict],
    rate_overlay: list[dict],
    bitflyer_rate: dict,
    bitflyer_rate_snapshot: dict,
    bitflyer_rate_trades: dict,
    get_text: Callable[[str, str], str],
    section_title_with_range: Callable[[str, str], str],
    format_metric_number: Callable[..., str],
    api_chart_columns_and_labels: Callable[[pd.DataFrame, str], tuple[list[str], dict[str, str]]],
) -> None:
    with live_shell.panel_container(
        label=section_title_with_range(
            get_text(lang, "health_section_api_chart"),
            range_key,
        ),
        tone="primary",
    ):
        if not api_ws_series:
            import streamlit as st

            st.info(get_text(lang, "health_value_no_data"))
            return

        import streamlit as st

        api_df = pd.DataFrame(api_ws_series)
        api_df["ts"] = pd.to_datetime(api_df["ts"], utc=True)

        latest_api = api_df.iloc[-1].to_dict() if not api_df.empty else {}
        api_metric_mode = str(latest_api.get("api_metric_mode") or "short")

        a1, a2, a3, a4 = st.columns(4)
        if api_metric_mode == "short":
            a1.metric(
                get_text(lang, "health_metric_req_1m"),
                "-" if not bitflyer_rate else format_metric_number(bitflyer_rate.get("requests_60s")),
            )
            a2.metric(
                get_text(lang, "health_metric_req_5m"),
                "-" if not bitflyer_rate else format_metric_number(bitflyer_rate.get("requests_300s")),
            )
            a3.metric(
                get_text(lang, "health_metric_req_snapshot_1m"),
                "-" if not bitflyer_rate_snapshot else format_metric_number(bitflyer_rate_snapshot.get("requests_60s")),
            )
            a4.metric(
                get_text(lang, "health_metric_req_trades_1m"),
                "-" if not bitflyer_rate_trades else format_metric_number(bitflyer_rate_trades.get("requests_60s")),
            )
        else:
            a1.metric(
                get_text(lang, "health_chart_api_events"),
                format_metric_number(latest_api.get("api_events")),
            )
            a2.metric(
                get_text(lang, "health_chart_warn_error_events"),
                format_metric_number(latest_api.get("warn_error_events")),
            )
            a3.metric(
                get_text(lang, "health_chart_429_events"),
                format_metric_number(latest_api.get("events_429")),
            )
            a4.metric(
                get_text(lang, "health_metric_budget_300s"),
                "-" if not bitflyer_rate else format_metric_number(bitflyer_rate.get("requests_300s")),
            )

        api_chart_columns, api_chart_labels = api_chart_columns_and_labels(api_df, lang)
        if api_chart_columns:
            api_chart_df = api_df.set_index("ts")[api_chart_columns].rename(columns=api_chart_labels)
            st.line_chart(api_chart_df, height=260, width="stretch")
        else:
            st.info(get_text(lang, "health_value_no_data"))

        if rate_overlay:
            overlay_df = pd.DataFrame(rate_overlay)
            overlay_df["ts"] = pd.to_datetime(overlay_df["ts"], utc=True)

            o1, o2, o3, o4 = st.columns(4)
            latest_overlay = overlay_df.iloc[-1].to_dict() if not overlay_df.empty else {}

            o1.metric(
                get_text(lang, "health_metric_budget_60s"),
                format_metric_number(latest_overlay.get("budget_60s")),
            )
            o2.metric(
                get_text(lang, "health_metric_budget_300s"),
                format_metric_number(latest_overlay.get("budget_300s")),
            )
            o3.metric(
                get_text(lang, "health_metric_target_ratio"),
                format_metric_number(latest_overlay.get("target_utilization"), decimals=1, percent=True),
            )
            o4.metric(
                get_text(lang, "health_metric_hard_cap_ratio"),
                format_metric_number(latest_overlay.get("hard_cap_utilization"), decimals=1, percent=True),
            )

            if api_metric_mode == "short":
                overlay_chart_df = overlay_df.set_index("ts")[
                    [
                        "utilization",
                        "active_target_ratio",
                        "target_utilization",
                        "hard_cap_utilization",
                    ]
                ].rename(
                    columns={
                        "utilization": get_text(lang, "health_chart_current_utilization"),
                        "active_target_ratio": get_text(lang, "health_chart_active_target_ratio"),
                        "target_utilization": get_text(lang, "health_chart_target_utilization"),
                        "hard_cap_utilization": get_text(lang, "health_chart_hard_cap_utilization"),
                    }
                )
                st.line_chart(overlay_chart_df, height=220, width="stretch")
            else:
                st.caption(get_text(lang, "health_chart_api_overlay_current_only_short_caption"))

        st.caption(get_text(lang, "health_chart_api_caption"))
        if api_metric_mode != "short":
            st.caption(get_text(lang, "health_chart_api_long_range_caption"))
            st.caption(get_text(lang, "health_chart_api_overlay_current_only_caption"))
        st.caption(get_text(lang, "health_chart_unfinished_bucket_caption"))


def render_ws_chart_panel(
    *,
    lang: str,
    range_key: str,
    api_ws_series: list[dict],
    get_text: Callable[[str, str], str],
    section_title_with_range: Callable[[str, str], str],
    format_metric_number: Callable[..., str],
) -> None:
    with live_shell.panel_container(
        label=section_title_with_range(
            get_text(lang, "health_section_ws_chart"),
            range_key,
        ),
        tone="primary",
    ):
        import streamlit as st

        if not api_ws_series:
            st.info(get_text(lang, "health_value_no_data"))
            return

        ws_df = pd.DataFrame(api_ws_series)
        ws_df["ts"] = pd.to_datetime(ws_df["ts"], utc=True)

        latest_ws = ws_df.iloc[-1].to_dict() if not ws_df.empty else {}

        w1, w2, w3 = st.columns(3)
        w1.metric(
            get_text(lang, "health_metric_ws_events_1m"),
            "-" if not latest_ws else format_metric_number(latest_ws.get("ws_events")),
        )
        w2.metric(
            get_text(lang, "health_metric_gap_1m"),
            "-" if not latest_ws else format_metric_number(latest_ws.get("gap_events")),
        )
        w3.metric(
            get_text(lang, "health_metric_resync_1m"),
            "-" if not latest_ws else format_metric_number(latest_ws.get("resync_events")),
        )

        ws_chart_df = ws_df.set_index("ts")[
            [
                "ws_events",
                "ws_exec_events",
                "gap_events",
                "resync_events",
            ]
        ].rename(
            columns={
                "ws_events": get_text(lang, "health_chart_ws_events"),
                "ws_exec_events": get_text(lang, "health_chart_ws_exec_events"),
                "gap_events": get_text(lang, "health_chart_gap_events"),
                "resync_events": get_text(lang, "health_chart_resync_events"),
            }
        )
        st.line_chart(ws_chart_df, height=220, width="stretch")
        st.caption(get_text(lang, "health_chart_ws_caption"))
        st.caption(get_text(lang, "health_chart_unfinished_bucket_caption"))


def render_layer3_chart_panel(
    *,
    lang: str,
    range_key: str,
    layer3_series: list[dict],
    layer3_semantic_usage_rows: list[dict],
    layer3_semantic_usage_summary: dict,
    layer3_runtime_contract_summary: dict,
    layer3_orderbook_runtime_summary: dict,
    market_latest: dict,
    market_diag: dict,
    get_text: Callable[[str, str], str],
    section_title_with_range: Callable[[str, str], str],
    health_value_label: Callable[[str | None, str], str],
) -> None:
    with live_shell.panel_container(
        label=section_title_with_range(
            get_text(lang, "health_section_layer3_chart"),
            range_key,
        ),
        tone="primary",
    ):
        import streamlit as st

        if not layer3_series:
            st.info(get_text(lang, "health_value_no_data"))
            return

        def bool_label(flag: bool) -> str:
            return get_text(lang, "health_value_yes") if flag else get_text(lang, "health_value_no")

        l1, l2, l3, l4 = st.columns(4)
        l1.metric(
            get_text(lang, "health_metric_trust_state"),
            health_value_label(
                market_latest.get("trust_state") or market_diag.get("preferred_row_trust_state"),
                lang,
            ),
        )
        l2.metric(
            get_text(lang, "health_metric_continuity_state"),
            health_value_label(
                market_latest.get("continuity_state") or market_diag.get("preferred_row_continuity_state"),
                lang,
            ),
        )
        l3.metric(
            get_text(lang, "health_metric_interpretation"),
            health_value_label(
                market_latest.get("interpretation_bucket")
                or market_diag.get("preferred_row_interpretation_bucket"),
                lang,
            ),
        )
        l4.metric(
            get_text(lang, "health_metric_freshness"),
            health_value_label(market_diag.get("preferred_row_freshness"), lang),
        )

        if range_key == "1h":
            layer3_df = pd.DataFrame(layer3_series)
            layer3_df["ts"] = pd.to_datetime(layer3_df["ts"], utc=True)
            layer3_chart_df = layer3_df.set_index("ts")[
                [
                    "trust_score",
                    "continuity_score",
                    "interpretation_score",
                    "freshness_score",
                ]
            ].rename(
                columns={
                    "trust_score": get_text(lang, "health_chart_trust_score"),
                    "continuity_score": get_text(lang, "health_chart_continuity_score"),
                    "interpretation_score": get_text(lang, "health_chart_interpretation_score"),
                    "freshness_score": get_text(lang, "health_chart_freshness_score"),
                }
            )
            st.line_chart(layer3_chart_df, height=220, width="stretch")
        else:
            st.caption(get_text(lang, "health_chart_layer3_current_only_caption"))

        if layer3_runtime_contract_summary:
            r1, r2, r3, r4 = st.columns(4)
            r1.metric(
                get_text(lang, "health_label_runtime_wiring"),
                health_value_label(
                    str(layer3_runtime_contract_summary.get("wiring_status") or "-"),
                    lang,
                ),
            )
            r2.metric(
                get_text(lang, "health_label_observer_field"),
                bool_label(bool(layer3_runtime_contract_summary.get("observer_present"))),
            )
            r3.metric(
                get_text(lang, "health_label_summary_field"),
                bool_label(bool(layer3_runtime_contract_summary.get("usage_summary_present"))),
            )
            r4.metric(
                get_text(lang, "health_label_source_series"),
                bool_label(bool(layer3_runtime_contract_summary.get("source_series_present"))),
            )
            st.caption(
                get_text(lang, "health_caption_runtime_freshness_prefix")
                + str(layer3_runtime_contract_summary.get("freshness") or "UNKNOWN")
            )

        if layer3_orderbook_runtime_summary:
            st.caption(
                get_text(lang, "health_caption_orderbook_source_prefix")
                + str(layer3_orderbook_runtime_summary.get("contract_status_source") or "unknown")
            )
            st.caption(
                get_text(lang, "health_caption_orderbook_freshness_prefix")
                + str(layer3_orderbook_runtime_summary.get("freshness") or "UNKNOWN")
            )

            o1, o2, o3, o4, o5, o6 = st.columns(6)
            o1.metric(
                get_text(lang, "health_label_orderbook_wiring"),
                health_value_label(
                    str(layer3_orderbook_runtime_summary.get("wiring_status") or "-"),
                    lang,
                ),
            )
            o2.metric(
                get_text(lang, "health_label_present_count"),
                int(layer3_orderbook_runtime_summary.get("present_count") or 0),
            )
            o3.metric(
                get_text(lang, "health_label_near_wall"),
                bool_label(bool(layer3_orderbook_runtime_summary.get("near_wall_present"))),
            )
            o4.metric(
                get_text(lang, "health_label_support"),
                bool_label(bool(layer3_orderbook_runtime_summary.get("support_present"))),
            )
            o5.metric(
                get_text(lang, "health_label_resistance"),
                bool_label(bool(layer3_orderbook_runtime_summary.get("resistance_present"))),
            )
            o6.metric(
                get_text(lang, "health_label_persistence"),
                bool_label(bool(layer3_orderbook_runtime_summary.get("persistence_present"))),
            )

            st.caption(
                get_text(lang, "health_label_near_wall_side")
                + "="
                + str(layer3_orderbook_runtime_summary.get("near_wall_side") or "-")
                + " / "
                + get_text(lang, "health_label_support_side")
                + "="
                + str(layer3_orderbook_runtime_summary.get("support_side") or "-")
                + " / "
                + get_text(lang, "health_label_resistance_side")
                + "="
                + str(layer3_orderbook_runtime_summary.get("resistance_side") or "-")
                + " / "
                + get_text(lang, "health_label_persistence_event")
                + "="
                + str(layer3_orderbook_runtime_summary.get("persistence_event_name") or "-")
                + " / "
                + get_text(lang, "health_label_persistence_side")
                + "="
                + str(layer3_orderbook_runtime_summary.get("persistence_side") or "-")
                + " / "
                + get_text(lang, "health_label_persistence_observable")
                + "="
                + bool_label(bool(layer3_orderbook_runtime_summary.get("persistence_observable")))
            )

            if str(layer3_orderbook_runtime_summary.get("wiring_status") or "") == "partial":
                st.caption(get_text(lang, "health_caption_orderbook_partial_meaning"))

            active_event_names = layer3_orderbook_runtime_summary.get("active_event_names") or []
            if not isinstance(active_event_names, list):
                active_event_names = []

            st.caption(
                get_text(lang, "health_caption_orderbook_active_events_prefix")
                + (
                    ", ".join(str(name) for name in active_event_names if str(name).strip())
                    if active_event_names
                    else get_text(lang, "health_value_none_boundary")
                )
            )

            active_event_contracts = layer3_orderbook_runtime_summary.get("active_event_contracts") or []
            if not isinstance(active_event_contracts, list):
                active_event_contracts = []

            contract_parts: list[str] = []
            for event in active_event_contracts:
                if not isinstance(event, dict):
                    continue
                event_name = str(event.get("event_name") or "").strip()
                if not event_name:
                    continue
                event_family = str(event.get("event_family") or "unknown")
                usage_grade = str(event.get("usage_grade") or "unknown")
                side = str(event.get("side") or "-")
                contract_parts.append(
                    f"{event_name}[family={event_family}, grade={usage_grade}, side={side}]"
                )

            st.caption(
                get_text(lang, "health_caption_orderbook_active_contracts_prefix")
                + (
                    ", ".join(contract_parts[:6])
                    if contract_parts
                    else get_text(lang, "health_value_none_boundary")
                )
            )

        if layer3_semantic_usage_summary:
            st.caption(
                get_text(lang, "health_caption_semantic_source_prefix")
                + str(layer3_semantic_usage_summary.get("source_kind") or "unknown")
            )

            s1, s2, s3, s4, s5 = st.columns(5)
            s1.metric(
                get_text(lang, "health_label_semantic_observer"),
                str(layer3_semantic_usage_summary.get("observer_status") or "-"),
            )
            s2.metric(
                get_text(lang, "health_label_strong"),
                int(layer3_semantic_usage_summary.get("strong_count") or 0),
            )
            s3.metric(
                get_text(lang, "health_label_watch"),
                int(
                    (layer3_semantic_usage_summary.get("watch_count") or 0)
                    + (layer3_semantic_usage_summary.get("watch_weak_count") or 0)
                ),
            )
            s4.metric(
                get_text(lang, "health_label_tentative"),
                int(layer3_semantic_usage_summary.get("tentative_count") or 0),
            )
            s5.metric(
                get_text(lang, "health_label_invalid"),
                int(layer3_semantic_usage_summary.get("invalid_count") or 0),
            )

        if layer3_semantic_usage_rows:
            usage_df = pd.DataFrame(layer3_semantic_usage_rows)
            usage_df = usage_df[
                [
                    "event_family",
                    "usage_grade",
                ]
            ]
            st.dataframe(usage_df, width="stretch")

        st.caption(get_text(lang, "health_chart_layer3_caption"))
        st.caption(get_text(lang, "health_chart_unfinished_bucket_caption"))