# path: ./tools/diagnose_phase4a_prediction_system_ps_q25s_warroom_prediction_single_producer_60s_implementation_planning.py
# desc: Read-only diagnostic for PS-Q25S WarRoom prediction single producer 60s implementation planning.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25s_single_producer_60s_implementation_planning.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25S_WARROOM_PREDICTION_SINGLE_PRODUCER_60S_IMPLEMENTATION_PLANNING_2026-06-30.md"
Q25R_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25R_WARROOM_PREDICTION_CADENCE_PLANNING_GATE_INTAKE_2026-06-30.md"
Q25L_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25L_WARROOM_PREDICTION_PRODUCER_CADENCE_OPTIONS_HUMAN_GATE_2026-06-30.md"
Q25M_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25M_WARROOM_PREDICTION_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_2026-06-30.md"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"

TOKEN = "GRANT_Q25M_PREDICTION_CADENCE_IMPLEMENTATION_PLANNING_ONLY"
SELECTED = "single_producer_60s_candidate"


def run_warroom_prediction_single_producer_60s_implementation_planning_diagnostic() -> dict:
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    q25r_text = Q25R_DOC.read_text(encoding="utf-8-sig") if Q25R_DOC.exists() else ""
    q25l_text = Q25L_DOC.read_text(encoding="utf-8-sig") if Q25L_DOC.exists() else ""
    q25m_text = Q25M_DOC.read_text(encoding="utf-8-sig") if Q25M_DOC.exists() else ""
    contract_text = CONTRACT.read_text(encoding="utf-8-sig")
    blockers: list[str] = []
    for marker in (
        "ps_q25s_warroom_prediction_single_producer_60s_implementation_planning=true",
        "q25m_gate_token_received=true",
        f"gate_token={TOKEN}",
        "cadence_option_selected=true",
        f"selected_option_id={SELECTED}",
        "selected_option_family=single_producer",
        "selected_target_cadence_sec=60",
        "implementation_planning_only=true",
        "implementation_plan_added=true",
        "implementation_allowed_by_this_packet=false",
        "must_stop_before_code_or_scheduler_change=true",
        "requires_next_slice_for_disabled_implementation_preflight=true",
        "production_code_changed=false",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
        "scheduler_enabled=false",
        "broker_private_api_allowed=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "ps_q25r_warroom_prediction_cadence_planning_gate_intake=true",
        "q25m_gate_token_received=true",
        f"gate_token={TOKEN}",
        "implementation_planning_lane_opened=true",
        "cadence_option_selected=false",
        "selected_option_id=unselected",
        "implementation_allowed_by_this_packet=false",
    ):
        if marker not in q25r_text:
            blockers.append(f"q25r_marker_required:{marker}")
    for marker in (
        "cadence_option_decision_packet_added=true",
        SELECTED,
        "single_producer_60s_candidate: future medium-risk option; explicit gate and scheduler diff required.",
        "producer_cadence_changed=false",
        "scheduler_action_changed=false",
    ):
        if marker not in q25l_text:
            blockers.append(f"q25l_marker_required:{marker}")
    for marker in (
        "cadence_gate_awaiting_human_packet_added=true",
        "implementation_allowed_by_this_packet=false",
        "must_stop_before_implementation=true",
        TOKEN,
    ):
        if marker not in q25m_text:
            blockers.append(f"q25m_marker_required:{marker}")
    for marker in (
        "PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_VERSION",
        "RECOMMENDED_CADENCE_SEC = 300",
        "MINIMUM_CADENCE_SEC = 60",
        "implementation_allowed_by_this_packet",
        "keep_current_300s_context_only_until_gate",
    ):
        if marker not in contract_text:
            blockers.append(f"contract_marker_required:{marker}")
    packet = {
        "single_producer_60s_implementation_planning_version": "prediction_warroom.single_producer_60s_implementation_planning.ps_q25s.v1",
        "q25m_gate_token_received": True,
        "gate_token_matches_expected": True,
        "cadence_option_selected": True,
        "selected_option_id": SELECTED,
        "selected_option_family": "single_producer",
        "selected_target_cadence_sec": 60,
        "implementation_planning_only": True,
        "implementation_plan_added": True,
        "implementation_allowed_by_this_packet": False,
        "must_stop_before_code_or_scheduler_change": True,
        "requires_next_slice_for_disabled_implementation_preflight": True,
        "safe_default_until_next_slice": "keep_current_300s_context_only_until_gate",
        "future_guard_conditions": {
            "no_overlap_runs": True,
            "skip_or_fail_closed_on_overlap": True,
            "default_enabled": False,
            "scheduler_enabled_initially": False,
            "producer_enabled_initially": False,
            "runtime_artifact_write_initially": False,
            "status_artifact_write_initially": False,
            "warroom_ui_trigger": False,
            "autotrade_trigger": False,
            "broker_private_api": False,
            "ledger_append": False,
            "mode_apply": False,
            "parameter_apply": False,
            "rollback_disable_path_required": True,
            "status_visibility_required_before_enablement": True,
        },
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
            "must_stop_before_code_or_scheduler_change",
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
    result = run_warroom_prediction_single_producer_60s_implementation_planning_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
