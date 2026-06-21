# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py
# desc: PS-Q12B Streamlit read-only panel that connects the PS-Q12A latest prediction source adapter to the top/default-expanded WarRoom prediction review section. It may read D-hot latest prediction JSON through PS-Q12A only; no runtime writes, AutoTrade, broker, mode, approval, or ledger behavior.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

import streamlit as st

from .prediction_warroom_latest_prediction_source_adapter import (
    LATEST_PREDICTION_SOURCE_ADAPTER_VERSION,
    build_prediction_warroom_latest_prediction_source_adapter,
)

PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION = "prediction_warroom_latest_prediction_source_review_panel.ps_q12b.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def latest_prediction_source_status_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Return compact operator-readable PS-Q12B source status rows without rendering."""
    data = _as_mapping(packet)
    summary = _as_mapping(data.get("source_summary"))
    return [
        {
            "name": "adapter_state",
            "value": data.get("adapter_state"),
            "operator_note_ja": "latest prediction source adapter の状態",
            "read_only": True,
            "execution": "false",
        },
        {
            "name": "prediction_run_id",
            "value": summary.get("prediction_run_id"),
            "operator_note_ja": "表示対象の推論 run id",
            "read_only": True,
            "execution": "false",
        },
        {
            "name": "generated_at",
            "value": summary.get("generated_at"),
            "operator_note_ja": "推論生成時刻",
            "read_only": True,
            "execution": "false",
        },
        {
            "name": "market_uid",
            "value": summary.get("market_uid"),
            "operator_note_ja": "対象マーケット",
            "read_only": True,
            "execution": "false",
        },
        {
            "name": "signal_strength",
            "value": f"{summary.get('signal_strength_percent')} / {summary.get('signal_strength_band')}",
            "operator_note_ja": "推論シグナル強度",
            "read_only": True,
            "execution": "false",
        },
        {
            "name": "review_packet_ready",
            "value": data.get("review_packet_ready"),
            "operator_note_ja": "Q9G 表示用 review packet の準備状態",
            "read_only": True,
            "execution": "false",
        },
        {
            "name": "session_state_updated",
            "value": data.get("session_state_updated"),
            "operator_note_ja": "既存 Q9G panel へ渡す session_state handoff 状態",
            "read_only": True,
            "execution": "false",
        },
    ]


def latest_prediction_source_boundary_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Return PS-Q12B safety boundary rows without rendering."""
    data = _as_mapping(packet)
    return [
        {"boundary": "top_default_expanded_review_panel", "enabled": True},
        {"boundary": "ps_q12a_adapter_called", "enabled": data.get("q9b_loader_called_by_this_adapter") is True},
        {"boundary": "actual_file_read_attempted", "enabled": data.get("actual_file_read_attempted") is True},
        {"boundary": "payload_decode_attempted", "enabled": data.get("payload_decode_attempted") is True},
        {"boundary": "review_packet_session_handoff", "enabled": data.get("session_state_updated") is True},
        {"boundary": "warroom_page_mutation", "enabled": False},
        {"boundary": "runtime_artifact_write", "enabled": False},
        {"boundary": "approval_or_authorization", "enabled": False},
        {"boundary": "decision_or_command_ledger_append", "enabled": False},
        {"boundary": "autotrade_trigger", "enabled": False},
        {"boundary": "broker_private_api", "enabled": False},
    ]


def build_prediction_warroom_latest_prediction_source_review_panel_packet(
    *,
    session_state: MutableMapping[str, Any] | None,
    allow_actual_read: bool = True,
    store_in_session_state: bool = True,
) -> dict[str, Any]:
    """Build the PS-Q12B panel packet and optionally seed Q9G session_state via PS-Q12A/Q10K."""
    adapter_packet = build_prediction_warroom_latest_prediction_source_adapter(
        allow_actual_read=allow_actual_read,
        session_state=session_state,
        store_in_session_state=store_in_session_state,
    ).to_dict()
    ready = bool(adapter_packet.get("ready_for_warroom_review_panel")) and bool(adapter_packet.get("session_state_updated"))
    return {
        "panel_version": PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION,
        "panel_id": f"{PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION}:latest:{'ready' if ready else 'blocked'}",
        "panel_state": "latest_prediction_source_review_panel_ready" if ready else "latest_prediction_source_review_panel_blocked",
        "adapter_version": LATEST_PREDICTION_SOURCE_ADAPTER_VERSION,
        "adapter_packet": adapter_packet,
        "status_rows": latest_prediction_source_status_rows(adapter_packet),
        "boundary_rows": latest_prediction_source_boundary_rows(adapter_packet),
        "top_default_expanded_review_panel_connected": True,
        "q9g_session_state_seed_attempted": store_in_session_state,
        "q9g_session_state_seed_ready": ready,
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "warroom_page_mutation_allowed": False,
        "warroom_panel_mutation_allowed": False,
        "runtime_artifact_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "authorization_grant_requested": False,
        "autotrade_trigger_enabled": False,
    }


def render_prediction_warroom_latest_prediction_source_review_panel() -> Mapping[str, Any]:
    """Render PS-Q12B read-only source status and seed existing Q9G panel through session_state."""
    panel = build_prediction_warroom_latest_prediction_source_review_panel_packet(
        session_state=st.session_state,
        allow_actual_read=True,
        store_in_session_state=True,
    )
    adapter = _as_mapping(panel.get("adapter_packet"))
    st.caption(
        "PS-Q12B latest prediction source is read-only and display-only: "
        "D-hot latest prediction JSON may be read/decode via PS-Q12A, but no runtime write, "
        "no approval, no ledger, no AutoTrade, no broker/private API."
    )
    st.caption(
        "panel_version={panel}; panel_state={state}; adapter_state={adapter_state}; "
        "loaded_payloads={loaded}; review_ready={review_ready}; session_handoff={handoff}".format(
            panel=PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION,
            state=panel.get("panel_state"),
            adapter_state=adapter.get("adapter_state"),
            loaded=adapter.get("loaded_payload_count"),
            review_ready=adapter.get("review_packet_ready"),
            handoff=adapter.get("session_state_updated"),
        )
    )
    rows = _list(panel.get("status_rows"))
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    boundary_rows = _list(panel.get("boundary_rows"))
    if boundary_rows:
        st.dataframe(boundary_rows, width="stretch", hide_index=True)
    blockers = _list(adapter.get("blocked_reasons"))
    warnings = _list(adapter.get("warning_reasons"))
    if blockers:
        st.caption("latest_prediction_source_blocked_reasons=" + ", ".join(str(item) for item in blockers))
    if warnings:
        st.caption("latest_prediction_source_warning_reasons=" + ", ".join(str(item) for item in warnings))
    return panel
