# path: ./tools/diagnose_phase4a_prediction_system_ps_q25x_disabled_single_producer_60s_dry_run_design_checkpoint.py
# desc: Read-only diagnostic for PS-Q25X disabled single-producer 60s dry-run design checkpoint.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint import (  # noqa: E402
    SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25x_disabled_single_producer_60s_dry_run_design_checkpoint.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25X_DISABLED_SINGLE_PRODUCER_60S_DRY_RUN_DESIGN_CHECKPOINT_2026-06-30.md"
Q25W_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25W_DISABLED_SINGLE_PRODUCER_60S_DRY_RUN_PLANNING_2026-06-30.md"
SRC = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint.py"
SRC_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_disabled_single_producer_60s_dry_run_design_checkpoint_diagnostic() -> dict:
    blockers: list[str] = []
    doc_text = _read(DOC)
    q25w_text = _read(Q25W_DOC)
    src_text = _read(SRC)
    src_test_text = _read(SRC_TEST)
    for marker in (
        "ps_q25x_disabled_single_producer_60s_dry_run_design_checkpoint=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "disabled_dry_run_design_checkpoint_added=true",
        "checkpoint_only=true",
        "read_only=true",
        "non_executing=true",
        "ready_for_future_disabled_dry_run_execution_gate_planning=true",
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
        "ps_q25w_disabled_single_producer_60s_dry_run_planning=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "dry_run_planning_only=true",
        "ready_for_future_disabled_dry_run_design_checkpoint=true",
        "manual_one_shot_run_allowed=false",
        "execute_dry_run_allowed=false",
        "scheduler_enablement_allowed=false",
    ):
        if marker not in q25w_text:
            blockers.append(f"q25w_marker_required:{marker}")
    for marker in (
        "SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION",
        "build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint",
        "ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION",
        "FUTURE_EXECUTION_BOUNDARY",
        "forbidden_request_in_ps_q25x",
        "ready_for_future_disabled_dry_run_execution_gate_planning",
    ):
        if marker not in src_text:
            blockers.append(f"src_marker_required:{marker}")
    for marker in (
        "test_q25x_checkpoint_ready_and_non_executing",
        "test_q25x_references_q16k_boundary_without_invoking_it",
        "test_q25x_blocks_execution_write_lock_and_scheduler_requests",
    ):
        if marker not in src_test_text:
            blockers.append(f"src_test_marker_required:{marker}")
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint().to_dict()
    if packet.get("checkpoint_version") != SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION:
        blockers.append("packet_version_mismatch")
    if packet.get("ready_for_future_disabled_dry_run_execution_gate_planning") is not True:
        blockers.append("packet_not_ready_for_future_disabled_dry_run_execution_gate_planning")
    for key in (
        "execute_dry_run_enabled",
        "manual_one_shot_run_invoked_by_this_checkpoint",
        "future_dry_run_invoked_by_this_checkpoint",
        "q16k_checkpoint_invoked_by_this_checkpoint",
        "status_artifact_write_performed_by_this_checkpoint",
        "runtime_artifact_write_performed_by_this_checkpoint",
        "prediction_artifact_write_performed_by_this_checkpoint",
        "latest_manifest_written",
        "run_sidecars_written",
        "lock_file_created_by_this_checkpoint",
        "lock_file_deleted_by_this_checkpoint",
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
            "checkpoint_only",
            "read_only",
            "non_executing",
            "ready_for_future_disabled_dry_run_execution_gate_planning",
            "execute_dry_run_enabled",
            "manual_one_shot_run_invoked_by_this_checkpoint",
            "future_dry_run_invoked_by_this_checkpoint",
            "q16k_checkpoint_invoked_by_this_checkpoint",
            "status_artifact_write_performed_by_this_checkpoint",
            "runtime_artifact_write_performed_by_this_checkpoint",
            "prediction_artifact_write_performed_by_this_checkpoint",
            "latest_manifest_written",
            "run_sidecars_written",
            "lock_file_created_by_this_checkpoint",
            "lock_file_deleted_by_this_checkpoint",
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
    result = run_disabled_single_producer_60s_dry_run_design_checkpoint_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
