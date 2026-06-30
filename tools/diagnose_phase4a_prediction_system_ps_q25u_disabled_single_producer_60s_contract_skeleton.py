# path: ./tools/diagnose_phase4a_prediction_system_ps_q25u_disabled_single_producer_60s_contract_skeleton.py
# desc: Read-only diagnostic for PS-Q25U disabled single-producer 60s contract/skeleton.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_contract_skeleton import (  # noqa: E402
    SELECTED_CADENCE_OPTION_ID,
    SELECTED_TARGET_CADENCE_SEC,
    SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_contract_skeleton,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25u_disabled_single_producer_60s_contract_skeleton.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25U_DISABLED_SINGLE_PRODUCER_60S_CONTRACT_SKELETON_2026-06-30.md"
Q25T_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25T_SINGLE_PRODUCER_60S_DISABLED_IMPLEMENTATION_PREFLIGHT_2026-06-30.md"
SRC = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_contract_skeleton.py"
SRC_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_contract_skeleton.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _q25t_packet() -> dict:
    return {
        "selected_option_id": SELECTED_CADENCE_OPTION_ID,
        "selected_target_cadence_sec": SELECTED_TARGET_CADENCE_SEC,
        "preflight_only": True,
        "implementation_allowed_by_this_packet": False,
        "manual_one_shot_run_allowed": False,
        "scheduler_enablement_allowed": False,
    }


def run_disabled_single_producer_60s_contract_skeleton_diagnostic() -> dict:
    doc_text = _read(DOC)
    q25t_text = _read(Q25T_DOC)
    src_text = _read(SRC)
    test_text = _read(SRC_TEST)
    blockers: list[str] = []
    for marker in (
        "ps_q25u_disabled_single_producer_60s_contract_skeleton=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "disabled_contract_skeleton_added=true",
        "production_code_skeleton_added=true",
        "contract_skeleton_only=true",
        "implementation_allowed_by_this_packet=false",
        "manual_one_shot_run_allowed=false",
        "scheduler_enablement_allowed=false",
        "producer_enablement_allowed=false",
        "runtime_artifact_write_allowed=false",
        "broker_private_api_allowed=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "ps_q25t_single_producer_60s_disabled_implementation_preflight=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "preflight_only=true",
        "implementation_allowed_by_this_packet=false",
        "manual_one_shot_run_allowed=false",
        "scheduler_enablement_allowed=false",
    ):
        if marker not in q25t_text:
            blockers.append(f"q25t_marker_required:{marker}")
    for marker in (
        "SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION",
        "SELECTED_TARGET_CADENCE_SEC = 60",
        "build_prediction_warroom_single_producer_60s_disabled_contract_skeleton",
        "request_manual_one_shot_run",
        "request_scheduler_enable",
        "request_latest_manifest_write",
        "forbidden_request_in_ps_q25u",
        "would_send_to_broker",
    ):
        if marker not in src_text:
            blockers.append(f"src_marker_required:{marker}")
    for marker in (
        "test_q25u_ready_packet_is_disabled_and_non_executing",
        "test_q25u_blocks_all_runtime_enablement_requests",
        "test_q25u_missing_preflight_remains_disabled_observation_only",
    ):
        if marker not in test_text:
            blockers.append(f"src_test_marker_required:{marker}")
    packet = build_prediction_warroom_single_producer_60s_disabled_contract_skeleton(q25t_preflight_packet=_q25t_packet()).to_dict()
    if packet.get("skeleton_version") != SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION:
        blockers.append("packet_version_mismatch")
    if packet.get("ready_for_future_disabled_single_producer_60s_skeleton_validation") is not True:
        blockers.append("packet_not_ready_for_disabled_skeleton_validation")
    for key in (
        "ready_for_manual_one_shot_run",
        "ready_for_scheduler_enablement",
        "ready_for_producer_enablement",
        "scheduler_enabled",
        "producer_enabled",
        "scheduled_loop_enabled",
        "manual_one_shot_run_invoked_by_this_skeleton",
        "prediction_build_requested",
        "actual_export_runner_invoked",
        "bounded_manual_refresh_invoked",
        "would_write_runtime_artifact",
        "would_write_status_artifact",
        "would_write_prediction_artifact",
        "would_write_view_artifact",
        "latest_manifest_written",
        "run_sidecars_written",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "parameter_apply_allowed",
        "mode_apply_allowed",
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
            "contract_skeleton_only",
            "read_only",
            "non_executing",
            "default_enabled",
            "ready_for_manual_one_shot_run",
            "ready_for_scheduler_enablement",
            "ready_for_producer_enablement",
            "scheduler_enabled",
            "producer_enabled",
            "scheduled_loop_enabled",
            "manual_one_shot_run_invoked_by_this_skeleton",
            "prediction_build_requested",
            "actual_export_runner_invoked",
            "bounded_manual_refresh_invoked",
            "would_write_runtime_artifact",
            "would_write_status_artifact",
            "would_write_prediction_artifact",
            "would_write_view_artifact",
            "latest_manifest_written",
            "run_sidecars_written",
            "warroom_ui_trigger_enabled",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
            "ledger_append_allowed",
            "parameter_apply_allowed",
            "mode_apply_allowed",
            "would_send_to_broker",
        )},
    }


def main() -> int:
    result = run_disabled_single_producer_60s_contract_skeleton_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
