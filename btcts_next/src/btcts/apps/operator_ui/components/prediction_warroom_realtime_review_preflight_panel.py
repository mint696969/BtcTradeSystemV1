# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_realtime_review_preflight_panel.py
# desc: PS-Q13B Streamlit display-only panel for PS-Q13A WarRoom real-time prediction review preflight. Renders review rows only; no runtime writes, parameter mutation, AutoTrade, broker, mode/order, approval, or ledger behavior.

from __future__ import annotations

from typing import Any, Mapping

import streamlit as st

from .prediction_warroom_realtime_review_preflight_contract import (
    PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION,
    build_prediction_warroom_realtime_review_preflight,
)

PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_PANEL_VERSION = "prediction_warroom_realtime_review_preflight_panel.ps_q13b.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def prediction_warroom_realtime_review_surface_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Return compact PS-Q13B review surface rows without rendering."""
    data = _as_mapping(packet)
    rows: list[dict[str, Any]] = []
    for item in _list(data.get("review_surfaces")):
        row = _as_mapping(item)
        rows.append(
            {
                "surface_id": row.get("surface_id"),
                "label_ja": row.get("label_ja"),
                "state": row.get("state"),
                "source": row.get("source"),
                "operator_note_ja": row.get("operator_note_ja"),
                "read_only": row.get("read_only") is True,
                "execution": bool(row.get("execution")),
                "autotrade": bool(row.get("autotrade")),
                "broker": bool(row.get("broker")),
            }
        )
    return rows


def prediction_warroom_realtime_review_boundary_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Return compact responsibility/safety boundary rows without rendering."""
    data = _as_mapping(packet)
    boundary = _as_mapping(data.get("responsibility_boundary"))
    rows = [
        {
            "boundary": str(key),
            "owner": str(value),
            "read_only": True,
            "execution": False,
        }
        for key, value in boundary.items()
    ]
    rows.extend(
        {
            "boundary": str(item),
            "owner": "forbidden_next_behavior",
            "read_only": True,
            "execution": False,
        }
        for item in _list(data.get("forbidden_next_behavior"))
    )
    return rows


def build_prediction_warroom_realtime_review_preflight_panel_packet(
    *,
    latest_prediction_source_panel: Mapping[str, Any] | Any | None = None,
    prediction_system_result: Mapping[str, Any] | Any | None = None,
    scenario_core_output: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    """Build a PS-Q13B display packet from the PS-Q13A preflight contract."""
    preflight = build_prediction_warroom_realtime_review_preflight(
        latest_prediction_source_panel=latest_prediction_source_panel,
        prediction_system_result=prediction_system_result,
        scenario_core_output=scenario_core_output,
    ).to_dict()
    packet = {
        "panel_version": PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_PANEL_VERSION,
        "preflight_version": PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION,
        "panel_state": "realtime_review_preflight_panel_ready" if preflight.get("ready_for_future_warroom_ui_slice") else "realtime_review_preflight_panel_review_only_not_ready",
        "preflight_packet": preflight,
        "surface_rows": prediction_warroom_realtime_review_surface_rows(preflight),
        "boundary_rows": prediction_warroom_realtime_review_boundary_rows(preflight),
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "review_only": True,
        "render_intent_only": True,
        "warroom_page_mutation_allowed": False,
        "runtime_artifact_write_allowed": False,
        "parameter_mutation_allowed": False,
        "parameter_version_append_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_mutate_live_parameters": False,
        "would_append_parameter_version": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "decision_ledger_append_requested": False,
        "approval_append_requested": False,
        "authorization_grant_requested": False,
        "autotrade_trigger_enabled": False,
    }
    return packet


def render_prediction_warroom_realtime_review_preflight_panel(
    *,
    latest_prediction_source_panel: Mapping[str, Any] | Any | None = None,
    prediction_system_result: Mapping[str, Any] | Any | None = None,
    scenario_core_output: Mapping[str, Any] | Any | None = None,
) -> Mapping[str, Any]:
    """Render PS-Q13B review-only preflight rows in WarRoom."""
    packet = build_prediction_warroom_realtime_review_preflight_panel_packet(
        latest_prediction_source_panel=latest_prediction_source_panel,
        prediction_system_result=prediction_system_result,
        scenario_core_output=scenario_core_output,
    )
    preflight = _as_mapping(packet.get("preflight_packet"))
    st.caption(
        "PS-Q13B realtime prediction review preflight is display-only: "
        "human/GPT review surfaces only; no parameter apply, no runtime write, no ledger, "
        "no AutoTrade, no broker/private API."
    )
    st.caption(
        "panel_version={panel}; preflight_state={state}; run_id={run_id}; signal={signal}/{band}; "
        "scenario_trace={trace}; gpt_digest={digest}; ready_for_future_ui={ready}".format(
            panel=PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_PANEL_VERSION,
            state=preflight.get("preflight_state"),
            run_id=preflight.get("prediction_run_id"),
            signal=preflight.get("signal_strength_percent"),
            band=preflight.get("signal_strength_band"),
            trace=preflight.get("scenario_trace_present"),
            digest=preflight.get("gpt_review_digest_present"),
            ready=preflight.get("ready_for_future_warroom_ui_slice"),
        )
    )
    surface_rows = _list(packet.get("surface_rows"))
    if surface_rows:
        st.dataframe(surface_rows, width="stretch", hide_index=True)
    boundary_rows = _list(packet.get("boundary_rows"))
    if boundary_rows:
        st.caption("PS-Q13B boundaries are review-only and do not authorize execution or parameter mutation.")
        st.dataframe(boundary_rows, width="stretch", hide_index=True)
    return packet
