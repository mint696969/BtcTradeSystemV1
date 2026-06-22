# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py
# desc: PS-Q12B/PS-Q12G Streamlit read-only panel that connects the PS-Q12A latest prediction source adapter to the top/default-expanded WarRoom prediction review section and makes warning/readiness state operator-readable. It may read D-hot latest prediction JSON through PS-Q12A only; no runtime writes, AutoTrade, broker, mode, approval, or ledger behavior.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

import streamlit as st

from .prediction_warroom_latest_prediction_source_adapter import (
    LATEST_PREDICTION_SOURCE_ADAPTER_VERSION,
    build_prediction_warroom_latest_prediction_source_adapter,
)

PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION = "prediction_warroom_latest_prediction_source_review_panel.ps_q12b.v1"
PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION = "prediction_warroom_latest_prediction_source_readability_polish.ps_q12g.v1"
PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_UICHECK_SNAPSHOT_VERSION = "prediction_warroom_latest_prediction_source_uicheck_snapshot.ps_q12h.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _bool_label(value: Any) -> str:
    return "ready" if value is True else "not_ready"


def _severity(*, ready: bool, blocked: bool = False, warning: bool = False) -> str:
    if blocked:
        return "blocker"
    if warning:
        return "warning"
    return "ok" if ready else "attention"


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


def latest_prediction_source_readability_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Return PS-Q12G display-only readiness rows for quick operator scanning."""
    panel = _as_mapping(packet)
    adapter = _as_mapping(panel.get("adapter_packet")) if "adapter_packet" in panel else panel
    summary = _as_mapping(adapter.get("source_summary"))
    blocker_count = _int(adapter.get("blocker_count")) or len(_list(adapter.get("blocked_reasons")))
    warning_count = _int(adapter.get("warning_count")) or len(_list(adapter.get("warning_reasons")))
    loaded_payloads = _int(adapter.get("loaded_payload_count"))
    review_ready = adapter.get("review_packet_ready") is True
    session_handoff = adapter.get("session_state_updated") is True
    read_succeeded = adapter.get("actual_file_read_succeeded") is True
    decode_succeeded = adapter.get("payload_decode_succeeded") is True
    return [
        {
            "item": "source_panel",
            "state": panel.get("panel_state") or adapter.get("adapter_state"),
            "severity": _severity(ready=review_ready and session_handoff and blocker_count == 0, blocked=blocker_count > 0),
            "operator_note_ja": "WarRoom 推論ソース表示の全体状態",
            "read_only": True,
            "execution": "false",
        },
        {
            "item": "payload_load_decode",
            "state": f"loaded={loaded_payloads}; read={_bool_label(read_succeeded)}; decode={_bool_label(decode_succeeded)}",
            "severity": _severity(ready=loaded_payloads > 0 and read_succeeded and decode_succeeded, blocked=blocker_count > 0),
            "operator_note_ja": "D-hot latest prediction の read/decode 状態",
            "read_only": True,
            "execution": "false",
        },
        {
            "item": "q9g_review_handoff",
            "state": f"review_ready={review_ready}; session_handoff={session_handoff}",
            "severity": _severity(ready=review_ready and session_handoff, blocked=blocker_count > 0),
            "operator_note_ja": "既存 Q9G review panel への handoff 状態",
            "read_only": True,
            "execution": "false",
        },
        {
            "item": "warnings",
            "state": str(warning_count),
            "severity": _severity(ready=warning_count == 0, warning=warning_count > 0),
            "operator_note_ja": "operator review 用 warning 件数。実行許可ではない",
            "read_only": True,
            "execution": "false",
        },
        {
            "item": "blockers",
            "state": str(blocker_count),
            "severity": _severity(ready=blocker_count == 0, blocked=blocker_count > 0),
            "operator_note_ja": "0 以外なら WarRoom 表示は fail-closed / blocked",
            "read_only": True,
            "execution": "false",
        },
        {
            "item": "signal",
            "state": f"{summary.get('signal_strength_percent')} / {summary.get('signal_strength_band')}",
            "severity": "review_only",
            "operator_note_ja": "推論シグナル表示。売買指示ではない",
            "read_only": True,
            "execution": "false",
        },
    ]


def latest_prediction_source_issue_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Return display-only blocker/warning rows for PS-Q12G operator readability."""
    panel = _as_mapping(packet)
    adapter = _as_mapping(panel.get("adapter_packet")) if "adapter_packet" in panel else panel
    rows: list[dict[str, Any]] = []
    for reason in _list(adapter.get("blocked_reasons")):
        rows.append(
            {
                "severity": "blocker",
                "reason": str(reason),
                "operator_note_ja": "この理由がある間は review ready ではありません",
                "read_only": True,
                "execution": "false",
            }
        )
    for reason in _list(adapter.get("warning_reasons")):
        rows.append(
            {
                "severity": "warning",
                "reason": str(reason),
                "operator_note_ja": "operator review 用の注意。実行許可ではありません",
                "read_only": True,
                "execution": "false",
            }
        )
    if not rows:
        rows.append(
            {
                "severity": "ok",
                "reason": "no_blockers_or_warnings_reported_by_latest_prediction_source",
                "operator_note_ja": "blocker/warning は報告されていません",
                "read_only": True,
                "execution": "false",
            }
        )
    return rows


