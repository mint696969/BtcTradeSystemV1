# path: ./tools/diagnose_phase4a_prediction_system_ps_q25r_warroom_prediction_cadence_planning_gate_intake.py
# desc: Read-only diagnostic for PS-Q25R WarRoom prediction cadence planning gate intake.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25r_cadence_planning_gate_intake.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25R_WARROOM_PREDICTION_CADENCE_PLANNING_GATE_INTAKE_2026-06-30.md"
Q25L_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25L_WARROOM_PREDICTION_PRODUCER_CADENCE_OPTIONS_HUMAN_GATE_2026-06-30.md"
Q25M_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25M_WARROOM_PREDICTION_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_2026-06-30.md"
Q25Q_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25Q_WARROOM_PREDICTION_DISPLAY_CLOSEOUT_HANDOFF_2026-06-30.md"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"

TOKEN = "GRANT_Q25M_PREDICTION_CADENCE_IMPLEMENTATION_PLANNING_ONLY"
OPTIONS = (
    "keep_current_300s_context_only_until_gate",
    "single_producer_60s_candidate",
    "split_lane_30s_tactical_300s_context_candidate",
    "micro_15s_high_frequency_not_recommended",
)


def run_warroom_prediction_cadence_planning_gate_intake_diagnostic() -> dict:
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    q25l_text = Q25L_DOC.read_text(encoding="utf-8-sig") if Q25L_DOC.exists() else ""
    q25m_text = Q25M_DOC.read_text(encoding="utf-8-sig") if Q25M_DOC.exists() else ""
    q25q_text = Q25Q_DOC.read_text(encoding="utf-8-sig") if Q25Q_DOC.exists() else ""
    contract_text = CONTRACT.read_text(encoding="utf-8-sig")
    blockers: list[str] = []
    for marker in (
        "ps_q25r_warroom_prediction_cadence_planning_gate_intake=true",
        "q25m_gate_token_received=true",
        f"gate_token={TOKEN}",
        "planning_intake_only=true",
        "implementation_planning_lane_opened=true",
        "cadence_option_selected=false",
        "selected_option_id=unselected",
        "option_selection_required_before_implementation_plan=true",
        "implementation_allowed_by_this_packet=false",
        "must_stop_before_producer_or_scheduler_change=true",
        "production_code_changed=false",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
        "scheduler_enabled=false",
        "broker_private_api_allowed=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for option in OPTIONS:
        if option not in doc_text:
            blockers.append(f"doc_option_required:{option}")
        if option not in q25l_text:
            blockers.append(f"q25l_option_required:{option}")
    for marker in (
        "cadence_option_decision_packet_added=true",
        "human_gate_required_before_any_change=true",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
    ):
        if marker not in q25l_text:
            blockers.append(f"q25l_marker_required:{marker}")
    for marker in (
        "cadence_gate_awaiting_human_packet_added=true",
        "human_decision_recorded=false",
        "implementation_allowed_by_this_packet=false",
        "must_stop_before_implementation=true",
        TOKEN,
    ):
        if marker not in q25m_text:
            blockers.append(f"q25m_marker_required:{marker}")
    for marker in (
        "display_lane_closed_out=true",
        "cadence_lane_stopped_at_human_gate=true",
        "safe_default_option_id=keep_current_300s_context_only_until_gate",
    ):
        if marker not in q25q_text:
            blockers.append(f"q25q_marker_required:{marker}")
    for marker in (
        "PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_VERSION",
        "implementation_allowed_by_this_packet",
        "keep_current_300s_context_only_until_gate",
    ):
        if marker not in contract_text:
            blockers.append(f"contract_marker_required:{marker}")
    packet = {
        "cadence_planning_gate_intake_version": "prediction_warroom.cadence_planning_gate_intake.ps_q25r.v1",
        "q25m_gate_token_received": True,
        "gate_token_matches_expected": True,
        "planning_intake_only": True,
        "implementation_planning_lane_opened": True,
        "cadence_option_selected": False,
        "selected_option_id": "unselected",
        "option_selection_required_before_implementation_plan": True,
        "available_options": list(OPTIONS),
        "implementation_allowed_by_this_packet": False,
        "must_stop_before_producer_or_scheduler_change": True,
        "safe_default_option_id": "keep_current_300s_context_only_until_gate",
        "production_code_changed": False,
        "producer_cadence_changed": False,
        "scheduler_action_changed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": packet,
        "safety": {key: packet[key] for key in (
            "production_code_changed",
            "implementation_allowed_by_this_packet",
            "must_stop_before_producer_or_scheduler_change",
            "producer_cadence_changed",
            "scheduler_action_changed",
            "scheduler_enabled",
            "producer_enabled",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "prediction_artifact_write_allowed",
            "view_artifact_write_allowed",
            "latest_manifest_written",
            "run_sidecars_written",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
            "ledger_append_allowed",
            "mode_apply_allowed",
            "parameter_apply_allowed",
            "would_send_to_broker",
        )},
    }


def main() -> int:
    result = run_warroom_prediction_cadence_planning_gate_intake_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
