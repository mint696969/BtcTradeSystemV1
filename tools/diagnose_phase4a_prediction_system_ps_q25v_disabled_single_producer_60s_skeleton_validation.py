# path: ./tools/diagnose_phase4a_prediction_system_ps_q25v_disabled_single_producer_60s_skeleton_validation.py
# desc: Read-only diagnostic for PS-Q25V disabled single-producer 60s skeleton validation.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_validation_packet import (  # noqa: E402
    SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_validation_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25v_disabled_single_producer_60s_skeleton_validation.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25V_DISABLED_SINGLE_PRODUCER_60S_SKELETON_VALIDATION_2026-06-30.md"
Q25U_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25U_DISABLED_SINGLE_PRODUCER_60S_CONTRACT_SKELETON_2026-06-30.md"
SRC = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_validation_packet.py"
SRC_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_validation_packet.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_disabled_single_producer_60s_skeleton_validation_diagnostic() -> dict:
    blockers: list[str] = []
    doc_text = _read(DOC)
    q25u_text = _read(Q25U_DOC)
    src_text = _read(SRC)
    src_test_text = _read(SRC_TEST)
    for marker in (
        "ps_q25v_disabled_single_producer_60s_skeleton_validation=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "disabled_validation_packet_added=true",
        "validation_only=true",
        "read_only=true",
        "non_executing=true",
        "ready_for_disabled_dry_run_planning=true",
        "manual_one_shot_run_allowed=false",
        "scheduler_enablement_allowed=false",
        "producer_enablement_allowed=false",
        "scheduler_enabled=false",
        "producer_enabled=false",
        "runtime_artifact_write_allowed=false",
        "broker_private_api_allowed=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "ps_q25u_disabled_single_producer_60s_contract_skeleton=true",
        "selected_option_id=single_producer_60s_candidate",
        "selected_target_cadence_sec=60",
        "contract_skeleton_only=true",
        "manual_one_shot_run_allowed=false",
        "scheduler_enablement_allowed=false",
        "producer_enablement_allowed=false",
    ):
        if marker not in q25u_text:
            blockers.append(f"q25u_marker_required:{marker}")
    for marker in (
        "SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION",
        "build_prediction_warroom_single_producer_60s_disabled_validation_packet",
        "build_prediction_warroom_non_ui_scheduled_producer_runner().to_dict()",
        "forbidden_request_in_ps_q25v",
        "ready_for_disabled_dry_run_planning",
    ):
        if marker not in src_text:
            blockers.append(f"src_marker_required:{marker}")
    for marker in (
        "test_q25v_validation_ready_and_non_executing",
        "test_q25v_embeds_disabled_skeleton_and_runner_packets",
        "test_q25v_blocks_forbidden_requests",
    ):
        if marker not in src_test_text:
            blockers.append(f"src_test_marker_required:{marker}")
    packet = build_prediction_warroom_single_producer_60s_disabled_validation_packet().to_dict()
    if packet.get("validation_version") != SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION:
        blockers.append("packet_version_mismatch")
    if packet.get("ready_for_disabled_dry_run_planning") is not True:
        blockers.append("packet_not_ready_for_disabled_dry_run_planning")
    for key in (
        "manual_one_shot_run_invoked_by_this_validation",
        "q16b_runner_invoked_for_actual_refresh",
        "q16b_status_artifact_written",
        "q16b_latest_prediction_artifact_written",
        "scheduler_enabled",
        "producer_enabled",
        "runtime_artifact_write_enabled",
        "status_artifact_write_enabled",
        "prediction_artifact_write_enabled",
        "latest_manifest_written",
        "run_sidecars_written",
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
            "validation_only",
            "read_only",
            "non_executing",
            "ready_for_disabled_dry_run_planning",
            "manual_one_shot_run_invoked_by_this_validation",
            "q16b_runner_invoked_for_actual_refresh",
            "q16b_status_artifact_written",
            "q16b_latest_prediction_artifact_written",
            "scheduler_enabled",
            "producer_enabled",
            "runtime_artifact_write_enabled",
            "status_artifact_write_enabled",
            "prediction_artifact_write_enabled",
            "latest_manifest_written",
            "run_sidecars_written",
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
    result = run_disabled_single_producer_60s_skeleton_validation_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