def build_prediction_warroom_latest_prediction_source_uicheck_snapshot(packet: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Return a compact safe snapshot for GPT UI Check automation; display-only, no IO."""
    panel = _as_mapping(packet)
    adapter = _as_mapping(panel.get("adapter_packet")) if "adapter_packet" in panel else panel
    summary = _as_mapping(adapter.get("source_summary"))
    blocker_count = _int(adapter.get("blocker_count")) or len(_list(adapter.get("blocked_reasons")))
    warning_count = _int(adapter.get("warning_count")) or len(_list(adapter.get("warning_reasons")))
    return {
        "snapshot_version": PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_UICHECK_SNAPSHOT_VERSION,
        "panel_version": panel.get("panel_version") or PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION,
        "readability_polish_version": panel.get("readability_polish_version") or PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION,
        "panel_state": panel.get("panel_state"),
        "adapter_state": adapter.get("adapter_state"),
        "prediction_run_id": summary.get("prediction_run_id"),
        "generated_at": summary.get("generated_at"),
        "market_uid": summary.get("market_uid"),
        "signal_strength_percent": summary.get("signal_strength_percent"),
        "signal_strength_band": summary.get("signal_strength_band"),
        "loaded_payload_count": _int(adapter.get("loaded_payload_count")),
        "actual_file_read_succeeded": adapter.get("actual_file_read_succeeded") is True,
        "payload_decode_succeeded": adapter.get("payload_decode_succeeded") is True,
        "review_packet_ready": adapter.get("review_packet_ready") is True,
        "session_state_updated": adapter.get("session_state_updated") is True,
        "q9g_session_state_seed_ready": panel.get("q9g_session_state_seed_ready") is True,
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "readability_row_count": len(_list(panel.get("readability_rows"))),
        "issue_row_count": len(_list(panel.get("issue_rows"))),
        "safe_boundary": {
            "read_only": panel.get("read_only") is True,
            "non_executing": panel.get("non_executing") is True,
            "display_only": panel.get("display_only") is True,
            "warroom_page_mutation_allowed_false": panel.get("warroom_page_mutation_allowed") is False,
            "warroom_panel_mutation_allowed_false": panel.get("warroom_panel_mutation_allowed") is False,
            "runtime_artifact_write_allowed_false": panel.get("runtime_artifact_write_allowed") is False,
            "approval_or_authorization_allowed_false": panel.get("approval_or_authorization_allowed") is False,
            "ledger_append_allowed_false": panel.get("ledger_append_allowed") is False,
            "autotrade_trigger_allowed_false": panel.get("autotrade_trigger_allowed") is False,
            "broker_private_api_allowed_false": panel.get("broker_private_api_allowed") is False,
            "would_write_runtime_artifact_false": panel.get("would_write_runtime_artifact") is False,
            "would_send_to_broker_false": panel.get("would_send_to_broker") is False,
        },
        "operator_note": "PS-Q12H uicheck snapshot is display-only; no execution, no approval, no ledger, no AutoTrade, no broker/private API, no runtime write.",
    }


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
    panel: dict[str, Any] = {
        "panel_version": PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION,
        "readability_polish_version": PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READABILITY_POLISH_VERSION,
        "panel_id": f"{PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_REVIEW_PANEL_VERSION}:latest:{'ready' if ready else 'blocked'}",
        "panel_state": "latest_prediction_source_review_panel_ready" if ready else "latest_prediction_source_review_panel_blocked",
        "adapter_version": LATEST_PREDICTION_SOURCE_ADAPTER_VERSION,
        "adapter_packet": adapter_packet,
        "status_rows": latest_prediction_source_status_rows(adapter_packet),
        "boundary_rows": latest_prediction_source_boundary_rows(adapter_packet),
        "top_default_expanded_review_panel_connected": True,
        "q9g_session_state_seed_attempted": store_in_session_state,
        "q9g_session_state_seed_ready": ready,
        "warning_readability_polish": True,
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
    panel["readability_rows"] = latest_prediction_source_readability_rows(panel)
    panel["issue_rows"] = latest_prediction_source_issue_rows(panel)
    panel["uicheck_snapshot"] = build_prediction_warroom_latest_prediction_source_uicheck_snapshot(panel)
    return panel


def render_prediction_warroom_latest_prediction_source_review_panel() -> Mapping[str, Any]:
    """Render PS-Q12B/PS-Q12G read-only source status and seed existing Q9G panel through session_state."""
    panel = build_prediction_warroom_latest_prediction_source_review_panel_packet(
        session_state=st.session_state,
        allow_actual_read=True,
        store_in_session_state=True,
    )
    adapter = _as_mapping(panel.get("adapter_packet"))
    st.session_state["warroom_latest_prediction_source_review_panel_uicheck_snapshot"] = _as_mapping(panel.get("uicheck_snapshot"))
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
    readability_rows = _list(panel.get("readability_rows"))
    if readability_rows:
        st.caption(
            "PS-Q12G readability summary is display-only: warning/blocker/ready states are for operator review; "
            "no execution, no approval, no ledger, no AutoTrade, no broker/private API."
        )
        st.dataframe(readability_rows, width="stretch", hide_index=True)
    rows = _list(panel.get("status_rows"))
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    issue_rows = _list(panel.get("issue_rows"))
    if issue_rows:
        st.caption("PS-Q12G warning/blocker detail rows are review-only and do not enable execution.")
        st.dataframe(issue_rows, width="stretch", hide_index=True)
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
