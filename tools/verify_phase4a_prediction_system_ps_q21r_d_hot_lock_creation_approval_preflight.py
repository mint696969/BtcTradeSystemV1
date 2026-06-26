# path: ./tools/verify_phase4a_prediction_system_ps_q21r_d_hot_lock_creation_approval_preflight.py
# desc: PS-Q21R read-only D-hot lock creation approval/rollback preflight. No D-hot lock creation, no acquire/release, no scheduler registration, no producer loop, no runner invocation, no artifact writes, no AutoTrade/broker.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.verify_phase4a_prediction_system_ps_q21q_read_only_lock_scheduler_status_visibility import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    LOCK_RELATIVE_PATH,
    build_lock_scheduler_status_visibility_packet,
    run_visibility,
)

PREFLIGHT_VERSION = "prediction_warroom.d_hot_lock_creation_approval_preflight.ps_q21r.v1"
REQUIRED_OPERATOR_CONFIRMATION = "CREATE_D_HOT_LOCK_FILE_ONCE_WITH_ROLLBACK_PLAN"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _false_boundary_fields() -> dict[str, Any]:
    return {
        "d_hot_lock_file_creation_allowed_now": False,
        "d_hot_lock_file_write_allowed_now": False,
        "lock_acquire_allowed_now": False,
        "lock_release_allowed_now": False,
        "scheduler_registration_allowed": False,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "producer_loop_allowed": False,
        "recurring_enablement_allowed_now": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
        "d_hot_lock_file_created": False,
        "d_hot_lock_file_written": False,
        "lock_acquire_attempted": False,
        "lock_release_attempted": False,
        "scheduler_registered": False,
        "scheduler_started": False,
        "scheduled_loop_enabled": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "bounded_manual_refresh_invoked": False,
        "actual_export_runner_invoked": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "warroom_ui_trigger_invoked": False,
    }


def build_d_hot_lock_creation_approval_preflight(*, visibility_packet: Mapping[str, Any]) -> dict[str, Any]:
    visibility = _as_mapping(visibility_packet)
    blockers: list[str] = []
    if visibility.get("ok") is not True:
        blockers.append("visibility_packet_ok_required")
    if visibility.get("visibility_state") != "lock_scheduler_status_visible_non_stale_disabled_no_lock":
        blockers.append("visibility_state_non_stale_disabled_no_lock_required")
    if visibility.get("latest_prediction_non_stale") is not True:
        blockers.append("latest_prediction_non_stale_required")
    if visibility.get("latest_status_success_observed") is not True:
        blockers.append("latest_status_success_required")
    if visibility.get("disabled_boundary_preserved") is not True:
        blockers.append("disabled_boundary_preserved_required")
    if visibility.get("d_hot_lock_artifact_exists") is not False:
        blockers.append("d_hot_lock_artifact_absent_required_before_creation_preflight")
    if visibility.get("scheduler_enabled") is not False:
        blockers.append("scheduler_disabled_required")
    if visibility.get("producer_enabled") is not False:
        blockers.append("producer_disabled_required")
    preflight_ready = not blockers
    return {
        "ok": True,
        "preflight_version": PREFLIGHT_VERSION,
        "preflight_state": "d_hot_lock_creation_preflight_ready_for_separate_approval_no_creation" if preflight_ready else "d_hot_lock_creation_preflight_blocked_no_creation",
        "preflight_ready_for_separate_approval": preflight_ready,
        "preflight_blockers": blockers,
        "separate_operator_approval_required": True,
        "required_operator_confirmation": REQUIRED_OPERATOR_CONFIRMATION,
        "rollback_plan_required": True,
        "hot_root": str(DEFAULT_HOT_ROOT),
        "d_hot_lock_artifact_path_design": str(DEFAULT_HOT_ROOT / LOCK_RELATIVE_PATH),
        "visibility_state": str(visibility.get("visibility_state") or ""),
        "visibility_attention_reasons": list(visibility.get("visibility_attention_reasons") or []),
        "generated_at": str(visibility.get("generated_at") or ""),
        "age_sec": visibility.get("age_sec"),
        "latest_prediction_non_stale": visibility.get("latest_prediction_non_stale") is True,
        "latest_status_success_observed": visibility.get("latest_status_success_observed") is True,
        "disabled_boundary_preserved": visibility.get("disabled_boundary_preserved") is True,
        "d_hot_lock_artifact_exists": visibility.get("d_hot_lock_artifact_exists") is True,
        "producer_state": str(visibility.get("producer_state") or ""),
        "producer_enabled": visibility.get("producer_enabled") is True,
        "scheduler_enabled": visibility.get("scheduler_enabled") is True,
        "output_count": int(visibility.get("output_count") or 0),
        "status_warnings": list(visibility.get("status_warnings") or []),
        "approval_preflight_contract": {
            "operator_confirmation_required": REQUIRED_OPERATOR_CONFIRMATION,
            "clean_worktree_required": True,
            "visibility_packet_non_stale_disabled_no_lock_required": True,
            "d_hot_lock_absent_required_before_creation": True,
            "single_file_creation_scope_required": True,
            "create_one_lock_file_only": True,
            "write_lock_owner_fields_required": ["run_id", "pid", "host", "started_at_utc", "expires_at_utc", "reason"],
            "post_create_readback_required": True,
            "post_create_visibility_recheck_required": True,
            "rollback_plan_required": True,
            "rollback_remove_lock_file_only": True,
            "scheduler_registration_still_separate_approval": True,
            "producer_loop_enablement_still_separate_approval": True,
        },
        "rollback_plan": {
            "rollback_trigger_examples": [
                "created_lock_payload_invalid",
                "post_create_readback_failed",
                "visibility_recheck_unexpected",
                "operator_abort_before_scheduler_registration",
            ],
            "rollback_scope": "delete_only_the_new_d_hot_lock_file_if_it_was_created_by_the_approved_slice",
            "rollback_must_not_delete_prediction_or_status_artifacts": True,
            "rollback_must_not_register_scheduler": True,
            "rollback_must_not_enable_producer_loop": True,
            "rollback_must_not_touch_broker_or_autotrade": True,
        },
        "next_allowed_slice_after_explicit_approval": "single_d_hot_lock_file_creation_smoke_no_acquire_no_scheduler_no_producer",
        "read_only_approval_preflight_only": True,
        **_false_boundary_fields(),
    }


def run_preflight(*, hot_root: Path | None = None) -> dict[str, Any]:
    visibility = run_visibility(hot_root=hot_root or DEFAULT_HOT_ROOT)
    result = build_d_hot_lock_creation_approval_preflight(visibility_packet=visibility)
    result["latest_prediction_artifact_path"] = visibility.get("latest_prediction_artifact_path")
    result["status_artifact_path"] = visibility.get("status_artifact_path")
    result["d_hot_lock_artifact_path"] = visibility.get("d_hot_lock_artifact_path")
    return result


def main() -> int:
    result = run_preflight()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
