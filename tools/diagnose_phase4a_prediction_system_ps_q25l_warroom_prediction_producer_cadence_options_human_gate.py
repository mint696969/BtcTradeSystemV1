# path: ./tools/diagnose_phase4a_prediction_system_ps_q25l_warroom_prediction_producer_cadence_options_human_gate.py
# desc: Read-only diagnostic for PS-Q25L WarRoom prediction producer cadence options human-gate decision packet.

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
    PREDICTION_WARROOM_PRODUCER_CADENCE_OPTION_DECISION_VERSION,
    build_prediction_warroom_producer_cadence_option_decision_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25l_warroom_prediction_producer_cadence_options_human_gate.v1"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25L_WARROOM_PREDICTION_PRODUCER_CADENCE_OPTIONS_HUMAN_GATE_2026-06-30.md"


def run_warroom_prediction_producer_cadence_options_human_gate_diagnostic() -> dict:
    packet = build_prediction_warroom_producer_cadence_option_decision_packet()
    blocked = build_prediction_warroom_producer_cadence_option_decision_packet(selected_option_id="single_producer_60s_candidate")
    gated_apply = build_prediction_warroom_producer_cadence_option_decision_packet(selected_option_id="single_producer_60s_candidate", explicit_human_gate_granted=True, request_apply_selected_option=True)
    contract_text = CONTRACT.read_text(encoding="utf-8-sig")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if packet.get("cadence_option_decision_version") != PREDICTION_WARROOM_PRODUCER_CADENCE_OPTION_DECISION_VERSION:
        blockers.append("cadence_option_decision_version_required")
    if packet.get("decision_state") != "cadence_options_ready_human_gate_decision_required":
        blockers.append("default_decision_state_required")
    if packet.get("option_row_count") != 4:
        blockers.append("four_option_rows_required")
    if packet.get("options_requiring_gate_count") != 3:
        blockers.append("three_gate_options_required")
    if packet.get("recommended_safe_default_option_id") != "keep_current_300s_context_only_until_gate":
        blockers.append("safe_default_option_required")
    option_ids = {row.get("option_id") for row in packet.get("option_rows", []) if isinstance(row, dict)}
    for option_id in ("keep_current_300s_context_only_until_gate", "single_producer_60s_candidate", "split_lane_30s_tactical_300s_context_candidate", "micro_15s_high_frequency_not_recommended"):
        if option_id not in option_ids:
            blockers.append(f"option_required:{option_id}")
    if blocked.get("decision_state") != "blocked_or_waiting_for_explicit_human_gate":
        blockers.append("selected_gate_option_must_block_without_gate")
    if "selected_option_requires_explicit_human_gate" not in blocked.get("blocked_reasons", []):
        blockers.append("selected_gate_option_blocker_required")
    if gated_apply.get("decision_state") != "blocked_or_waiting_for_explicit_human_gate":
        blockers.append("gated_apply_must_still_require_separate_implementation_slice")
    if "separate_implementation_slice_required_after_gate" not in gated_apply.get("blocked_reasons", []):
        blockers.append("separate_implementation_slice_blocker_required")
    for marker in ("PREDICTION_WARROOM_PRODUCER_CADENCE_OPTION_DECISION_VERSION", "CADENCE_OPTION_DECISION_CANDIDATES", "build_prediction_warroom_producer_cadence_option_decision_packet", "producer_cadence_changed"):
        if marker not in contract_text:
            blockers.append(f"contract_marker_required:{marker}")
    for marker in ("cadence_option_decision_packet_added=true", "decision_packet_only=true", "human_gate_required_before_any_change=true", "producer_cadence_changed=false", "scheduler_action_changed=false"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("planning_only", "decision_packet_only", "read_only", "non_executing", "contract_only", "display_only", "human_gate_required_before_any_change"):
        if packet.get(key) is not True:
            blockers.append(f"packet_true_required:{key}")
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "parameter_staging_write_allowed", "would_send_to_broker"):
        if packet.get(key) is not False or blocked.get(key) is not False or gated_apply.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": packet,
        "blocked_selected_option_packet": blocked,
        "gated_apply_packet": gated_apply,
        "safety": {
            "planning_only": True,
            "decision_packet_only": True,
            "contract_only": True,
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
    result = run_warroom_prediction_producer_cadence_options_human_gate_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
