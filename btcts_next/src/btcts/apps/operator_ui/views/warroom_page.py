# path: ./btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py
# desc: Replay / Research artifact を基に市場分析と AI 解釈を行う War Room 専用ページ。

from __future__ import annotations

from typing import Callable
import json
import streamlit as st

from btcts.apps.operator_ui.components import agent_panels
from btcts.apps.operator_ui.components import ai_conversation_panel
from btcts.apps.operator_ui.components import ai_market_summary_panel
from btcts.apps.operator_ui.components import ai_reasoning_panel
from btcts.apps.operator_ui.components import ai_operator_panel
from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components import ai_signal_panel
from btcts.apps.operator_ui.components import liquidity_pressure_panel
from btcts.apps.operator_ui.components import market_monitor
from btcts.apps.operator_ui.components import market_regime_panel
from btcts.apps.operator_ui.components import risk_monitor_panel
from btcts.apps.operator_ui.components import strategy_state_panel
from btcts.apps.operator_ui.components import trade_flow_monitor
from btcts.apps.operator_ui.components import watch_list_panel
from btcts.apps.operator_ui.components import warroom_header
from btcts.apps.operator_ui.components import warroom_timeline
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_execution_market_summary_status_payload,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    active_event_compact_reading_line,
)
from btcts.apps.operator_ui.components.evidence_presentation_panel import (
    render_evidence_presentation_panel,
)
from btcts.apps.operator_ui.components.evidence_presentation_lowering_bridge import (
    lower_warroom_session_state_evidence_presentation_for_ui,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.components import warroom_alert_engine
from btcts.apps.operator_ui.components import decision_log_panel
from btcts.apps.operator_ui.components.live_shell import get_registered_slots
from btcts.apps.operator_ui.components.slot_definitions import (
    WarroomGraphWidgetBundle,
    warroom_chart_sensitive,
    warroom_chart_sensitive_count,
    warroom_graph_overlay_contract,
    warroom_graph_widget_bundle,
    warroom_graph_widget_ids,
    warroom_layout_hints,
    warroom_overlay_contract_count,
    warroom_overlay_enabled,
    warroom_overlay_widget_ids,
    warroom_partial_update_enabled,
    warroom_first_partial_redraw_candidate,
    warroom_refresh_mode_counts,
    warroom_refresh_policy,
    warroom_rerender_scope_counts,
    warroom_all_widget_ids,
    warroom_widget_slot,
    warroom_widget_zone_ids,
)


_GRAPH_WIDGET_RENDERERS = {
    "market_monitor": market_monitor.render,
    "liquidity_pressure": liquidity_pressure_panel.render,
    "trade_flow_monitor": trade_flow_monitor.render,
}


def _warroom_reading_block_order() -> tuple[str, ...]:
    return (
        "current_market_summary_reading",
        "current_active_event_reading",
        "current_tactic_prediction_reading",
        "operator_support_review_reading",
    )


def _warroom_reading_block_captions() -> dict[str, str]:
    return {
        "current_market_summary_reading": (
            "read current regime / source / compact market state first"
        ),
        "current_active_event_reading": (
            "read active event / liquidity / graph context as current market evidence"
        ),
        "current_tactic_prediction_reading": (
            "read tactic stance / prediction as review support, not execution"
        ),
        "operator_support_review_reading": (
            "read watch / timeline / decision support as operator review context"
        ),
    }


def _warroom_active_event_reading_caption() -> str:
    summary_payload = load_execution_market_summary_status_payload()
    return active_event_compact_reading_line(summary_payload)


def _warroom_evidence_presentation_payload() -> dict | None:
    """Return bridge-normalized evidence presentation payload from session_state only."""
    for key in (
        "warroom_evidence_presentation_payload",
        "health_warroom_evidence_presentation_payload",
        "real_data_validation_evidence_presentation",
        "evidence_presentation_payload",
    ):
        payload = st.session_state.get(key)
        if isinstance(payload, dict):
            lowered = lower_warroom_session_state_evidence_presentation_for_ui(st.session_state, payload)
            normalized_payload = lowered.get("warroom_evidence_presentation_payload")
            return normalized_payload if isinstance(normalized_payload, dict) else payload
    return None



def _render_warroom_scrollable_json_block(payload: object, *, max_height_px: int = 280) -> None:
    """Render existing WarRoom diagnostics payload as read-only presentation JSON."""
    live_shell.render_scrollable_text_block(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        max_height_px=max_height_px,
        monospace=True,
    )



def _warroom_diagnostics_enabled(*, key: str, label: str) -> bool:
    enabled = bool(st.checkbox(label, value=False, key=key))
    if not enabled:
        st.caption(
            "diagnostics rendering is paused by default; enable this checkbox "
            "only when inspecting this diagnostic block."
        )
    return enabled

def _render_warroom_reading_caption(text: str, *, max_height_px: int = 120) -> None:
    """Render WarRoom reading captions as wrapped, local-scroll, operator review text."""
    live_shell.render_scrollable_text_block(
        text,
        max_height_px=max_height_px,
        monospace=True,
    )

def _render_warroom_primary_reading_overview(
    *,
    fragment_enabled: bool,
) -> None:
    _render_fragmentable_warroom_widget(
        "warroom_header",
        warroom_header.render,
        fragment_enabled=fragment_enabled,
    )

    with live_shell.slot_widget_from_meta(
        warroom_widget_slot("warroom_alert_engine")
    ):
        warroom_alert_engine.render()

    with live_shell.slot_widget_from_meta(
        warroom_widget_slot("ai_operator_panel")
    ):
        ai_operator_panel.render()


def _render_warroom_active_event_and_graph_reading(
    *,
    fragment_enabled: bool,
) -> None:
    _render_fragmentable_warroom_widget(
        "market_regime",
        market_regime_panel.render,
        fragment_enabled=fragment_enabled,
    )

    graph_widget_bundles = [
        warroom_graph_widget_bundle(widget_id)
        for widget_id in warroom_graph_widget_ids()
    ]
    for bundle in graph_widget_bundles:
        _render_graph_widget_bundle(
            bundle,
            fragment_enabled=fragment_enabled,
        )


def _render_warroom_tactic_prediction_reading(
    *,
    fragment_enabled: bool,
) -> None:
    _render_fragmentable_warroom_widget(
        "ai_signal",
        ai_signal_panel.render,
        fragment_enabled=fragment_enabled,
    )

    _render_fragmentable_warroom_widget(
        "strategy_state",
        strategy_state_panel.render,
        fragment_enabled=fragment_enabled,
    )

    _render_fragmentable_warroom_widget(
        "risk_monitor",
        risk_monitor_panel.render,
        fragment_enabled=fragment_enabled,
    )

    _render_fragmentable_warroom_widget(
        "agent_panels",
        agent_panels.render,
        fragment_enabled=fragment_enabled,
    )


def _render_warroom_operator_support_review() -> None:
    with live_shell.slot_widget_from_meta(
        warroom_widget_slot("decision_log_panel")
    ):
        decision_log_panel.render()

    with live_shell.slot_widget_from_meta(
        warroom_widget_slot("watch_list_panel")
    ):
        watch_list_panel.render()

    with live_shell.slot_widget_from_meta(
        warroom_widget_slot("warroom_timeline")
    ):
        warroom_timeline.render()


def _render_warroom_evidence_presentation() -> None:
    evidence_payload = _warroom_evidence_presentation_payload()
    render_evidence_presentation_panel(evidence_payload, expanded=False)


def _render_fragmentable_warroom_widget(
    widget_id: str,
    render_body: Callable[[], None],
    *,
    fragment_enabled: bool = False,
) -> None:
    slot_meta = warroom_widget_slot(widget_id)

    if fragment_enabled:
        live_shell.render_fragment_slot(
            slot_meta,
            render_body,
            enabled=True,
        )
        return

    with live_shell.slot_widget_from_meta(slot_meta):
        render_body()


def _render_graph_widget_bundle(
    bundle: WarroomGraphWidgetBundle,
    *,
    fragment_enabled: bool = False,
) -> None:
    renderer = _GRAPH_WIDGET_RENDERERS.get(str(bundle["widget_id"]))
    if renderer is None:
        return

    widget_id = str(bundle["widget_id"])
    slot_meta = bundle["slot_meta"]

    def _render_body() -> None:
        renderer(
            overlay_contract=bundle["overlay_contract"],
        )

    if (
        fragment_enabled
        and warroom_partial_update_enabled(widget_id)
        and warroom_chart_sensitive(widget_id)
    ):
        live_shell.render_fragment_slot(
            slot_meta,
            _render_body,
            enabled=True,
        )
        return

    with live_shell.slot_widget_from_meta(slot_meta):
        _render_body()


def _expected_warroom_widget_ids() -> set[str]:
    return set(warroom_all_widget_ids())


def _missing_registered_widget_ids(slot_rows: list[dict]) -> list[str]:
    actual_widget_ids = {str(row.get("widget_id")) for row in slot_rows}
    return sorted(_expected_warroom_widget_ids().difference(actual_widget_ids))


def _unexpected_registered_zone_ids(slot_rows: list[dict]) -> list[str]:
    actual_zone_ids = {
        str(row.get("zone_id"))
        for row in slot_rows
        if row.get("zone_id") is not None
    }
    return sorted(actual_zone_ids.difference(set(warroom_widget_zone_ids())))


def _warroom_refresh_diagnostics_summary(
    *,
    default_sec: int = 15,
) -> dict[str, int | bool]:
    graph_fragment_widget_ids = [
        widget_id
        for widget_id in warroom_graph_widget_ids()
        if (
            warroom_partial_update_enabled(widget_id)
            and warroom_chart_sensitive(widget_id)
        )
    ]
    non_graph_fragment_widget_ids = [
        "warroom_header",
        "market_regime",
        "ai_signal",
        "strategy_state",
        "risk_monitor",
        "agent_panels",
    ]
    fragment_widget_ids = [
        *non_graph_fragment_widget_ids,
        *graph_fragment_widget_ids,
    ]

    fragment_modes = [
        str(warroom_widget_slot(widget_id).get("refresh_mode", "static"))
        for widget_id in non_graph_fragment_widget_ids
    ] + [
        str(warroom_refresh_policy(widget_id).get("mode", "static"))
        for widget_id in graph_fragment_widget_ids
    ]

    fragment_interval_sec = (
        min(
            live_shell.refresh_mode_interval_sec(
                mode,
                default_sec=default_sec,
            )
            for mode in fragment_modes
        )
        if fragment_modes
        else int(default_sec)
    )
    page_reload_interval_sec = live_shell.page_non_fragment_refresh_interval_sec(
        "warroom",
        default_sec=default_sec,
    )

    return {
        "fragment_widget_count": len(fragment_widget_ids),
        "fragment_interval_sec": int(fragment_interval_sec),
        "page_reload_interval_sec": int(page_reload_interval_sec),
        "hybrid_refresh": bool(fragment_widget_ids),
    }


def render():
    _render_warroom_page_body()


def _render_warroom_page_body() -> None:
    lang = st.session_state.get("ui_lang", "en")
    fragment_enabled = bool(st.session_state.get("ui_auto_refresh", True))

    live_shell.render_compact_page_header(get_text(lang, "warroom_title"))

    with live_shell.render_folded_section(get_text(lang, "ui_label_guide"), expanded=False):
        st.caption(
            get_text(lang, "warroom_caption")
        )

    with live_shell.zone_container(
        label=get_text(lang, "ui_label_overview"),
        zone_kind="overview",
    ):
        block_captions = _warroom_reading_block_captions()
        _render_warroom_reading_caption(
            "warroom_reading_blocks="
            + " > ".join(_warroom_reading_block_order()),
            max_height_px=90,
        )
        _render_warroom_reading_caption(
            "current_market_summary_reading: "
            + block_captions["current_market_summary_reading"],
            max_height_px=90,
        )
        _render_warroom_primary_reading_overview(
            fragment_enabled=fragment_enabled,
        )

    with live_shell.zone_container(
        label=get_text(lang, "ui_label_primary_live"),
        zone_kind="primary_live",
    ):
        block_captions = _warroom_reading_block_captions()
        _render_warroom_reading_caption(
            "current_active_event_reading: "
            + block_captions["current_active_event_reading"],
            max_height_px=90,
        )
        _render_warroom_reading_caption(
            "active_event_compact: "
            + _warroom_active_event_reading_caption(),
            max_height_px=120,
        )
        _render_warroom_active_event_and_graph_reading(
            fragment_enabled=fragment_enabled,
        )
        _render_warroom_reading_caption(
            "current_tactic_prediction_reading: "
            + block_captions["current_tactic_prediction_reading"],
            max_height_px=90,
        )
        _render_warroom_tactic_prediction_reading(
            fragment_enabled=fragment_enabled,
        )

    with live_shell.zone_container(
        label=get_text(lang, "ui_label_operator_support"),
        zone_kind="secondary",
    ):
        block_captions = _warroom_reading_block_captions()
        _render_warroom_reading_caption(
            "operator_support_review_reading: "
            + block_captions["operator_support_review_reading"],
            max_height_px=90,
        )
        _render_warroom_operator_support_review()
        with live_shell.slot_widget_from_meta(
            warroom_widget_slot("evidence_presentation_panel")
        ):
            _render_warroom_evidence_presentation()

    with live_shell.render_folded_section(get_text(lang, "ui_slot_diagnostics_title"), expanded=False):
        if _warroom_diagnostics_enabled(
            key="warroom_run_slot_diagnostics",
            label="Run WarRoom slot diagnostics",
        ):
            slot_rows = get_registered_slots("warroom")
            if slot_rows:
                st.dataframe(slot_rows, width="stretch")

                overlay_rows = [
                    row
                    for row in slot_rows
                    if row.get("overlay_enabled")
                ]
                partial_update_rows = [
                    row
                    for row in slot_rows
                    if row.get("partial_update_enabled")
                ]
                st.caption(
                    get_text(
                        lang,
                        "warroom_overlay_enabled_widgets_caption",
                    ).format(
                        count=len(overlay_rows),
                        total=warroom_overlay_contract_count(),
                    )
                )
                st.caption(
                    get_text(
                        lang,
                        "warroom_partial_update_enabled_widgets_caption",
                    ).format(
                        count=len(partial_update_rows),
                        total=warroom_overlay_contract_count(),
                    )
                )
                missing_widget_ids = _missing_registered_widget_ids(slot_rows)
                if missing_widget_ids:
                    st.warning(
                        "missing slot registrations: " + ", ".join(missing_widget_ids)
                    )

                unexpected_zone_ids = _unexpected_registered_zone_ids(slot_rows)
                if unexpected_zone_ids:
                    st.warning(
                        "unexpected zone ids: " + ", ".join(unexpected_zone_ids)
                    )
            else:
                st.info(get_text(lang, "ui_slot_registry_empty_warroom"))

    with live_shell.render_folded_section(
        get_text(lang, "warroom_graph_overlay_diagnostics_title"),
        expanded=False,
    ):
        if _warroom_diagnostics_enabled(
            key="warroom_run_graph_overlay_diagnostics",
            label="Run WarRoom graph overlay diagnostics",
        ):
            overlay_diag = {
                widget_id: {
                    "overlay_enabled": warroom_overlay_enabled(widget_id),
                    "partial_update_enabled": warroom_partial_update_enabled(widget_id),
                    "refresh_policy": warroom_refresh_policy(widget_id),
                    "chart_sensitive": warroom_chart_sensitive(widget_id),
                    "overlay_contract": warroom_graph_overlay_contract(widget_id),
                    "layout_hints": warroom_layout_hints(widget_id),
                }
                for widget_id in warroom_overlay_widget_ids()
            }
            _render_warroom_scrollable_json_block(overlay_diag, max_height_px=320)
            st.caption(
                get_text(
                    lang,
                    "warroom_overlay_diagnostics_targets_caption",
                ).format(
                    count=warroom_overlay_contract_count(),
                )
            )
            st.caption(
                get_text(
                    lang,
                    "warroom_chart_sensitive_widgets_caption",
                ).format(
                    count=warroom_chart_sensitive_count(),
                )
            )
            st.caption(
                get_text(
                    lang,
                    "warroom_refresh_modes_caption",
                ).format(
                    counts=warroom_refresh_mode_counts(),
                )
            )
            refresh_diag = _warroom_refresh_diagnostics_summary()
            if refresh_diag["hybrid_refresh"]:
                st.caption(
                    get_text(
                        lang,
                        "warroom_hybrid_refresh_caption",
                    )
                )
            st.caption(
                get_text(
                    lang,
                    "warroom_fragment_refresh_caption",
                ).format(
                    count=refresh_diag["fragment_widget_count"],
                    interval=refresh_diag["fragment_interval_sec"],
                )
            )
            st.caption(
                get_text(
                    lang,
                    "warroom_page_reload_refresh_caption",
                ).format(
                    interval=refresh_diag["page_reload_interval_sec"],
                )
            )
            st.caption(
                "rerender scope counts: "
                + str(warroom_rerender_scope_counts())
            )
            first_candidate = warroom_first_partial_redraw_candidate()
            if first_candidate is not None:
                st.caption(
                    "first partial redraw candidate: "
                    + first_candidate
                )
                if first_candidate == "market_monitor":
                    st.caption(
                        "W3 entry fixed: market_monitor"
                    )

    with live_shell.render_folded_section(get_text(lang, "ui_label_ai_diagnostics"), expanded=False):
        if _warroom_diagnostics_enabled(
            key="warroom_run_ai_diagnostics",
            label="Run WarRoom AI diagnostics",
        ):
            with live_shell.slot_widget_from_meta(
                warroom_widget_slot("ai_reasoning_panel")
            ):
                ai_reasoning_panel.render()

            with live_shell.slot_widget_from_meta(
                warroom_widget_slot("ai_market_summary_panel")
            ):
                ai_market_summary_panel.render()

            with live_shell.slot_widget_from_meta(
                warroom_widget_slot("ai_conversation_panel")
            ):
                ai_conversation_panel.render()
