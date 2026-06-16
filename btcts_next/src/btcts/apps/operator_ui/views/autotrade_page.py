# path: ./btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py
# desc: AutoTrade observer/control-request surface. UI does not own execution.

from __future__ import annotations

from datetime import datetime, timezone
import json
import uuid

import streamlit as st

from btcts.autotrade.config import initial_parameter_set_v0_1, initial_registry
from btcts.autotrade.health import build_autotrade_runtime_health_snapshot
from btcts.autotrade.ledger import summarize_forecast_outcome_ledger, summarize_observer_run_ledger, summarize_shadow_decision_ledger
from btcts.autotrade.execution import (
    CommandRequest,
    CommandType,
    current_mode_state,
    default_command_ledger_path,
    preview_latest_mode_change_command_apply_with_readiness_recheck,
    read_command_ledger_rows,
    submit_mode_change_command_request,
    summarize_command_ledger,
    summarize_mode_state,
    validate_and_append_command,
)
from btcts.autotrade.mode_runtime_gate import build_mode_runtime_gate
from btcts.autotrade.modes import AutoTradeMode, HumanControlMode, default_human_control_for_mode
from btcts.autotrade.readiness import evaluate_autotrade_live_readiness
from btcts.apps.operator_ui.components import live_shell


COMMAND_MAP = {
    "REQUEST_HALT_NEW": CommandType.REQUEST_HALT_NEW,
    "REQUEST_HALT_AND_CANCEL": CommandType.REQUEST_HALT_AND_CANCEL,
    "REQUEST_EMERGENCY_FLATTEN": CommandType.REQUEST_EMERGENCY_FLATTEN,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _command_id(command: str) -> str:
    return f"cmd_ui_{command.lower()}_{uuid.uuid4().hex[:12]}"


def _render_json(payload: object, *, max_height_px: int = 260) -> None:
    live_shell.render_scrollable_text_block(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        max_height_px=max_height_px,
        monospace=True,
    )


def _submit_command_request(command: str, *, confirmed: bool, current_mode: AutoTradeMode, target: str | None, note: str = "") -> dict:
    command_type = COMMAND_MAP[command]
    request = CommandRequest(
        command_id=_command_id(command),
        command_type=command_type,
        requested_by="operator_ui",
        requested_at=_utc_now(),
        current_mode=current_mode.value,
        target=target,
        confirmation=bool(confirmed),
        reason_codes=("operator_ui_request", command.lower()),
        note=note,
    )
    record = validate_and_append_command(default_command_ledger_path(ensure=True), request)
    return {
        "ui_action": "command_request_recorded",
        "accepted_by_validation": record.accepted,
        "blocked_by": list(record.blocked_by),
        "ledger_path": str(default_command_ledger_path(ensure=False)),
        "record": record.to_dict(),
        "execution_owner": "autotrade_runtime/execution_runtime_not_ui",
        "would_send_to_broker": False,
    }



def _submit_mode_change_request(
    *,
    current_mode: str,
    target_mode: str,
    human_confirmed: bool,
    allow_warnings: bool,
) -> dict:
    result = submit_mode_change_command_request(
        current_mode=current_mode,
        target_mode=target_mode,
        requested_by="operator_ui",
        human_confirmed=human_confirmed,
        allow_warnings=allow_warnings,
        enforce_parameter_bundle_runtime=enforce_parameter_bundle_runtime,
        required_parameter_bundle_stage=required_parameter_bundle_stage,
        max_observer_run_age_sec=120,
        max_lines=500,
    )
    data = result.to_dict()
    readiness_data = data.get("readiness") if isinstance(data.get("readiness"), dict) else {}
    readiness_health = readiness_data.get("health") if isinstance(readiness_data.get("health"), dict) else {}
    readiness_observer_runs = readiness_health.get("observer_runs") if isinstance(readiness_health.get("observer_runs"), dict) else {}
    return {
        "ui_action": "mode_change_command_request_recorded",
        "accepted": data.get("accepted"),
        "blocked_by": data.get("blocked_by"),
        "ledger_path": data.get("ledger_path"),
        "command_record": data.get("command_record"),
        "readiness": {
            "ready": readiness_data.get("ready"),
            "current_mode": readiness_data.get("current_mode"),
            "target_mode": readiness_data.get("target_mode"),
            "blocked_by": readiness_data.get("blocked_by"),
            "warnings": readiness_data.get("warnings"),
            "health_state": readiness_health.get("health_state"),
            "observer_run_fresh": readiness_health.get("observer_run_fresh"),
            "observer_latest_run_id": readiness_observer_runs.get("latest_run_id"),
            "observer_latest_blocked_by": readiness_observer_runs.get("latest_blocked_by"),
            "observer_latest_would_send_to_broker": readiness_observer_runs.get("latest_would_send_to_broker"),
            "observer_latest_bounded": readiness_observer_runs.get("latest_bounded"),
        },
        "mode_changed": False,
        "would_send_to_broker": False,
        "execution_owner": "autotrade_runtime/mode_controller_not_ui",
    }

def _recent_command_rows(limit: int = 5) -> list[dict]:
    path = default_command_ledger_path(ensure=False)
    read = read_command_ledger_rows(path, max_lines=limit)
    return [row.to_dict() for row in read.rows[-limit:]]


def _render_top_critical_state() -> None:
    ps = initial_parameter_set_v0_1()
    registry = initial_registry()
    current_mode = current_mode_state(max_lines=500).current_mode
    human_control = default_human_control_for_mode(current_mode)

    st.subheader("Critical State / Emergency")
    cols = st.columns(5)
    cols[0].metric("Mode", current_mode.value)
    cols[1].metric("Human Control", human_control.value)
    cols[2].metric("Live Orders", "disabled")
    cols[3].metric("Kill Switch", "clear")
    cols[4].metric("Parameter Set", ps.parameter_set_id)

    cols2 = st.columns(5)
    cols2[0].metric("Leverage Cap", f"{ps.margin_policy.leverage_cap:.1f}x")
    cols2[1].metric("Normal Margin", f"{ps.margin_policy.normal_margin_target_pct:.0f}%")
    cols2[2].metric("Attack Floor", f"{ps.margin_policy.attack_margin_floor_pct:.0f}%")
    cols2[3].metric("Open Orders", "unknown/not connected")
    cols2[4].metric("Position", "unknown/not connected")

    st.caption(
        "Observer surface only. UI records command requests to ledger, but does not execute broker orders."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("HALT_NEW request", key="autotrade_halt_new_request"):
            st.session_state["autotrade_last_command_record"] = _submit_command_request(
                "REQUEST_HALT_NEW",
                confirmed=False,
                current_mode=current_mode,
                target="halt_new",
            )
    with c2:
        halt_cancel_confirmed = st.checkbox("Confirm halt+cancel request", key="autotrade_halt_cancel_confirm")
        if st.button("HALT_AND_CANCEL request", key="autotrade_halt_cancel_request"):
            st.session_state["autotrade_last_command_record"] = _submit_command_request(
                "REQUEST_HALT_AND_CANCEL",
                confirmed=halt_cancel_confirmed,
                current_mode=current_mode,
                target="halt_and_cancel",
                note="dangerous command; confirmation controls accepted/rejected validation",
            )
    with c3:
        flatten_confirmed = st.checkbox("Confirm emergency flatten request", key="autotrade_flatten_confirm")
        if st.button("EMERGENCY_FLATTEN request", key="autotrade_flatten_request"):
            st.session_state["autotrade_last_command_record"] = _submit_command_request(
                "REQUEST_EMERGENCY_FLATTEN",
                confirmed=flatten_confirmed,
                current_mode=current_mode,
                target="flatten",
                note="dangerous command; UI records request only",
            )

    record = st.session_state.get("autotrade_last_command_record")
    if isinstance(record, dict):
        st.markdown("#### Last command ledger record")
        _render_json(record, max_height_px=220)

    st.markdown("#### Recent command ledger")
    _render_json(
        {
            "ledger_path": str(default_command_ledger_path(ensure=False)),
            "recent": _recent_command_rows(limit=5),
        },
        max_height_px=260,
    )

    st.markdown("#### Registry snapshot")
    _render_json(registry.to_dict(), max_height_px=180)





def _render_mode_state_status() -> None:
    st.subheader("Mode State")
    summary = summarize_mode_state(max_lines=500)
    data = summary.to_dict()

    cols = st.columns(5)
    cols[0].metric("Current Mode", summary.current_mode.value)
    cols[1].metric("Previous Mode", summary.previous_mode.value)
    cols[2].metric("Rows", summary.total_rows)
    cols[3].metric("Latest Changed", summary.latest_changed_at or "default")
    cols[4].metric("Skipped Rows", summary.skipped_rows)

    st.caption("Mode state summary is read-only. UI does not apply mode-change commands, append mode_state, or send broker orders.")
    _render_json(
        {
            "ledger_path": data.get("path"),
            "exists": data.get("exists"),
            "total_rows": data.get("total_rows"),
            "skipped_rows": data.get("skipped_rows"),
            "current_mode": data.get("current_mode"),
            "previous_mode": data.get("previous_mode"),
            "latest_changed_at": data.get("latest_changed_at"),
            "latest_source_command_id": data.get("latest_source_command_id"),
            "latest_requested_by": data.get("latest_requested_by"),
            "latest_accepted": data.get("latest_accepted"),
            "latest_mode_changed": data.get("latest_mode_changed"),
            "latest_ledger_event": data.get("latest_ledger_event"),
            "latest_reason_codes": data.get("latest_reason_codes"),
            "latest_blocked_by": data.get("latest_blocked_by"),
            "latest_would_send_to_broker": data.get("latest_would_send_to_broker"),
            "mode_counts": data.get("mode_counts"),
            "blocked_by_counts": data.get("blocked_by_counts"),
            "error_samples": data.get("error_samples"),
            "would_send_to_broker": False,
            "read_only": True,
        },
        max_height_px=300,
    )

def _render_mode_runtime_gate_status() -> None:
    st.subheader("Mode Runtime Gate")
    gate = build_mode_runtime_gate(max_lines=500)
    data = gate.to_dict()

    cols = st.columns(5)
    cols[0].metric("Current Mode", gate.current_mode.value)
    cols[1].metric("Observer", str(gate.allow_observer_cycle))
    cols[2].metric("Shadow Append", str(gate.allow_shadow_decision_append))
    cols[3].metric("Outcome Resolve", str(gate.allow_forecast_outcome_resolution))
    cols[4].metric("Live Capability", str(gate.allow_live_order_capability))

    st.caption("Mode runtime gate is read-only. UI does not run observer/shadow cycles, append ledgers, apply mode changes, or send broker orders.")
    _render_json(
        {
            "current_mode": data.get("current_mode"),
            "source_command_id": data.get("source_command_id"),
            "changed_at": data.get("changed_at"),
            "allow_observer_cycle": data.get("allow_observer_cycle"),
            "allow_shadow_decision_append": data.get("allow_shadow_decision_append"),
            "allow_forecast_outcome_resolution": data.get("allow_forecast_outcome_resolution"),
            "allow_paper_order": data.get("allow_paper_order"),
            "allow_armed_dry_run": data.get("allow_armed_dry_run"),
            "allow_live_order_capability": data.get("allow_live_order_capability"),
            "live_requires_readiness_risk_execution_safety": data.get("live_requires_readiness_risk_execution_safety"),
            "blocked_by": data.get("blocked_by"),
            "warnings": data.get("warnings"),
            "would_send_to_broker": False,
            "read_only": True,
        },
        max_height_px=300,
    )



def _render_mode_change_apply_preview_status() -> None:
    st.subheader("Mode Change Apply Preview")
    preview = preview_latest_mode_change_command_apply_with_readiness_recheck(max_lines=500, max_observer_run_age_sec=120, allow_warnings=False)
    data = preview.to_dict()

    cols = st.columns(5)
    cols[0].metric("Would Apply", str(preview.would_apply))
    cols[1].metric("Would Reject", str(preview.would_reject_by_readiness))
    cols[2].metric("Next Command", preview.command_id or "none")
    cols[3].metric("Before → After", f"{preview.current_mode_before} → {preview.current_mode_after}")
    cols[4].metric("Readiness", str(preview.readiness_ready))

    readiness_data = data.get("readiness") if isinstance(data.get("readiness"), dict) else {}
    readiness_health = readiness_data.get("health") if isinstance(readiness_data.get("health"), dict) else {}
    readiness_observer_runs = readiness_health.get("observer_runs") if isinstance(readiness_health.get("observer_runs"), dict) else {}

    st.caption("Mode-change apply preview is read-only. UI does not apply commands, append mode_state, or send broker orders.")
    _render_json(
        {
            "would_apply": data.get("would_apply"),
            "would_reject_by_readiness": data.get("would_reject_by_readiness"),
            "skip_reason": data.get("skip_reason"),
            "command_id": data.get("command_id"),
            "candidate_command_type": data.get("candidate_command_type"),
            "candidate_requested_by": data.get("candidate_requested_by"),
            "candidate_requested_at": data.get("candidate_requested_at"),
            "candidate_current_mode": data.get("candidate_current_mode"),
            "candidate_target_mode": data.get("candidate_target_mode"),
            "candidate_accepted": data.get("candidate_accepted"),
            "candidate_blocked_by": data.get("candidate_blocked_by"),
            "candidate_readiness_note_present": data.get("candidate_readiness_note_present"),
            "candidate_readiness_ready": data.get("candidate_readiness_ready"),
            "candidate_readiness_current_mode": data.get("candidate_readiness_current_mode"),
            "candidate_readiness_target_mode": data.get("candidate_readiness_target_mode"),
            "candidate_readiness_blocked_by": data.get("candidate_readiness_blocked_by"),
            "candidate_readiness_warnings": data.get("candidate_readiness_warnings"),
            "candidate_readiness_health_state": data.get("candidate_readiness_health_state"),
            "candidate_readiness_observer_latest_run_id": data.get("candidate_readiness_observer_latest_run_id"),
            "candidate_readiness_observer_latest_blocked_by": data.get("candidate_readiness_observer_latest_blocked_by"),
            "candidate_readiness_observer_latest_would_send_to_broker": data.get("candidate_readiness_observer_latest_would_send_to_broker"),
            "candidate_readiness_observer_latest_bounded": data.get("candidate_readiness_observer_latest_bounded"),
            "current_mode_before": data.get("current_mode_before"),
            "current_mode_after": data.get("current_mode_after"),
            "mode_changed": data.get("mode_changed"),
            "readiness_ready": data.get("readiness_ready"),
            "blocked_by": data.get("blocked_by"),
            "warnings": readiness_data.get("warnings"),
            "health_state": readiness_health.get("health_state"),
            "readiness_observer_latest_run_id": readiness_observer_runs.get("latest_run_id"),
            "readiness_observer_latest_blocked_by": readiness_observer_runs.get("latest_blocked_by"),
            "readiness_observer_latest_would_send_to_broker": readiness_observer_runs.get("latest_would_send_to_broker"),
            "readiness_observer_latest_bounded": readiness_observer_runs.get("latest_bounded"),
            "readiness": data.get("readiness"),
            "candidate_command_count": data.get("candidate_command_count"),
            "already_applied_command_ids": data.get("already_applied_command_ids"),
            "command_read_skipped_count": data.get("command_read_skipped_count"),
            "mode_state_read_skipped_count": data.get("mode_state_read_skipped_count"),
            "command_path": data.get("command_path"),
            "mode_state_path": data.get("mode_state_path"),
            "would_send_to_broker": False,
            "read_only": True,
        },
        max_height_px=300,
    )

def _render_command_request_status() -> None:
    st.subheader("Command Requests")
    summary = summarize_command_ledger(max_lines=500)
    data = summary.to_dict()

    cols = st.columns(5)
    cols[0].metric("Command Rows", summary.total_rows)
    cols[1].metric("Accepted", summary.accepted_count)
    cols[2].metric("Rejected", summary.rejected_count)
    cols[3].metric("Latest Type", summary.latest_command_type or "none")
    cols[4].metric("Skipped Rows", summary.skipped_rows)

    st.caption("Command request summary is read-only. This panel does not append requests, change mode, or send broker orders.")
    _render_json(
        {
            "ledger_path": data.get("path"),
            "exists": data.get("exists"),
            "total_rows": data.get("total_rows"),
            "accepted_count": data.get("accepted_count"),
            "rejected_count": data.get("rejected_count"),
            "skipped_rows": data.get("skipped_rows"),
            "latest_command_id": data.get("latest_command_id"),
            "latest_command_type": data.get("latest_command_type"),
            "latest_target": data.get("latest_target"),
            "latest_current_mode": data.get("latest_current_mode"),
            "latest_accepted": data.get("latest_accepted"),
            "latest_requested_by": data.get("latest_requested_by"),
            "latest_requested_at": data.get("latest_requested_at"),
            "latest_blocked_by": data.get("latest_blocked_by"),
            "latest_readiness_observer_run_id": data.get("latest_readiness_observer_run_id"),
            "latest_readiness_observer_blocked_by": data.get("latest_readiness_observer_blocked_by"),
            "latest_readiness_observer_would_send_to_broker": data.get("latest_readiness_observer_would_send_to_broker"),
            "latest_readiness_observer_bounded": data.get("latest_readiness_observer_bounded"),
            "latest_mode_change_readiness_command_id": data.get("latest_mode_change_readiness_command_id"),
            "latest_mode_change_readiness_requested_by": data.get("latest_mode_change_readiness_requested_by"),
            "latest_mode_change_readiness_requested_at": data.get("latest_mode_change_readiness_requested_at"),
            "latest_mode_change_readiness_accepted": data.get("latest_mode_change_readiness_accepted"),
            "latest_mode_change_readiness_command_blocked_by": data.get("latest_mode_change_readiness_command_blocked_by"),
            "latest_mode_change_readiness_ready": data.get("latest_mode_change_readiness_ready"),
            "latest_mode_change_readiness_current_mode": data.get("latest_mode_change_readiness_current_mode"),
            "latest_mode_change_readiness_target_mode": data.get("latest_mode_change_readiness_target_mode"),
            "latest_mode_change_readiness_blocked_by": data.get("latest_mode_change_readiness_blocked_by"),
            "latest_mode_change_readiness_warnings": data.get("latest_mode_change_readiness_warnings"),
            "latest_mode_change_readiness_health_state": data.get("latest_mode_change_readiness_health_state"),
            "latest_mode_change_readiness_observer_run_id": data.get("latest_mode_change_readiness_observer_run_id"),
            "latest_mode_change_readiness_observer_blocked_by": data.get("latest_mode_change_readiness_observer_blocked_by"),
            "latest_mode_change_readiness_observer_would_send_to_broker": data.get("latest_mode_change_readiness_observer_would_send_to_broker"),
            "latest_mode_change_readiness_observer_bounded": data.get("latest_mode_change_readiness_observer_bounded"),
            "command_type_counts": data.get("command_type_counts"),
            "target_counts": data.get("target_counts"),
            "blocked_by_counts": data.get("blocked_by_counts"),
            "error_samples": data.get("error_samples"),
            "would_send_to_broker": False,
            "read_only": True,
        },
        max_height_px=320,
    )


def _parameter_bundle_runtime_summary_view(parameter_bundle_runtime: dict) -> dict:
    registry = parameter_bundle_runtime.get("registry") if isinstance(parameter_bundle_runtime.get("registry"), dict) else {}
    return {
        "schema_version": parameter_bundle_runtime.get("schema_version"),
        "registry_exists": parameter_bundle_runtime.get("registry_exists"),
        "event_ledger_exists": parameter_bundle_runtime.get("event_ledger_exists"),
        "event_count": parameter_bundle_runtime.get("event_count"),
        "latest_event_type": parameter_bundle_runtime.get("latest_event_type"),
        "latest_event_ts": parameter_bundle_runtime.get("latest_event_ts"),
        "active_shadow_bundle_id": registry.get("active_shadow_bundle_id"),
        "active_paper_bundle_id": registry.get("active_paper_bundle_id"),
        "active_live_bundle_id": registry.get("active_live_bundle_id"),
        "last_known_good_bundle_id": registry.get("last_known_good_bundle_id"),
        "rollback_bundle_id": registry.get("rollback_bundle_id"),
        "pending_draft_bundle_id": registry.get("pending_draft_bundle_id"),
        "retired_bundle_ids": registry.get("retired_bundle_ids"),
        "warnings": parameter_bundle_runtime.get("warnings"),
        "blocked_by": parameter_bundle_runtime.get("blocked_by"),
        "would_send_to_broker": False,
        "read_only": True,
    }


def _render_runtime_health_status() -> None:
    st.subheader("Runtime Health")
    health = build_autotrade_runtime_health_snapshot(max_observer_run_age_sec=120, max_lines=500)
    data = health.to_dict()
    runtime = data.get("runtime") or {}
    runtime_paths = (runtime.get("paths") or {}) if isinstance(runtime, dict) else {}
    observer_runs = data.get("observer_runs") or {}
    shadow_decisions = data.get("shadow_decisions") or {}
    forecast_outcomes = data.get("forecast_outcomes") or {}
    parameter_bundle_runtime = data.get("parameter_bundle_runtime") if isinstance(data.get("parameter_bundle_runtime"), dict) else {}
    parameter_bundle_view = _parameter_bundle_runtime_summary_view(parameter_bundle_runtime)

    cols = st.columns(5)
    cols[0].metric("Health", health.health_state)
    cols[1].metric("Observer Fresh", str(health.observer_run_fresh))
    cols[2].metric("Observer Age", "none" if health.observer_run_age_sec is None else f"{health.observer_run_age_sec:.0f}s")
    cols[3].metric("Latest Action", shadow_decisions.get("latest_action") or "none")
    cols[4].metric("Latest Outcome", forecast_outcomes.get("latest_result") or "none")

    bundle_cols = st.columns(5)
    bundle_cols[0].metric("Bundle Registry", "present" if parameter_bundle_view.get("registry_exists") else "missing")
    bundle_cols[1].metric("Bundle Events", parameter_bundle_view.get("event_count") or 0)
    bundle_cols[2].metric("Shadow Bundle", parameter_bundle_view.get("active_shadow_bundle_id") or "none")
    bundle_cols[3].metric("Live Bundle", parameter_bundle_view.get("active_live_bundle_id") or "none")
    bundle_cols[4].metric("Latest Bundle Event", parameter_bundle_view.get("latest_event_type") or "none")

    st.caption("Runtime health snapshot is read-only. UI does not run observer cycles, append ledgers, mutate parameter bundles, or send broker orders.")
    _render_json(
        {
            "health_state": data.get("health_state"),
            "generated_at": data.get("generated_at"),
            "observer_run_fresh": data.get("observer_run_fresh"),
            "observer_run_age_sec": data.get("observer_run_age_sec"),
            "max_observer_run_age_sec": data.get("max_observer_run_age_sec"),
            "blocked_by": data.get("blocked_by"),
            "warnings": data.get("warnings"),
            "runtime": {
                "runtime_root": runtime_paths.get("runtime_root"),
                "source": runtime_paths.get("source"),
                "core_runtime_root": runtime_paths.get("core_runtime_root"),
                "expected_hot_runtime_root": runtime.get("expected_hot_runtime_root"),
                "live_ready": runtime.get("live_ready"),
                "cold_runtime_detected": runtime.get("cold_runtime_detected"),
                "hot_runtime_detected": runtime.get("hot_runtime_detected"),
                "runtime_warnings": runtime.get("warnings"),
                "runtime_blocked_by": runtime.get("blocked_by"),
            },
            "observer_runs": {
                "latest_run_id": observer_runs.get("latest_run_id"),
                "latest_finished_at": observer_runs.get("latest_finished_at"),
                "latest_completed_cycles": observer_runs.get("latest_completed_cycles"),
                "latest_duplicate_snapshot_skipped_count": observer_runs.get("latest_duplicate_snapshot_skipped_count"),
                "latest_skip_duplicate_snapshot": observer_runs.get("latest_skip_duplicate_snapshot"),
                "latest_blocked_by": observer_runs.get("latest_blocked_by"),
                "latest_would_send_to_broker": observer_runs.get("latest_would_send_to_broker"),
                "latest_bounded": observer_runs.get("latest_bounded"),
                "total_rows": observer_runs.get("total_rows"),
            },
            "shadow_decisions": {
                "latest_decision_id": shadow_decisions.get("latest_decision_id"),
                "latest_snapshot_id": shadow_decisions.get("latest_snapshot_id"),
                "latest_forecast_id": shadow_decisions.get("latest_forecast_id"),
                "latest_action": shadow_decisions.get("latest_action"),
                "total_rows": shadow_decisions.get("total_rows"),
            },
            "forecast_outcomes": {
                "latest_forecast_id": forecast_outcomes.get("latest_forecast_id"),
                "latest_result": forecast_outcomes.get("latest_result"),
                "latest_forecast_confidence": forecast_outcomes.get("latest_forecast_confidence"),
                "total_rows": forecast_outcomes.get("total_rows"),
            },
            "parameter_bundle_runtime": parameter_bundle_view,
            "would_send_to_broker": False,
            "read_only": True,
        },
        max_height_px=360,
    )


def _render_live_readiness_preflight() -> None:
    st.subheader("Live Readiness Preflight")
    mode_values = [mode.value for mode in AutoTradeMode]
    mode_state_current_mode = current_mode_state(max_lines=500).current_mode
    cols_input = st.columns(4)
    current_mode_value = cols_input[0].selectbox(
        "Current mode preview",
        mode_values,
        index=mode_values.index(mode_state_current_mode.value),
        key="autotrade_readiness_current_mode_preview",
    )
    target_mode_value = cols_input[1].selectbox(
        "Target mode preview",
        mode_values,
        index=mode_values.index(AutoTradeMode.LIVE_MIN_SIZE.value),
        key="autotrade_readiness_target_mode_preview",
    )
    human_confirmed = cols_input[2].checkbox(
        "Human confirmed preview",
        value=False,
        key="autotrade_readiness_human_confirmed_preview",
        help="Preview only. This does not request or change mode.",
    )
    allow_warnings = cols_input[3].checkbox(
        "Allow warnings preview",
        value=False,
        key="autotrade_readiness_allow_warnings_preview",
        help="Preview only. Runtime still blocks on hard health failures.",
    )

    bundle_cols = st.columns(2)
    enforce_parameter_bundle_runtime = not bundle_cols[0].checkbox(
        "Disable parameter bundle runtime check preview",
        value=False,
        key="autotrade_readiness_disable_parameter_bundle_runtime_check_preview",
        help="Preview only. Dangerous targets normally require an active runtime parameter bundle.",
    )
    required_parameter_bundle_stage = bundle_cols[1].selectbox(
        "Required parameter bundle stage preview",
        ("shadow", "paper", "live", "rollback", "last_known_good", "pending_draft"),
        index=2,
        key="autotrade_readiness_required_parameter_bundle_stage_preview",
    )

    result = evaluate_autotrade_live_readiness(
        current_mode=current_mode_value,
        target_mode=target_mode_value,
        human_confirmed=human_confirmed,
        allow_warnings=allow_warnings,
        max_observer_run_age_sec=120,
        max_lines=500,
    )
    data = result.to_dict()
    health = data.get("health") or {}
    runtime = health.get("runtime") or {}
    health_observer_runs = health.get("observer_runs") if isinstance(health.get("observer_runs"), dict) else {}
    parameter_bundle_runtime = data.get("parameter_bundle_runtime") if isinstance(data.get("parameter_bundle_runtime"), dict) else {}
    parameter_bundle_view = _parameter_bundle_runtime_summary_view(parameter_bundle_runtime)

    cols = st.columns(5)
    cols[0].metric("Ready", str(result.ready))
    cols[1].metric("Transition", str(result.transition_allowed))
    cols[2].metric("Confirm Required", str(result.human_confirmation_required))
    cols[3].metric("Health", health.get("health_state") or "unknown")
    cols[4].metric("Mode Changed", str(result.mode_changed))

    st.caption("Readiness preflight is read-only. UI does not change mode, append readiness records, or send broker orders.")
    _render_json(
        {
            "current_mode": data.get("current_mode"),
            "mode_state_current_mode": mode_state_current_mode.value,
            "mode_state_source": "mode_state.jsonl/current_mode_state",
            "target_mode": data.get("target_mode"),
            "ready": data.get("ready"),
            "transition_allowed": data.get("transition_allowed"),
            "human_confirmation_required": data.get("human_confirmation_required"),
            "human_confirmed": data.get("human_confirmed"),
            "allow_warnings": data.get("allow_warnings"),
            "enforce_parameter_bundle_runtime": enforce_parameter_bundle_runtime,
            "required_parameter_bundle_stage": required_parameter_bundle_stage,
            "parameter_bundle_runtime": parameter_bundle_view,
            "blocked_by": data.get("blocked_by"),
            "warnings": data.get("warnings"),
            "health_state": health.get("health_state"),
            "observer_run_fresh": health.get("observer_run_fresh"),
            "readiness_observer_latest_run_id": health_observer_runs.get("latest_run_id"),
            "readiness_observer_latest_blocked_by": health_observer_runs.get("latest_blocked_by"),
            "readiness_observer_latest_would_send_to_broker": health_observer_runs.get("latest_would_send_to_broker"),
            "readiness_observer_latest_bounded": health_observer_runs.get("latest_bounded"),
            "runtime_live_ready": runtime.get("live_ready"),
            "runtime_hot_detected": runtime.get("hot_runtime_detected"),
            "runtime_cold_detected": runtime.get("cold_runtime_detected"),
            "would_send_to_broker": False,
            "read_only": True,
            "mode_changed": False,
        },
        max_height_px=320,
    )


    st.markdown("#### Mode-change command request")
    st.caption("Records a REQUEST_MODE_CHANGE command request only. This does not change mode or send broker orders.")
    if st.button("Record mode-change request", key="autotrade_record_mode_change_request"):
        st.session_state["autotrade_last_mode_change_request_record"] = _submit_mode_change_request(
            current_mode=current_mode_value,
            target_mode=target_mode_value,
            human_confirmed=human_confirmed,
            allow_warnings=allow_warnings,
        )
    mode_change_record = st.session_state.get("autotrade_last_mode_change_request_record")
    if isinstance(mode_change_record, dict):
        _render_json(mode_change_record, max_height_px=280)

def _render_operation_visibility() -> None:
    ps = initial_parameter_set_v0_1()
    st.subheader("Operation / Decision Visibility")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("5m Forecast", "contract ready")
    c2.metric("Temporal Flow", ", ".join(str(v) for v in ps.temporal_flow.windows_sec))
    c3.metric("Command Ledger", "request-only")
    c4.metric("Real Orders", "not connected")

    st.markdown("#### Current contracts")
    _render_json(
        {
            "read_model": "AutoTradeSnapshot + TemporalFlowFeatures",
            "forecast": "Forecast5m with forecast_id and T+300s target_ts",
            "strategy": "ActionCandidate + reason_codes",
            "risk": "RiskGateResult fail-closed",
            "ledger": "ShadowDecisionRecord / Performance / ForecastCalibration / CommandRequestLedger",
            "no_live_execution_in_ui": True,
        },
        max_height_px=220,
    )




def _render_observer_run_status() -> None:
    st.subheader("Observer Runs")
    summary = summarize_observer_run_ledger(max_lines=200)
    data = summary.to_dict()

    cols = st.columns(5)
    cols[0].metric("Run Rows", summary.total_rows)
    cols[1].metric("Completed Cycles", summary.latest_completed_cycles if summary.latest_completed_cycles is not None else "none")
    cols[2].metric("Shadow Appends", summary.latest_appended_shadow_decision_count if summary.latest_appended_shadow_decision_count is not None else "none")
    cols[3].metric("Outcome Appends", summary.latest_appended_forecast_outcome_count if summary.latest_appended_forecast_outcome_count is not None else "none")
    cols[4].metric("Dup Snapshot Skip", summary.latest_duplicate_snapshot_skipped_count if summary.latest_duplicate_snapshot_skipped_count is not None else "none")

    st.caption("Observer run summary is read-only. UI does not run observer cycles or append observer run records.")
    _render_json(
        {
            "ledger_path": data.get("path"),
            "exists": data.get("exists"),
            "total_rows": data.get("total_rows"),
            "skipped_rows": data.get("skipped_rows"),
            "latest_run_id": data.get("latest_run_id"),
            "latest_started_at": data.get("latest_started_at"),
            "latest_finished_at": data.get("latest_finished_at"),
            "latest_completed_cycles": data.get("latest_completed_cycles"),
            "latest_appended_shadow_decision_count": data.get("latest_appended_shadow_decision_count"),
            "latest_appended_forecast_outcome_count": data.get("latest_appended_forecast_outcome_count"),
            "latest_duplicate_snapshot_skipped_count": data.get("latest_duplicate_snapshot_skipped_count"),
            "latest_skip_duplicate_snapshot": data.get("latest_skip_duplicate_snapshot"),
            "latest_blocked_by": data.get("latest_blocked_by"),
            "latest_would_send_to_broker": data.get("latest_would_send_to_broker"),
            "latest_bounded": data.get("latest_bounded"),
            "total_completed_cycles": data.get("total_completed_cycles"),
            "total_appended_shadow_decision_count": data.get("total_appended_shadow_decision_count"),
            "total_appended_forecast_outcome_count": data.get("total_appended_forecast_outcome_count"),
            "total_duplicate_snapshot_skipped_count": data.get("total_duplicate_snapshot_skipped_count"),
            "blocked_by_counts": data.get("blocked_by_counts"),
            "error_samples": data.get("error_samples"),
            "would_send_to_broker": False,
            "read_only": True,
        },
        max_height_px=320,
    )

def _render_shadow_decision_status() -> None:
    st.subheader("Shadow Decision Ledger")
    summary = summarize_shadow_decision_ledger(max_lines=200)
    data = summary.to_dict()

    cols = st.columns(5)
    cols[0].metric("Rows", summary.total_rows)
    cols[1].metric("Latest Action", summary.latest_action or "none")
    cols[2].metric("Forecast Confidence", summary.latest_forecast_confidence or "none")
    cols[3].metric("Risk Allowed", str(summary.latest_risk_allowed))
    cols[4].metric("Skipped Rows", summary.skipped_rows)

    st.caption("Shadow ledger summary is read-only. UI does not run shadow cycles or append shadow decisions.")
    _render_json(
        {
            "ledger_path": data.get("path"),
            "exists": data.get("exists"),
            "latest_decision_id": data.get("latest_decision_id"),
            "latest_snapshot_id": data.get("latest_snapshot_id"),
            "latest_forecast_id": data.get("latest_forecast_id"),
            "latest_action": data.get("latest_action"),
            "latest_forecast_direction": data.get("latest_forecast_direction"),
            "latest_forecast_confidence": data.get("latest_forecast_confidence"),
            "latest_risk_allowed": data.get("latest_risk_allowed"),
            "latest_executable": data.get("latest_executable"),
            "action_counts": data.get("action_counts"),
            "forecast_confidence_counts": data.get("forecast_confidence_counts"),
            "blocked_by_counts": data.get("blocked_by_counts"),
            "reason_code_counts": data.get("reason_code_counts"),
            "error_samples": data.get("error_samples"),
            "would_send_to_broker": False,
            "read_only": True,
        },
        max_height_px=320,
    )


def _render_forecast_calibration_status() -> None:
    st.subheader("Forecast Outcomes / Calibration")
    summary = summarize_forecast_outcome_ledger(max_lines=500)
    data = summary.to_dict()
    calibration = data.get("calibration") or {}

    cols = st.columns(5)
    cols[0].metric("Outcome Rows", summary.total_rows)
    cols[1].metric("Hit Rate", "none" if calibration.get("hit_rate") is None else f"{calibration.get('hit_rate'):.2f}")
    cols[2].metric("Miss Rate", "none" if calibration.get("miss_rate") is None else f"{calibration.get('miss_rate'):.2f}")
    cols[3].metric("Unscorable", "none" if calibration.get("unscorable_rate") is None else f"{calibration.get('unscorable_rate'):.2f}")
    cols[4].metric("Latest Result", summary.latest_result or "none")

    st.caption("Forecast outcome summary is read-only. UI does not resolve outcomes or append forecast outcome records.")
    _render_json(
        {
            "ledger_path": data.get("path"),
            "exists": data.get("exists"),
            "total_rows": data.get("total_rows"),
            "calibration": calibration,
            "latest_forecast_id": data.get("latest_forecast_id"),
            "latest_result": data.get("latest_result"),
            "latest_forecast_direction": data.get("latest_forecast_direction"),
            "latest_forecast_confidence": data.get("latest_forecast_confidence"),
            "latest_actual_snapshot_id": data.get("latest_actual_snapshot_id"),
            "latest_divergence_reasons": data.get("latest_divergence_reasons"),
            "divergence_reason_counts": data.get("divergence_reason_counts"),
            "by_confidence": data.get("by_confidence"),
            "by_driver": data.get("by_driver"),
            "by_parameter_set": data.get("by_parameter_set"),
            "would_send_to_broker": False,
            "read_only": True,
        },
        max_height_px=360,
    )

def _render_parameter_settings() -> None:
    ps = initial_parameter_set_v0_1()
    st.subheader("Settings / Parameter Set v0.1")
    st.caption("Editable UI staging comes later. This milestone displays initial defaults and command ledger requests only.")

    settings = {
        "parameter_set_id": ps.parameter_set_id,
        "status": ps.status.value,
        "product_type": ps.product_type.value,
        "exchange": ps.exchange,
        "symbol": ps.symbol,
        "aggressiveness": ps.aggressiveness.value,
        "margin_policy": ps.margin_policy,
        "loss_limits": ps.loss_limits,
        "entry_quality": ps.entry_quality,
        "forecast": ps.forecast,
        "temporal_flow": ps.temporal_flow,
        "cancel_reprice": ps.cancel_reprice,
        "attack_mode": ps.attack_mode,
        "auto_manual": ps.auto_manual,
    }
    _render_json(settings, max_height_px=420)

    st.markdown("#### Auto / Manual preview")
    auto_execution_enabled = st.checkbox(
        "Auto execution enabled preview",
        value=False,
        key="autotrade_auto_execution_enabled_preview",
        help="Preview only. Live activation still requires command ledger/runtime validation.",
    )
    manual_approval_required = st.checkbox(
        "Manual approval required preview",
        value=True,
        key="autotrade_manual_approval_required_preview",
    )
    _render_json(
        {
            "human_control_mode_preview": (
                HumanControlMode.AUTO_ALLOWED.value if auto_execution_enabled and not manual_approval_required else HumanControlMode.MANUAL_APPROVE.value
            ),
            "auto_execution_enabled_checkbox": auto_execution_enabled,
            "manual_approval_required_checkbox": manual_approval_required,
            "does_not_bypass_risk_gates": True,
        },
        max_height_px=180,
    )


def render():
    st.title("AutoTrade")
    st.caption("Logic-driven AutoTrade observer/control-request tab. No broker execution from UI.")
    _render_top_critical_state()
    st.divider()
    _render_mode_state_status()
    st.divider()
    _render_mode_runtime_gate_status()
    st.divider()
    _render_mode_change_apply_preview_status()
    st.divider()
    _render_command_request_status()
    st.divider()
    _render_runtime_health_status()
    st.divider()
    _render_live_readiness_preflight()
    st.divider()
    _render_operation_visibility()
    st.divider()
    _render_observer_run_status()
    st.divider()
    _render_shadow_decision_status()
    st.divider()
    _render_forecast_calibration_status()
    st.divider()
    _render_parameter_settings()
