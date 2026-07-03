# path: ./btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py
# desc: Replay / Research artifact を基に市場分析と AI 解釈を行う War Room 専用ページ。

from __future__ import annotations

from datetime import datetime, timezone
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

# Backward-compatible alias for existing WarRoom refresh-path tests and callers.
# The execution-market loader remains the canonical implementation.
load_market_summary_status_payload = load_execution_market_summary_status_payload
from btcts.apps.operator_ui.components.market_summary_presenter import (
    active_event_compact_reading_line,
)
from btcts.apps.operator_ui.components.evidence_presentation_panel import (
    render_evidence_presentation_panel,
)
from btcts.apps.operator_ui.components.evidence_presentation_lowering_bridge import (
    lower_warroom_session_state_evidence_presentation_for_ui,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (
    build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (
    render_latest_prediction_warroom_display_panel,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (
    render_warroom_live_market_nowcast_panel,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_operator_focus_nav_panel import (
    render_warroom_operator_focus_nav,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (
    render_warroom_market_regime_card_shell,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_sections import (
    render_warroom_focus_section,
)
from btcts.apps.operator_ui.prediction_warroom.panels import warroom_latest_prediction_quick_status_panel as quick_status_panel
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.prediction_warroom.v2.transport import (
    WARROOM_V2_OPERATOR_DIAGNOSTIC_OBSERVATION_STATE_KEY,
    WARROOM_V2_OPERATOR_VISIBLE_PANEL_OBSERVATION_STATE_KEY,
    WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY,
    WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_STATE_KEY,
    WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_STATE_KEY,
    WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_STATE_KEY,
    WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY,
    WARROOM_V2_SHADOW_RENDERER_OBSERVATION_STATE_KEY,
    WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_STATE_KEY,
    WARROOM_V2_STREAMLIT_SHADOW_STATE_KEY,
    build_warroom_v2_operator_diagnostic_observation_packet,
    build_warroom_v2_operator_visible_panel_observation_packet,
    build_warroom_v2_operator_visible_panel_gate_observation_packet,
    build_warroom_v2_ws_display_adapter_observation_packet,
    build_warroom_v2_ws_display_client_observation_packet,
    build_warroom_v2_ws_display_connection_status_observation_packet,
    build_warroom_v2_operator_review_observation_packet,
    build_warroom_v2_shadow_renderer_observation_packet,
    build_warroom_v2_streamlit_local_loop_observation_packet,
    build_warroom_v2_streamlit_shadow_integration_packet,
)
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


WARROOM_HEADER_LEGACY_SECTION_JAPANESE_LOCALIZATION_VERSION = "prediction_warroom.header_legacy_section_japanese_localization.ps_q26d.v1"
WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_VERSION = "prediction_warroom.top_reading_caption_japanese_localization.ps_q26h.v1"
WARROOM_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_VERSION = "prediction_warroom.allowed_tech_term_label_help_text.ps_q26k.v1"
WARROOM_MARKET_REGIME_CARD_PREVIEW_ENABLEMENT_VERSION = "prediction_warroom.market_regime_card_preview_enablement.ps_q27p.v1"
WARROOM_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT_HINT = r"D:\\btc_ts_hot"
_GRAPH_WIDGET_RENDERERS = {
    "market_monitor": market_monitor.render,
    "liquidity_pressure": liquidity_pressure_panel.render,
    "trade_flow_monitor": trade_flow_monitor.render,
}



def _warroom_utc_now_iso_q27p() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_warroom_market_regime_card_preview_enablement_packet(
    *,
    preview_enabled: bool = True,
    operator_confirmed_read_only: bool = True,
    hot_root: str | None = WARROOM_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT_HINT,
    generated_at: str = "",
) -> dict:
    """Return render kwargs for the market-regime card preview gate.

    Default is real D-hot read-only preview for personal WarRoom use. The
    operator can turn the existing checkbox off to fall back to sample cards.
    """
    requested = bool(preview_enabled)
    confirmed = bool(operator_confirmed_read_only)
    root = "" if hot_root is None else str(hot_root)
    enabled = bool(requested and confirmed and root)
    if not requested:
        disabled_reason = "preview_checkbox_off"
    elif not confirmed:
        disabled_reason = "operator_read_only_confirmation_required"
    elif not root:
        disabled_reason = "explicit_hot_root_required"
    else:
        disabled_reason = ""
    render_kwargs = {
        "preview_enabled": False,
        "hot_root": None,
        "generated_at": generated_at,
    }
    if enabled:
        render_kwargs = {
            "preview_enabled": True,
            "hot_root": root,
            "generated_at": generated_at,
        }
    return {
        "ok": True,
        "enablement_version": WARROOM_MARKET_REGIME_CARD_PREVIEW_ENABLEMENT_VERSION,
        "market_regime_only": True,
        "preview_enabled_requested": requested,
        "operator_confirmed_read_only": confirmed,
        "preview_enabled_effective": enabled,
        "disabled_reason": disabled_reason,
        "render_kwargs": render_kwargs,
        "warroom_page_preview_default_on": True,
        "explicit_operator_checkbox_required": False,
        "explicit_source_root_required": True,
        "explicit_source_root_read_allowed": enabled,
        "disabled_path_reads_root": False,
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
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
            "現在の市場summary / source / compact market state を最初に確認します"
        ),
        "current_active_event_reading": (
            "現在のactive event / liquidity / graph context を市場証拠として確認します"
        ),
        "current_tactic_prediction_reading": (
            "予測はreview補助として読みます。実行指示ではありません（tactic stance は参考情報です）"
        ),
        "operator_support_review_reading": (
            "watch / timeline / decision support はoperator reviewの文脈として確認します"
        ),
    }


def _warroom_active_event_reading_caption() -> str:
    summary_payload = load_market_summary_status_payload()
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


def _prediction_warroom_display_fragment_enabled(*, page_fragment_enabled: bool) -> bool:
    """Keep the WarRoom prediction display refreshing by default, independent of broad page reload."""
    return bool(
        page_fragment_enabled
        or st.session_state.get("warroom_prediction_auto_refresh_enabled", True)
    )


def _bool_display(value: object) -> str:
    return quick_status_panel._bool_display(value)


# PS-Q26R compatibility wrappers: implementation moved to warroom_latest_prediction_quick_status_panel.
# Legacy searchable markers intentionally remain in warroom_page.py:
# PS_Q18AU_OBSERVATION_QUICK_STATUS
# Prediction WarRoom latest summary observation quick status

def _q26d_localize_observation_value(value: object) -> object:
    return quick_status_panel._q26d_localize_observation_value(value)


def _q26d_prediction_observation_quick_status_rows(packet: dict) -> list[dict]:
    return quick_status_panel._q26d_prediction_observation_quick_status_rows(packet)


def _q26d_prediction_observation_plain_text(packet: dict) -> str:
    return quick_status_panel._q26d_prediction_observation_plain_text(packet)


def build_warroom_q26d_header_legacy_section_localization_packet() -> dict:
    return quick_status_panel.build_warroom_q26d_header_legacy_section_localization_packet()


def _q26h_bool_ja(value: object) -> str:
    return quick_status_panel._q26h_bool_ja(value)


def _q26h_observation_plain_text(packet: dict) -> str:
    return quick_status_panel._q26h_observation_plain_text(packet)


def _q26h_observation_quick_status_rows(packet: dict) -> list[dict]:
    return quick_status_panel._q26h_observation_quick_status_rows(packet)


def build_warroom_q26h_top_reading_caption_japanese_localization_packet() -> dict:
    return quick_status_panel.build_warroom_q26h_top_reading_caption_japanese_localization_packet()


def warroom_allowed_tech_term_help_rows() -> list[dict]:
    return quick_status_panel.warroom_allowed_tech_term_help_rows()


def build_warroom_q26k_allowed_tech_term_label_help_text_packet() -> dict:
    return quick_status_panel.build_warroom_q26k_allowed_tech_term_label_help_text_packet()


def _prediction_warroom_latest_prediction_observation_cleanup_summary_packet(
    *,
    q18aj_packet: dict | object | None,
    q18ak_packet: dict | object | None,
) -> dict:
    return quick_status_panel._prediction_warroom_latest_prediction_observation_cleanup_summary_packet(
        q18aj_packet=q18aj_packet,
        q18ak_packet=q18ak_packet,
    )


def _prediction_warroom_latest_prediction_observation_cleanup_summary_rows(packet: dict) -> list[dict]:
    return quick_status_panel._prediction_warroom_latest_prediction_observation_cleanup_summary_rows(packet)


def _render_prediction_warroom_latest_prediction_observation_cleanup_summary_section(*, fragment_enabled: bool) -> None:
    return quick_status_panel._render_prediction_warroom_latest_prediction_observation_cleanup_summary_section(
        fragment_enabled=fragment_enabled,
    )


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




def _record_warroom_v2_transport_shadow_integration_state(*, fragment_enabled: bool, prediction_fragment_enabled: bool) -> None:
    # Hidden session_state key: warroom_v2_transport_shadow_integration_q31e
    fragment_summary = dict(_warroom_refresh_diagnostics_summary())
    fragment_summary["page_fragment_enabled"] = bool(fragment_enabled)
    fragment_summary["prediction_fragment_enabled"] = bool(prediction_fragment_enabled)
    st.session_state[WARROOM_V2_STREAMLIT_SHADOW_STATE_KEY] = build_warroom_v2_streamlit_shadow_integration_packet(
        fragment_summary=fragment_summary,
        messages=[],
        consumer_state=None,
        subscribed_topics=None,
        frame_id="warroom-page-shadow",
    )
    # Hidden session_state key: warroom_v2_streamlit_local_loop_observation_q31i
    st.session_state[WARROOM_V2_STREAMLIT_LOCAL_LOOP_OBSERVATION_STATE_KEY] = build_warroom_v2_streamlit_local_loop_observation_packet(
        fragment_summary=fragment_summary,
        messages=[],
        consumer_state=None,
    )
    # Hidden session_state key: warroom_v2_shadow_renderer_observation_q31m
    st.session_state[WARROOM_V2_SHADOW_RENDERER_OBSERVATION_STATE_KEY] = build_warroom_v2_shadow_renderer_observation_packet(
        fragment_summary=fragment_summary,
        messages=[],
        consumer_state=None,
    )
    # Hidden session_state key: warroom_v2_operator_review_observation_q31o
    st.session_state[WARROOM_V2_OPERATOR_REVIEW_OBSERVATION_STATE_KEY] = build_warroom_v2_operator_review_observation_packet(
        fragment_summary=fragment_summary,
        messages=[],
        consumer_state=None,
    )
    # Hidden session_state key: warroom_v2_operator_diagnostic_observation_q31r
    st.session_state[WARROOM_V2_OPERATOR_DIAGNOSTIC_OBSERVATION_STATE_KEY] = build_warroom_v2_operator_diagnostic_observation_packet(
        fragment_summary=fragment_summary,
        messages=[],
        consumer_state=None,
        visible_diagnostic_requested=False,
        operator_read_only_ack=False,
    )
    # Hidden session_state key: warroom_v2_operator_visible_panel_observation_q31u
    st.session_state[WARROOM_V2_OPERATOR_VISIBLE_PANEL_OBSERVATION_STATE_KEY] = build_warroom_v2_operator_visible_panel_observation_packet(
        fragment_summary=fragment_summary,
        messages=[],
        consumer_state=None,
        visible_diagnostic_requested=False,
        diagnostic_read_only_ack=False,
        operator_visible_panel_requested=False,
        operator_read_only_ack=False,
    )
    # Hidden session_state key: warroom_v2_operator_visible_panel_gate_observation_q31w
    st.session_state[WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY] = build_warroom_v2_operator_visible_panel_gate_observation_packet(
        fragment_summary=fragment_summary,
        messages=[],
        consumer_state=None,
        visible_diagnostic_requested=False,
        diagnostic_read_only_ack=False,
        operator_visible_panel_requested=False,
        operator_visible_panel_read_only_ack=False,
        visible_panel_gate_requested=False,
        visible_panel_gate_read_only_ack=False,
    )
    # Hidden session_state key: warroom_v2_ws_display_adapter_observation_q31z
    st.session_state[WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_STATE_KEY] = build_warroom_v2_ws_display_adapter_observation_packet(
        fragment_summary=fragment_summary,
        messages=[],
    )
    # Hidden session_state key: warroom_v2_ws_display_client_observation_q32b
    st.session_state[WARROOM_V2_WS_DISPLAY_CLIENT_OBSERVATION_STATE_KEY] = build_warroom_v2_ws_display_client_observation_packet(
        fragment_summary=fragment_summary,
        messages=[],
    )
    # Hidden session_state key: warroom_v2_ws_display_connection_status_observation_q32d
    st.session_state[WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_STATE_KEY] = build_warroom_v2_ws_display_connection_status_observation_packet(
        fragment_summary=fragment_summary,
        messages=[],
    )

def _warroom_operator_first_render_path_cleanup_packet() -> dict:
    """Return PS-Q18AZ normal UI cleanup state; keeps reusable legacy code out of normal render path."""
    return {
        "ok": True,
        "cleanup_version": "prediction_warroom.q18az_operator_first_render_path_cleanup.v1",
        "cleanup_state": "normal_warroom_ui_operator_first_dev_preflight_sections_removed",
        "normal_ui_path_operator_first": True,
        "latest_prediction_quick_status_kept": True,
        "prediction_warroom_dev_preflight_sections_rendered_in_normal_path": False,
        "legacy_dev_helpers_deleted_this_slice": False,
        "future_extension_contracts_preserved": True,
        "removed_from_normal_ui_path": [
            "Prediction WarRoom real payload review",
            "Prediction WarRoom disabled widget skeleton review",
            "Prediction WarRoom source readiness preflight",
            "Prediction WarRoom source read probe status",
            "Prediction WarRoom latest summary props candidate status",
            "Prediction WarRoom latest summary render-disabled packet status",
            "Prediction WarRoom latest summary mapped payload render-disabled packet status",
            "Prediction WarRoom latest summary mapped payload values",
            "Prediction WarRoom latest summary operator value summary",
            "Prediction WarRoom latest summary real source handoff preflight",
            "Prediction WarRoom latest summary safe display mount",
            "Prediction WarRoom mount review",
        ],
        "removed_section_count": 12,
        "preserved_for_future_extension": [
            "latest_prediction_payload_contracts",
            "payload_to_widget_props_mapping_contract",
            "latest_prediction_summary_widget_props_schema",
            "bounded_refresh_packet_builder",
            "freshness_fallback_packet_builder",
            "real_render_implementation_gate_docs",
            "rollback_to_skeleton_contract",
            "manual_ui_smoke_contract_pattern",
        ],
        "real_prediction_widget_rendering_allowed": False,
        "real_prediction_widget_render_invoked": False,
        "streamlit_real_widget_render_invoked": False,
        "component_runtime_binding_allowed": False,
        "component_props_bound_to_runtime": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "next_safe_slice": "PS-Q18BA WarRoom legacy prediction dev helper/import prune",
    }


def _record_warroom_operator_first_render_path_cleanup_state() -> None:
    st.session_state["warroom_operator_first_render_path_cleanup"] = (
        _warroom_operator_first_render_path_cleanup_packet()
    )


def render():
    _render_warroom_page_body()


def _render_warroom_page_body() -> None:
    lang = st.session_state.get("ui_lang", "en")
    fragment_enabled = bool(st.session_state.get("ui_auto_refresh", True))

    live_shell.render_compact_page_header(get_text(lang, "warroom_title"))

    with render_warroom_focus_section("operator_focus_nav"):
        render_warroom_operator_focus_nav()

    with render_warroom_focus_section("market_regime_card_sample"):
        market_regime_preview_enabled = bool(
            st.checkbox(
                "地合い preview",
                value=True,
                key="warroom_market_regime_card_preview_enabled_q27p",
            )
        )
        market_regime_preview_enablement_packet = build_warroom_market_regime_card_preview_enablement_packet(
            preview_enabled=market_regime_preview_enabled,
            operator_confirmed_read_only=market_regime_preview_enabled,
            hot_root=WARROOM_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT_HINT,
            generated_at=_warroom_utc_now_iso_q27p(),
        )
        st.session_state["warroom_market_regime_card_preview_enablement_q27p"] = dict(
            market_regime_preview_enablement_packet
        )
        render_warroom_market_regime_card_shell(
            **market_regime_preview_enablement_packet["render_kwargs"]
        )

    with live_shell.render_folded_section(get_text(lang, "ui_label_guide"), expanded=False):
        st.caption(
            get_text(lang, "warroom_caption")
        )

    prediction_fragment_enabled = _prediction_warroom_display_fragment_enabled(page_fragment_enabled=fragment_enabled)


    _record_warroom_v2_transport_shadow_integration_state(
        fragment_enabled=fragment_enabled,
        prediction_fragment_enabled=prediction_fragment_enabled,
    )

    # Prediction WarRoom latest summary observation quick status
    with render_warroom_focus_section("prediction_quick_status_detail"):
        _render_prediction_warroom_latest_prediction_observation_cleanup_summary_section(fragment_enabled=prediction_fragment_enabled)

    with render_warroom_focus_section("live_nowcast"):
        render_warroom_live_market_nowcast_panel(fragment_enabled=fragment_enabled)

    with render_warroom_focus_section("latest_prediction_read_model"):
        render_latest_prediction_warroom_display_panel(fragment_enabled=prediction_fragment_enabled)

    _record_warroom_operator_first_render_path_cleanup_state()

    with render_warroom_focus_section("header_alert_operator"):
        _render_warroom_primary_reading_overview(
            fragment_enabled=fragment_enabled,
        )

    with render_warroom_focus_section("market_evidence_detail"):
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

    with render_warroom_focus_section("operator_support_detail"):
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
