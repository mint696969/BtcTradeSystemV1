# path: ./tools/diagnose_phase4a_prediction_system_ps_q25w_disabled_single_producer_60s_dry_run_planning.py
# desc: Read-only diagnostic for PS-Q25W disabled single-producer 60s dry-run planning.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet import (  # noqa: E402
    SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25w_disabled_single_producer_60s_dry_run_planning.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25W_DISABLED_SINGLE_PRODUCER_60S_DRY_RUN_PLANNING_2026-06-30.md"
Q25V_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25V_DISABLED_SINGLE_PRODUCER_60S_SKELETON_VALIDATION_2026-06-30.md"
SRC = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet.py"
SRC_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_disabled_single_producer_60s_dry_run_planning_diagnostic() -> dict:
    blockers: list[str] = []
    doc_text = _read(DOC)
    q25v_text = _read(Q25V_DOC)
    src_text = _read(SRC)
    src_test_text = _read(SRC_TEST)
    for marker in (
        "ps_q25w_disabled_single_producer_60s_dry_run_planning=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "disabled_dry_run_planning_packet_added=true",
        "dry_run_planning_only=true",
        "read_only=true",
        "non_executing=true",
        "ready_for_future_disabled_dry_run_design_checkpoint=true",
        "manual_one_shot_run_allowed=false",
        "execute_dry_run_allowed=false",
        "scheduler_enablement_allowed=false",
        "producer_enablement_allowed=false",
        "lock_file_created=false",
        "lock_file_deleted=false",
        "broker_private_api_allowed=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "ps_q25v_disabled_single_producer_60s_skeleton_validation=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "validation_only=true",
        "ready_for_disabled_dry_run_planning=true",
        "manual_one_shot_run_allowed=false",
        "scheduler_enablement_allowed=false",
        "producer_enablement_allowed=false",
    ):
        if marker not in q25v_text:
            blockers.append(f"q25v_marker_required:{marker}")
    for marker in (
        "SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION",
        "build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet",
        "GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION",
        "PLAN_STEPS",
        "forbidden_request_in_ps_q25w",
        "ready_for_future_disabled_dry_run_design_checkpoint",
    ):
        if marker not in src_text:
            blockers.append(f"src_marker_required:{marker}")
    for marker in (
        "test_q25w_planning_ready_and_non_executing",
        "test_q25w_references_q16l_plan_without_invoking_it",
        "test_q25w_blocks_execution_write_lock_and_scheduler_requests",
    ):
        if marker not in src_test_text:
            blockers.append(f"src_test_marker_required:{marker}")
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet().to_dict()
    if packet.get("planning_version") != SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION:
        blockers.append("packet_version_mismatch")
    if packet.get("ready_for_future_disabled_dry_run_design_checkpoint") is not True:
        blockers.append("packet_not_ready_for_future_disabled_dry_run_design_checkpoint")
    for key in (
        "execute_dry_run_enabled",
        "manual_one_shot_run_invoked_by_this_planning",
        "future_dry_run_invoked_by_this_planning",
        "q16l_execution_plan_invoked_by_this_planning",
        "status_artifact_write_performed_by_this_planning",
        "runtime_artifact_write_performed_by_this_planning",
        "prediction_artifact_write_performed_by_this_planning",
        "latest_manifest_written",
        "run_sidecars_written",
        "lock_file_created_by_this_planning",
        "lock_file_deleted_by_this_planning",
        "scheduler_enabled",
        "producer_enabled",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        if packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": packet,
        "safety": {key: packet[key] for key in (
            "dry_run_planning_only",
            "read_only",
            "non_executing",
            "ready_for_future_disabled_dry_run_design_checkpoint",
            "execute_dry_run_enabled",
            "manual_one_shot_run_invoked_by_this_planning",
            "future_dry_run_invoked_by_this_planning",
            "q16l_execution_plan_invoked_by_this_planning",
            "status_artifact_write_performed_by_this_planning",
            "runtime_artifact_write_performed_by_this_planning",
            "prediction_artifact_write_performed_by_this_planning",
            "latest_manifest_written",
            "run_sidecars_written",
            "lock_file_created_by_this_planning",
            "lock_file_deleted_by_this_planning",
            "scheduler_enabled",
            "producer_enabled",
            "warroom_ui_trigger_enabled",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
            "ledger_append_allowed",
            "mode_apply_allowed",
            "parameter_apply_allowed",
            "would_send_to_broker",
        )},
    }


def main() -> int:
    result = run_disabled_single_producer_60s_dry_run_planning_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
