# path: ./tools/diagnose_phase4a_prediction_system_ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet.py
# desc: Read-only diagnostic for PS-Q25Y disabled single-producer 60s dry-run human gate packet.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet import (  # noqa: E402
    DRY_RUN_HUMAN_GATE_TOKEN,
    SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_HUMAN_GATE_PACKET_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25Y_DISABLED_SINGLE_PRODUCER_60S_DRY_RUN_HUMAN_GATE_PACKET_2026-06-30.md"
Q25X_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25X_DISABLED_SINGLE_PRODUCER_60S_DRY_RUN_DESIGN_CHECKPOINT_2026-06-30.md"
SRC = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet.py"
SRC_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_disabled_single_producer_60s_dry_run_human_gate_packet_diagnostic() -> dict:
    blockers: list[str] = []
    doc_text = _read(DOC)
    q25x_text = _read(Q25X_DOC)
    src_text = _read(SRC)
    src_test_text = _read(SRC_TEST)
    for marker in (
        "ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "dry_run_human_gate_packet_added=true",
        "gate_marker_only=true",
        "decision_packet_only=true",
        "human_gate_required_before_any_dry_run=true",
        "human_gate_granted_by_this_packet=false",
        "separate_execution_slice_required=true",
        "ready_for_future_disabled_manual_dry_run_gate_decision=true",
        "manual_one_shot_run_allowed=false",
        "execute_dry_run_allowed=false",
        "broker_private_api_allowed=false",
        DRY_RUN_HUMAN_GATE_TOKEN,
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "ps_q25x_disabled_single_producer_60s_dry_run_design_checkpoint=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "checkpoint_only=true",
        "ready_for_future_disabled_dry_run_execution_gate_planning=true",
        "manual_one_shot_run_allowed=false",
        "execute_dry_run_allowed=false",
    ):
        if marker not in q25x_text:
            blockers.append(f"q25x_marker_required:{marker}")
    for marker in (
        "SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_HUMAN_GATE_PACKET_VERSION",
        "DRY_RUN_HUMAN_GATE_TOKEN",
        "build_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet",
        "gate_token_detected_but_execution_requires_separate_future_slice",
        "forbidden_request_in_ps_q25y",
    ):
        if marker not in src_text:
            blockers.append(f"src_marker_required:{marker}")
    for marker in (
        "test_q25y_default_gate_packet_awaits_human_and_is_non_executing",
        "test_q25y_token_intent_still_does_not_grant_execution",
        "test_q25y_blocks_execution_write_lock_and_scheduler_requests",
    ):
        if marker not in src_test_text:
            blockers.append(f"src_test_marker_required:{marker}")
    default_packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet().to_dict()
    token_packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet(supplied_gate_token=DRY_RUN_HUMAN_GATE_TOKEN).to_dict()
    if default_packet.get("gate_version") != SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_HUMAN_GATE_PACKET_VERSION:
        blockers.append("default_packet_version_mismatch")
    if default_packet.get("gate_state") != "awaiting_human_dry_run_gate_decision":
        blockers.append("default_gate_state_required")
    if token_packet.get("gate_state") != "human_gate_intent_detected_separate_execution_slice_required":
        blockers.append("token_gate_state_required")
    if token_packet.get("execute_dry_run_allowed_by_this_packet") is not False:
        blockers.append("token_packet_must_not_allow_dry_run")
    for packet_name, packet in (("default", default_packet), ("token", token_packet)):
        for key in ("gate_marker_only", "decision_packet_only", "read_only", "non_executing", "human_gate_required_before_any_dry_run", "separate_execution_slice_required", "ready_for_future_disabled_manual_dry_run_gate_decision"):
            if packet.get(key) is not True:
                blockers.append(f"{packet_name}_packet_true_required:{key}")
        for key in ("human_gate_granted_by_this_packet", "execute_dry_run_allowed_by_this_packet", "execute_dry_run_enabled", "manual_one_shot_run_invoked_by_this_gate", "future_dry_run_invoked_by_this_gate", "status_artifact_write_performed_by_this_gate", "runtime_artifact_write_performed_by_this_gate", "prediction_artifact_write_performed_by_this_gate", "latest_manifest_written", "run_sidecars_written", "lock_file_created_by_this_gate", "lock_file_deleted_by_this_gate", "scheduler_enabled", "producer_enabled", "warroom_ui_trigger_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
            if packet.get(key) is not False:
                blockers.append(f"{packet_name}_packet_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "default_packet": default_packet,
        "token_intent_packet": token_packet,
        "safety": {
            "gate_marker_only": True,
            "decision_packet_only": True,
            "read_only": True,
            "non_executing": True,
            "human_gate_required_before_any_dry_run": True,
            "human_gate_granted_by_this_packet": False,
            "separate_execution_slice_required": True,
            "execute_dry_run_allowed_by_this_packet": False,
            "execute_dry_run_enabled": False,
            "manual_one_shot_run_invoked_by_this_gate": False,
            "status_artifact_write_performed_by_this_gate": False,
            "runtime_artifact_write_performed_by_this_gate": False,
            "prediction_artifact_write_performed_by_this_gate": False,
            "latest_manifest_written": False,
            "run_sidecars_written": False,
            "lock_file_created_by_this_gate": False,
            "lock_file_deleted_by_this_gate": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_disabled_single_producer_60s_dry_run_human_gate_packet_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
