# path: ./tools/diagnose_phase4a_prediction_system_ps_q25m_warroom_prediction_producer_cadence_gate_awaiting_human.py
# desc: Read-only diagnostic for PS-Q25M WarRoom prediction producer cadence gate awaiting human decision.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_VERSION,
    PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_DECISION_TOKEN,
    build_prediction_warroom_producer_cadence_gate_awaiting_human_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25m_warroom_prediction_producer_cadence_gate_awaiting_human.v1"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25M_WARROOM_PREDICTION_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_2026-06-30.md"


def run_warroom_prediction_producer_cadence_gate_awaiting_human_diagnostic() -> dict:
    default_packet = build_prediction_warroom_producer_cadence_gate_awaiting_human_packet()
    safe_default = build_prediction_warroom_producer_cadence_gate_awaiting_human_packet(operator_selected_option_id="keep_current_300s_context_only_until_gate")
    gated_intent = build_prediction_warroom_producer_cadence_gate_awaiting_human_packet(operator_selected_option_id="single_producer_60s_candidate", explicit_gate_token=PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_DECISION_TOKEN)
    implementation_request = build_prediction_warroom_producer_cadence_gate_awaiting_human_packet(operator_selected_option_id="single_producer_60s_candidate", explicit_gate_token=PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_DECISION_TOKEN, request_start_implementation=True)
    contract_text = CONTRACT.read_text(encoding="utf-8-sig")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if default_packet.get("cadence_gate_awaiting_human_version") != PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_VERSION:
        blockers.append("cadence_gate_awaiting_human_version_required")
    if default_packet.get("gate_state") != "awaiting_human_cadence_gate_decision":
        blockers.append("default_gate_state_required")
    if default_packet.get("human_decision_recorded") is not False:
        blockers.append("human_decision_must_not_be_recorded")
    if default_packet.get("implementation_allowed_by_this_packet") is not False:
        blockers.append("implementation_must_not_be_allowed")
    if default_packet.get("must_stop_before_implementation") is not True:
        blockers.append("must_stop_before_implementation_required")
    if safe_default.get("gate_state") != "safe_default_selected_no_change":
        blockers.append("safe_default_state_required")
    if gated_intent.get("gate_state") != "human_gate_intent_detected_separate_implementation_slice_required":
        blockers.append("gated_intent_state_required")
    if "separate_implementation_slice_required_after_human_gate" not in gated_intent.get("blocked_reasons", []):
        blockers.append("separate_slice_blocker_required")
    if implementation_request.get("implementation_allowed_by_this_packet") is not False:
        blockers.append("implementation_request_must_still_not_be_allowed")
    if "implementation_request_blocked_separate_slice_required" not in implementation_request.get("blocked_reasons", []):
        blockers.append("implementation_request_blocker_required")
    for marker in ("PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_AWAITING_HUMAN_VERSION", "PREDICTION_WARROOM_PRODUCER_CADENCE_GATE_DECISION_TOKEN", "build_prediction_warroom_producer_cadence_gate_awaiting_human_packet", "implementation_allowed_by_this_packet"):
        if marker not in contract_text:
            blockers.append(f"contract_marker_required:{marker}")
    for marker in ("cadence_gate_awaiting_human_packet_added=true", "gate_marker_only=true", "human_decision_recorded=false", "implementation_allowed_by_this_packet=false", "must_stop_before_implementation=true", "producer_cadence_changed=false", "scheduler_action_changed=false"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for packet_name, packet in (("default", default_packet), ("safe", safe_default), ("gated", gated_intent), ("implementation", implementation_request)):
        for key in ("planning_only", "gate_marker_only", "decision_packet_only", "read_only", "non_executing", "contract_only", "display_only", "human_gate_required_before_any_change", "must_stop_before_implementation"):
            if packet.get(key) is not True:
                blockers.append(f"{packet_name}_packet_true_required:{key}")
        for key in ("human_decision_recorded", "implementation_allowed_by_this_packet", "producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "parameter_staging_write_allowed", "would_send_to_broker"):
            if packet.get(key) is not False:
                blockers.append(f"{packet_name}_packet_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "default_packet": default_packet,
        "safe_default_packet": safe_default,
        "gated_intent_packet": gated_intent,
        "implementation_request_packet": implementation_request,
        "safety": {
            "planning_only": True,
            "gate_marker_only": True,
            "decision_packet_only": True,
            "human_decision_recorded": False,
            "implementation_allowed_by_this_packet": False,
            "must_stop_before_implementation": True,
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
        },
    }


def main() -> int:
    result = run_warroom_prediction_producer_cadence_gate_awaiting_human_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
