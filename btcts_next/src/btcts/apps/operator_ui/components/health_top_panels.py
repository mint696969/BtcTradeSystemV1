# path: ./btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py
# desc: Health ページ上部の guide / summary / continuity 群を外出しした helper。

from __future__ import annotations

from collections.abc import Callable
import html

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components.health_continuity import (
    render_continuity_legend,
    render_continuity_rail,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    active_event_compact_reading_line,
)
from btcts.apps.operator_ui.components.slot_definitions import health_widget_slot


def render_read_guide_section(
    *,
    lang: str,
    get_text: Callable[[str, str], str],
) -> None:
    with live_shell.render_folded_section(
        get_text(lang, "health_section_read_guide"),
        expanded=False,
    ):
        st.caption(f"1. {get_text(lang, 'health_read_guide_line1')}")
        st.caption(f"2. {get_text(lang, 'health_read_guide_line2')}")
        st.caption(f"3. {get_text(lang, 'health_read_guide_line3')}")



def _health_summary_level(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if not normalized or normalized in {"-", "unknown", "データなし", "no data"}:
        return "gray"
    if any(token in normalized for token in ("危険", "critical", "error", "failed", "broken", "down", "disconnected")):
        return "red"
    if any(token in normalized for token in ("注意", "warning", "warn", "stale", "degraded", "backoff")):
        return "yellow"
    if any(token in normalized for token in ("正常", "healthy", "running", "normal", "live", "ok")):
        return "green"
    return "gray"


def _render_health_summary_card(*, title: str, value: str, details: list[str]) -> None:
    palette = {
        "green": ("#16a34a", "#f0fdf4", "#86efac"),
        "yellow": ("#a16207", "#fefce8", "#fde047"),
        "red": ("#dc2626", "#fef2f2", "#fca5a5"),
        "gray": ("#6b7280", "#f8fafc", "#cbd5e1"),
    }
    level = _health_summary_level(value)
    accent, background, border = palette[level]
    detail_text = " / ".join(str(item).strip() for item in details if str(item).strip())
    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    safe_detail = html.escape(detail_text)
    card_html = (
        f'<div style="box-sizing:border-box;height:88px;border:1px solid {border};'
        f'border-left:4px solid {accent};border-radius:8px;background:{background};'
        'padding:8px 10px;overflow:hidden;">'
        f'<div style="font-size:0.875rem;line-height:1.15;color:#374151;margin-bottom:2px;">{safe_title}</div>'
        f'<div style="font-size:1.25rem;line-height:1.2;font-weight:500;color:{accent};margin-bottom:4px;">{safe_value}</div>'
        '<div style="font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;'
        'font-size:0.78rem;line-height:1.25;color:#4b5563;display:-webkit-box;'
        '-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere;">'
        f'{safe_detail}</div></div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def _render_health_summary_card_styles() -> None:
    # Styles are intentionally inline so Streamlit reruns/fragments cannot drop card styling.
    return


def render_collector_summary_metric(
    *,
    lang: str,
    status_payload: dict,
    health_payload: dict,
    get_text: Callable[[str, str], str],
    collector_summary_label: Callable[[dict, dict, str], str],
    digest_caption: str | None = None,
) -> None:
    _render_health_summary_card(
        title=get_text(lang, "health_summary_collector"),
        value=collector_summary_label(status_payload, health_payload, lang),
        details=[digest_caption or ""],
    )


def render_api_summary_metric(
    *,
    lang: str,
    bitflyer_rate: dict,
    get_text: Callable[[str, str], str],
    api_summary_label: Callable[[dict, str], str],
    digest_caption: str | None = None,
) -> None:
    _render_health_summary_card(
        title=get_text(lang, "health_summary_api"),
        value=api_summary_label(bitflyer_rate, lang),
        details=[digest_caption or ""],
    )


def render_ws_summary_metric(
    *,
    lang: str,
    origin_payload: dict,
    get_text: Callable[[str, str], str],
    ws_summary_label: Callable[[dict, str], str],
    digest_caption: str | None = None,
) -> None:
    _render_health_summary_card(
        title=get_text(lang, "health_summary_ws"),
        value=ws_summary_label(origin_payload, lang),
        details=[digest_caption or ""],
    )


def build_health_digest_layer3_summary_caption(
    *,
    widget,
    payload: dict | None,
) -> str:
    if widget is None or not payload:
        return "health_digest unavailable"

    semantic_block = dict(payload.get("semantic_observability") or {})
    orderbook_block = dict(payload.get("orderbook_active_event_observability") or {})

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
    persistence_observable = bool(
        orderbook_block.get(
            "persistence_observable",
            payload.get("orderbook_persistence_observable"),
        )
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
    active_event_compact_rows = int(
        orderbook_block.get(
            "active_event_compact_rows_count",
            payload.get("orderbook_active_event_compact_rows_count"),
        )
        or 0
    )
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
        f"persistence_observable={persistence_observable} / "
        f"semantic_rows={semantic_rows} / "
        f"summary_slots={summary_slots} / "
        f"slots_present={slots_present} / "
        f"active_events={active_events} / "
        f"active_event_names={active_event_names} / "
        f"active_event_compact_rows={active_event_compact_rows} / "
        f"active_event_rows={active_event_rows} / "
        f"age={age_text} / "
        f"event_ts={event_ts}"
    )


def build_health_digest_operational_reading_caption(
    *,
    widget,
    payload: dict | None,
) -> str:
    if widget is None or not payload:
        return "health_operational_reading unavailable"

    orderbook_block = dict(payload.get("orderbook_active_event_observability") or {})

    trust = str(getattr(widget, "trust_key", None) or "unknown")
    continuity = str(getattr(widget, "continuity_key", None) or "unknown")
    interpretation = str(getattr(widget, "interpretation_key", None) or "unknown")
    observer_status = str(getattr(widget, "semantic_observer_status_key", None) or "unknown")
    source_kind = str(getattr(widget, "source_kind", None) or "unknown")

    active_event_line = active_event_compact_reading_line(
        {
            "orderbook_active_event_compact_rows": list(
                orderbook_block.get("active_event_compact_rows")
                or payload.get("orderbook_active_event_compact_rows")
                or []
            ),
            "orderbook_active_event_contracts": list(
                orderbook_block.get("active_event_contracts")
                or payload.get("orderbook_active_event_contracts")
                or []
            ),
            "orderbook_active_event_names": list(
                orderbook_block.get("active_event_names")
                or getattr(widget, "orderbook_active_event_names", [])
                or []
            ),
        }
    )

    return (
        f"health_operational_reading={interpretation} / "
        f"trust={trust} / "
        f"continuity={continuity} / "
        f"observer_status={observer_status} / "
        f"active_event={active_event_line} / "
        f"source={source_kind} / "
        "review_mode=operator_review_only / "
        "execution=not_instruction"
    )


def build_health_digest_collector_summary_caption(
    *,
    widget,
    payload: dict | None,
) -> str:
    if widget is None or not payload:
        return "health_digest unavailable"

    collector_runtime = dict(payload.get("collector_runtime") or {})
    collector_mode = str(getattr(widget, "collector_mode_key", None) or "unknown")
    collector_ok = getattr(widget, "collector_ok", None)
    runtime_kind = str(collector_runtime.get("runtime_kind") or "unknown")

    return (
        f"mode={collector_mode} / "
        f"ok={collector_ok} / "
        f"runtime_kind={runtime_kind}"
    )


def build_health_digest_api_summary_caption(
    *,
    widget,
    payload: dict | None,
) -> str:
    if widget is None or not payload:
        return "health_digest unavailable"

    api_runtime = dict(payload.get("api_runtime") or {})
    api_mode = str(getattr(widget, "api_mode_key", None) or "unknown")
    utilization = api_runtime.get("utilization")
    requests_60s = int(api_runtime.get("requests_60s") or 0)

    util_text = "-" if utilization is None else f"{float(utilization) * 100:.1f}%"
    return (
        f"mode={api_mode} / "
        f"utilization={util_text} / "
        f"requests_60s={requests_60s}"
    )


def build_health_digest_ws_summary_caption(
    *,
    widget,
    payload: dict | None,
) -> str:
    if widget is None or not payload:
        return "health_digest unavailable"

    ws_runtime = dict(payload.get("ws_runtime") or {})
    board_state = str(getattr(widget, "ws_board_state_key", None) or "unknown")
    executions_state = str(getattr(widget, "ws_executions_state_key", None) or "unknown")
    board_freshness = str(ws_runtime.get("board_freshness") or "UNKNOWN")
    executions_freshness = str(ws_runtime.get("executions_freshness") or "UNKNOWN")

    return (
        f"board={board_state} ({board_freshness}) / "
        f"exec={executions_state} ({executions_freshness})"
    )


def render_layer3_summary_metric(
    *,
    lang: str,
    market_latest: dict,
    market_diag: dict,
    get_text: Callable[[str, str], str],
    layer3_summary_label: Callable[[dict, dict, str], str],
    digest_caption: str | None = None,
    operational_reading_caption: str | None = None,
) -> None:
    _render_health_summary_card(
        title=get_text(lang, "health_summary_layer3"),
        value=layer3_summary_label(market_latest, market_diag, lang),
        details=[digest_caption or "", operational_reading_caption or ""],
    )


def render_overview_summary_panel(
    *,
    lang: str,
    status_payload: dict,
    health_payload: dict,
    bitflyer_rate: dict,
    origin_payload: dict,
    market_latest: dict,
    market_diag: dict,
    get_text: Callable[[str, str], str],
    collector_summary_label: Callable[[dict, dict, str], str],
    api_summary_label: Callable[[dict, str], str],
    ws_summary_label: Callable[[dict, str], str],
    layer3_summary_label: Callable[[dict, dict, str], str],
) -> None:
    _render_health_summary_card_styles()
    c1, c2, c3, c4 = live_shell.responsive_columns(4, compact=True)

    with c1:
        with live_shell.slot_widget_from_meta(
            health_widget_slot("collector_summary")
        ):
            render_collector_summary_metric(
                lang=lang,
                status_payload=status_payload,
                health_payload=health_payload,
                get_text=get_text,
                collector_summary_label=collector_summary_label,
            )

    with c2:
        with live_shell.slot_widget_from_meta(
            health_widget_slot("api_summary")
        ):
            render_api_summary_metric(
                lang=lang,
                bitflyer_rate=bitflyer_rate,
                get_text=get_text,
                api_summary_label=api_summary_label,
            )

    with c3:
        with live_shell.slot_widget_from_meta(
            health_widget_slot("ws_summary")
        ):
            render_ws_summary_metric(
                lang=lang,
                origin_payload=origin_payload,
                get_text=get_text,
                ws_summary_label=ws_summary_label,
            )

    with c4:
        with live_shell.slot_widget_from_meta(
            health_widget_slot("layer3_summary")
        ):
            render_layer3_summary_metric(
                lang=lang,
                market_latest=market_latest,
                market_diag=market_diag,
                get_text=get_text,
                layer3_summary_label=layer3_summary_label,
            )


def render_continuity_panels(
    *,
    lang: str,
    range_key: str,
    api_continuity_rail: list[dict],
    ws_continuity_rail: list[dict],
    get_text: Callable[[str, str], str],
    section_title_with_range: Callable[[str, str], str],
) -> None:
    with live_shell.slot_widget_from_meta(
        health_widget_slot("api_continuity_panel")
    ):
        if api_continuity_rail:
            render_continuity_rail(
                api_continuity_rail,
                lang,
                range_key=range_key,
                show_legend=False,
            )
        else:
            st.info(get_text(lang, "health_value_no_data"))

    with live_shell.slot_widget_from_meta(
        health_widget_slot("ws_continuity_panel")
    ):
        if ws_continuity_rail:
            render_continuity_rail(
                ws_continuity_rail,
                lang,
                range_key=range_key,
                show_legend=False,
            )
        else:
            st.info(get_text(lang, "health_value_no_data"))

    if api_continuity_rail or ws_continuity_rail:
        render_continuity_legend(range_key=range_key, lang=lang)
        st.caption(
            (
                "API REST / WS Board / WS Executions の連続性を見ます。"
                "セル幅は表示レンジに合わせて、1分・30分・3時間へ切り替わります。"
                "緑=安定、黄=注意、橙=不安定、赤=危険、灰=データなし。"
            )
            if lang == "ja"
            else (
                "This summarizes continuity for API REST, WS Board, and WS Executions. "
                "Cell duration follows the selected range: 1 minute, 30 minutes, or 3 hours. "
                "Green=stable, yellow=attention, "
                "orange=unstable, red=danger, gray=no data."
            )
        )