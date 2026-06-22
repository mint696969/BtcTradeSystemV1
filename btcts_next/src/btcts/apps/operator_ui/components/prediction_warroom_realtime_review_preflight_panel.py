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
PREDICTION_WARROOM_REALTIME_REVIEW_READABILITY_VERSION = "prediction_warroom_realtime_review_readability.ps_q13c.v1"
PREDICTION_WARROOM_REALTIME_REVIEW_UICHECK_SNAPSHOT_VERSION = "prediction_warroom_realtime_review_uicheck_snapshot.ps_q13d.v1"


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


def prediction_warroom_realtime_review_summary_cards(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Return human-readable summary cards for quick WarRoom scanning without rendering."""
    data = _as_mapping(packet)
    return [
        {
            "card": "prediction_run",
            "label_ja": "推論run",
            "value": data.get("prediction_run_id") or "missing",
            "state": data.get("preflight_state"),
            "operator_note_ja": "表示対象の推論run。売買指示ではない。",
            "read_only": True,
            "execution": False,
        },
        {
            "card": "signal_strength",
            "label_ja": "シグナル強度",
            "value": f"{data.get('signal_strength_percent')} / {data.get('signal_strength_band')}",
            "state": "review_only",
            "operator_note_ja": "強度の確認用。triggerやorderには接続しない。",
            "read_only": True,
            "execution": False,
        },
        {
            "card": "warning_blocker",
            "label_ja": "warning/blocker",
            "value": f"warnings={data.get('latest_prediction_warning_count')}; blockers={data.get('latest_prediction_blocker_count')}",
            "state": "blocked" if int(data.get("latest_prediction_blocker_count") or 0) else "review",
            "operator_note_ja": "情報品質と確認阻害要因。freshness bypassではない。",
            "read_only": True,
            "execution": False,
        },
        {
            "card": "scenario_gpt_context",
            "label_ja": "Scenario/GPT",
            "value": f"scenario_trace={data.get('scenario_trace_present')}; gpt_digest={data.get('gpt_review_digest_present')}",
            "state": "present" if data.get("scenario_trace_present") and data.get("gpt_review_digest_present") else "waiting_for_context",
            "operator_note_ja": "GPTと一緒に説明・矛盾・注意点を見るための材料。",
            "read_only": True,
            "execution": False,
        },
    ]


def prediction_warroom_gpt_review_checklist_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Return GPT-assisted review checklist rows without rendering or sending data out."""
    data = _as_mapping(packet)
    return [
        {
            "check": "source_and_freshness",
            "question_ja": "この推論run、生成時刻、market_uid、warning/blockerは現在の確認対象として妥当か？",
            "state": "review_required",
            "source": "latest_prediction_source",
            "gpt_use": "explain_and_flag_inconsistency",
            "read_only": True,
            "execution": False,
        },
        {
            "check": "scenario_trace_consistency",
            "question_ja": "scenario trace / evidence / invalidation / switch hint に矛盾や不足はないか？",
            "state": "available" if data.get("scenario_trace_present") else "waiting_for_trace",
            "source": "scenario_trace_review",
            "gpt_use": "summarize_trace_and_risks",
            "read_only": True,
            "execution": False,
        },
        {
            "check": "operator_action_review",
            "question_ja": "人間が今見るべき要点、保留理由、次に確認すべき情報源は何か？",
            "state": "review_required",
            "source": "gpt_assisted_explanation_context",
            "gpt_use": "propose_review_questions_only",
            "read_only": True,
            "execution": False,
        },
    ]


def prediction_warroom_parameter_adjustment_candidate_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Return proposal-only parameter review rows; no apply/staging write is performed."""
    data = _as_mapping(packet)
    warning_count = int(data.get("latest_prediction_warning_count") or 0)
    blocker_count = int(data.get("latest_prediction_blocker_count") or 0)
    signal = data.get("signal_strength_percent")
    signal_band = str(data.get("signal_strength_band") or "unknown")
    return [
        {
            "candidate": "source_quality_sensitivity",
            "current_observation": f"warnings={warning_count}; blockers={blocker_count}",
            "review_prompt_ja": "source quality warningが継続する場合、表示上の注意強度や採用条件を見直す候補。",
            "proposal_state": "blocked_review_first" if blocker_count else "proposal_only",
            "apply_allowed": False,
            "staging_write_allowed": False,
            "read_only": True,
            "execution": False,
        },
        {
            "candidate": "signal_strength_threshold",
            "current_observation": f"signal={signal} / {signal_band}",
            "review_prompt_ja": "シグナル強度の見え方・注意帯・人間確認閾値の調整候補。売買trigger閾値ではない。",
            "proposal_state": "proposal_only",
            "apply_allowed": False,
            "staging_write_allowed": False,
            "read_only": True,
            "execution": False,
        },
        {
            "candidate": "scenario_trace_required_fields",
            "current_observation": f"scenario_trace={data.get('scenario_trace_present')}; gpt_digest={data.get('gpt_review_digest_present')}",
            "review_prompt_ja": "GPTレビューに必要なtrace/gpt digest項目の不足を確認する候補。",
            "proposal_state": "proposal_only",
            "apply_allowed": False,
            "staging_write_allowed": False,
            "read_only": True,
            "execution": False,
        },
    ]


def build_prediction_warroom_realtime_review_uicheck_snapshot(packet: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Return a compact safe snapshot for GPT UI Check automation; display-only, no IO."""
    data = _as_mapping(packet)
    preflight = _as_mapping(data.get("preflight_packet"))
    summary_cards = _list(data.get("summary_cards"))
    gpt_rows = _list(data.get("gpt_review_checklist_rows"))
    parameter_rows = _list(data.get("parameter_adjustment_candidate_rows"))
    surface_rows = _list(data.get("surface_rows"))
    boundary_rows = _list(data.get("boundary_rows"))
    return {
        "snapshot_version": PREDICTION_WARROOM_REALTIME_REVIEW_UICHECK_SNAPSHOT_VERSION,
        "panel_version": data.get("panel_version"),
        "readability_version": data.get("readability_version"),
        "preflight_version": data.get("preflight_version"),
        "panel_state": data.get("panel_state"),
        "preflight_state": preflight.get("preflight_state"),
        "prediction_run_id": preflight.get("prediction_run_id"),
        "generated_at": preflight.get("generated_at"),
        "market_uid": preflight.get("market_uid"),
        "signal_strength_percent": preflight.get("signal_strength_percent"),
        "signal_strength_band": preflight.get("signal_strength_band"),
        "latest_prediction_source_panel_present": preflight.get("latest_prediction_source_panel_present") is True,
        "latest_prediction_review_ready": preflight.get("latest_prediction_review_ready") is True,
        "latest_prediction_blocker_count": int(preflight.get("latest_prediction_blocker_count") or 0),
        "latest_prediction_warning_count": int(preflight.get("latest_prediction_warning_count") or 0),
        "scenario_trace_present": preflight.get("scenario_trace_present") is True,
        "gpt_review_digest_present": preflight.get("gpt_review_digest_present") is True,
        "ready_for_future_warroom_ui_slice": preflight.get("ready_for_future_warroom_ui_slice") is True,
        "summary_card_count": len(summary_cards),
        "gpt_review_checklist_count": len(gpt_rows),
        "parameter_adjustment_candidate_count": len(parameter_rows),
        "surface_row_count": len(surface_rows),
        "boundary_row_count": len(boundary_rows),
        "parameter_apply_allowed_any": any(_as_mapping(row).get("apply_allowed") is True for row in parameter_rows),
        "parameter_staging_write_allowed_any": any(_as_mapping(row).get("staging_write_allowed") is True for row in parameter_rows),
        "safe_boundary": {
            "read_only": data.get("read_only") is True,
            "non_executing": data.get("non_executing") is True,
            "display_only": data.get("display_only") is True,
            "review_only": data.get("review_only") is True,
            "warroom_page_mutation_allowed_false": data.get("warroom_page_mutation_allowed") is False,
            "runtime_artifact_write_allowed_false": data.get("runtime_artifact_write_allowed") is False,
            "parameter_mutation_allowed_false": data.get("parameter_mutation_allowed") is False,
            "parameter_version_append_allowed_false": data.get("parameter_version_append_allowed") is False,
            "approval_or_authorization_allowed_false": data.get("approval_or_authorization_allowed") is False,
            "ledger_append_allowed_false": data.get("ledger_append_allowed") is False,
            "autotrade_trigger_allowed_false": data.get("autotrade_trigger_allowed") is False,
            "broker_private_api_allowed_false": data.get("broker_private_api_allowed") is False,
            "would_write_runtime_artifact_false": data.get("would_write_runtime_artifact") is False,
            "would_mutate_live_parameters_false": data.get("would_mutate_live_parameters") is False,
            "would_append_parameter_version_false": data.get("would_append_parameter_version") is False,
            "would_send_to_broker_false": data.get("would_send_to_broker") is False,
            "broker_execution_requested_false": data.get("broker_execution_requested") is False,
            "mode_apply_requested_false": data.get("mode_apply_requested") is False,
            "command_ledger_append_requested_false": data.get("command_ledger_append_requested") is False,
            "decision_ledger_append_requested_false": data.get("decision_ledger_append_requested") is False,
            "approval_append_requested_false": data.get("approval_append_requested") is False,
            "authorization_grant_requested_false": data.get("authorization_grant_requested") is False,
            "autotrade_trigger_enabled_false": data.get("autotrade_trigger_enabled") is False,
            "parameter_apply_allowed_any_false": not any(_as_mapping(row).get("apply_allowed") is True for row in parameter_rows),
            "parameter_staging_write_allowed_any_false": not any(_as_mapping(row).get("staging_write_allowed") is True for row in parameter_rows),
        },
        "operator_note": "PS-Q13D uicheck snapshot is display-only; no parameter apply, no staging write, no runtime write, no ledger, no AutoTrade, no broker/private API.",
    }


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
        "summary_cards": prediction_warroom_realtime_review_summary_cards(preflight),
        "gpt_review_checklist_rows": prediction_warroom_gpt_review_checklist_rows(preflight),
        "parameter_adjustment_candidate_rows": prediction_warroom_parameter_adjustment_candidate_rows(preflight),
        "readability_version": PREDICTION_WARROOM_REALTIME_REVIEW_READABILITY_VERSION,
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
    packet["uicheck_snapshot"] = build_prediction_warroom_realtime_review_uicheck_snapshot(packet)
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
    st.session_state["warroom_realtime_review_preflight_panel_uicheck_snapshot"] = _as_mapping(packet.get("uicheck_snapshot"))
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
    summary_cards = _list(packet.get("summary_cards"))
    if summary_cards:
        st.caption("PS-Q13C quick summary cards are human/GPT review-only and do not authorize action.")
        st.dataframe(summary_cards, width="stretch", hide_index=True)
    gpt_rows = _list(packet.get("gpt_review_checklist_rows"))
    if gpt_rows:
        st.caption("PS-Q13C GPT review checklist: explain, flag inconsistency, and propose review questions only.")
        st.dataframe(gpt_rows, width="stretch", hide_index=True)
    parameter_rows = _list(packet.get("parameter_adjustment_candidate_rows"))
    if parameter_rows:
        st.caption("PS-Q13C parameter candidates are proposal/review only: apply=false, staging_write=false.")
        st.dataframe(parameter_rows, width="stretch", hide_index=True)
    surface_rows = _list(packet.get("surface_rows"))
    if surface_rows:
        st.dataframe(surface_rows, width="stretch", hide_index=True)
    boundary_rows = _list(packet.get("boundary_rows"))
    if boundary_rows:
        st.caption("PS-Q13B boundaries are review-only and do not authorize execution or parameter mutation.")
        st.dataframe(boundary_rows, width="stretch", hide_index=True)
    return packet
